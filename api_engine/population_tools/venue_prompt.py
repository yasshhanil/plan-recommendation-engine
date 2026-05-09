"""
Venue Analysis Prompt
Structured prompt for venue validation and tagging
"""

from typing import List

VENUE_BATCH_ANALYSIS_PROMPT = """You are given structured data about multiple venues.

Your task:
1. For EACH venue, determine whether it is suitable for inclusion in a curated outing/experience planning app.
2. If suitable, generate a concise summary and assign tags.
3. If NOT suitable, mark it as rejected.

---

WHAT MAKES A VALID VENUE:

A venue should:
- Be a clear destination people intentionally visit (e.g., cafe, restaurant, bar, arcade, cinema, park, shopping area)
- Offer a defined experience (e.g., dining, entertainment, activity, leisure)
- Be suitable as a meaningful stop in a multi-step plan

---

WHAT TO REJECT:

Reject the venue if it is:
- A generic public space (e.g., random square, street, market area without a specific attraction)
- A transitional or pass-through location (e.g., walkway, open plaza without defined purpose)
- Lacking a clear primary activity or experience
- Too vague, low-effort, or not something users would actively choose as a destination

---

CRITICAL REJECTION RULE:

A venue must be a strong, intentional destination.

Reject the venue if:
- It is something people encounter incidentally rather than plan to visit
- It lacks a defined or structured experience
- It is commonly passed through rather than specifically chosen
- It does not justify being a primary stop in a plan

Examples of places to REJECT:
- generic public squares
- open market areas without a specific attraction
- spots mainly used for passing time (e.g., feeding pigeons, sitting casually)

Even if it has activity or is outdoors, reject it if the experience is weak or not purposeful.

SELF-CHECK:

Ask yourself:
"Would a user feel excited or satisfied if this was suggested as a main stop?"

If the answer is no → reject.

---

NON-EXPERIENTIAL LANDMARK RULE:

Reject venues that are primarily:
- statues
- standalone monuments
- memorials
- decorative or symbolic structures

These may have historical or cultural significance, but should be rejected if they do NOT offer a structured or engaging experience.

A venue must involve active participation (e.g., dining, shopping, exploring, entertainment) or meaningful time spent.

Simply viewing or briefly stopping at a landmark is NOT sufficient.

---

PARK VALIDATION RULE:

Parks are valid ONLY if they are widely recognized destinations where people intentionally spend time (e.g., large, well-known parks with activities, walking trails, or social gatherings).

Reject:
- small parks
- unnamed green areas
- spaces where the main attraction is a statue or a minor feature

---

TIME VALUE CHECK:

Ask:
"Would a typical user spend at least 20–30 minutes here intentionally?"

If NO → reject.

---

CATEGORY TAG PRIORITY RULE:

Assign category tags based on the PRIMARY reason a person intentionally visits the venue.

Do not assign broad secondary categories just because they are technically possible.

Examples:
- A restaurant with ambiance is still primarily "restaurant", not "activity"
- A bar with music is still primarily "bar", not "activity"
- A cafe where people sit for long periods is still primarily "cafe", not "activity"

---

ACTIVITY TAG ASSIGNMENT RULE:

DO NOT assign "activity" tag to food/drink venues (cafe, restaurant, dessert, bar) UNLESS:

The venue has a PROPER SOLID ACTIVITY as a core part of the experience, such as:
- Live cooking classes, workshops, or interactive food experiences
- Board game cafes with extensive game libraries and dedicated gaming areas
- Karaoke bars with private rooms and professional setup
- Sports bars with multiple large screens for viewing major sporting events
- Breweries with active brewing tours/tasting experiences
- Entertainment venues that happen to serve food but where the activity is the main draw

Examples of what DOES NOT qualify for "activity" tag:
- Regular restaurants with nice ambiance
- Standard cafes where people just eat/drink
- Bars with background music
- Food courts
- Casual dining establishments

The activity must be a significant, structured experience that people specifically seek out, not just a secondary feature of a food establishment.

For non-food venues, assign "activity" when the venue is primarily used for:
- escape rooms
- bowling
- billiards / pool / snooker
- virtual reality gaming
- workshops (art, pottery, creative sessions)
- live performances
- theatre / plays / drama
- stand-up comedy / open mic
- concerts / live music
- exhibitions
- sports / recreational play

IMPORTANT:

A venue does NOT need to be a traditional arcade or formal entertainment center
to receive the "activity" tag.

If the main reason people visit is participation, engagement, or a planned experience,
"activity" should usually be assigned.

When unsure, prefer assigning "activity" rather than omitting it.

---

REVIEW INTERPRETATION RULE:

Do not confuse detailed or historical reviews with a strong venue experience.

Long or informative reviews do NOT make a place a valid destination unless they describe an engaging activity or experience that justifies being a primary stop.

---

TOURIST ATTRACTION FILTER:

For tourist attractions, eliminate all niche/non-major attractions.

Accept ONLY:
- Major, widely recognized tourist destinations
- Iconic landmarks that people travel specifically to visit
- Well-known attractions with significant cultural/historical importance

Reject:
- Minor statues, small memorials, local monuments
- Niche or specialized attractions
- Places that are not primary tourist destinations
- Attractions that locals would know but tourists wouldn't seek out

Ask: "Is this a major attraction that would appear in top 10 tourist guides for the city?"

If NO → reject.

---

TAG OPTIONS:

CATEGORY_TAGS:
['cafe', 'restaurant', 'dessert', 'bar', 'activity', 'arcade', 'cinema', 'park', 'shopping']

VIBE_TAGS:
['cozy', 'fancy', 'aesthetic', 'casual', 'lively', 'quiet', 'romantic', 'trendy', 'family_friendly']

SPECIAL_TAGS:
['date_spot', 'group_friendly', 'quick_stop', 'late_night', 'outdoor', 'indoor']

PRICE_TAGS:
['affordable', 'moderate', 'upscale']

---

RULES:

- For EACH venue: First decide: should this venue be rejected?
- If rejected:
  - Set "rejected": true
  - Return empty arrays for all tag fields
  - Summary should briefly explain why it is not suitable (1 line max)

- If NOT rejected:
  - Set "rejected": false
  - Assign:
    - 1–2 category tags (at least 1 required)
    - 2–4 vibe tags
    - 1–3 special tags (only if clearly supported)
    - exactly 1 price tag

- Use ONLY the tags provided above. Do NOT invent new tags.

- Base your decisions on:
  - raw_types
  - review text
  - overall context

- Prioritize strong, intentional experiences over generic descriptions.

- Avoid generic summaries like "nice place" or "good spot".

- Infer price tag from context:
  - expensive, luxury → upscale
  - normal pricing → moderate
  - cheap, budget → affordable

- If unsure whether it's a real destination, lean toward rejection.

---

INPUT:
{venues_json}

---

OUTPUT FORMAT (strict JSON array):

[
  {{
    "venue_id": <number>,
    "rejected": <true/false>,
    "summary": "...",
    "category_tags": ["..."],
    "vibe_tags": ["..."],
    "special_tags": ["..."],
    "price_tags": ["..."]
  }},
  {{
    "venue_id": <number>,
    "rejected": <true/false>,
    "summary": "...",
    "category_tags": ["..."],
    "vibe_tags": ["..."],
    "special_tags": ["..."],
    "price_tags": ["..."]
  }},
  ...
]

IMPORTANT: Return an ARRAY with ONE object for EACH venue in the input, in the same order."""

VENUE_ANALYSIS_PROMPT = """You are given structured data about a venue.

Your task:
1. Determine whether this venue is suitable for inclusion in a curated outing/experience planning app.
2. If suitable, generate a concise summary and assign tags.
3. If NOT suitable, mark it as rejected.

---

WHAT MAKES A VALID VENUE:

A venue should:
- Be a clear destination people intentionally visit (e.g., cafe, restaurant, bar, arcade, cinema, park, shopping area)
- Offer a defined experience (e.g., dining, entertainment, activity, leisure)
- Be suitable as a meaningful stop in a multi-step plan

---

WHAT TO REJECT:

Reject the venue if it is:
- A generic public space (e.g., random square, street, market area without a specific attraction)
- A transitional or pass-through location (e.g., walkway, open plaza without defined purpose)
- Lacking a clear primary activity or experience
- Too vague, low-effort, or not something users would actively choose as a destination

---

CRITICAL REJECTION RULE:

A venue must be a strong, intentional destination.

Reject the venue if:
- It is something people encounter incidentally rather than plan to visit
- It lacks a defined or structured experience
- It is commonly passed through rather than specifically chosen
- It does not justify being a primary stop in a plan

Examples of places to REJECT:
- generic public squares
- open market areas without a specific attraction
- spots mainly used for passing time (e.g., feeding pigeons, sitting casually)

Even if it has activity or is outdoors, reject it if the experience is weak or not purposeful.

SELF-CHECK:

Ask yourself:
"Would a user feel excited or satisfied if this was suggested as a main stop?"

If the answer is no → reject.

---

NON-EXPERIENTIAL LANDMARK RULE:

Reject venues that are primarily:
- statues
- standalone monuments
- memorials
- decorative or symbolic structures

These may have historical or cultural significance, but should be rejected if they do NOT offer a structured or engaging experience.

A venue must involve active participation (e.g., dining, shopping, exploring, entertainment) or meaningful time spent.

Simply viewing or briefly stopping at a landmark is NOT sufficient.

---

PARK VALIDATION RULE:

Parks are valid ONLY if they are widely recognized destinations where people intentionally spend time (e.g., large, well-known parks with activities, walking trails, or social gatherings).

Reject:
- small parks
- unnamed green areas
- spaces where the main attraction is a statue or a minor feature

---

TIME VALUE CHECK:

Ask:
"Would a typical user spend at least 20–30 minutes here intentionally?"

If NO → reject.

---

CATEGORY TAG PRIORITY RULE:

Assign category tags based on the PRIMARY reason a person intentionally visits the venue.

Do not assign broad secondary categories just because they are technically possible.

Examples:
- A restaurant with ambiance is still primarily "restaurant", not "activity"
- A bar with music is still primarily "bar", not "activity"
- A cafe where people sit for long periods is still primarily "cafe", not "activity"

---

ACTIVITY TAG ASSIGNMENT RULE:

DO NOT assign "activity" tag to food/drink venues (cafe, restaurant, dessert, bar) UNLESS:

The venue has a PROPER SOLID ACTIVITY as a core part of the experience, such as:
- Live cooking classes, workshops, or interactive food experiences
- Board game cafes with extensive game libraries and dedicated gaming areas
- Karaoke bars with private rooms and professional setup
- Sports bars with multiple large screens for viewing major sporting events
- Breweries with active brewing tours/tasting experiences
- Entertainment venues that happen to serve food but where the activity is the main draw

Examples of what DOES NOT qualify for "activity" tag:
- Regular restaurants with nice ambiance
- Standard cafes where people just eat/drink
- Bars with background music
- Food courts
- Casual dining establishments

The activity must be a significant, structured experience that people specifically seek out, not just a secondary feature of a food establishment.

---

REVIEW INTERPRETATION RULE:

Do not confuse detailed or historical reviews with a strong venue experience.

Long or informative reviews do NOT make a place a valid destination unless they describe an engaging activity or experience that justifies being a primary stop.

---

TOURIST ATTRACTION FILTER:

For tourist attractions, eliminate all niche/non-major attractions.

Accept ONLY:
- Major, widely recognized tourist destinations
- Iconic landmarks that people travel specifically to visit
- Well-known attractions with significant cultural/historical importance

Reject:
- Minor statues, small memorials, local monuments
- Niche or specialized attractions
- Places that are not primary tourist destinations
- Attractions that locals would know but tourists wouldn't seek out

Ask: "Is this a major attraction that would appear in top 10 tourist guides for the city?"

If NO → reject.

---

TAG OPTIONS:

CATEGORY_TAGS:
['cafe', 'restaurant', 'dessert', 'bar', 'activity', 'arcade', 'cinema', 'park', 'shopping']

VIBE_TAGS:
['cozy', 'fancy', 'aesthetic', 'casual', 'lively', 'quiet', 'romantic', 'trendy', 'family_friendly']

SPECIAL_TAGS:
['date_spot', 'group_friendly', 'quick_stop', 'late_night', 'outdoor', 'indoor']

PRICE_TAGS:
['affordable', 'moderate', 'upscale']

---

RULES:

- First decide: should this venue be rejected?
- If rejected:
  - Set "rejected": true
  - Return empty arrays for all tag fields
  - Summary should briefly explain why it is not suitable (1 line max)

- If NOT rejected:
  - Set "rejected": false
  - Assign:
    - 1–2 category tags (at least 1 required)
    - 2–4 vibe tags
    - 1–3 special tags (only if clearly supported)
    - exactly 1 price tag

- Use ONLY the tags provided above. Do NOT invent new tags.

- Base your decisions on:
  - raw_types
  - review text
  - overall context

- Prioritize strong, intentional experiences over generic descriptions.

- Avoid generic summaries like "nice place" or "good spot".

- Infer price tag from context:
  - expensive, luxury → upscale
  - normal pricing → moderate
  - cheap, budget → affordable

- If unsure whether it's a real destination, lean toward rejection.

---

INPUT:
{venue_json}

---

OUTPUT FORMAT (strict JSON):

{{
  "venue_id": <number>,
  "rejected": <true/false>,
  "summary": "...",
  "category_tags": ["..."],
  "vibe_tags": ["..."],
  "special_tags": ["..."],
  "price_tags": ["..."]
}}"""


def get_batch_venue_prompt(venues_batch: List[dict]) -> str:
    """Get the formatted batch venue analysis prompt"""
    import json
    
    # Format all venues data as JSON array for the prompt
    venues_json = json.dumps(venues_batch, indent=2)
    
    return VENUE_BATCH_ANALYSIS_PROMPT.format(venues_json=venues_json)


def get_venue_prompt(venue_data: dict) -> str:
    """Get the formatted venue analysis prompt"""
    import json
    
    # Format the venue data as JSON for the prompt
    venue_json = json.dumps(venue_data, indent=2)
    
    return VENUE_ANALYSIS_PROMPT.format(venue_json=venue_json)
