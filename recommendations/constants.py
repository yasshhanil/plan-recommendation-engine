"""
Constants for the Plan Recommendation Engine
"""

VENUE_SWITCH_PROBABILITY = 0.9

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
        "No rush. Two slower stops in a row is actually where the best conversations tend to happen.",
        "You're keeping the whole evening unhurried — some nights are just better that way.",
        "There's no agenda here, and that's exactly the point."
    ],

    ("soft", "anchored"): [
        "A lighter start before something more substantial — you'll arrive at the next stop in exactly the right headspace.",
        "You're easing in before the main event. Good way to make sure the centerpiece actually lands.",
        "The slower opening earns the next stop. You'll feel the difference."
    ],

    ("soft", "energetic"): [
        "The quiet start makes what's coming hit differently. You'll feel the shift when you get there.",
        "Starting calm before something active is one of those sequences that tends to just work.",
        "By the time you arrive at the next stop, you'll be ready for it."
    ],

    ("soft", "nightlife"): [
        "You're letting the night breathe before it opens up. There's something nice about arriving at the bar already relaxed.",
        "The calm start makes the later energy feel earned, not forced.",
        "This is how a good night builds — slowly, then all at once."
    ],

    ("soft", "exploration"): [
        "Starting relaxed sets you up to wander properly. No agenda, just seeing what catches your eye.",
        "A slower opener gives the rest of the evening room to take its own shape.",
        "The best kind of wandering starts from a place of zero pressure."
    ],

    ("anchored", "soft"): [
        "Good call — after something substantial, somewhere quieter to just sit with it makes the whole evening feel complete.",
        "Moving to something slower after the main stop gives the night a proper landing.",
        "You've had the centerpiece. Now you get to actually enjoy the afterglow."
    ],

    ("anchored", "anchored"): [
        "Both stops carry some weight. This is an evening with substance — nothing rushed, nothing skipped.",
        "Not every night needs a high point. Sometimes two grounded stops in a row is exactly right.",
        "You're building something that has real texture to it."
    ],

    ("anchored", "energetic"): [
        "Full and settled, then somewhere to move. The energy shift after something grounded tends to catch people off guard in the best way.",
        "You're not ending on a plateau — there's still somewhere for the night to go.",
        "After the anchor, the active stop is going to feel like a second wind."
    ],

    ("anchored", "nightlife"): [
        "Dinner first, drinks after. The classics are classic for a reason — you'll hit the bar already in a good groove.",
        "The main stop sets you up for it. By the time you're out, you'll want exactly what's next.",
        "This sequence tends to snowball. In a good way."
    ],

    ("anchored", "exploration"): [
        "You've had the anchor. The rest of the night can take its own shape now.",
        "No fixed plan after this one — and that's actually the better half of the evening.",
        "One solid stop, then room to wander. That balance usually works well."
    ],

    ("energetic", "soft"): [
        "You'll want this. Somewhere to actually land after the energy peaks — it hits different when you're properly wound down.",
        "Slowing down after a high is its own reward. The contrast makes both stops better.",
        "The active stretch earns the quiet one. That's a good sequence."
    ],

    ("energetic", "anchored"): [
        "Earn the meal. Moving to something more settled after the active stretch is one of the better sequences you can do.",
        "You'll arrive at the next stop with a good kind of tired. The kind that makes sitting down feel right.",
        "The momentum finds a place to rest here. That's not a bad thing."
    ],

    ("energetic", "energetic"): [
        "You're building on it. Some nights just want to stay in motion — this is that kind of night.",
        "The energy has nowhere to go but forward. Lean into it.",
        "Not slowing down yet. There's more to do and you're going to do it."
    ],

    ("energetic", "nightlife"): [
        "The energy has nowhere to go but out. Active into nightlife is one of those transitions that tends to just work.",
        "You're arriving at the bar already warmed up. Everyone around you is starting cold.",
        "The momentum carries. By the time you get there, the night is already yours."
    ],

    ("energetic", "exploration"): [
        "After the active stretch, a little wandering gives you room to come down without actually stopping.",
        "The structure loosens here — which, after something high-energy, is exactly what you want.",
        "Less direction, more instinct. Good place to be after the earlier stop."
    ],

    ("nightlife", "soft"): [
        "Ending somewhere quiet after the bar gives the night a proper landing. Less abrupt than just calling it.",
        "Good instinct — the softer finish makes the whole evening feel more intentional.",
        "A calmer closer turns a good night into a night you'll actually remember clearly."
    ],

    ("nightlife", "anchored"): [
        "Late-night food hits different. This is a genuinely good closer — something real to end on.",
        "You're not just tapering off — you're ending on something that means something.",
        "The bar set the mood. Now you get to sit in it properly."
    ],

    ("nightlife", "energetic"): [
        "Not done yet. There's something a little chaotic about this combination and that's kind of the point.",
        "You're keeping the engine running. The night isn't ready to slow down and neither are you.",
        "This is the kind of itinerary that turns into a story."
    ],

    ("nightlife", "nightlife"): [
        "You're not slowing down. Two nightlife stops is a deliberate call — commit to it and you'll have a better time.",
        "The whole evening lives in this register. Lean in.",
        "Some nights are just about staying out. This is one of them."
    ],

    ("nightlife", "exploration"): [
        "The night starts to follow you at this point. Less plan, more instinct — that's usually where the good stuff happens.",
        "After the bar, nowhere specific to be. That's actually a pretty good place to be.",
        "The structure is gone and the evening is better for it."
    ],

    ("exploration", "soft"): [
        "After moving around for a bit, sitting somewhere relaxed is its own reward. You'll appreciate it more for having wandered first.",
        "The contrast earns itself — restless first, then settled. That's a satisfying arc.",
        "You've covered ground. Now you get to just be somewhere."
    ],

    ("exploration", "anchored"): [
        "Wandering gives you an appetite — in more ways than one. Sitting down to something proper afterward actually feels earned.",
        "The exploratory stretch builds toward this. The next stop is going to feel like exactly the right place to land.",
        "You've been out there. Now there's somewhere real to arrive."
    ],

    ("exploration", "energetic"): [
        "The restlessness builds while you're out there. By the time you hit the next stop, you'll be ready to move.",
        "Wandering first means you're already in the right mindset for what's next.",
        "The energy has been simmering. Now it has somewhere to go."
    ],

    ("exploration", "nightlife"): [
        "You've been wandering — now the night has somewhere to actually land. The bar feels like a reward at this point.",
        "The open-ended stretch leads somewhere specific. That's a satisfying way to arrive.",
        "All that movement lands here. It's going to feel right."
    ],

    ("exploration", "exploration"): [
        "No anchor tonight — just letting the city lead. This kind of evening either becomes a story or a very good walk.",
        "You're giving the night full permission to surprise you. That's a good call.",
        "Nowhere to be, everywhere to go. Some evenings are just like that."
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
