import random
import json
import logging
import requests
import io
import os
import tempfile
from typing import Dict, List, Optional, Any
from google.cloud import storage
from django.conf import settings
from django.db import models as django_models
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from .models import Venue, Area, TAGS_CONSTANT
from .constants import TAGS_CONSTANT, VENUE_SWITCH_PROBABILITY, tag_weight_chart, tag_decay_chart, venue_scoring_weights, CATEGORY_ENERGIES, ENERGY_TRANSITIONS

logger = logging.getLogger(__name__)


def fetch_google_places_image_url(photo_name: str, max_width: int = 400) -> Optional[str]:
    """
    Generate Google Places API (New) photo media URL
    """

    api_key = settings.GOOGLE_PLACES_API_KEY

    if not photo_name:
        return None

    try:
        image_url = (
            f"https://places.googleapis.com/v1/"
            f"{photo_name}/media"
            f"?maxWidthPx={max_width}"
            f"&key={api_key}"
        )

        return image_url

    except Exception as e:
        logger.error(f"Error generating image URL: {str(e)}")
        return None


def bulk_upload_venue_images(venues: List[Venue]) -> Dict[int, Optional[str]]:
    """
    Bulk upload images for multiple venues to GCS using batch operations.

    Args:
        venues: List of Venue objects

    Returns:
        Dictionary mapping venue_id to GCS image URL (or None if failed)
    """

    venue_urls = {}
    client = storage.Client()
    bucket = client.bucket(settings.GS_BUCKET_NAME)

    blobs_to_check = []
    for venue in venues:
        if not venue.photo_reference:
            venue_urls[venue.id] = None
            continue
        gcs_path = f"venue_images/{venue.id}.jpg"
        blobs_to_check.append((venue, gcs_path))

    existing_venues = set()
    for venue, gcs_path in blobs_to_check:
        logger.info(f"[bulk_upload_venue_images] Checking if image exists for {venue.name} at {gcs_path}")
        blob = bucket.blob(gcs_path)
        if blob.exists():
            url = f"{settings.MEDIA_URL}{venue.id}.jpg"
            venue_urls[venue.id] = url
            existing_venues.add(venue.id)
            logger.info(f"[bulk_upload_venue_images] Image already exists for {venue.name}")
            if venue.image_url != url:
                venue.image_url = url
                venue.save(update_fields=['image_url'])

    venues_to_refresh = [v for v in venues if v.id not in existing_venues and v.photo_reference]

    for venue in venues_to_refresh:
        try:
            image_url = fetch_google_places_image_url(venue.photo_reference)
            if not image_url:
                venue_urls[venue.id] = None
                continue

            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                gcs_path = f"venue_images/{venue.id}.jpg"
                blob = bucket.blob(gcs_path)
                blob.upload_from_string(response.content, content_type='image/jpeg')
                url = f"{settings.MEDIA_URL}{venue.id}.jpg"
                venue_urls[venue.id] = url
                logger.info(f"[bulk_upload_venue_images] Uploaded image for {venue.name}")
                # Update venue image_url in database
                venue.image_url = url
                venue.save(update_fields=['image_url'])
            else:
                logger.error(f"[bulk_upload_venue_images] Failed to fetch for {venue.name}: HTTP {response.status_code}")
                venue_urls[venue.id] = None
        except Exception as e:
            logger.error(f"[bulk_upload_venue_images] Error for {venue.name}: {str(e)}")
            venue_urls[venue.id] = None

    return venue_urls


def filter_based_on_special_tags(venues, selected_tags: Dict) -> list:
    """
    Filter venues based on special tag rules.

    Rules:
    - If 'indoor' is selected, filter out parks
    - If 'family_friendly' is selected, filter out bars

    Args:
        venues: QuerySet of Venue objects
        selected_tags: Dictionary of selected tags from user input

    Returns:
        Filtered list of Venue objects
    """
    special_tags = selected_tags.get('special_tags', [])

    if 'indoor' in special_tags:
        venues = venues.exclude(tags__contains='"park"')

    if 'family_friendly' in special_tags:
        venues = venues.exclude(tags__contains='"bar"')

    return list(venues)


def get_energy_transition(previous_tags: Dict, current_tags: Dict) -> Optional[str]:
    """
    Get energy transition description between two stages based on their selected tags.

    Args:
        previous_tags: Selected tags for the previous stage
        current_tags: Selected tags for the current stage

    Returns:
        Energy transition text or None
    """
    if not previous_tags or not current_tags:
        return None

    previous_category = previous_tags.get('category_tags')
    current_category = current_tags.get('category_tags')

    previous_energy = CATEGORY_ENERGIES.get(previous_category)
    current_energy = CATEGORY_ENERGIES.get(current_category)

    if previous_energy and current_energy:
        transition_key = (previous_energy, current_energy)
        transitions = ENERGY_TRANSITIONS.get(transition_key, [])
        if transitions:
            return random.choice(transitions)

    return None


def ensure_category_tags_prioritized(template_weights: Dict, input_tags: Dict) -> Dict:
    """
    Ensure input category tags are prioritized in stage_1 weights.
    If input category tags are missing or not in top 2, make them the highest weight.
    
    Args:
        template_weights: Template stage weights dictionary
        input_tags: User input tags dictionary
        
    Returns:
        Adjusted template weights dictionary
    """
    stage_1_weights = template_weights.get('stage_1', {})
    stage_1_category_weights = stage_1_weights.get('category_tags', {})
    input_category_tags = input_tags.get('category_tags', [])
    
    sorted_stage_1 = sorted(stage_1_category_weights.items(), key=lambda x: x[1], reverse=True)
    top_2_tags = [tag for tag, _ in sorted_stage_1[:2]]
    
    needs_adjustment = False
    for cat_tag in input_category_tags:
        if cat_tag not in stage_1_category_weights or cat_tag not in top_2_tags:
            needs_adjustment = True
            break
    
    if needs_adjustment:
        logger.info(f"Adjusting stage_1 category weights to prioritize input category tags: {input_category_tags}")
        max_weight = max(stage_1_category_weights.values()) if stage_1_category_weights else 1.0
        for cat_tag in input_category_tags:
            stage_1_category_weights[cat_tag] = max_weight + 1.0
        stage_1_weights['category_tags'] = stage_1_category_weights
        template_weights['stage_1'] = stage_1_weights
    
    return template_weights


def assign_weights(tags: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Assign weights to tags based on their importance
    
    Args:
        tags: Dictionary of tags with their values
        
    Returns:
        Dictionary with tags and their weights
    """
    weights = {k:{} for k,_ in TAGS_CONSTANT.items()}
    
    for tag_type in TAGS_CONSTANT:
        selected_tags = tags.get(tag_type, [])
        all_tags = TAGS_CONSTANT[tag_type]
        other_tags = [tag for tag in all_tags if tag not in selected_tags]
        
        if selected_tags:
            selected_weight = round(tag_weight_chart.get(tag_type) / len(selected_tags), 2)
            for tag in selected_tags:
                weights[tag_type][tag] = selected_weight
        
        if other_tags:
            other_weight = round((1 - tag_weight_chart.get(tag_type)) / len(other_tags), 2)
            for tag in other_tags:
                weights[tag_type][tag] = other_weight
    
    return weights


def generate_plan(weighted_tags: Dict, input_tags: Dict, area_id: Optional[int] = None, num_recommendations: int = 3, template_id: Optional[str] = None) -> Dict:
    """
    Generate a plan with multiple venue recommendations
    
    Args:
        weighted_tags: Dictionary of weighted tags
        input_tags: Dictionary of user input tags
        area_id: Optional area ID to filter by
        num_recommendations: Number of venue recommendations to generate
        
    Returns:
        Dictionary with venue IDs and comprehensive venue data
    """
    
    venue_ids = []
    venue_data = []
    selected_tags_list = []
    previous_selected_tags = None
    venue_switch_chance = VENUE_SWITCH_PROBABILITY
    for i in range(num_recommendations):
        logger.info(f"[generate_plan] Generating plan for stage {i+1}")
        if i > 0:
            area_id, venue_switch_chance = area_switcher(area_id, venue_switch_chance, i+1)
        venue_id_choices, selected_tags = find_venue_with_retry(weighted_tags, input_tags, area_id, venue_ids)

        if venue_id_choices is None:
            continue

        selected_venue_ids = [venue["id"] for venue in venue_id_choices["selected_venues"]]
        venue_ids.append(selected_venue_ids)
        transition = None
        if previous_selected_tags:
            transition = get_energy_transition(previous_selected_tags, selected_tags)

        venue_data.append((venue_id_choices["selected_venues"], transition))
        selected_tags_list.append(selected_tags)

        previous_selected_tags = selected_tags

    return {
        "venue_ids": venue_ids,
        "venue_data": venue_data,
        "selected_tags": selected_tags_list
    }


def generate_plan_from_template(weighted_template_tags: Dict, input_tags: Dict, area_id: Optional[int] = None, num_recommendations: int = 3, template_id: Optional[str] = None) -> Dict:
    """
    Generate a plan with multiple venue recommendations
    
    Args:
        weighted_template_tags: Dictionary of weighted template tags
        input_tags: Dictionary of user input tags
        area_id: Optional area ID to filter by
        num_recommendations: Number of venue recommendations to generate
        
    Returns:
        Dictionary with venue IDs and comprehensive venue data
    """
    
    venue_ids = []
    venue_data = []
    selected_tags_list = []
    previous_selected_tags = None
    venue_switch_chance = VENUE_SWITCH_PROBABILITY
    area = Area.objects.only('name','state').get(id=area_id)
    area_name = area.name
    state = area.state
    for i in range(num_recommendations):
        stage_key = f"stage_{i+1}"
        stage_weights = weighted_template_tags.get(stage_key, {})
        logger.info(f"[generate_plan_from_template] Generating plan for stage {i+1}")

        if i > 0:
            area_id, venue_switch_chance = area_switcher(area_id, venue_switch_chance, i+1)
            area_name = Area.objects.get(id=area_id).name


        venue_id_choices, selected_tags = find_venue_with_retry(stage_weights, input_tags, area_id, venue_ids)
        if venue_id_choices is None:
            continue

        transition = None
        if previous_selected_tags:
            transition = get_energy_transition(previous_selected_tags, selected_tags)

        venue_data.append((venue_id_choices["selected_venues"], area_name, transition))
        selected_tags_list.append(selected_tags)

        previous_selected_tags = selected_tags

    return {
        "venue_data": venue_data,
        "state": state
    }

def area_switcher(area_id: int, venue_switch_chance: float, stage: int) -> tuple[int, float]:
    """
    Switch to a connected area if random condition is met
    
    Args:
        area_id: Current area ID
        venue_switch_chance: Probability of switching areas (0.0 to 1.0)
        stage: Current plan stage number
        
    Returns:
        tuple: (new_area_id, new_venue_switch_chance)
    """
    switching_venues = random.random() < venue_switch_chance
    
    if switching_venues and stage > 0:
        area_obj = Area.objects.filter(id=area_id).first()
        connected_area_ids = area_obj.get_connected_areas()
        
        if connected_area_ids:
            new_area_id = random.choice(connected_area_ids)
            logger.info(f"[area_switcher] Switching areas for stage {stage} from {area_id} to {new_area_id}")
            return new_area_id, 0.0
    
    return area_id, venue_switch_chance


def find_venue_with_retry(weighted_tags: Dict[str, float], input_tags: Dict[str, List[str]], area_id: int, venue_ids: List[List[int]]) -> Optional[Dict[str, Any]]:
    """
    Find venues by tags with retry logic
    
    Args:
        weighted_tags: Dictionary of tags with their weights
        input_tags: List of input tags
        area_id: Area ID to search in
        venue_ids: List of already selected venue IDs
        
    Returns:
        Dictionary with venue choices or None if no venues found after retries
    """
    retry_count = 0
    while retry_count < 3:
        selected_tags = select_tags_by_weight(weighted_tags, input_tags)
        logger.info(f"[find_venue_with_retry] selected_tags: {selected_tags}")
        venue_id_choices = find_venue_by_tags(selected_tags, area_id, venue_ids, input_tags)

        if venue_id_choices is not None:
            return venue_id_choices, selected_tags

        logger.info("[find_venue_with_retry] No venues found, trying again...")
        retry_count += 1

    return None, None


def select_tags_by_weight(weights: Dict[str, float], input_tags: Dict[str, List[str]], apply_decay: bool = True) -> Dict[str, str]:
    """
    Randomly select one tag from each category based on weights
    
    Args:
        weights: Dictionary of tag weights
        input_tags: Dictionary of user input tags by category
        
    Returns:
        Dictionary with one selected tag per category
    """
    if not weights:
        return {}

    selected_tags = {}
    for tag_type, tag_weights in weights.items():
        if tag_weights:
            # Weighted random selection
            tags = list(tag_weights.keys())
            weight_values = list(tag_weights.values())
            selected_tag = random.choices(tags, weights=weight_values, k=1)[0]
            selected_tag_weight = weights[tag_type][selected_tag]
            
            user_tags = input_tags.get(tag_type, [])
            if apply_decay and selected_tag in user_tags:
                decay_rate = tag_decay_chart['user_selected'][tag_type]
                weights[tag_type][selected_tag] = selected_tag_weight * decay_rate
            elif apply_decay:
                decay_rate = tag_decay_chart['random_selected'][tag_type]
                weights[tag_type][selected_tag] = selected_tag_weight * decay_rate
            
            selected_tags[tag_type] = selected_tag
    
    return selected_tags


def find_venue_by_tags(selected_tags: Dict[str, str], area_id: Optional[int] = None, exclude_venue_ids: Optional[List[int]] = None, input_tags: Optional[Dict[str, List[str]]] = None) -> Optional[Dict]:
    """
    Find venues that match the selected tags

    Args:
        selected_tags: Dictionary with one selected tag per category
        area_id: Optional area ID to filter by
        exclude_venue_ids: Optional list of venue IDs to exclude
        input_tags: Original user input tags for filtering

    Returns:
        Dictionary with selected venues, their scores, and highest score, or None
    """
    if exclude_venue_ids:
        all_excluded_venue_ids = [venue_id for stage_venue_list in exclude_venue_ids for venue_id in stage_venue_list]
        logger.info(f"[find_venue_by_tags] Excluding venue IDs: {all_excluded_venue_ids}")
        venues = Venue.objects.filter(area_id=area_id).exclude(id__in=all_excluded_venue_ids)
        logger.info(f"[find_venue_by_tags] Venue count after exclude: {venues.count()}")
    else:
        venues = Venue.objects.filter(area_id=area_id)

    special_tags_filtered = filter_based_on_special_tags(venues, input_tags)
    venue_scores = score_venues(special_tags_filtered, selected_tags)
    
    if not venue_scores:
        return None

    return select_scored_venues(venue_scores)


def select_scored_venues(venue_scores: List[tuple]) -> Dict[str, Any]:
    """
    Select venues from scored venues using weighted random selection
    
    Args:
        venue_scores: List of (venue_id, score) tuples sorted by score
        
    Returns:
        Dictionary with selected venues and highest score
    """
    if len(venue_scores) <= 3:
        shortlist = venue_scores
    else:
        shortlist_size = max(4, min(16, int(len(venue_scores) * 0.6)))
        shortlist = venue_scores[:shortlist_size]
    
    venue_score_ids, venue_score_values = zip(*shortlist)
    venue_scores_len = len(venue_score_ids)
    selected_venues = []
    if venue_scores_len >=3:
        part_size = venue_scores_len // 3
        for part in range(3):
            start_idx = part * part_size
            end_idx = start_idx + part_size if part < 2 else venue_scores_len
            part_venue_subset = list(zip(venue_score_ids[start_idx:end_idx], venue_score_values[start_idx:end_idx]))
            logger.info("[select_scored_venues] Part venue subset: {}".format(part_venue_subset))
            if part_venue_subset:
                selected_venue = random.choices(list(dict(part_venue_subset).keys()))[0]
                selected_venues.append(selected_venue)
                logger.info("[select_scored_venues] Selected venue {} with score {} from part {}".format(selected_venue, dict(part_venue_subset)[selected_venue], part))
                del dict(part_venue_subset)[selected_venue]
    else:
        selected_venues = venue_score_ids

    venues_list = list(Venue.objects.filter(id__in=selected_venues))

    if selected_venues:
        Venue.objects.filter(id__in=selected_venues).update(shown_count=django_models.F('shown_count') + 1)

    if venues_list:
        bulk_upload_venue_images(venues_list)
        venues_list = list(Venue.objects.filter(id__in=selected_venues))

    venue_image_urls = {v.id: v.image_url for v in venues_list}

    selected_with_scores = []
    for venue_id in selected_venues:
        for vid, score in venue_scores:
            if vid == venue_id:
                venue = Venue.objects.filter(id=venue_id).first()
                if venue:
                    venue_tags = json.loads(venue.tags) if venue.tags else {"category_tags": [], "vibe_tags": [], "special_tags": [], "price_tags": []}
                    image_url = venue_image_urls.get(venue_id)

                    venue_data = {
                        "id": venue.id,
                        "title": venue.name,
                        "summary": venue.summary,
                        "tags": venue_tags,
                        "address": venue.formatted_address,
                        "google_maps_uri": venue.google_maps_uri,
                        "google_image_code": venue.photo_reference,
                        "image_url": image_url,
                        "score": score,
                        "lat": venue.lat,
                        "lng": venue.lng
                    }
                    selected_with_scores.append(venue_data)
                break
    
    logger.info("[select_scored_venues] Total venues in shortlist: {}".format(len(shortlist)))
    
    return {
        "selected_venues": selected_with_scores,
    }


def score_venues(venues: List[Venue], selected_tags: Dict[str, str]) -> List[tuple]:
    """
    Score venues based on tag matches using weighted scoring
    
    Args:
        venues: List of Venue objects
        selected_tags: Dictionary with one selected tag per category
        
    Returns:
        List of (venue_id, score) tuples sorted by score (highest first)
    """
    venue_scores = []
    
    for venue in venues:
        venue_tags = {}
        
        venue_tags = json.loads(venue.tags) if venue.tags else {"category_tags": [], "vibe_tags": [], "special_tags": [], "price_tags": []}
        
        venue_category_tags = venue_tags.get('category_tags', [])
        user_selected_category_tag = selected_tags.get('category_tags', '')
       
        if user_selected_category_tag in venue_category_tags:
            tag_score = venue_scoring_weights.get('category_tags', 0)
            
            for tag_type, selected_tag in selected_tags.items():
                if tag_type != 'category_tags' and selected_tag in venue_tags.get(tag_type, []):
                    tag_score += venue_scoring_weights.get(tag_type, 0)
            
            venue_scores.append((venue.id, tag_score))
    
    venue_scores.sort(key=lambda x: x[1], reverse=True)
    return venue_scores


def generate_share_image(venue_ids: List[int], city: str, area: List[str], plan_id: int, state: str = None, headline: str = None) -> Optional[str]:
    """
    Generate a shareable image for a plan using HTML/CSS rendering and upload to Google Cloud Storage.

    Args:
        venue_ids: List of venue IDs in the plan
        city: City name
        area: List of area names
        plan_id: Plan ID for filename
        state: Optional state name
        headline: Optional headline for the card

    Returns:
        URL of the uploaded image, or None if generation fails
    """
    try:
        # Fetch venues
        venues = Venue.objects.filter(id__in=venue_ids)
        if not venues:
            logger.warning(f"No venues found for plan {plan_id}")
            return None

        # Extract venue images
        venue_images = [venue.image_url for venue in venues if venue.image_url]
        background_image = venue_images[0] if venue_images else None

        # Extract categories for subtitle with human-friendly names
        category_mapping = {
            'cafe': 'Coffee',
            'bar': 'Cocktails',
            'restaurant': 'Dinner',
            'dessert': 'Dessert',
            'activity': 'Live',
            'entertainment': 'Shows',
            'shopping': 'Shopping'
        }

        categories = []
        for venue in venues:
            if venue.tags:
                try:
                    tags = json.loads(venue.tags)
                    cat_tags = tags.get('category_tags', [])
                    if cat_tags:
                        categories.extend(cat_tags[:1])
                except:
                    pass
        categories = list(dict.fromkeys(categories))

        human_categories = [category_mapping.get(cat, cat.capitalize()) for cat in categories[:4]]
        subtitle = ' • '.join(human_categories) if human_categories else None

        area_str = ', '.join(area) if isinstance(area, list) else str(area)
        if city:
            location = f"{area_str}, {city}"
        else:
            location = area_str

        if headline:
            title = headline
        elif city:
            if 'bar' in categories or 'nightlife' in categories:
                titles = [
                    f"Late Hours in {city}",
                    f"Cocktails After Dark",
                    f"The Night Opens Up Here",
                    f"Drinks & Conversation",
                ]
            elif 'restaurant' in categories or 'cafe' in categories:
                titles = [
                    f"A Slower Night in {city}",
                    f"Evening That Builds Slowly",
                    f"Dinner & Conversation",
                    f"Quiet Hours in {city}",
                ]
            elif 'activity' in categories or 'entertainment' in categories:
                titles = [
                    f"An Evening to Remember",
                    f"Live & Unforgettable",
                    f"Tonight in {city}",
                    f"The Night Comes Alive",
                ]
            else:
                titles = [
                    f"Evening in {city}",
                    f"Tonight in {city}",
                    f"A Night in {city}",
                    f"After Hours in {city}",
                ]

            title = titles[plan_id % len(titles)]
        else:
            title = "Your Plan"

        html_content = render_to_string('share_card.html', {
            'background_image': background_image,
            'title': title,
            'subtitle': subtitle,
            'location': location,
        })

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={'width': 360, 'height': 640},
                device_scale_factor=3
            )

            page.set_content(html_content)

            screenshot_bytes = page.screenshot(type='png')

            browser.close()

        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        filename = f'share_images/plan_{plan_id}.png'
        blob = bucket.blob(filename)
        blob.upload_from_file(io.BytesIO(screenshot_bytes), content_type='image/png')

        public_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        logger.error(f"Error generating share image for plan {plan_id}: {e}")
        return None
