"""
Initial data fetching script for testing data format and quality.
FastAPI version - fetches a small sample of venues from Google Places API.
"""

import os
import requests
import json
import math
import sys
from pathlib import Path

# Add parent directory to path to import from there
sys.path.append(str(Path(__file__).parent.parent))

from models import Venue, Area, ApiQuery, TAG_STRUCTURE, validate_tags, tags_to_json
from database import engine as default_engine
from sqlmodel import SQLModel, Session, select, create_engine
from datetime import datetime
from venue_utils import process_places_to_venues

# Global area and state variables
AREA_NAME = 'Noida Sector 18'
STATE_NAME = 'Uttar Pradesh'

# Test region - Noida Sector 18 (major commercial and residential area with a mix of local and international retail and dining options)
TEST_LOCATION = {
    'name': AREA_NAME,
    'lat': 28.5671476,
    'lng': 77.3185692,
    'radius': 3000  # 3km radius to cover Noida Sector 18 and surrounding areas
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
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = 'https://maps.googleapis.com/maps/api/place'
        
    def text_search(self, query, location, radius=500, max_results=20):
        """Search for places using Google Places API (New) - Text Search"""
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': PLACES_FIELD_MASK
        }
        
        # Calculate rectangle bounds around the center point
        lat_offset = radius / 111320  # Approximate meters per degree latitude
        lng_offset = radius / (111320 * abs(math.cos(math.radians(location['lat']))))  # Adjust for longitude
        
        data = {
            'textQuery': query,
            # Remove location restriction to allow broader search based on text query
            'maxResultCount': max_results,
            'minRating': 3.8,
            'languageCode': 'en'
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None
    
        
    def create_test_area(self, session):
        """Create test area in database using provided session"""
        # Check if area already exists
        statement = select(Area).where(Area.name == TEST_LOCATION['name'])
        existing_area = session.exec(statement).first()
        if existing_area:
            print(f"Area '{TEST_LOCATION['name']}' already exists")
            return existing_area
        
        area = Area(
            name=TEST_LOCATION['name'],
            lat=TEST_LOCATION['lat'],
            lng=TEST_LOCATION['lng'],
            country='India',
            state='Delhi',
            is_active=True
        )
        
        session.add(area)
        session.commit()
        session.refresh(area)
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
            'category': set(),
            'vibe': set(),
            'special': set(),
            'price': set()
        }
        
        name_lower = venue_data['name'].lower()
        types = venue_data.get('types', [])
        
        # Category tags based on types and name
        if 'cafe' in types or 'cafe' in name_lower:
            tags['category'].add('cafe')
        if 'restaurant' in types or 'restaurant' in name_lower:
            tags['category'].add('restaurant')
        if 'bar' in types or 'bar' in name_lower or 'pub' in name_lower:
            tags['category'].add('bar')
        if 'shopping_mall' in types or 'store' in types:
            tags['category'].add('shopping')
        if 'movie_theater' in types or 'cinema' in name_lower:
            tags['category'].add('cinema')
        
        # Convert price level string to numeric for comparison
        price_level = self.convert_price_level(venue_data.get('price_level', 'PRICE_LEVEL_MODERATE'))
        
        # Price and vibe tags based on price level
        if price_level >= 4:
            tags['price'].add('premium')
            tags['vibe'].add('fancy')
        elif price_level == 3:
            tags['price'].add('expensive')
            tags['vibe'].add('upscale')
        elif price_level <= 2:
            tags['price'].add('affordable')
        
        # Additional vibe tags based on name
        if 'cafe' in name_lower or 'coffee' in name_lower:
            tags['vibe'].add('cozy')
        
        # Special tags
        if 'romantic' in name_lower or price_level >= 4:
            tags['special'].add('date_spot')
        
        # Convert sets back to lists for JSON serialization
        return {key: list(value) for key, value in tags.items()}
    
    def fetch_and_store_venues(self, query=BULK_SEARCH_QUERY, max_venues=20):
        """Fetch venues and store in database"""
        print(f"Fetching test data for {TEST_LOCATION['name']}...")
        print(f"Using query: {query}")
        
        # Get the absolute path to the api_engine directory (parent of population_tools)
        api_engine_path = Path(__file__).parent.parent
        db_path = api_engine_path / "plan_engine.db"
        
        # Create a new engine with the correct absolute path
        db_url = f'sqlite:///{db_path.absolute()}'
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        
        # Create database tables function
        def create_db_and_tables():
            SQLModel.metadata.create_all(engine)
        
        try:
            # Ensure database and tables exist
            create_db_and_tables()
            
            # Create single session for entire operation
            session = Session(engine)
            
            area = self.create_test_area(session)
            venues_created = 0
            processed_place_ids = set()
            
            try:
                # Single bulk fetch instead of multiple queries
                print(f"\nBulk search: {query}")
                
                results = self.text_search(query, TEST_LOCATION, max_results=max_venues)
                
                if not results or 'places' not in results:
                    print(f"Failed to fetch bulk results: {results}")
                    # Track failed query
                    api_query = ApiQuery(
                        query=query,
                        location=TEST_LOCATION['name'],
                        field_mask=PLACES_FIELD_MASK,
                        max_venues=max_venues,
                        response_json=json.dumps(results) if results else None,
                        venues_found=0,
                        venues_stored=0,
                        success=False
                    )
                    session.add(api_query)
                    session.commit()
                    return
                
                places = results.get('places', [])
                print(f"Found {len(places)} total places")
                
                # Track successful query (will update venues_stored later)
                api_query = ApiQuery(
                    query=query,
                    location=TEST_LOCATION['name'],
                    field_mask=PLACES_FIELD_MASK,
                    max_venues=max_venues,
                    response_json=json.dumps(results),
                    venues_found=len(places),
                    venues_stored=0  # Will update after processing
                )
                session.add(api_query)
                session.commit()
                session.refresh(api_query)
                
                # Debug: Print all available fields for the first place
                if places:
                    print(f"\nDEBUG - First place fields: {list(places[0].keys())}")
                    if 'googleMapsUri' in places[0]:
                        print(f"DEBUG - googleMapsUri found: {places[0].get('googleMapsUri')}")
                    else:
                        print(f"DEBUG - googleMapsUri NOT found in place data")
                
                # Process places using common function
                venues_saved, venues_skipped, errors = process_places_to_venues(
                    places[:max_venues],  # Limit to max_venues
                    area.id,
                    session,
                    min_rating_count=30,
                    generate_tags=True,
                    area_lat=area.lat,
                    area_lng=area.lng
                )
                
                venues_created = venues_saved
            
            finally:
                # Update the API query with final venue count
                if venues_created > 0:
                    api_query.venues_stored = venues_created
                    session.commit()
                    print(f"Updated API query record: {venues_created} venues stored")
                
                session.close()
            
            print(f"\nCompleted! Created {venues_created} venues in database")
        
        finally:
            # No need to restore DATABASE_URL since we're using a local engine
            pass

def main():
    """Main execution function - fetches top-rated venues only"""
    if not os.getenv('GOOGLE_PLACES_API_KEY'):
        print("Error: GOOGLE_PLACES_API_KEY environment variable not set")
        print("Please set it in your environment:")
        print("PowerShell: $env:GOOGLE_PLACES_API_KEY = 'your_key_here'")
        print("CMD: set GOOGLE_PLACES_API_KEY=your_key_here")
        return
    
    fetcher = DataFetcher()
    
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
        f"escape rooms mystery rooms puzzle games within 15 minutes max of {AREA_NAME} {STATE_NAME}",           # save 4
        f"bowling billiards pool snooker indoor sports within 15 minutes max of {AREA_NAME} {STATE_NAME}",       # save 4
        f"live music venues gigs concerts within 15 minutes max of {AREA_NAME} {STATE_NAME}",                    # save 4
        f"theatre plays drama performance venues within 15 minutes max of {AREA_NAME} {STATE_NAME}",             # save 3
        f"stand up comedy open mic venues within 15 minutes max of {AREA_NAME} {STATE_NAME}",                    # save 3
        f"art workshops pottery workshops creative workshops within 15 minutes max of {AREA_NAME} {STATE_NAME}", # save 3
        f"virtual reality gaming VR experiences within 15 minutes max of {AREA_NAME} {STATE_NAME}",              # save 3
        f"board game cafes game lounges indoor entertainment within 15 minutes max of {AREA_NAME} {STATE_NAME}"  # save 3
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
    for category_name, queries in all_queries:
        max_venues = max_venues_per_category[category_name]
        print(f"\n🔍 Fetching {category_name.lower()} (max {max_venues} per query)...")
        for query in queries:
            fetcher.fetch_and_store_venues(query=query, max_venues=max_venues)

if __name__ == "__main__":
    main()
