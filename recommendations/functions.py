import random
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from django.db.models import Q, Count, Avg
from .models import Venue, Area, TAGS_CONSTANT
from .constants import TAGS_CONSTANT, VENUE_SWITCH_PROBABILITY, tag_weight_chart, tag_decay_chart, venue_scoring_weights
from django.conf import settings

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
    venue_switch_chance = VENUE_SWITCH_PROBABILITY
    for i in range(num_recommendations):
        logger.info(f"[generate_plan] Generating plan for stage {i+1}")
        if i > 0:
            area_id, venue_switch_chance = area_switcher(area_id, venue_switch_chance, i+1)
        venue_id_choices = find_venue_with_retry(weighted_tags, input_tags, area_id, venue_ids)
        
        if venue_id_choices is None:
            continue
        
        selected_venue_ids = [venue["id"] for venue in venue_id_choices["selected_venues"]]
        venue_ids.append(selected_venue_ids)
        venue_data.append(venue_id_choices["selected_venues"])
    
    return {
        "venue_ids": venue_ids,
        "venue_data": venue_data
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
    venue_switch_chance = VENUE_SWITCH_PROBABILITY
    for i in range(num_recommendations):
        stage_key = f"stage_{i+1}"
        stage_weights = weighted_template_tags.get(stage_key, {})
        # print(f"[generate_plan_from_template] Stage {i+1} weights: {stage_weights}")
        print(f"[generate_plan_from_template] Generating plan for stage {i+1}")

        if i > 0:
            area_id, venue_switch_chance = area_switcher(area_id, venue_switch_chance, i+1)


        venue_id_choices = find_venue_with_retry(stage_weights, input_tags, area_id, venue_ids)
        if venue_id_choices is None:
            continue
        
        selected_venue_ids = [venue["id"] for venue in venue_id_choices["selected_venues"]]
        venue_ids.append(selected_venue_ids)
        venue_data.append(venue_id_choices["selected_venues"])
    
    return {
        "venue_ids": venue_ids,
        "venue_data": venue_data
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
        selected_tags = select_tags_by_weight(weighted_tags, input_tags, apply_decay=False)
        venue_id_choices = find_venue_by_tags(selected_tags, area_id, venue_ids)
        
        if venue_id_choices is not None:
            return venue_id_choices
            
        logger.info("[find_venue_with_retry] No venues found, trying again...")
        retry_count += 1
    
    return None


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
                logger.info("[select_tags_by_weight] Applied decay to user selected tag {}".format(selected_tag))
            elif apply_decay:
                decay_rate = tag_decay_chart['random_selected'][tag_type]
                weights[tag_type][selected_tag] = selected_tag_weight * decay_rate
                logger.info("[select_tags_by_weight] Applied decay to random selected tag {}".format(selected_tag))
                decay_rate = tag_decay_chart['random_selected'][tag_type]
                weights[tag_type][selected_tag] = selected_tag_weight * decay_rate
                logger.info("[select_tags_by_weight] Applied decay to random selected tag {}".format(selected_tag))
            
            selected_tags[tag_type] = selected_tag
    
    return selected_tags


def find_venue_by_tags(selected_tags: Dict[str, str], area_id: Optional[int] = None, exclude_venue_ids: Optional[List[int]] = None) -> Optional[Dict]:
    """
    Find venues that match the selected tags
    
    Args:
        selected_tags: Dictionary with one selected tag per category
        area_id: Optional area ID to filter by
        
    Returns:
        Dictionary with selected venues, their scores, and highest score, or None
    """
    if exclude_venue_ids:
        all_excluded_venue_ids = [venue_id for stage_venue_list in exclude_venue_ids for venue_id in stage_venue_list]
        venues = Venue.objects.filter(area_id=area_id).exclude(id__in=all_excluded_venue_ids)
    else:
        venues = Venue.objects.filter(area_id=area_id)
    
    venue_scores = score_venues(venues, selected_tags)
    
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
                

    selected_with_scores = []
    for venue_id in selected_venues:
        for vid, score in venue_scores:
            if vid == venue_id:
                venue = Venue.objects.filter(id=venue_id).first()
                if venue:
                    venue_tags = json.loads(venue.tags) if venue.tags else {"category_tags": [], "vibe_tags": [], "special_tags": [], "price_tags": []}
                    image_url = fetch_google_places_image_url(venue.photo_reference)
                    
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
