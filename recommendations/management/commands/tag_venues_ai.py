"""
Django management command to analyze venues using AI (Gemini)
Compatible version of the API engine analyze_venues.py for Django
"""

import os
import json
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from recommendations.models import Venue, TAG_STRUCTURE
import google.generativeai as genai
from .venue_prompt import get_batch_venue_prompt


class VenueAIAnalyzer:
    def __init__(self):
        # Check API key
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise CommandError("GEMINI_API_KEY not found in settings or environment variables")
        
        # Configure AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Retry configuration
        self.max_retries = 5
        self.base_delay = 2  # seconds
        self.max_delay = 60  # seconds

    def generate_content_with_retry(self, prompt):
        """Generate content with exponential backoff retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if error is retryable
                is_retryable = any(code in error_str for code in ['503', '504', '429', 'timeout', 'overloaded'])
                
                if not is_retryable or attempt == self.max_retries - 1:
                    raise  # Re-raise if not retryable or max retries exhausted
                
                # Calculate exponential backoff delay
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                print(f"⚠️  Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                print(f"   Retrying in {delay} seconds...")
                time.sleep(delay)
        
        raise Exception(f"Max retries ({self.max_retries}) exceeded")

    
    def analyze_venues_batch(self, venue_ids):
        """Analyze multiple venues by IDs in batches"""
        try:
            # Fetch venues from database
            venues = []
            venue_objects = {}
            
            if not venue_ids:
                # Analyze venues without summary
                venue_queryset = Venue.objects.filter(summary__isnull=True) | Venue.objects.filter(summary='')
            else:
                venue_queryset = Venue.objects.filter(id__in=venue_ids)
            
            for venue in venue_queryset:
                venue_objects[venue.id] = venue
                venue_data = {
                    'venue_id': venue.id,
                    'name': venue.name,
                    'rating': venue.rating,
                    'user_rating_count': venue.user_rating_count,
                    'price_level': venue.price_level,
                    'raw_types': json.loads(venue.raw_types) if venue.raw_types else [],
                    'reviews': json.loads(venue.reviews) if venue.reviews else []
                }
                venues.append(venue_data)
            
            if not venues:
                return []
            
            # Process venues in batches
            batch_size = 10  # Reduced from 10 to avoid timeouts
            all_results = []
            
            for i in range(0, len(venues), batch_size):
                batch_venues = venues[i:i + batch_size]
                batch_number = i // batch_size + 1
                total_batches = (len(venues) + batch_size - 1) // batch_size
                
                print(f"\n📦 Processing batch {batch_number}/{total_batches} ({len(batch_venues)} venues)")
                
                prompt = get_batch_venue_prompt(batch_venues)
                venue_names = [v['name'] for v in batch_venues]
                print(f"🏢 Analyzing: {', '.join(venue_names)}")
                
                try:
                    # Make the API request with retry logic
                    response = self.generate_content_with_retry(prompt)
                    
                    # Clean and parse the response
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '').strip()
                    
                    # Parse JSON response
                    result = json.loads(response_text)
                    
                    # Handle both single result and array of results
                    if isinstance(result, dict):
                        results = [result]
                    elif isinstance(result, list):
                        results = result
                    else:
                        print(f"❌ Unexpected response format for batch {batch_number}")
                        continue
                    
                    # Process results and update database
                    updated_venues = []
                    for venue_result in results:
                        venue_id = venue_result.get('venue_id')
                        venue_name = next((v['name'] for v in batch_venues if v['venue_id'] == venue_id), 'Unknown')
                        
                        if not venue_result.get('rejected', True):
                            print(f"\n✅ Venue NOT REJECTED - {venue_name} (ID: {venue_id})")
                            print(f"   Summary: {venue_result.get('summary', 'N/A')}")
                            print(f"   Categories: {venue_result.get('category_tags', [])}")
                            print(f"   Vibes: {venue_result.get('vibe_tags', [])}")
                            print(f"   Special: {venue_result.get('special_tags', [])}")
                            print(f"   Price: {venue_result.get('price_tags', [])}")
                            
                            # Update venue in database
                            if venue_id in venue_objects:
                                venue = venue_objects[venue_id]
                                
                                # Update summary
                                if venue_result.get('summary'):
                                    venue.summary = venue_result['summary']
                                    print(f"   💾 Updated summary in database")
                                
                                # Update tags
                                new_tags = {
                                    'category_tags': venue_result.get('category_tags', []),
                                    'vibe_tags': venue_result.get('vibe_tags', []),
                                    'special_tags': venue_result.get('special_tags', []),
                                    'price_tags': venue_result.get('price_tags', [])
                                }
                                
                                # Get existing tags
                                existing_tags = TAG_STRUCTURE.copy()
                                if venue.tags:
                                    try:
                                        existing_tags = json.loads(venue.tags)
                                    except json.JSONDecodeError:
                                        existing_tags = TAG_STRUCTURE.copy()
                                
                                # Merge tags without duplication
                                merged_tags = {}
                                for tag_type in ['category_tags', 'vibe_tags', 'special_tags', 'price_tags']:
                                    existing_set = set(existing_tags.get(tag_type, []))
                                    new_set = set(new_tags.get(tag_type, []))
                                    merged_tags[tag_type] = sorted(list(existing_set.union(new_set)))
                                
                                # Save merged tags
                                venue.tags = json.dumps(merged_tags)
                                print(f"   💾 Updated tags in database")
                                
                                updated_venues.append(venue)
                        else:
                            print(f"❌ Venue REJECTED - {venue_name} (ID: {venue_id}): {venue_result.get('summary', 'No reason provided')}")
                            
                            # Mark as rejected
                            if venue_id in venue_objects:
                                venue = venue_objects[venue_id]
                                venue.summary = "rejected"
                                updated_venues.append(venue)
                                print(f"   💾 Marked as rejected in database")
                    
                    # Save changes to database for this batch
                    if updated_venues:
                        Venue.objects.bulk_update(updated_venues, ['summary', 'tags'])
                        print(f"\n💾 Saved {len(updated_venues)} venues to database")
                    
                    print(f"✅ Batch {batch_number} complete: {len(results)}/{len(batch_venues)} venues processed")
                    all_results.extend(results)
                    
                    # Small delay between batches to avoid rate limiting
                    if batch_number < total_batches:
                        time.sleep(5)  # Increased from 2 to 5 seconds
                        
                except Exception as e:
                    print(f"❌ Error processing batch {batch_number}: {e}")
                    continue
            
            print(f"\n🎉 All batches complete! Total processed: {len(all_results)} venues")
            return all_results
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error analyzing batch: {e}")
            return []


class Command(BaseCommand):
    help = 'Analyze venues using AI (Gemini) and generate summaries/tags'

    def add_arguments(self, parser):
        parser.add_argument(
            'venue_ids',
            nargs='*',
            type=int,
            help='Specific venue IDs to analyze (optional, analyzes all without summary if not provided)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show analysis without saving to database'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting AI venue analysis...")
        
        try:
            # Initialize analyzer
            analyzer = VenueAIAnalyzer()
        except CommandError as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        
        # Get venue IDs
        venue_ids = options['venue_ids']
        
        if venue_ids:
            # Verify specific venue IDs exist
            existing_venues = Venue.objects.filter(id__in=venue_ids)
            existing_ids = list(existing_venues.values_list('id', flat=True))
            
            if not existing_ids:
                self.stdout.write(self.style.WARNING("No valid venues found to analyze"))
                return
            
            missing_ids = set(venue_ids) - set(existing_ids)
            if missing_ids:
                for missing_id in missing_ids:
                    self.stdout.write(self.style.WARNING(f"Venue with ID {missing_id} not found"))
            
            final_venue_ids = existing_ids
            self.stdout.write(f"Analyzing specified venue IDs: {final_venue_ids}")
        else:
            # Analyze all venues without summary
            final_venue_ids = []
            self.stdout.write("Analyzing all venues without summary...")
        
        # Analyze venues
        print("\n" + "="*60)
        print("🚀 STARTING AI VENUE ANALYSIS")
        print("="*60)
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved"))
            # For dry run, we would need to modify the analyzer to not save
            # For now, just show what would be analyzed
            if final_venue_ids:
                venues = Venue.objects.filter(id__in=final_venue_ids)
            else:
                venues = Venue.objects.filter(summary__isnull=True) | Venue.objects.filter(summary='')
            
            self.stdout.write(f"Would analyze {venues.count()} venues:")
            for venue in venues[:10]:  # Show first 10
                self.stdout.write(f"  - {venue.name} (ID: {venue.id})")
            if venues.count() > 10:
                self.stdout.write(f"  ... and {venues.count() - 10} more")
            return
        
        results = analyzer.analyze_venues_batch(final_venue_ids)
        
        # Summary
        print("\n" + "="*60)
        print(f"📊 ANALYSIS COMPLETE")
        print(f"✅ Processed {len(results)} venues")
        print("="*60)
        
        rejected_count = sum(1 for r in results if r.get('rejected', True))
        accepted_count = len(results) - rejected_count
        
        print(f"\n📈 SUMMARY:")
        print(f"   Accepted: {accepted_count}")
        print(f"   Rejected: {rejected_count}")
        print(f"   Total: {len(results)}")
        
        self.stdout.write(self.style.SUCCESS("AI venue analysis complete!"))
