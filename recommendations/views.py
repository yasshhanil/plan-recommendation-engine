"""
Django views for the Plan Recommendation Engine API
"""

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from django.shortcuts import render
import json
import logging
import math
import random

from .functions import (
    assign_weights,
    generate_plan,
    generate_plan_from_template,
    ensure_category_tags_prioritized,
    generate_share_image
)
from django.template.loader import render_to_string
from django.db import models as django_models
from .models import Area, Plan, Venue, Wishlister, TAG_STRUCTURE
from .templates import select_best_template, get_confidence_level
from .template_constants import PLAN_STAGE_WEIGHTS_2_STAGE, PLAN_STAGE_WEIGHTS_3_STAGE, TEMPLATE_COPY
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
        area_id = 1
        weighted_tags = assign_weights(input_tags)
        print("Weighted tags:", weighted_tags)
        
        result = generate_plan(weighted_tags, input_tags, area_id, num_recommendations=3)
        
        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def template_recommendation(request):
    """
    Template-based recommendation endpoint with template selection.
    
    Expected POST body (JSON):
    - tags (optional): JSON string with tag preferences
      Format: {"category_tags": ["cafe", "restaurant"], "vibe_tags": ["cozy", "romantic"], 
               "special_tags": ["date_spot"], "price_tags": ["moderate"]}
      Valid category_tags: cafe, restaurant, dessert, bar, activity, arcade, cinema, park, shopping
      Valid vibe_tags: cozy, fancy, aesthetic, casual, lively, quiet, romantic, trendy, family_friendly
      Valid special_tags: date_spot, group_friendly, quick_stop, late_night, outdoor, indoor
      Valid price_tags: affordable, moderate, upscale
    - area_id (optional): Specific area ID (randomly selected if not provided)
    
    Returns:
    JSON response with template scores, confidence level, and venue recommendations
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
        except:
            body = {}
        
        tags = body.get('tags', None)
        area_id = body.get('area_id', None)
        city_id = body.get('city_id', None)

        if not area_id and city_id:
            random_area = Area.objects.filter(city_id=city_id, is_active=True).order_by('?').first()
            if random_area:
                area_id = random_area.id
        
        if not tags:
            input_tags = {
                "category_tags": ["cafe", "activity"],
                "vibe_tags": ["cozy"], 
                "special_tags": ["group_friendly"],
                "price_tags": ["upscale"]
            }
        elif isinstance(tags, dict):
            input_tags = tags
        else:
            input_tags = json.loads(tags)
        
        print("input_tags:", input_tags)
       
        number_of_stages = 2
        
        template_id, template_score, confidence_score, all_scores = select_best_template(input_tags)
        
        sorted_scores = sorted(all_scores.values(), reverse=True)
        top_score = sorted_scores[0]
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
        margin = top_score - second_score
        
        confidence_level = get_confidence_level(top_score, margin)
        if confidence_level == "low":
            logger.info("Using weighted tags for low confidence")
            weighted_tags = assign_weights(input_tags)
            plan_result = generate_plan(weighted_tags, input_tags, area_id, num_recommendations=number_of_stages)
        else:
            logger.info(f"Using template {template_id} for {confidence_level} confidence")
            if number_of_stages == 2:
                template_weights = PLAN_STAGE_WEIGHTS_2_STAGE.get(template_id, {}).get(confidence_level, {})
            else:
                template_weights = PLAN_STAGE_WEIGHTS_3_STAGE.get(template_id, {}).get(confidence_level, {})
            template_weights = ensure_category_tags_prioritized(template_weights, input_tags)
            plan_result = generate_plan_from_template(template_weights, input_tags, area_id, num_recommendations=number_of_stages)

        result = {
            "all_scores": all_scores,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "template_score": template_score,
            "template_id": template_id,
            "venue_data": plan_result.get('venue_data',{}),
            "state": plan_result.get('state', '')
        }

        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)



@csrf_exempt
def save_plan(request):
    """Save a plan endpoint"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
        except:
            body = {}

        ids = body.get('ids', [])
        city_id = body.get('city_id', None)
        areas = list(dict.fromkeys(body.get('area', [])))  # Deduplicate, preserve order
        user_tags = body.get('user_tags', {})
        state = body.get('state', None)

        if not ids or not city_id or not areas:
            return JsonResponse({"error": "Missing required fields: ids, city_id, area"}, status=400)

        from .models import City
        try:
            city_obj = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse({"error": f"City with id {city_id} not found"}, status=404)

        # Extract tags from venues to calculate best template
        venues = Venue.objects.filter(id__in=ids)
        aggregated_tags = TAG_STRUCTURE.copy()

        for venue in venues:
            if venue.tags:
                try:
                    venue_tags = json.loads(venue.tags)
                    # Aggregate tags from all venues
                    for tag_type, tags_list in venue_tags.items():
                        if isinstance(tags_list, list):
                            for tag in tags_list:
                                if tag not in aggregated_tags[tag_type]:
                                    aggregated_tags[tag_type].append(tag)
                except:
                    pass

        # Calculate best template based on aggregated venue tags
        template_id = None
        headline = None
        description = None
        if venues.exists():
            try:
                template_id, template_score, confidence_score, all_scores = select_best_template(aggregated_tags)

                # Generate headline and description based on template and areas
                if template_id and template_id in TEMPLATE_COPY:
                    if 'titles' in TEMPLATE_COPY[template_id]:
                        title_options = TEMPLATE_COPY[template_id]['titles']
                        headline_template = random.choice(title_options)

                        # Use first area for single-area style headlines
                        headline = headline_template.format(area=areas[0] if areas else city_obj.name)

                    if 'descriptions' in TEMPLATE_COPY[template_id]:
                        description_options = TEMPLATE_COPY[template_id]['descriptions']
                        description = random.choice(description_options)

            except Exception as e:
                logger.warning(f"Failed to calculate template, headline, or description for plan: {e}")

        plan = Plan.objects.create(
            city=city_obj,
            area=areas,
            ids=ids,
            user_tags=user_tags,
            template_id=template_id,
            headline=headline,
            description=description
        )

        if ids:
            Venue.objects.filter(id__in=ids).update(saved_count_this_month=django_models.F('saved_count_this_month') + 1)

        # Generate shareable image
        share_image_url = generate_share_image(ids, city_obj.name, areas, plan.id, state, headline)
        if share_image_url:
            plan.share_image_url = share_image_url
            plan.save()

        return JsonResponse({
            "success": True,
            "plan_id": plan.id,
            "share_token": str(plan.share_token),
            "template_id": template_id,
            "headline": headline,
            "description": description,
            "share_image_url": share_image_url,
            "message": "Plan saved successfully"
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_plans(request):
    """Get all plans endpoint"""
    if request.method == 'GET':
        plans = Plan.objects.all().order_by('-created_at')
        plans_data = []
        for plan in plans:
            plans_data.append({
                "id": plan.id,
                "city": plan.city.name if plan.city else None,
                "area": plan.area,
                "venue_ids": plan.ids,
                "user_tags": plan.user_tags,
                "template_id": plan.template_id,
                "share_token": plan.share_token,
                "headline": plan.headline,
                "description": plan.description,
                "share_image_url": plan.share_image_url,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
            })

        return JsonResponse({
            "success": True,
            "plans": plans_data,
            "count": len(plans_data)
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_venues_by_ids(request):
    """Get venue data by IDs endpoint"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
        except:
            body = {}

        venue_ids = body.get('ids', [])

        if not venue_ids:
            return JsonResponse({"error": "Missing required field: ids"}, status=400)

        venues = Venue.objects.filter(id__in=venue_ids)
        venues_data = []

        for venue in venues:
            venue_tags = json.loads(venue.tags) if venue.tags else {"category_tags": [], "vibe_tags": [], "special_tags": [], "price_tags": []}

            venue_data = {
                "id": venue.id,
                "area": venue.area.name,
                "title": venue.name,
                "summary": venue.summary,
                "tags": venue_tags,
                "address": venue.formatted_address,
                "google_maps_uri": venue.google_maps_uri,
                "google_image_code": venue.photo_reference,
                "image_url": venue.image_url,
                "lat": venue.lat,
                "lng": venue.lng,
                "rating": venue.rating,
                "price_level": venue.price_level,
                "user_rating_count": venue.user_rating_count
            }
            venues_data.append(venue_data)

        return JsonResponse({
            "success": True,
            "venues": venues_data,
            "count": len(venues_data)
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_areas_by_city(request):
    """Return all active areas for a given city name"""
    if request.method == 'GET':
        city_name = request.GET.get('city')
        if not city_name:
            return JsonResponse({"error": "Missing required parameter: city"}, status=400)

        areas = (
            Area.objects
            .filter(city__name__iexact=city_name, is_active=True)
            .select_related('city__country')
            .order_by('name')
        )

        if not areas.exists():
            return JsonResponse({"error": f"No areas found for city: {city_name}"}, status=404)

        return JsonResponse({
            "success": True,
            "city": areas.first().city.name,
            "country": areas.first().city.country.name,
            "areas": [{"id": a.id, "name": a.name} for a in areas]
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_cities(request):
    """Return all active cities with their country and areas"""
    if request.method == 'GET':
        from .models import City
        cities = (
            City.objects
            .filter(is_active=True)
            .select_related('country')
            .prefetch_related('areas')
            .order_by('name')
        )
        return JsonResponse({
            "success": True,
            "cities": [
                {
                    "id": c.id,
                    "name": c.name,
                    "country": c.country.name,
                    "country_code": c.country.code,
                    "areas": [
                        {"id": a.id, "name": a.name}
                        for a in c.areas.filter(is_active=True).order_by('name')
                    ]
                }
                for c in cities
            ]
        })
    return JsonResponse({"error": "Method not allowed"}, status=405)


def plan_landing_page(request, token):
    """Landing page to display plan for users without the app"""
    plan = Plan.objects.filter(share_token=token).first()

    if not plan:
        return render(request, 'plan_landing.html', {'plan': None, 'error': 'Plan not found'})

    def _haversine(lat1, lng1, lat2, lng2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
        return round(R * 2 * math.asin(math.sqrt(a)), 1)

    def _fmt_area(raw):
        return raw.replace('_', ' ').title() if raw else None

    price_symbols = {0: 'Free', 1: '$', 2: '$$', 3: '$$$', 4: '$$$$'}

    # Fetch venues if plan has venue_ids, preserving order and parsing tags
    venues = []
    if plan.ids:
        venue_map = {v.id: v for v in Venue.objects.filter(id__in=plan.ids)}
        plan_areas = plan.area if isinstance(plan.area, list) else []
        prev_lat = prev_lng = None
        for i, venue_id in enumerate(plan.ids):
            venue = venue_map.get(venue_id)
            if not venue:
                continue
            tags = {}
            if venue.tags:
                try:
                    tags = json.loads(venue.tags)
                except (json.JSONDecodeError, TypeError):
                    pass
            distance_km = None
            if prev_lat is not None and venue.lat and venue.lng:
                distance_km = _haversine(prev_lat, prev_lng, float(venue.lat), float(venue.lng))
            raw_area = plan_areas[i] if i < len(plan_areas) else (plan_areas[-1] if plan_areas else None)
            venues.append({
                'name': venue.name,
                'summary': venue.summary,
                'image_url': venue.image_url,
                'formatted_address': venue.formatted_address,
                'google_maps_uri': venue.google_maps_uri,
                'rating': float(venue.rating) if venue.rating is not None else None,
                'price_display': price_symbols.get(venue.price_level, ''),
                'tags': tags,
                'area': _fmt_area(raw_area),
                'distance_km': distance_km,
            })
            prev_lat, prev_lng = venue.lat, venue.lng

    plan_area_display = ', '.join(_fmt_area(a) for a in (plan.area or []) if a)

    context = {
        'plan': plan,
        'venues': venues,
        'plan_area_display': plan_area_display,
    }

    return render(request, 'plan_landing.html', context)


@csrf_exempt
def preview_share_card(request):
    """Preview share card design in browser using existing plan data"""
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')
        if plan_id:
            plan = Plan.objects.filter(id=plan_id).first()
        else:
            plan = Plan.objects.order_by('-created_at').first()

        if not plan:
            return JsonResponse({"error": "No plans found in database"}, status=404)

        venues = Venue.objects.filter(id__in=plan.ids).order_by('-rating') if plan.ids else []

        venue_images = [venue.image_url for venue in venues if venue.image_url]
        background_image = venue_images[0] if venue_images else None

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

        # Map categories to human-friendly names
        human_categories = [category_mapping.get(cat, cat.capitalize()) for cat in categories[:4]]
        subtitle = ' • '.join(human_categories) if human_categories else None

        # Build location string with city
        city_name = plan.city.name if plan.city else None
        area_str = ', '.join(plan.area) if isinstance(plan.area, list) else str(plan.area)
        if city_name:
            location = f"{area_str}, {city_name}"
        else:
            location = area_str

        # Use headline if available, otherwise generate title
        if plan.headline:
            title = plan.headline
        elif city_name:
            # Generate contextual title based on categories
            if 'bar' in categories or 'nightlife' in categories:
                titles = [
                    f"Late Hours in {city_name}",
                    f"Cocktails After Dark",
                    f"The Night Opens Up Here",
                    f"Drinks & Conversation",
                ]
            elif 'restaurant' in categories or 'cafe' in categories:
                titles = [
                    f"A Slower Night in {city_name}",
                    f"Evening That Builds Slowly",
                    f"Dinner & Conversation",
                    f"Quiet Hours in {city_name}",
                ]
            elif 'activity' in categories or 'entertainment' in categories:
                titles = [
                    f"An Evening to Remember",
                    f"Live & Unforgettable",
                    f"Tonight in {city_name}",
                    f"The Night Comes Alive",
                ]
            else:
                titles = [
                    f"Evening in {city_name}",
                    f"Tonight in {city_name}",
                    f"A Night in {city_name}",
                    f"After Hours in {city_name}",
                ]

            # Select title based on plan id for consistency
            title = titles[plan.id % len(titles)]
        else:
            title = "Your Plan"

        # Render HTML template
        venue_names = [v.name for v in venues]

        html_content = render_to_string('share_card.html', {
            'background_image': background_image,
            'title': title,
            'subtitle': subtitle,
            'location': location,
            'venue_names': venue_names,
        })

        return HttpResponse(html_content, content_type='text/html')

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def join_waitlist(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = (body.get('email') or '').strip().lower()
    city = (body.get('city') or '').strip()

    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return JsonResponse({"error": "Invalid email address"}, status=400)

    if not city:
        return JsonResponse({"error": "City is required"}, status=400)

    _, created = Wishlister.objects.get_or_create(email=email, defaults={'city': city})
    if not created:
        return JsonResponse({"message": "You're already on the list!"}, status=200)

    return JsonResponse({"message": "You're on the list!"}, status=201)

