"""
Django management command to fetch venue data from Google Places API
Compatible version of the FastAPI fetch_test_data.py for Django
"""

import os
import requests
import json
import math
from django.core.management.base import BaseCommand
from django.conf import settings
from recommendations.models import Venue, Area, ApiQuery, TAG_STRUCTURE, validate_tags, tags_to_json

# Global area and state variables
AREA_NAME = 'DUMBO'
STATE_NAME = 'New York'

# Test region
TEST_LOCATION = {
    'name': AREA_NAME,
    'lat': 40.7033,
    'lng': -73.9881,
    'radius': 3000  # 3km radius
}

# Filter for top-rated venues only
MIN_RATING = 4.0

# Bulk search queries for different categories
ACTIVITIES_BULK_QUERY = f"best places activities entertainment attractions museums parks theaters cinemas bowling arcade gaming shopping in {TEST_LOCATION['name']}"

FOOD_BULK_QUERY = f"best restaurants cafes bars food dining cuisine eateries bistros pubs in {TEST_LOCATION['name']}"

# Combined query for backward compatibility
BULK_SEARCH_QUERY = f"best places activities restaurants cafes bars shopping entertainment attractions museums parks theaters cinemas bowling arcade gaming in {TEST_LOCATION['name']}"

# Field mask for Google Places API - defines which fields to request
PLACES_FIELD_MASK = 'places.id,places.displayName,places.rating,places.userRatingCount,places.priceLevel,places.location,places.types,places.primaryType,places.formattedAddress,places.reviews,places.businessStatus,places.googleMapsUri,places.photos'


class DataFetcher:
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not found in settings")
        
        self.base_url = 'https://places.googleapis.com/v1/places:searchText'
        self.headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': PLACES_FIELD_MASK
        }
        
        # Track processed place IDs for deduplication
        self.processed_place_ids = set()

    def text_search(self, query, location, radius=500, max_results=20):
        """Search for places using Google Places API (New) - Text Search"""
        data = {
            'textQuery': query,
            'maxResultCount': max_results,
            'minRating': 3.8,
            'languageCode': 'en'
        }
        
        try:
            response = requests.post(self.base_url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None
    
    def create_test_area(self):
        """Create test area in database using Django ORM"""
        # Check if area already exists
        existing_area = Area.objects.filter(name=TEST_LOCATION['name']).first()
        if existing_area:
            print(f"Area '{TEST_LOCATION['name']}' already exists")
            return existing_area
        
        area = Area.objects.create(
            name=TEST_LOCATION['name'],
            lat=TEST_LOCATION['lat'],
            lng=TEST_LOCATION['lng'],
            country='India',
            state=STATE_NAME,
            is_active=True
        )
        print(f"Created area: {area.name}")
        return area

    def convert_price_level(self, price_level_str):
        """Convert Google Places API price level string to numeric value"""
        price_level_map = {
            'PRICE_LEVEL_FREE': 0,
            'PRICE_LEVEL_INEXPENSIVE': 1,
            'PRICE_LEVEL_MODERATE': 2,
            'PRICE_LEVEL_EXPENSIVE': 3,
            'PRICE_LEVEL_VERY_EXPENSIVE': 4
        }
        return price_level_map.get(price_level_str, 2)
    
    def sample_tags_for_venue(self, venue_data):
        """Generate sample tags based on venue data (rule-based for testing)"""
        # Use sets for automatic deduplication
        tags = {
            'category_tags': set(),
            'vibe_tags': set(),
            'special_tags': set(),
            'price_tags': set()
        }
        
        name_lower = venue_data['name'].lower()
        types = venue_data.get('types', [])
        
        # Category tags based on types and name
        if 'cafe' in types or 'cafe' in name_lower:
            tags['category_tags'].add('cafe')
        if 'restaurant' in types or 'restaurant' in name_lower:
            tags['category_tags'].add('restaurant')
        if 'bar' in types or 'bar' in name_lower or 'pub' in name_lower:
            tags['category_tags'].add('bar')
        if 'shopping_mall' in types or 'store' in types:
            tags['category_tags'].add('shopping')
        if 'movie_theater' in types or 'cinema' in name_lower:
            tags['category_tags'].add('cinema')
        
        # Convert price level string to numeric for comparison
        price_level = self.convert_price_level(venue_data.get('price_level', 'PRICE_LEVEL_MODERATE'))
        
        # Price and vibe tags based on price level
        if price_level >= 4:
            tags['price_tags'].add('premium')
            tags['vibe_tags'].add('fancy')
        elif price_level == 3:
            tags['price_tags'].add('expensive')
            tags['vibe_tags'].add('upscale')
        elif price_level <= 2:
            tags['price_tags'].add('affordable')
        
        # Additional vibe tags based on name
        if 'cafe' in name_lower or 'coffee' in name_lower:
            tags['vibe_tags'].add('cozy')
        
        # Special tags
        if 'romantic' in name_lower or price_level >= 4:
            tags['special_tags'].add('date_spot')
        
        # Convert sets back to lists for JSON serialization
        return {key: list(value) for key, value in tags.items()}
    
    def should_skip_venue(self, place_data, min_rating_count=30, area_lat=None, area_lng=None):
        """Check if a venue should be skipped based on filtering criteria"""
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

    def create_venue_from_place_data(self, place_data, area_id, generate_tags=True):
        """Create a Venue object from Google Places API data"""
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
                tags = self.sample_tags_for_venue({
                    'name': display_name,
                    'types': place_data.get('types', []),
                    'price_level': place_data.get('priceLevel')
                })
                tags_json = tags_to_json(tags)
            else:
                tags_json = json.dumps(TAG_STRUCTURE)
            
            # Process reviews
            reviews_json = None
            if 'reviews' in place_data:
                reviews = place_data['reviews'][:5]  # Limit to 5 reviews
                reviews_json = json.dumps(reviews)
            
            # Convert price level
            price_level_numeric = self.convert_price_level(place_data.get('priceLevel', 'PRICE_LEVEL_MODERATE'))
            
            # Create venue data
            venue_data = {
                'place_id': place_data.get('id'),
                'name': display_name,
                'lat': location.get('latitude', 0),
                'lng': location.get('longitude', 0),
                'rating': place_data.get('rating', 0.0),
                'user_rating_count': place_data.get('userRatingCount', 0),
                'price_level': price_level_numeric,
                'area_id': area_id,
                'raw_types': json.dumps(place_data.get('types', [])),
                'tags': tags_json,
                'reviews': reviews_json,
                'photo_reference': photo_reference,
                'google_maps_uri': place_data.get('googleMapsUri'),
                'formatted_address': place_data.get('formattedAddress'),
                'summary': None
            }
            
            return venue_data
            
        except Exception as e:
            print(f"Error creating venue from place data: {e}")
            return None

    def fetch_and_store_venues(self, query=BULK_SEARCH_QUERY, max_venues=20, area=None):
        """Fetch venues and store in database"""
        print(f"Fetching test data for {TEST_LOCATION['name']}...")
        print(f"Using query: {query}")
        
        venues_created = 0
        processed_place_ids = set()
        
        try:
            # Single bulk fetch instead of multiple queries
            print(f"\nBulk search: {query}")
            
            results = self.text_search(query, TEST_LOCATION, radius=TEST_LOCATION['radius'], max_results=max_venues)
            
            if not results or 'places' not in results:
                print(f"Failed to fetch bulk results: {results}")
                # Track failed query
                api_query = ApiQuery.objects.create(
                    query=query,
                    location=TEST_LOCATION['name'],
                    field_mask=PLACES_FIELD_MASK,
                    max_venues=max_venues,
                    response_json=json.dumps(results) if results else None,
                    venues_found=0,
                    venues_stored=0,
                    success=False
                )
                return
            
            places = results.get('places', [])
            print(f"Found {len(places)} total places")
            
            # Track successful query (will update venues_stored later)
            api_query = ApiQuery.objects.create(
                query=query,
                location=TEST_LOCATION['name'],
                field_mask=PLACES_FIELD_MASK,
                max_venues=max_venues,
                response_json=json.dumps(results),
                venues_found=len(places),
                venues_stored=0  # Will update after processing
            )
            
            # Debug: Print all available fields for the first place
            if places:
                print(f"\nDEBUG - First place fields: {list(places[0].keys())}")
                if 'googleMapsUri' in places[0]:
                    print(f"DEBUG - googleMapsUri found: {places[0].get('googleMapsUri')}")
                else:
                    print(f"DEBUG - googleMapsUri NOT found in place data")
            
            # Process places
            for place in places[:max_venues]:
                # Check if we should skip this venue
                should_skip, skip_reason = self.should_skip_venue(place, 30, area.lat, area.lng)
                if should_skip:
                    display_name = place.get('displayName', {}).get('text', 'Unknown')
                    print(f"Skipping {display_name} - {skip_reason}")
                    continue
                
                place_id = place.get('id')
                if place_id in processed_place_ids:
                    continue
                    
                processed_place_ids.add(place_id)
                
                # Check if venue already exists
                if Venue.objects.filter(place_id=place_id).exists():
                    display_name = place.get('displayName', {}).get('text', 'Unknown')
                    print(f"Venue already exists: {display_name}")
                    continue
                
                # Create venue
                venue_data = self.create_venue_from_place_data(place, area.id, generate_tags=True)
                if venue_data:
                    Venue.objects.create(**venue_data)
                    venues_created += 1
                    print(f"Created venue {venues_created}: {venue_data['name']}")
                    print(f"  Rating: {venue_data['rating']}, Price: {venue_data['price_level']}, Reviews: {venue_data['user_rating_count']}")
        
            # Update the API query with final venue count
            if venues_created > 0:
                api_query.venues_stored = venues_created
                api_query.save()
                print(f"Updated API query record: {venues_created} venues stored")
            
            print(f"\nCompleted! Created {venues_created} venues in database")
        
        except Exception as e:
            print(f"Error: {e}")


class Command(BaseCommand):
    help = 'Fetch venue data from Google Places API and populate Django database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fetched without saving to database'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting venue data fetch from Google Places API...")

        # Initialize fetcher
        try:
            fetcher = DataFetcher()
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            return
        
        # Category-specific queries with time constraint using global AREA_NAME and STATE_NAME
        cafe_queries = [
            f"specialty coffee cafes within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"cozy cafes for sitting and coffee within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"aesthetic brunch cafes within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        restaurant_queries = [
            f"popular dine in restaurants within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"casual lunch dinner restaurants within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"well rated restaurants for outings within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        dessert_queries = [
            f"dessert cafes pastry bakeries within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"ice cream gelato dessert spots within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"late evening dessert places within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        bar_queries = [
            f"cocktail bars lounges within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"popular nightlife bars within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"upscale bars for evening outings within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        activity_queries = [
            f"escape rooms mystery rooms puzzle games within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"bowling billiards pool snooker indoor sports within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"live music venues gigs concerts within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"theatre plays drama performance venues within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"stand up comedy open mic venues within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"art workshops pottery workshops creative workshops within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"virtual reality gaming VR experiences within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"bookstores book cafes reading lounges libraries within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"karaoke lounges singing rooms within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"trampoline parks adventure zones within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"go karting racing tracks within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"laser tag paintball indoor combat games within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"rock climbing bouldering indoor adventure within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"cooking classes culinary workshops within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"dance classes dance studios within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"spa wellness massage centers within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"board game cafes game lounges indoor entertainment within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        arcade_queries = [
            f"gaming arcades within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"bowling arcade gaming zones within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"pool snooker gaming lounges within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        cinema_queries = [
            f"movie theatres multiplex within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"cinema halls within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        park_queries = [
            f"major parks gardens within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"popular outdoor walking parks within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"well known leisure parks within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]

        shopping_queries = [
            f"shopping markets within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"popular retail markets within 15 minutes max of {AREA_NAME} {STATE_NAME}",
            f"mall shopping destinations within 15 minutes max of {AREA_NAME} {STATE_NAME}"
        ]
        
        print("=" * 60)
        print(f"FETCHING VENUES BY CATEGORY IN {AREA_NAME.upper()}")
        print("=" * 60)
        
        # Fetch venues by category
        all_queries = [
            ("CAFES", cafe_queries),
            ("RESTAURANTS", restaurant_queries),
            ("DESSERTS", dessert_queries),
            ("BARS", bar_queries),
            ("ACTIVITIES", activity_queries),
            ("ARCADES", arcade_queries),
            ("CINEMAS", cinema_queries),
            ("PARKS", park_queries),
            ("SHOPPING", shopping_queries)
        ]
        
        # Define max venues per query by category
        max_venues_per_category = {
            "CAFES": 20,
            "RESTAURANTS": 20,
            "BARS": 20,
            "DESSERTS": 20,
            "ACTIVITIES": 20,
            "ARCADES": 20,
            "PARKS": 20,
            "SHOPPING": 20,
            "CINEMAS": 20
        }
        
        # Create area
        area = fetcher.create_test_area()
        
        for category_name, queries in all_queries:
            max_venues = max_venues_per_category[category_name]
            print(f"\n🔍 Fetching {category_name.lower()} (max {max_venues} per query)...")
            for query in queries:
                if options['dry_run']:
                    print(f"DRY RUN - Would query: {query}")
                else:
                    fetcher.fetch_and_store_venues(query=query, max_venues=max_venues, area=area)
        
        if not options['dry_run']:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("Completed!"))
