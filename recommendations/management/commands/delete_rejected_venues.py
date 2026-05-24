"""
Django management command to list and delete venues with summary='rejected'
"""

from django.core.management.base import BaseCommand
from recommendations.models import Venue


class Command(BaseCommand):
    help = 'List count of venues with summary=rejected and delete them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show count without deleting'
        )

    def handle(self, *args, **options):
        self.stdout.write("Checking venues with summary='rejected'...")

        # Get rejected venues
        rejected_venues = Venue.objects.filter(summary='rejected')
        count = rejected_venues.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No venues with summary='rejected' found"))
            return

        self.stdout.write(f"Found {count} venues with summary='rejected'")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("Dry run mode - no deletions performed"))
            return

        # Confirm deletion
        confirm = input(f"Are you sure you want to delete {count} venues? (yes/no): ")
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Deletion cancelled"))
            return

        # Delete venues
        deleted_count = rejected_venues.delete()[0]
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} venues"))
