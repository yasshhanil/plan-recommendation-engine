"""
Django management command to bulk upload venue images to Google Cloud Storage
"""

from django.core.management.base import BaseCommand
from recommendations.models import Venue
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
            '--limit',
            type=int,
            help='Limit number of venues to process'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-upload images even if image_url already exists'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting bulk venue image upload to GCS...")

        # Get venues to process
        venues = Venue.objects.filter(
            photo_reference__isnull=False,
            summary__isnull=False
        ).exclude(summary='rejected')

        if options['area_id']:
            venues = venues.filter(area_id=options['area_id'])
            self.stdout.write(f"Filtering by area_id: {options['area_id']}")

        if options['force']:
            self.stdout.write("Force mode: Re-uploading all images")
        else:
            venues = venues.filter(image_url__isnull=True)
            self.stdout.write("Only uploading venues without image_url")

        if options['limit']:
            venues = venues[:options['limit']]
            self.stdout.write(f"Limiting to {options['limit']} venues")

        total_venues = venues.count()
        if total_venues == 0:
            self.stdout.write(self.style.WARNING("No venues to process"))
            return

        self.stdout.write(f"Processing {total_venues} venues...")

        # Bulk upload images
        venue_urls = bulk_upload_venue_images(list(venues))

        # Report results
        uploaded_count = sum(1 for url in venue_urls.values() if url is not None)
        failed_count = total_venues - uploaded_count

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"Total venues processed: {total_venues}")
        self.stdout.write(self.style.SUCCESS(f"Successfully uploaded: {uploaded_count}"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
        self.stdout.write("=" * 60)
