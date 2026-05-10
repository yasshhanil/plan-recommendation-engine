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

from .services import (
    assign_weights,
    generate_plan
)

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
        area_id = 1
        
        weighted_tags = assign_weights(input_tags)
        print("Weighted tags:", weighted_tags)
        
        result = generate_plan(weighted_tags, input_tags, area_id, num_recommendations=3)
        
        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)
