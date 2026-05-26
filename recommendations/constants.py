"""
Constants for the Plan Recommendation Engine
"""

VENUE_SWITCH_PROBABILITY = 0.2

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
    'price_tags': 0.7
}

CATEGORY_ENERGIES = {
    "cafe": "soft",
    "dessert": "soft",
    "park": "soft",

    "restaurant": "anchored",
    "cinema": "anchored",

    "activity": "energetic",
    "arcade": "energetic",

    "bar": "nightlife",

    "shopping": "exploration"
}

ENERGY_TRANSITIONS = {
    ("soft", "soft"): [
        "Keeping the pace slower here usually makes the conversation flow more naturally.",
        "The relaxed atmosphere carries well into the next stop.",
        "This pairing works nicely when you don't want the evening to feel rushed."
    ],

    ("soft", "anchored"): [
        "Starting lighter before settling into something more substantial usually works well here.",
        "The slower opening makes the next stop feel more intentional.",
        "This transition gives the evening a stronger centerpiece without feeling abrupt."
    ],

    ("soft", "energetic"): [
        "The quieter start makes the energy shift feel more noticeable later on.",
        "This route gradually pulls the evening into something more lively.",
        "A calmer opening helps the more active stop stand out better."
    ],

    ("soft", "nightlife"): [
        "This pacing usually works well if you want the night to build gradually.",
        "Starting softer makes the later nightlife stretch feel more natural.",
        "The route eases into a more social atmosphere instead of jumping straight into it."
    ],

    ("soft", "exploration"): [
        "A relaxed opening works well before wandering through nearby spots.",
        "This kind of transition keeps the evening feeling flexible.",
        "The pacing opens up naturally after the slower start."
    ],

    ("anchored", "soft"): [
        "A lighter stop afterward helps the evening slow down naturally.",
        "This pairing usually keeps the route from feeling too heavy all the way through.",
        "The softer follow-up balances the pacing nicely."
    ],

    ("anchored", "anchored"): [
        "Keeping both stops more grounded gives the evening a steadier rhythm.",
        "This progression works well when you want the pacing to stay consistent.",
        "The route stays balanced without changing energy too aggressively."
    ],

    ("anchored", "energetic"): [
        "The shift into something more active keeps the evening from plateauing.",
        "This usually works well when the night needs a little momentum afterward.",
        "The pacing becomes noticeably livelier after the slower stretch."
    ],

    ("anchored", "nightlife"): [
        "The evening naturally becomes more social after the central stop.",
        "This transition usually works well later into the night.",
        "The pacing gradually leans into a more lively atmosphere."
    ],

    ("anchored", "exploration"): [
        "The route becomes more flexible after the more structured stop.",
        "This keeps the evening from feeling overly planned.",
        "A more open-ended stretch afterward balances the pacing nicely."
    ],

    ("energetic", "soft"): [
        "Slowing things down afterward keeps the route from burning out too quickly.",
        "A calmer stop helps balance the earlier energy.",
        "This transition gives the evening room to breathe."
    ],

    ("energetic", "anchored"): [
        "The steadier follow-up helps ground the pacing a little.",
        "This usually works better than stacking too many high-energy stops together.",
        "The route settles slightly after the earlier momentum."
    ],

    ("energetic", "energetic"): [
        "Keeping the momentum going works well for this kind of route.",
        "The pacing stays lively without slowing down too early.",
        "This stretch keeps the evening feeling active throughout."
    ],

    ("energetic", "nightlife"): [
        "The momentum carries naturally into nightlife afterward.",
        "This transition usually feels pretty seamless later into the evening.",
        "The route builds naturally toward a more social atmosphere."
    ],

    ("energetic", "exploration"): [
        "Opening the pacing up afterward keeps the route from feeling repetitive.",
        "The evening becomes more flexible after the active stretch.",
        "This transition softens the structure slightly without losing momentum."
    ],

    ("nightlife", "soft"): [
        "A quieter stop afterward usually makes the ending feel smoother.",
        "This helps the route come down naturally after the nightlife stretch.",
        "The softer finish balances the later-night energy nicely."
    ],

    ("nightlife", "anchored"): [
        "The steadier stop afterward keeps the pacing from staying too intense.",
        "This transition helps settle the evening slightly.",
        "A more grounded follow-up balances the nightlife energy."
    ],

    ("nightlife", "energetic"): [
        "The route keeps its momentum going without slowing down yet.",
        "This works well if the goal is to keep the energy high throughout.",
        "The later stages stay consistently lively."
    ],

    ("nightlife", "nightlife"): [
        "Keeping both stops lively usually works best later into the evening.",
        "The route stays fully in late-night territory here.",
        "This progression keeps the social energy going throughout."
    ],

    ("nightlife", "exploration"): [
        "The route becomes less structured after the nightlife stretch.",
        "This gives the ending a more open-ended feel.",
        "The pacing loosens naturally afterward."
    ],

    ("exploration", "soft"): [
        "A calmer stop afterward helps the route settle naturally.",
        "This pairing slows things down after moving around more actively.",
        "The pacing becomes more relaxed after the exploratory stretch."
    ],

    ("exploration", "anchored"): [
        "The steadier stop afterward gives the evening more structure again.",
        "This transition helps ground the pacing slightly.",
        "A more central venue balances the exploratory stretch nicely."
    ],

    ("exploration", "energetic"): [
        "The pacing picks up naturally after the slower wandering stretch.",
        "This transition works well when the evening needs another energy shift.",
        "A more active stop changes the atmosphere noticeably."
    ],

    ("exploration", "nightlife"): [
        "The route naturally leans into nightlife afterward.",
        "This pacing works well when the evening gradually becomes more social.",
        "The energy builds steadily toward the later stages."
    ],

    ("exploration", "exploration"): [
        "Keeping the route flexible throughout gives it a more spontaneous feel.",
        "This progression works well when the evening is more about wandering between spots.",
        "The pacing stays open-ended without feeling directionless."
    ]
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
