"""
Django management command to refresh photo references for venues
"""

from django.core.management.base import BaseCommand
from recommendations.models import Venue, Area
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Refresh photo references for venues from Google Places API (New)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-id',
            type=int,
            help='Only refresh venues in a specific area'
        )
        parser.add_argument(
            '--venue-ids',
            type=str,
            help='Comma-separated list of venue IDs to refresh'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of venues to process'
        )

    def handle(self, *args, **options):
        from django.conf import settings

        api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR("GOOGLE_PLACES_API_KEY not found in settings"))
            return

        self.stdout.write("Starting photo reference refresh...")

        venues = []

        # Process specific venue IDs if provided
        if options['venue_ids']:
            venue_id_list = [int(vid.strip()) for vid in options['venue_ids'].split(',') if vid.strip()]
            self.stdout.write(f"Processing {len(venue_id_list)} specific venue IDs")
            venues = list(Venue.objects.filter(id__in=venue_id_list))

            if options['limit']:
                venues = venues[:options['limit']]

        else:
            # Process by area
            if options['area_id']:
                areas = Area.objects.filter(id=options['area_id'])
                self.stdout.write(f"Processing single area: {options['area_id']}")
            else:
                areas = Area.objects.filter(is_active=True)
                self.stdout.write(f"Processing all active areas")

            for area in areas:
                area_venues = list(Venue.objects.filter(area=area))
                venues.extend(area_venues)

                if options['limit'] and len(venues) >= options['limit']:
                    venues = venues[:options['limit']]
                    break

        if not venues:
            self.stdout.write(self.style.WARNING("No venues to process"))
            return

        self.stdout.write(f"Processing {len(venues)} venues...")

        updated_count = 0
        failed_count = 0
        failed_venues = []

        for venue in venues:
            if not venue.place_id:
                self.stdout.write(f"Skipping {venue.name} (ID: {venue.id}) - no place_id")
                failed_venues.append({'id': venue.id, 'name': venue.name, 'reason': 'No place_id'})
                failed_count += 1
                continue

            try:
                # Fetch place details from Google Places API (New)
                url = f"https://places.googleapis.com/v1/places/{venue.place_id}"
                headers = {
                    'Content-Type': 'application/json',
                    'X-Goog-Api-Key': api_key,
                    'X-Goog-FieldMask': 'photos'
                }

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if 'photos' in data:
                    photos = data.get('photos', [])
                    if photos:
                        # Get the first photo reference using 'name' field (New API format)
                        new_photo_reference = photos[0].get('name')

                        if new_photo_reference and new_photo_reference != venue.photo_reference:
                            venue.photo_reference = new_photo_reference
                            venue.save(update_fields=['photo_reference'])
                            self.stdout.write(f"✓ Updated {venue.name} (ID: {venue.id})")
                            updated_count += 1
                        else:
                            self.stdout.write(f"− No change for {venue.name} (ID: {venue.id})")
                    else:
                        self.stdout.write(f"⊘ No photos for {venue.name} (ID: {venue.id})")
                        failed_venues.append({'id': venue.id, 'name': venue.name, 'reason': 'No photos'})
                        failed_count += 1
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    self.stdout.write(f"✗ Failed for {venue.name} (ID: {venue.id}): {error_msg}")
                    failed_venues.append({'id': venue.id, 'name': venue.name, 'reason': error_msg})
                    failed_count += 1

            except Exception as e:
                self.stdout.write(f"✗ Error for {venue.name} (ID: {venue.id}): {str(e)}")
                failed_venues.append({'id': venue.id, 'name': venue.name, 'reason': str(e)})
                failed_count += 1

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write("SUMMARY")
        self.stdout.write('=' * 60)
        self.stdout.write(f"Total venues processed: {len(venues)}")
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count}"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
            self.stdout.write("\nFailed venues:")
            for fv in failed_venues:
                self.stdout.write(f"  - ID: {fv['id']}, Name: {fv['name']}, Reason: {fv['reason']}")
        self.stdout.write('=' * 60)
