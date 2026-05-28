"""
Django management command to bulk upload venue images to Google Cloud Storage
"""

from django.core.management.base import BaseCommand
from recommendations.models import Venue, Area
from recommendations.functions import bulk_upload_venue_images


class Command(BaseCommand):
    help = 'Bulk upload all venue images to GCS and update image_url field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-id',
            type=int,
            help='Only upload images for venues in a specific area'
        )
        parser.add_argument(
            '--venue-ids',
            type=str,
            help='Comma-separated list of venue IDs to process'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of venues to process'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting bulk venue image upload to GCS...")

        total_uploaded = 0
        total_failed = 0
        all_failed_venues = []

        # Process specific venue IDs if provided
        if options['venue_ids']:
            venue_id_list = [int(vid.strip()) for vid in options['venue_ids'].split(',') if vid.strip()]
            self.stdout.write(f"Processing {len(venue_id_list)} specific venue IDs")

            venues = Venue.objects.filter(
                id__in=venue_id_list,
                photo_reference__isnull=False,
                summary__isnull=False
            ).exclude(summary='rejected')

            if options['limit']:
                venues = venues[:options['limit']]
                self.stdout.write(f"Limiting to {options['limit']} venues")

            venue_count = venues.count()
            if venue_count == 0:
                self.stdout.write(self.style.WARNING("No venues to process"))
                return

            self.stdout.write(f"Processing {venue_count} venues...")

            # Bulk upload images
            venue_urls = bulk_upload_venue_images(list(venues))

            # Report results
            uploaded_count = sum(1 for url in venue_urls.values() if url is not None)
            failed_count = venue_count - uploaded_count
            total_uploaded += uploaded_count
            total_failed += failed_count

            # Track failed venues with details
            failed_venue_details = []
            for venue in venues:
                if venue_urls.get(venue.id) is None:
                    failed_venue_details.append({
                        'id': venue.id,
                        'name': venue.name,
                        'area': venue.area.name if venue.area else 'N/A'
                    })
                    all_failed_venues.append(venue.id)

            self.stdout.write(self.style.SUCCESS(f"Successfully uploaded: {uploaded_count}"))
            if failed_count > 0:
                self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
                self.stdout.write("\nFailed venues:")
                for detail in failed_venue_details:
                    self.stdout.write(f"  - ID: {detail['id']}, Name: {detail['name']}, Area: {detail['area']}")

        else:
            # Process by area
            if options['area_id']:
                areas = Area.objects.filter(id=options['area_id'])
                self.stdout.write(f"Processing single area: {options['area_id']}")
            else:
                areas = Area.objects.filter(is_active=True)
                self.stdout.write(f"Processing all active areas")

            for area in areas:
                self.stdout.write(f"\n{'=' * 60}")
                self.stdout.write(f"Processing area: {area.name} (ID: {area.id})")
                self.stdout.write('=' * 60)

                # Get venues for this area
                venues = Venue.objects.filter(
                    area=area,
                    photo_reference__isnull=False,
                    summary__isnull=False
                ).exclude(summary='rejected')

                if options['limit']:
                    venues = venues[:options['limit']]
                    self.stdout.write(f"Limiting to {options['limit']} venues")

                venue_count = venues.count()
                if venue_count == 0:
                    self.stdout.write(self.style.WARNING("No venues to process in this area"))
                    continue

                self.stdout.write(f"Processing {venue_count} venues in {area.name}...")

                # Bulk upload images
                venue_urls = bulk_upload_venue_images(list(venues))

                # Report results for this area
                uploaded_count = sum(1 for url in venue_urls.values() if url is not None)
                failed_count = venue_count - uploaded_count
                total_uploaded += uploaded_count
                total_failed += failed_count

                # Track failed venues with details
                failed_venue_details = []
                for venue in venues:
                    if venue_urls.get(venue.id) is None:
                        failed_venue_details.append({
                            'id': venue.id,
                            'name': venue.name
                        })
                        all_failed_venues.append(venue.id)

                self.stdout.write(self.style.SUCCESS(f"Successfully uploaded: {uploaded_count}"))
                if failed_count > 0:
                    self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
                    self.stdout.write("Failed venues in this area:")
                    for detail in failed_venue_details:
                        self.stdout.write(f"  - ID: {detail['id']}, Name: {detail['name']}")

        # Final summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write("FINAL SUMMARY")
        self.stdout.write('=' * 60)
        self.stdout.write(f"Total venues uploaded: {total_uploaded}")
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(f"Total failed: {total_failed}"))
            self.stdout.write(f"All failed venue IDs: {all_failed_venues}")
        self.stdout.write('=' * 60)
