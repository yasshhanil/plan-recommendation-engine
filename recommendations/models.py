"""
Django models for the Plan Recommendation Engine.

This module defines all database models for managing venues, areas, and plans with structured tagging.
"""

from django.db import models
from django.core.exceptions import ValidationError
import json
from datetime import datetime

from .constants import CATEGORY_TAGS, VIBE_TAGS, SPECIAL_TAGS, PRICE_TAGS, TAGS_CONSTANT

# Template for structured tag storage
TAG_STRUCTURE = {
    "category_tags": [],
    "vibe_tags": [],
    "special_tags": [],
    "price_tags": []
}


# ============================================================================
# AREA MODELS
# ============================================================================

class Area(models.Model):
    """Database model for Area."""
    name = models.CharField(max_length=255, unique=True, db_index=True, help_text="Unique area name")
    lat = models.FloatField(null=True, blank=True, help_text="Latitude coordinate")
    lng = models.FloatField(null=True, blank=True, help_text="Longitude coordinate")
    is_active = models.BooleanField(default=True, help_text="Whether area is active")
    country = models.CharField(max_length=255, null=True, blank=True, help_text="Country name")
    state = models.CharField(max_length=255, null=True, blank=True, help_text="State/region name")
    connected_areas = models.TextField(null=True, blank=True, help_text="Connected areas as JSON list")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "areas"
        ordering = ['name']
    
    def get_connected_areas(self):
        """
        Parse and return connected areas as a list of strings.
        
        Returns:
            List of connected area names, or empty list if no connected areas
        """
        if not self.connected_areas:
            return []
        
        try:
            return json.loads(self.connected_areas)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def __str__(self):
        return self.name


# ============================================================================
# VENUE MODELS
# ============================================================================

class Venue(models.Model):
    """Database model for Venue."""
    place_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="Google Places ID")
    name = models.CharField(max_length=255, help_text="Venue name")
    lat = models.FloatField(help_text="Latitude coordinate")
    lng = models.FloatField(help_text="Longitude coordinate")
    rating = models.FloatField(null=True, blank=True, help_text="Rating (1-5)")
    user_rating_count = models.IntegerField(null=True, blank=True, help_text="Number of user ratings")
    price_level = models.IntegerField(null=True, blank=True, help_text="Price level (1-4)")
    raw_types = models.TextField(null=True, blank=True, help_text="Raw Google Place types as JSON")
    reviews = models.TextField(null=True, blank=True, help_text="Reviews as JSON")
    photo_reference = models.TextField(null=True, blank=True, help_text="Google Places photo reference")
    google_maps_uri = models.URLField(max_length=500, null=True, blank=True, help_text="Google Maps URI for the place")
    formatted_address = models.TextField(null=True, blank=True, help_text="Formatted address of the venue")
    summary = models.TextField(null=True, blank=True, help_text="Venue summary (to be populated manually)")
    tags = models.TextField(null=True, blank=True, help_text="Structured tags as JSON")
    image_url = models.URLField(max_length=500, null=True, blank=True, help_text="Cached GCS image URL")
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='venues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "venues"
        ordering = ['name']
    
    @property
    def parsed_tags(self):
        """Parse tags JSON string into dictionary."""
        if not self.tags:
            return TAG_STRUCTURE.copy()
        return json.loads(self.tags)
    
    @property
    def parsed_reviews(self):
        """Parse reviews JSON string into list."""
        if not self.reviews:
            return []
        return json.loads(self.reviews)
    
    def __str__(self):
        return self.name


# ============================================================================
# PLAN MODELS
# ============================================================================

class Plan(models.Model):
    """Database model for Plan."""
    user_preferences = models.TextField(null=True, blank=True, help_text="User preferences as JSON")
    area = models.CharField(max_length=255, null=True, blank=True, help_text="Target area name")
    group_size = models.IntegerField(default=2, help_text="Number of people in group")
    venues = models.TextField(null=True, blank=True, help_text="Venue IDs in order as JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "plans"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Plan {self.id} for {self.area}"


class ApiQuery(models.Model):
    """Database model for tracking API queries."""
    query = models.CharField(max_length=500, help_text="Search query used")
    location = models.CharField(max_length=255, help_text="Location searched")
    field_mask = models.CharField(max_length=255, help_text="Field mask used in API request")
    max_venues = models.IntegerField(help_text="Maximum venues requested")
    response_json = models.TextField(null=True, blank=True, help_text="API response as JSON")
    venues_found = models.IntegerField(default=0, help_text="Number of venues found in response")
    venues_stored = models.IntegerField(default=0, help_text="Number of venues actually stored")
    success = models.BooleanField(default=True, help_text="Whether the request was successful")
    request_time = models.DateTimeField(auto_now_add=True, help_text="Time of API request")
    
    class Meta:
        db_table = "api_queries"
        ordering = ['-request_time']
    
    def __str__(self):
        return f"API Query {self.id}: {self.query} in {self.location}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_tags(tags_dict):
    """
    Validate tags against predefined values and ensure proper structure.
    
    Args:
        tags_dict: Dictionary of tags by category
        
    Returns:
        Validated tags dictionary with only allowed values
    """
    validated_tags = TAG_STRUCTURE.copy()
    tag_lists = {
        'category_tags': CATEGORY_TAGS,
        'vibe_tags': VIBE_TAGS,
        'special_tags': SPECIAL_TAGS,
        'price_tags': PRICE_TAGS
    }
    
    for category, tags_list in tags_dict.items():
        if category in validated_tags:
            valid_tags = [tag for tag in tags_list if tag in tag_lists.get(category, [])]
            validated_tags[category] = valid_tags
    
    return validated_tags


def tags_to_json(tags_dict):
    """
    Convert tags dictionary to JSON string for storage.
    
    Args:
        tags_dict: Dictionary of tags by category
        
    Returns:
        JSON string representation of validated tags
    """
    validated_tags = validate_tags(tags_dict)
    return json.dumps(validated_tags)


def json_to_tags(tags_json):
    """
    Convert JSON string to tags dictionary.
    
    Args:
        tags_json: JSON string of tags
        
    Returns:
        Tags dictionary, or empty structure if invalid
    """
    if not tags_json:
        return TAG_STRUCTURE.copy()
    
    try:
        return json.loads(tags_json)
    except (json.JSONDecodeError, TypeError):
        return TAG_STRUCTURE.copy()
