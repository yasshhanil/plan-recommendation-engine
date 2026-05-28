"""
One-time data fix: corrects price_tags (premium/expensive → upscale/moderate/affordable)
and removes 'upscale' incorrectly stored in vibe_tags.
"""

import json
from django.core.management.base import BaseCommand
from recommendations.models import Venue


def corrected_price_tag(price_level):
    if price_level >= 3:
        return 'upscale'
    elif price_level == 2:
        return 'moderate'
    return 'affordable'


class Command(BaseCommand):
    help = 'Fix incorrect price_tags and misplaced upscale vibe_tag on all venues'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fixed = 0
        skipped = 0

        for venue in Venue.objects.all():
            if not venue.tags:
                skipped += 1
                continue

            try:
                tags = json.loads(venue.tags)
            except (json.JSONDecodeError, TypeError):
                skipped += 1
                continue

            changed = False

            # Fix price_tags
            old_price = set(tags.get('price_tags', []))
            correct = corrected_price_tag(venue.price_level or 0)
            new_price = {correct}
            if old_price != new_price:
                tags['price_tags'] = list(new_price)
                changed = True

            # Remove 'upscale' from vibe_tags if present
            old_vibe = tags.get('vibe_tags', [])
            new_vibe = [t for t in old_vibe if t != 'upscale']
            if len(new_vibe) != len(old_vibe):
                tags['vibe_tags'] = new_vibe
                changed = True

            if changed:
                fixed += 1
                self.stdout.write(
                    f"  {venue.name} (price_level={venue.price_level}): "
                    f"price_tags {list(old_price)} → {list(new_price)}"
                )
                if not dry_run:
                    venue.tags = json.dumps(tags)
                    venue.save(update_fields=['tags'])

        label = 'Would fix' if dry_run else 'Fixed'
        self.stdout.write(self.style.SUCCESS(f"\n{label} {fixed} venues. Skipped {skipped}."))
