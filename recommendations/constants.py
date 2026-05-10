"""
Constants for the Plan Recommendation Engine
"""

VENUE_SWITCH_PROBABILITY = 0.7

CATEGORY_TAGS = [
    'cafe', 'restaurant', 'dessert', 'bar', 'activity', 
    'arcade', 'cinema', 'park', 'shopping'
]

VIBE_TAGS = [
    'cozy', 'fancy', 'aesthetic', 'casual', 'lively', 
    'quiet', 'romantic', 'trendy', 'family_friendly'
]

SPECIAL_TAGS = ['date_spot', 'group_friendly', 
 'quick_stop', 'late_night', 'outdoor', 'indoor']

PRICE_TAGS = ['affordable', 'moderate', 'upscale']

TAGS_CONSTANT = {
    'category_tags': CATEGORY_TAGS,
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
