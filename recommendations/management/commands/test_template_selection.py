"""
Django management command to test template selection with random tag combinations.
"""

from django.core.management.base import BaseCommand
import random
from recommendations.templates import select_best_template, get_confidence_level
from recommendations.constants import CATEGORY_TAGS, VIBE_TAGS, SPECIAL_TAGS, PRICE_TAGS, INTERNAL_CATEGORY_TAGS


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
        
        for i in range(count):
            self.stdout.write(self.style.WARNING(f'--- Test {i + 1} ---'))
            
            # Randomly select tags
            category_tags = random.sample(CATEGORY_TAGS, random.randint(1, 2))
            vibe_tags = random.sample(VIBE_TAGS, random.randint(1, 3))
            special_tags = random.sample(SPECIAL_TAGS, random.randint(0, 2)) if random.random() > 0.3 else []
            price_tags = random.sample(PRICE_TAGS, 1)
            
            # Display selected tags
            self.stdout.write(f'Category tags: {", ".join(category_tags)}')
            self.stdout.write(f'Vibe tags: {", ".join(vibe_tags)}')
            self.stdout.write(f'Special tags: {", ".join(special_tags) if special_tags else "None"}')
            self.stdout.write(f'Price tags: {", ".join(price_tags)}')
            
            # Create user tags dictionary
            user_tags = {
                'category_tags': category_tags,
                'vibe_tags': vibe_tags,
                'special_tags': special_tags,
                'price_tags': price_tags
            }
            
            # Call template assigner
            template_id, template_score, confidence_score, all_scores = select_best_template(user_tags)
            
            # Get confidence level
            confidence_level = get_confidence_level(confidence_score)
            
            # Display results
            self.stdout.write(self.style.SUCCESS(f'\nSelected Template: {template_id}'))
            self.stdout.write(f'Template Score: {template_score:.3f}')
            self.stdout.write(f'Confidence Score: {confidence_score:.3f} ({confidence_level})')
            self.stdout.write('All Template Scores:')
            for tid, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
                marker = ' <-- SELECTED' if tid == template_id else ''
                self.stdout.write(f'  {tid}: {score:.3f}{marker}')
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS(f'\nCompleted {count} tests.\n'))
