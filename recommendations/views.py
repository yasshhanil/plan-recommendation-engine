"""
Django views for the Plan Recommendation Engine API
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
import json
import logging
import random

from .functions import (
    assign_weights,
    generate_plan,
    generate_plan_from_template,
    ensure_category_tags_prioritized
)
from .models import Area
from .templates import select_best_template, get_confidence_level
from .template_constants import PLAN_STAGE_WEIGHTS
logger = logging.getLogger(__name__)


@csrf_exempt
def recommendation(request):
    """Recommendation endpoint with database integration"""
    if request.method == 'GET':
        tags = request.GET.get('tags', None)
        area_id = request.GET.get('area_id', None)
        
        input_tags = {
            "category_tags": ["cafe", "activity"],
            "vibe_tags": ["cozy", "romantic"], 
            "special_tags": ["date_spot"],
            "price_tags": ["upscale"]
        }
        areas = Area.objects.filter(is_active=True)
        area_id = random.choice(areas).id if areas else 1
        
        weighted_tags = assign_weights(input_tags)
        print("Weighted tags:", weighted_tags)
        
        result = generate_plan(weighted_tags, input_tags, area_id, num_recommendations=3)
        
        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def template_recommendation(request):
    """Template-based recommendation endpoint with template selection"""
    if request.method == 'GET':
        tags = request.GET.get('tags', None)
        area_id = request.GET.get('area_id', None)
        
        if not tags:
            input_tags = {
                "category_tags": ["cafe", "activity"],
                "vibe_tags": ["cozy"], 
                "special_tags": ["group_friendly"],
                "price_tags": ["upscale"]
            }
        else:
            input_tags = json.loads(tags)
        
        areas = Area.objects.filter(is_active=True)
        area_id = random.choice(areas).id if areas else 1
        
        template_id, template_score, confidence_score, all_scores = select_best_template(input_tags)
        
        sorted_scores = sorted(all_scores.values(), reverse=True)
        top_score = sorted_scores[0]
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
        margin = top_score - second_score
        
        confidence_level = get_confidence_level(top_score, margin)
        if confidence_level == "low":
            logger.info("Using weighted tags for low confidence")
            weighted_tags = assign_weights(input_tags)
            plan_result = generate_plan(weighted_tags, input_tags, area_id, num_recommendations=3)
        else:
            logger.info(f"Using template {template_id} for {confidence_level} confidence")
            template_weights = PLAN_STAGE_WEIGHTS.get(template_id, {}).get(confidence_level, {})
            template_weights = ensure_category_tags_prioritized(template_weights, input_tags)
            plan_result = generate_plan_from_template(template_weights, input_tags, area_id, num_recommendations=3)

        result = {
            "all_scores": all_scores,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "template_score": template_score,
            "template_id": template_id,
            "venue_data": plan_result.get("venue_data", [])
        }

        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)