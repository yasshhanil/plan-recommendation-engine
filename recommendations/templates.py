"""
Plan Templates for the Recommendation Engine

This module defines template profiles and selection logic for plan generation.
Templates influence venue selection based on category and vibe preferences.
"""

from typing import Dict, List, Optional, Tuple
import logging
from .template_constants import TEMPLATE_SCORE_WEIGHTS

logger = logging.getLogger(__name__)


# ============================================================================
# TEMPLATE PROFILES
# ============================================================================

TEMPLATE_PROFILES = {
    "date_night": {
        "name": "Date Night",
        "description": "Romantic and intimate plans",
        "category_weights": {
            "restaurant": 0.30,
            "dessert": 0.20,
            "bar": 0.20,
            "cafe": 0.30,
            "shopping": 0.10
        },
        "vibe_weights": {
            "romantic": 0.45,
            "fancy": 0.25,
            "aesthetic": 0.15,
            "cozy": 0.10,
            "quiet": 0.05
        },
        "special_weights": {
            "date_spot": 0.45,
            "late_night": 0.15,
            "indoor": 0.15,
            "outdoor": 0.15,
            "quick_stop": 0.05,
            "group_friendly": 0.05
        }
    },

    "social_energy": {
        "name": "Social Energy",
        "description": "Lively social experiences and energetic outings",
        "category_weights": {
            "bar": 0.30,
            "activity": 0.30,
            "restaurant": 0.15,
            "dessert": 0.10,
            "shopping": 0.10,
            "cafe": 0.05
        },
        "vibe_weights": {
            "lively": 0.35,
            "trendy": 0.30,
            "casual": 0.20,
            "aesthetic": 0.10,
            "cozy": 0.05
        },
        "special_weights": {
            "group_friendly": 0.35,
            "late_night": 0.25,
            "indoor": 0.15,
            "outdoor": 0.10,
            "quick_stop": 0.10,
            "date_spot": 0.05
        }
    },

    "easy_living": {
        "name": "Easy Living",
        "description": "Relaxed and slow-paced plans with cozy experiences",
        "category_weights": {
            "cafe": 0.30,
            "dessert": 0.25,
            "restaurant": 0.20,
            "shopping": 0.15,
            "activity": 0.10
        },
        "vibe_weights": {
            "cozy": 0.35,
            "quiet": 0.30,
            "aesthetic": 0.15,
            "casual": 0.10,
            "romantic": 0.10
        },
        "special_weights": {
            "indoor": 0.30,
            "outdoor": 0.20,
            "quick_stop": 0.15,
            "date_spot": 0.15,
            "group_friendly": 0.10,
            "late_night": 0.10
        }
    },

    "exploration_mode": {
        "name": "Exploration Mode",
        "description": "Discover new places and mixed experiences",
        "category_weights": {
            "activity": 0.45,
            "cafe": 0.20,
            "restaurant": 0.15,
            "shopping": 0.10,
            "dessert": 0.05,
            "bar": 0.05
        },
        "vibe_weights": {
            "lively": 0.30,
            "trendy": 0.25,
            "casual": 0.20,
            "aesthetic": 0.10,
            "quiet": 0.10,
            "cozy": 0.05
        },
        "special_weights": {
            "outdoor": 0.40,
            "quick_stop": 0.25,
            "group_friendly": 0.15,
            "indoor": 0.10,
            "late_night": 0.10
        }
    },

    "social_cafe_crawl": {
        "name": "Social Cafe Crawl",
        "description": "Cafe hopping and dessert-focused social plans",
        "category_weights": {
            "cafe": 0.40,
            "dessert": 0.35,
            "shopping": 0.10,
            "restaurant": 0.10,
            "activity": 0.05
        },
        "vibe_weights": {
            "aesthetic": 0.30,
            "cozy": 0.25,
            "casual": 0.20,
            "trendy": 0.15,
            "quiet": 0.10
        },
        "special_weights": {
            "quick_stop": 0.30,
            "group_friendly": 0.25,
            "indoor": 0.20,
            "date_spot": 0.10,
            "outdoor": 0.10,
            "late_night": 0.05
        }
    },
    
    "retail_therapy": {
        "name": "Retail Therapy",
        "description": "Shopping-focused outings with supporting food stops",
        "category_weights": {
            "shopping": 0.45,
            "cafe": 0.20,
            "dessert": 0.15,
            "restaurant": 0.10,
            "activity": 0.10
        },
        "vibe_weights": {
            "casual": 0.30,
            "trendy": 0.25,
            "aesthetic": 0.20,
            "lively": 0.15,
            "cozy": 0.10
        },
        "special_weights": {
            "outdoor": 0.30,
            "group_friendly": 0.25,
            "quick_stop": 0.20,
            "indoor": 0.15,
            "date_spot": 0.05,
            "late_night": 0.05
        }
    }
}


# ============================================================================
# TEMPLATE SELECTION
# ============================================================================

def calculate_template_match_score(
    user_tags: Dict[str, List[str]],
    template_profile: Dict[str, Dict],
    template_scoring_weights: Dict[str, float]
) -> float:
    """
    Calculate how well a template matches user preferences using overlap-based scoring.
    
    Args:
        user_tags: Dictionary of user-selected tags by category
        template_profile: Template's category and vibe weights
        template_scoring_weights: Weights for each tag type in scoring
        
    Returns:
        Match score between 0.0 and 1.0
    """
    # Calculate all tag type scores
    tag_config = [
        ('category_tags', 'category_weights', 'default'),
        ('vibe_tags', 'vibe_weights', 'default'),
        ('special_tags', 'special_weights', 'default')
    ]

    scores = {}
    for tag_key, weight_key, tag_type in tag_config:
        scores[tag_key] = calculate_tag_match(
            user_tags.get(tag_key, []),
            template_profile.get(weight_key, {}) if weight_key else None,
            tag_type
        )

    # Context match - placeholder for future implementation
    context_score = 0.5

    template_score = (
        scores['category_tags'] * template_scoring_weights.get('category', TEMPLATE_SCORE_WEIGHTS['category']) +
        scores['vibe_tags'] * template_scoring_weights.get('vibe', TEMPLATE_SCORE_WEIGHTS['vibe']) +
        scores['special_tags'] * template_scoring_weights.get('special', TEMPLATE_SCORE_WEIGHTS['special']) +
        context_score * template_scoring_weights.get('context', TEMPLATE_SCORE_WEIGHTS['context'])
    )

    return round(template_score, 3)


def calculate_tag_match(
    user_tags: List[str],
    template_weights: Optional[Dict[str, float]] = None,
    tag_type: str = 'default'
) -> float:
    """
    Calculate tag match score using overlap/dot product.
    
    Args:
        user_tags: User-selected tags
        template_weights: Template's tag weights (None for price tags)
        tag_type: Type of tag ('default', 'price')
        
    Returns:
        Match score between 0.0 and 1.0
    """
    if not user_tags:
        return 0.0

    if not template_weights:
        return 0.0

    user_weight = 1.0 / len(user_tags)

    overlap_score = 0.0
    for tag in user_tags:
        overlap_score += user_weight * template_weights.get(tag, 0.0)

    return round(overlap_score, 3)


def select_best_template(
    user_tags: Dict[str, List[str]],
    template_scoring_weights: Optional[Dict[str, float]] = None
) -> Tuple[Optional[str], float, float, Dict[str, float]]:
    """
    Select the best matching template based on user preferences.
    
    Args:
        user_tags: Dictionary of user-selected tags by category
        template_scoring_weights: Optional custom weights for scoring (uses defaults if not provided)
        
    Returns:
        Tuple of (template_id, template_score, confidence_score, all_template_scores)
    """
    if template_scoring_weights is None:
        template_scoring_weights = TEMPLATE_SCORE_WEIGHTS
    
    template_scores = {}
    
    for template_id, profile in TEMPLATE_PROFILES.items():
        score = calculate_template_match_score(
            user_tags,
            profile,
            template_scoring_weights
        )
        template_scores[template_id] = score
        logger.info(f"[select_best_template] {template_id}: {score}")
    
    # Find the best template
    best_template_id = max(template_scores, key=template_scores.get)
    best_score = template_scores[best_template_id]

    # Normalize scores to 0-1 range for confidence calculation
    max_possible_score = 0.25  # Adjusted for better confidence distribution
    normalized_best_score = min(best_score / max_possible_score, 1.0)

    # Calculate confidence based on normalized score and gap to second best
    sorted_scores = sorted(template_scores.values(), reverse=True)
    if len(sorted_scores) >= 2:
        second_best_score = sorted_scores[1]
        normalized_second_best = min(second_best_score / max_possible_score, 1.0)
        confidence = (normalized_best_score * 0.7) + ((normalized_best_score - normalized_second_best) * 0.3)
    else:
        confidence = normalized_best_score

    confidence = round(confidence, 3)
    
    logger.info(f"[select_best_template] Selected: {best_template_id} with score {best_score}, confidence {confidence}")
    
    return best_template_id, best_score, confidence, template_scores


def get_template_profile(template_id: str) -> Optional[Dict[str, Dict]]:
    """
    Get a template's profile by ID.
    
    Args:
        template_id: Template identifier
        
    Returns:
        Template profile dictionary or None if not found
    """
    return TEMPLATE_PROFILES.get(template_id)


def get_confidence_level(top_score: float, margin: float) -> str:
    """
    Determine confidence level based on top score and margin from second place.
    
    Args:
        top_score: The highest template score
        margin: The difference between top score and second place score
        
    Returns:
        Confidence level: 'high', 'medium', or 'low'
    """
    if top_score < 0.12:
        return 'low'
    elif margin < 0.01:
        return 'low'
    elif margin < 0.04:
        return 'medium'
    else:
        return 'high'
