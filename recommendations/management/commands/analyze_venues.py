"""
Django management command to analyze venue data
Compatible version of the FastAPI analyze_venues.py for Django
"""

import json
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q
from recommendations.models import Venue, Area


class Command(BaseCommand):
    help = 'Analyze venue data in Django database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-id',
            type=int,
            help='Analyze venues for specific area ID'
        )
        parser.add_argument(
            '--min-rating',
            type=float,
            default=0.0,
            help='Filter venues by minimum rating'
        )
        parser.add_argument(
            '--export-json',
            type=str,
            help='Export analysis results to JSON file'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting venue analysis...")

        # Build query
        queryset = Venue.objects.all()
        
        if options['area_id']:
            queryset = queryset.filter(area_id=options['area_id'])
            self.stdout.write(f"Filtering by area ID: {options['area_id']}")
        
        if options['min_rating'] > 0:
            queryset = queryset.filter(rating__gte=options['min_rating'])
            self.stdout.write(f"Filtering by minimum rating: {options['min_rating']}")

        # Basic statistics
        total_venues = queryset.count()
        if total_venues == 0:
            self.stdout.write(self.style.WARNING("No venues found matching criteria"))
            return

        avg_rating = queryset.aggregate(avg_rating=Avg('rating'))['avg_rating']
        rated_venues = queryset.exclude(rating__isnull=True).count()

        self.stdout.write(f"\n=== VENUE ANALYSIS ===")
        self.stdout.write(f"Total venues: {total_venues}")
        self.stdout.write(f"Venues with ratings: {rated_venues}")
        self.stdout.write(f"Average rating: {avg_rating:.2f}" if avg_rating else "No ratings")

        # Rating distribution
        self.stdout.write(f"\n=== RATING DISTRIBUTION ===")
        rating_ranges = [
            (4.5, 5.0, "Excellent (4.5-5.0)"),
            (4.0, 4.5, "Very Good (4.0-4.5)"),
            (3.5, 4.0, "Good (3.5-4.0)"),
            (3.0, 3.5, "Average (3.0-3.5)"),
            (0, 3.0, "Below Average (0-3.0)")
        ]

        for min_r, max_r, label in rating_ranges:
            count = queryset.filter(rating__gte=min_r, rating__lt=max_r).count()
            percentage = (count / total_venues) * 100
            self.stdout.write(f"{label}: {count} venues ({percentage:.1f}%)")

        # Price level distribution
        self.stdout.write(f"\n=== PRICE LEVEL DISTRIBUTION ===")
        price_levels = queryset.values('price_level').annotate(count=Count('price_level')).order_by('price_level')
        for price_data in price_levels:
            price_level = price_data['price_level'] or 'Not specified'
            count = price_data['count']
            percentage = (count / total_venues) * 100
            self.stdout.write(f"Price {price_level}: {count} venues ({percentage:.1f}%)")

        # Area breakdown
        self.stdout.write(f"\n=== AREA BREAKDOWN ===")
        areas = queryset.values('area__name').annotate(
            count=Count('id'),
            avg_rating=Avg('rating')
        ).order_by('-count')

        for area_data in areas:
            area_name = area_data['area__name'] or 'No area'
            count = area_data['count']
            avg_rating = area_data['avg_rating']
            self.stdout.write(f"{area_name}: {count} venues (avg rating: {avg_rating:.2f})" if avg_rating else f"{area_name}: {count} venues")

        # Top venues by rating
        self.stdout.write(f"\n=== TOP RATED VENUES ===")
        top_venues = queryset.filter(rating__isnull=False).order_by('-rating')[:10]
        for i, venue in enumerate(top_venues, 1):
            self.stdout.write(f"{i}. {venue.name} - Rating: {venue.rating} ({venue.area.name if venue.area else 'No area'})")

        # Venues without ratings
        no_rating = queryset.filter(rating__isnull=True).count()
        if no_rating > 0:
            self.stdout.write(f"\nVenues without ratings: {no_rating}")

        # Tag analysis (if tags exist)
        venues_with_tags = queryset.exclude(tags__isnull=True).exclude(tags='').count()
        if venues_with_tags > 0:
            self.stdout.write(f"\n=== TAG ANALYSIS ===")
            self.stdout.write(f"Venues with tags: {venues_with_tags}")
            
            # Simple tag frequency analysis
            all_tags = {}
            for venue in queryset.exclude(tags__isnull=True).exclude(tags=''):
                try:
                    if venue.tags:
                        tags_data = json.loads(venue.tags) if isinstance(venue.tags, str) else venue.tags
                        if isinstance(tags_data, dict):
                            for category, tag_list in tags_data.items():
                                if isinstance(tag_list, list):
                                    for tag in tag_list:
                                        all_tags[tag] = all_tags.get(tag, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue

            if all_tags:
                self.stdout.write("Top 20 most common tags:")
                sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:20]
                for tag, count in sorted_tags:
                    self.stdout.write(f"  {tag}: {count} venues")

        # Export results if requested
        if options['export_json']:
            analysis_data = {
                'total_venues': total_venues,
                'rated_venues': rated_venues,
                'average_rating': avg_rating,
                'rating_distribution': [
                    {
                        'range': label,
                        'count': queryset.filter(rating__gte=min_r, rating__lt=max_r).count(),
                        'percentage': (queryset.filter(rating__gte=min_r, rating__lt=max_r).count() / total_venues) * 100
                    }
                    for min_r, max_r, label in rating_ranges
                ],
                'price_levels': list(price_levels),
                'areas': list(areas),
                'top_venues': [
                    {
                        'name': venue.name,
                        'rating': venue.rating,
                        'area': venue.area.name if venue.area else None
                    }
                    for venue in top_venues
                ],
                'venues_without_ratings': no_rating,
                'venues_with_tags': venues_with_tags
            }

            with open(options['export_json'], 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f"Analysis exported to {options['export_json']}"))

        self.stdout.write(self.style.SUCCESS("Analysis complete!"))
