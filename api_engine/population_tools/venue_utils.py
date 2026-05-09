"""
Common utility functions for venue processing and validation
Shared between fetch_test_data.py and admin actions
"""

import json
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from models import Venue, TAG_STRUCTURE, validate_tags, tags_to_json
from sqlmodel import Session, select


def should_skip_venue(place_data: Dict[str, Any], min_rating_count: int = 30, 
                      area_lat: float = None, area_lng: float = None) -> tuple[bool, str]:
    """
    Check if a venue should be skipped based on filtering criteria
    
    Args:
        place_data: Raw place data from Google Places API
        min_rating_count: Minimum number of user ratings required
        area_lat: Area latitude for distance check
        area_lng: Area longitude for distance check
        
    Returns:
        tuple: (should_skip, reason)
    """
    import math
    
    # Check if place has required fields
    place_id = place_data.get('id')
    if not place_id:
        return True, "No place ID"
    
    # Check rating count
    user_rating_count = place_data.get('userRatingCount', 0)
    if user_rating_count < min_rating_count:
        display_name = place_data.get('displayName', {}).get('text', 'Unknown')
        return True, f"Insufficient ratings ({user_rating_count} < {min_rating_count})"
    
    # Check distance from area (if area coordinates provided)
    if area_lat is not None and area_lng is not None:
        location = place_data.get('location', {})
        venue_lat = location.get('latitude')
        venue_lng = location.get('longitude')
        
        if venue_lat is not None and venue_lng is not None:
            # Calculate distance using Haversine formula
            lat1, lon1, lat2, lon2 = map(math.radians, [area_lat, area_lng, venue_lat, venue_lng])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            distance = 6371 * 2 * math.asin(math.sqrt(a))  # Earth radius in km
            
                        
            if distance > 2.5:
                return True, f"Too far from area ({distance:.2f}km > 2.5km)"
    
    return False, ""


def create_venue_from_place_data(place_data: Dict[str, Any], area_id: int, 
                                generate_tags: bool = True) -> Optional[Venue]:
    """
    Create a Venue object from Google Places API data
    
    Args:
        place_data: Raw place data from Google Places API
        area_id: ID of the area to associate with the venue
        generate_tags: Whether to generate automatic tags
        
    Returns:
        Venue object or None if creation fails
    """
    try:
        display_name = place_data.get('displayName', {}).get('text', 'Unknown')
        location = place_data.get('location', {})
        
        # Extract photo reference from photos array
        photo_reference = None
        photos = place_data.get('photos', [])
        if photos:
            photo_reference = photos[0].get('name')  # Get first photo's reference
        
        # Generate tags if requested
        tags_json = None
        if generate_tags:
            from fetch_test_data import DataFetcher
            fetcher = DataFetcher()
            tags = fetcher.sample_tags_for_venue({
                'name': display_name, 
                'types': place_data.get('types', []), 
                'price_level': place_data.get('priceLevel')
            })
            tags_json = tags_to_json(tags)
        else:
            tags_json = json.dumps({"category_tags": [], "vibe_tags": [], "special_tags": [], "price_tags": []})
        
        # Process reviews
        reviews_json = None
        if 'reviews' in place_data:
            reviews = place_data['reviews'][:5]  # Limit to 5 reviews
            reviews_json = json.dumps(reviews)
        
        # Convert price level
        price_level_numeric = convert_price_level(place_data.get('priceLevel', 'PRICE_LEVEL_MODERATE'))
        
        # Create venue
        venue = Venue(
            place_id=place_data.get('id'),
            name=display_name,
            lat=location.get('latitude', 0),
            lng=location.get('longitude', 0),
            rating=place_data.get('rating', 0.0),
            user_rating_count=place_data.get('userRatingCount', 0),
            price_level=price_level_numeric,
            area_id=area_id,
            raw_types=json.dumps(place_data.get('types', [])),
            tags=tags_json,
            reviews=reviews_json,
            photo_reference=photo_reference,
            google_maps_uri=place_data.get('googleMapsUri'),
            formatted_address=place_data.get('formattedAddress'),
            summary=None  # Leave blank for manual population
        )
        
        return venue
        
    except Exception as e:
        print(f"Error creating venue from place data: {e}")
        return None


def convert_price_level(price_str: str) -> int:
    """
    Convert Google price level string to numeric
    
    Args:
        price_str: Google Places price level string
        
    Returns:
        Numeric price level (0-4)
    """
    price_map = {
        'PRICE_LEVEL_FREE': 0,
        'PRICE_LEVEL_INEXPENSIVE': 1,
        'PRICE_LEVEL_MODERATE': 2,
        'PRICE_LEVEL_EXPENSIVE': 3,
        'PRICE_LEVEL_VERY_EXPENSIVE': 4
    }
    return price_map.get(price_str, 2)


def process_places_to_venues(places: List[Dict[str, Any]], area_id: int, 
                            session, min_rating_count: int = 30,
                            generate_tags: bool = True, area_lat: float = None, 
                            area_lng: float = None) -> tuple[int, int, List[str]]:
    """
    Process a list of places and save valid venues to database
    
    Args:
        places: List of place data from Google Places API
        area_id: ID of the area to associate with venues
        session: Database session
        min_rating_count: Minimum number of user ratings required
        generate_tags: Whether to generate automatic tags
        area_lat: Area latitude for distance check
        area_lng: Area longitude for distance check
        
    Returns:
        tuple: (venues_saved, venues_skipped, error_messages)
    """
    from sqlmodel import select
    
    venues_saved = 0
    venues_skipped = 0
    errors = []
    processed_place_ids = set()
    
    for place in places:
        try:
            # Check if we should skip this venue
            should_skip, skip_reason = should_skip_venue(place, min_rating_count, area_lat, area_lng)
            if should_skip:
                display_name = place.get('displayName', {}).get('text', 'Unknown')
                print(f"Skipping {display_name} - {skip_reason}")
                venues_skipped += 1
                continue
            
            place_id = place.get('id')
            if place_id in processed_place_ids:
                venues_skipped += 1
                continue
                
            processed_place_ids.add(place_id)
            
            # Check if venue already exists
            existing = session.exec(select(Venue).where(Venue.place_id == place_id)).first()
            if existing:
                display_name = place.get('displayName', {}).get('text', 'Unknown')
                print(f"Venue already exists: {display_name}")
                venues_skipped += 1
                continue
            
            # Create venue
            venue = create_venue_from_place_data(place, area_id, generate_tags)
            if venue:
                session.add(venue)
                venues_saved += 1
                print(f"Created venue {venues_saved}: {venue.name}")
                print(f"  Rating: {venue.rating}, Price: {venue.price_level}, Reviews: {venue.user_rating_count}")
            else:
                venues_skipped += 1
                errors.append(f"Failed to create venue from place data")
                
        except Exception as e:
            venues_skipped += 1
            errors.append(f"Error processing place: {str(e)}")
    
    return venues_saved, venues_skipped, errors


def analyze_venues_batch(venue_ids: List[int], session: Session, model) -> List[Dict[str, Any]]:
    """Analyze multiple venues by IDs in batches of 10 and save results to database"""
    
    try:
        # Fetch venues from database by IDs
        venues = []
        venue_objects = {}  # Store venue objects for later updates
        if not venue_ids:
            venue_ids = [v.id for v in session.exec(select(Venue).where(Venue.summary.is_(None))).all()]
        print(f"Venue count: {len(venue_ids)}")
        for venue_id in venue_ids:
            venue = session.exec(select(Venue).where(Venue.id == venue_id)).first()
            if venue:
                venue_objects[venue_id] = venue  # Store the actual venue object
                # Convert venue to dict format expected by prompt
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
            else:
                print(f"⚠️  Venue with ID {venue_id} not found in database")
        
        if not venues:
            print("❌ No valid venues found for analysis")
            return []
        
        # Process venues in batches of 5
        batch_size = 10
        all_results = []
        
        for i in range(0, len(venues), batch_size):
            batch_venues = venues[i:i + batch_size]
            batch_number = i // batch_size + 1
            total_batches = (len(venues) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_number}/{total_batches} ({len(batch_venues)} venues)")
            
            # Import prompt function
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent.parent / 'data_population'))
            from venue_prompt import get_batch_venue_prompt
            
            prompt = get_batch_venue_prompt(batch_venues)
            
            venue_names = [v['name'] for v in batch_venues]
            print(f"🏢 Analyzing: {', '.join(venue_names)}")
            
            try:
                # Make the API request
                response = model.generate_content(prompt)
                
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
                
                # Process results and update database for non-rejected venues
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
                            
                            # Update tags - merge with existing tags without duplication
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
                            for tag_type in ['category', 'vibe', 'special', 'price']:
                                existing_set = set(existing_tags.get(tag_type, []))
                                new_set = set(new_tags.get(tag_type, []))
                                merged_tags[tag_type] = sorted(list(existing_set.union(new_set)))
                            
                            # Save merged tags
                            venue.tags = json.dumps(merged_tags)
                            print(f"   💾 Updated tags in database: {merged_tags}")
                            
                            updated_venues.append(venue)
                    else:
                        print(f"❌ Venue REJECTED - {venue_name} (ID: {venue_id}): {venue_result.get('summary', 'No reason provided')}")
                
                # Commit changes to database for this batch
                if updated_venues:
                    session.commit()
                    print(f"\n💾 Saved {len(updated_venues)} venues to database")
                
                print(f"✅ Batch {batch_number} complete: {len(results)}/{len(batch_venues)} venues processed")
                all_results.extend(results)
                
                # Small delay between batches to avoid rate limiting
                if batch_number < total_batches:
                    import time
                    time.sleep(2)
                    
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
