"""
Constants for the Plan Recommendation Engine
"""

VENUE_SWITCH_PROBABILITY = 0.22

CATEGORY_TAGS = [
    'cafe', 'restaurant', 'dessert', 'bar', 'activity', 'shopping'
]

# Internal tags (not user-facing)
INTERNAL_CATEGORY_TAGS = ['arcade', 'cinema', 'park']

VIBE_TAGS = [
    'cozy', 'fancy', 'aesthetic', 'casual', 'lively', 
    'quiet', 'romantic', 'trendy', 'family_friendly'
]

SPECIAL_TAGS = ['date_spot', 'group_friendly', 
 'quick_stop', 'late_night', 'outdoor', 'indoor']

PRICE_TAGS = ['affordable', 'moderate', 'upscale']

TAGS_CONSTANT = {
    'category_tags': CATEGORY_TAGS + INTERNAL_CATEGORY_TAGS,
    'vibe_tags': VIBE_TAGS,
    'special_tags': SPECIAL_TAGS,
    'price_tags': PRICE_TAGS
}

tag_weight_chart = {
    'category_tags': 0.7,
    'vibe_tags': 0.6,
    'special_tags': 0.4,
    'price_tags': 1.0
}

# Venue scoring weights
venue_scoring_weights = {
    'category_tags': 1.5,
    'vibe_tags': 0.65,
    'special_tags': 0.4,
    'price_tags': 0.5
}

tag_decay_chart = {
    'user_selected': {
        'category_tags': 0.3,
        'vibe_tags': 0.6,
        'special_tags': 0.75,
        'price_tags': 1.0
    },
    'random_selected': {
        'category_tags': 0.15,
        'vibe_tags': 0.4,
        'special_tags': 0.55,
        'price_tags': 1.0
    }
}

GOOGLE_PLACES_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
GOOGLE_PLACES_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"
MAX_IMAGE_WIDTH = 400  
