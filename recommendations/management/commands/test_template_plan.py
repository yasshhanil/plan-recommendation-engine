"""
Django management command to test template selection with random tag combinations.
"""

from django.core.management.base import BaseCommand
from django.test import Client
import random
import logging
import json
from recommendations.constants import CATEGORY_TAGS, VIBE_TAGS, SPECIAL_TAGS, PRICE_TAGS, INTERNAL_CATEGORY_TAGS

# Disable logging for cleaner output
logging.disable(logging.CRITICAL)


class Command(BaseCommand):
    help = 'Test template selection with random tag combinations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of random tag combinations to generate and test'
        )

    def handle(self, *args, **options):
        count = options['count']

        self.stdout.write(self.style.SUCCESS(f'\nTesting template selection with {count} random combinations...\n'))

        client = Client()

        for i in range(count):
            self.stdout.write(self.style.WARNING(f'--- Test {i + 1} ---'))

            # Randomly select tags
            category_tags = random.sample(CATEGORY_TAGS, random.randint(1, 2))
            vibe_tags = random.sample(VIBE_TAGS, random.randint(1, 3))
            special_tags = random.sample(SPECIAL_TAGS, random.randint(0, 2)) if random.random() > 0.3 else []
            price_tags = random.sample(PRICE_TAGS, 1)

            # Display input tags
            self.stdout.write('\nInput Tags:')
            self.stdout.write(f'  Category: {", ".join(category_tags)}')
            self.stdout.write(f'  Vibe: {", ".join(vibe_tags)}')
            self.stdout.write(f'  Special: {", ".join(special_tags) if special_tags else "None"}')
            self.stdout.write(f'  Price: {", ".join(price_tags)}')

            # Create tags as a single JSON object
            input_tags_json = json.dumps({
                'category_tags': category_tags,
                'vibe_tags': vibe_tags,
                'special_tags': special_tags,
                'price_tags': price_tags
            })

            # Call the view with tags as a single JSON object
            response = client.get('/api/template/', {
                'tags': input_tags_json
            })

            if response.status_code == 200:
                result = json.loads(response.content)
                self.stdout.write(self.style.SUCCESS(f'\nView Response:'))
                self.stdout.write(json.dumps(result, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f'\nError: Status code {response.status_code}'))

            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS(f'\nCompleted {count} tests.\n'))
