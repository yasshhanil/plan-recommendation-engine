"""
Django management command to tag venues with categories
Compatible version of the FastAPI venue tagging tools for Django
"""

import json
import re
from django.core.management.base import BaseCommand
from recommendations.models import Venue


class VenueTagger:
    def __init__(self):
        # Define tag patterns based on venue names, types, and addresses
        self.tag_patterns = {
            'cafe': [
                r'cafe', r'coffee', r'starbucks', r'barista', r'costa',
                r'blue tokai', r'chai', r'brew', r'roasters'
            ],
            'restaurant': [
                r'restaurant', r'bistro', r'eatery', r'dining', r'kitchen',
                r'grill', r'barbecue', r'pizza', r'burger', r'bakery'
            ],
            'bar': [
                r'bar', r'pub', r'tavern', r'brewery', r'lounge',
                r'wine', r'spirits', r'cocktail'
            ],
            'activity': [
                r'park', r'garden', r'museum', r'gallery', r'theater',
                r'cinema', r'bowling', r'arcade', r'gaming', r'sports'
            ],
            'shopping': [
                r'mall', r'market', r'shop', r'store', r'boutique',
                r'retail', r'plaza', r'complex'
            ],
            'entertainment': [
                r'club', r'disco', r'music', r'live', r'performance',
                r'concert', r'show', r'venue'
            ]
        }

        # Vibe tags
        self.vibe_patterns = {
            'cozy': [
                r'cozy', r'intimate', r'quaint', r'charming', r'warm'
            ],
            'romantic': [
                r'romantic', r'date', r'couples', r'intimate', r'elegant'
            ],
            'casual': [
                r'casual', r'relaxed', r'informal', r'friendly', r'laid back'
            ],
            'upscale': [
                r'fine dining', r'luxury', r'premium', r'upscale', r'elegant',
                r'sophisticated', r'high-end'
            ],
            'trendy': [
                r'trendy', r'modern', r'contemporary', r'hip', r'fashionable'
            ]
        }

        # Special tags
        self.special_patterns = {
            'date_spot': [
                r'romantic', r'date', r'intimate', r'elegant', r'fine dining'
            ],
            'family_friendly': [
                r'family', r'kids', r'children', r'all ages', r'family-friendly'
            ],
            'outdoor': [
                r'outdoor', r'terrace', r'garden', r'patio', r'rooftop',
                r'open air', r'alfresco'
            ],
            'pet_friendly': [
                r'pet', r'dog', r'animal', r'pet-friendly'
            ],
            'wifi': [
                r'wifi', r'wi-fi', r'internet', r'workspace'
            ]
        }

    def extract_tags_from_text(self, text, patterns):
        """Extract tags from text using regex patterns"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_tags = []
        
        for tag, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text_lower):
                    found_tags.append(tag)
                    break
        
        return found_tags

    def tag_venue(self, venue):
        """Generate tags for a single venue"""
        # Combine all text sources
        text_sources = [
            venue.name or '',
            venue.formatted_address or '',
            venue.raw_types or ''
        ]
        combined_text = ' '.join(text_sources)

        # Extract tags
        category_tags = self.extract_tags_from_text(combined_text, self.tag_patterns)
        vibe_tags = self.extract_tags_from_text(combined_text, self.vibe_patterns)
        special_tags = self.extract_tags_from_text(combined_text, self.special_patterns)

        # Price-based tags
        price_tags = []
        if venue.price_level:
            if venue.price_level <= 2:
                price_tags.append('affordable')
            elif venue.price_level == 3:
                price_tags.append('moderate')
            elif venue.price_level >= 4:
                price_tags.append('upscale')

        # Rating-based tags
        if venue.rating and venue.rating >= 4.5:
            special_tags.append('highly_rated')

        # Remove duplicates and return
        all_tags = {
            'category_tags': list(set(category_tags)),
            'vibe_tags': list(set(vibe_tags)),
            'special_tags': list(set(special_tags)),
            'price_tags': list(set(price_tags))
        }

        return all_tags


class Command(BaseCommand):
    help = 'Tag venues with automatic categorization based on names, types, and addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-id',
            type=int,
            help='Tag venues for specific area ID'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show tags that would be applied without saving'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing tags'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of venues to process'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting venue tagging...")

        # Get venues
        queryset = Venue.objects.all()
        
        if options['area_id']:
            queryset = queryset.filter(area_id=options['area_id'])
            self.stdout.write(f"Tagging venues for area ID: {options['area_id']}")
        
        if options['limit']:
            queryset = queryset[:options['limit']]
            self.stdout.write(f"Limiting to {options['limit']} venues")

        if not options['overwrite']:
            queryset = queryset.filter(Q(tags__isnull=True) | Q(tags=''))
            self.stdout.write("Only tagging venues without existing tags (use --overwrite to change this)")

        total_venues = queryset.count()
        if total_venues == 0:
            self.stdout.write(self.style.WARNING("No venues found to tag"))
            return

        self.stdout.write(f"Processing {total_venues} venues...")

        tagger = VenueTagger()
        tagged_count = 0
        skipped_count = 0

        for i, venue in enumerate(queryset, 1):
            self.stdout.write(f"[{i}/{total_venues}] Processing: {venue.name}")
            
            # Generate tags
            tags = tagger.tag_venue(venue)
            
            # Show tags
            total_tag_count = sum(len(tag_list) for tag_list in tags.values())
            self.stdout.write(f"  Generated {total_tag_count} tags:")
            for category, tag_list in tags.items():
                if tag_list:
                    self.stdout.write(f"    {category}: {', '.join(tag_list)}")

            if options['dry_run']:
                continue

            # Save tags
            if total_tag_count > 0:
                venue.tags = json.dumps(tags)
                venue.save()
                tagged_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Tagged and saved"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"  ⚠ No tags generated"))

        # Summary
        self.stdout.write(f"\n=== TAGGING SUMMARY ===")
        self.stdout.write(f"Total venues processed: {total_venues}")
        self.stdout.write(f"Venues tagged: {tagged_count}")
        self.stdout.write(f"Venues skipped: {skipped_count}")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes saved"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully tagged {tagged_count} venues!"))
