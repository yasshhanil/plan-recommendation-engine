"""
Management command to seed cities and areas, then fetch venues for each.
Run with: python manage.py add_areas --city chicago
          python manage.py add_areas --city london
          python manage.py add_areas             (all cities)
          python manage.py add_areas --no-fetch  (skip venue fetch)
"""

from django.core.management.base import BaseCommand
from recommendations.models import Country, City, Area
from recommendations.management.commands.fetch_venues import DataFetcher


CITIES = {
    'chicago': {
        'country': {'name': 'United States', 'code': 'US', 'timezone': 'America/Chicago', 'currency': 'USD'},
        'city': {'name': 'Chicago', 'state': 'Illinois', 'lat': 41.8781, 'lng': -87.6298},
        'max_distance_km': 1.5,   # mid-density city — neighbourhoods are distinct but not NYC-tight
        'areas': [
            # {'name': 'Wicker Park',  'lat': 41.9088, 'lng': -87.6777},
            # {'name': 'River North',  'lat': 41.8919, 'lng': -87.6348},
            {'name': 'Logan Square', 'lat': 41.9216, 'lng': -87.7076},
            {'name': 'West Loop',    'lat': 41.8827, 'lng': -87.6494},
            {'name': 'Lincoln Park', 'lat': 41.9217, 'lng': -87.6517},
            {'name': 'Pilsen',       'lat': 41.8563, 'lng': -87.6586},
        ],
    },
}

MAX_VENUES_PER_QUERY = 20


def build_queries(area_name, city_name):
    loc = f"{area_name} {city_name}"
    return [
        ("CAFES", [
            f"specialty coffee cafes within 15 minutes max of {loc}",
            f"cozy cafes for sitting and coffee within 15 minutes max of {loc}",
            f"aesthetic brunch cafes within 15 minutes max of {loc}",
        ]),
        ("RESTAURANTS", [
            f"popular dine in restaurants within 15 minutes max of {loc}",
            f"casual lunch dinner restaurants within 15 minutes max of {loc}",
            f"well rated restaurants for outings within 15 minutes max of {loc}",
        ]),
        ("DESSERTS", [
            f"dessert cafes pastry bakeries within 15 minutes max of {loc}",
            f"ice cream gelato dessert spots within 15 minutes max of {loc}",
            f"late evening dessert places within 15 minutes max of {loc}",
        ]),
        ("BARS", [
            f"cocktail bars lounges within 15 minutes max of {loc}",
            f"popular nightlife bars within 15 minutes max of {loc}",
            f"upscale bars for evening outings within 15 minutes max of {loc}",
        ]),
        ("ACTIVITIES", [
            f"escape rooms mystery rooms puzzle games within 15 minutes max of {loc}",
            f"bowling billiards pool snooker indoor sports within 15 minutes max of {loc}",
            f"live music venues gigs concerts within 15 minutes max of {loc}",
            f"theatre plays drama performance venues within 15 minutes max of {loc}",
            f"stand up comedy open mic venues within 15 minutes max of {loc}",
            f"art workshops pottery creative workshops within 15 minutes max of {loc}",
            f"virtual reality gaming VR experiences within 15 minutes max of {loc}",
            f"bookstores book cafes reading lounges within 15 minutes max of {loc}",
            f"karaoke lounges singing rooms within 15 minutes max of {loc}",
            f"board game cafes game lounges within 15 minutes max of {loc}",
            f"rock climbing bouldering indoor adventure within 15 minutes max of {loc}",
            f"cooking classes culinary workshops within 15 minutes max of {loc}",
        ]),
        ("ARCADES", [
            f"gaming arcades within 15 minutes max of {loc}",
            f"bowling arcade gaming zones within 15 minutes max of {loc}",
        ]),
        ("CINEMAS", [
            f"movie theatres multiplex within 15 minutes max of {loc}",
            f"cinema halls within 15 minutes max of {loc}",
        ]),
        ("PARKS", [
            f"major parks gardens within 15 minutes max of {loc}",
            f"popular outdoor walking parks within 15 minutes max of {loc}",
        ]),
        ("SHOPPING", [
            f"shopping markets within 15 minutes max of {loc}",
            f"popular retail markets within 15 minutes max of {loc}",
        ]),
    ]


class Command(BaseCommand):
    help = 'Seed cities/areas and fetch venues from Google Places API'

    def add_arguments(self, parser):
        parser.add_argument('--city', type=str, help='City key to process (london, chicago). Omit for all.')
        parser.add_argument('--no-fetch', action='store_true', help='Only create areas, skip venue fetching.')
        parser.add_argument('--dry-run', action='store_true', help='Print queries without saving anything.')

    def handle(self, *args, **options):
        city_key = options.get('city')
        targets = {city_key: CITIES[city_key]} if city_key and city_key in CITIES else CITIES

        fetcher = None
        if not options['no_fetch'] and not options['dry_run']:
            try:
                fetcher = DataFetcher()
            except ValueError as e:
                self.stdout.write(self.style.ERROR(str(e)))
                return

        for key, data in targets.items():
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Processing: {data['city']['name']}")
            self.stdout.write(f"{'='*60}")
            max_distance_km = data.get('max_distance_km', 2.0)

            # Country
            country, created = Country.objects.get_or_create(
                code=data['country']['code'],
                defaults={
                    'name': data['country']['name'],
                    'timezone': data['country']['timezone'],
                    'currency': data['country']['currency'],
                }
            )
            self.stdout.write(f"{'Created' if created else 'Found'} country: {country.name}")

            # City
            city, created = City.objects.get_or_create(
                name=data['city']['name'],
                country=country,
                defaults={
                    'state': data['city']['state'],
                    'lat': data['city']['lat'],
                    'lng': data['city']['lng'],
                    'is_active': True,
                }
            )
            self.stdout.write(f"{'Created' if created else 'Found'} city: {city.name}")

            for area_data in data['areas']:
                area, created = Area.objects.get_or_create(
                    name=area_data['name'],
                    city=city,
                    defaults={
                        'lat': area_data['lat'],
                        'lng': area_data['lng'],
                        'is_active': True,
                    }
                )
                self.stdout.write(f"\n  {'Created' if created else 'Found'} area: {area.name}")

                if options['no_fetch']:
                    continue

                queries = build_queries(area.name, city.name)
                for category_name, category_queries in queries:
                    self.stdout.write(f"  Fetching {category_name.lower()}...")
                    for query in category_queries:
                        if options['dry_run']:
                            self.stdout.write(f"    DRY RUN: {query}")
                        else:
                            fetcher.fetch_and_store_venues(
                                query=query,
                                max_venues=MAX_VENUES_PER_QUERY,
                                area=area,
                                max_distance_km=max_distance_km,
                            )

        self.stdout.write(self.style.SUCCESS('\nDone.'))
