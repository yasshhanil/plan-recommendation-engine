"""
SQLModel definitions for the Plan Recommendation Engine.

This module defines all database models, Pydantic schemas, and helper functions
for managing venues, areas, and plans with structured tagging.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import json

from constants import CATEGORY_TAGS, VIBE_TAGS, SPECIAL_TAGS, PRICE_TAGS, TAGS_CONSTANT

# Template for structured tag storage
TAG_STRUCTURE = {
    "category_tags": [],
    "vibe_tags": [],
    "special_tags": [],
    "price_tags": []
}


# ============================================================================
# ENUMS
# ============================================================================

class TagType(str, Enum):
    """Enumeration for tag categories."""
    CATEGORY = "category"
    VIBE = "vibe"
    SPECIAL = "special"
    PRICE = "price"


# ============================================================================
# AREA MODELS
# ============================================================================

class AreaBase(SQLModel):
    """Base model for Area with common fields."""
    name: str = Field(index=True, unique=True, description="Unique area name")
    lat: Optional[float] = Field(default=None, description="Latitude coordinate")
    lng: Optional[float] = Field(default=None, description="Longitude coordinate")
    is_active: bool = Field(default=True, description="Whether area is active")
    country: Optional[str] = Field(default=None, description="Country name")
    state: Optional[str] = Field(default=None, description="State/region name")
    connected_areas: Optional[str] = Field(default=None, description="Connected areas as JSON list")
    
    def get_connected_areas(self) -> List[str]:
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


class Area(AreaBase, table=True):
    """Database model for Area."""
    __tablename__ = "areas"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    venues: List["Venue"] = Relationship(back_populates="area")


class AreaPublic(AreaBase):
    """Public schema for Area (includes ID)."""
    id: int


# ============================================================================
# VENUE MODELS
# ============================================================================

class VenueBase(SQLModel):
    """Base model for Venue with common fields."""
    place_id: str = Field(index=True, unique=True, description="Google Places ID")
    name: str = Field(description="Venue name")
    lat: float = Field(description="Latitude coordinate")
    lng: float = Field(description="Longitude coordinate")
    rating: Optional[float] = Field(default=None, description="Rating (1-5)")
    user_rating_count: Optional[int] = Field(default=None, description="Number of user ratings")
    price_level: Optional[int] = Field(default=None, description="Price level (1-4)")
    raw_types: Optional[str] = Field(default=None, description="Raw Google Place types as JSON")
    reviews: Optional[str] = Field(default=None, description="Reviews as JSON")
    photo_reference: Optional[str] = Field(default=None, description="Google Places photo reference")
    google_maps_uri: Optional[str] = Field(default=None, description="Google Maps URI for the place")
    formatted_address: Optional[str] = Field(default=None, description="Formatted address of the venue")
    summary: Optional[str] = Field(default=None, description="Venue summary (to be populated manually)")
    tags: Optional[str] = Field(default=None, description="Structured tags as JSON")


class Venue(VenueBase, table=True):
    """Database model for Venue."""
    __tablename__ = "venues"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    area_id: Optional[int] = Field(default=None, foreign_key="areas.id")
    area: Optional[Area] = Relationship(back_populates="venues")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, 
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )


class VenueCreate(VenueBase):
    """Schema for creating a new venue."""
    area_id: int = Field(description="ID of the area this venue belongs to")
    tags: Optional[Dict[str, List[str]]] = Field(default=None, description="Structured tags")


class VenueUpdate(SQLModel):
    """Schema for updating an existing venue."""
    name: Optional[str] = Field(default=None, description="Venue name")
    rating: Optional[float] = Field(default=None, description="Rating (1-5)")
    price_level: Optional[int] = Field(default=None, description="Price level (1-4)")
    tags: Optional[Dict[str, List[str]]] = Field(default=None, description="Structured tags")


class VenuePublic(VenueBase):
    """Public schema for Venue (includes computed properties)."""
    id: int
    area_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    @property
    def parsed_tags(self) -> Dict[str, List[str]]:
        """Parse tags JSON string into dictionary."""
        if not self.tags:
            return TAG_STRUCTURE.copy()
        return json.loads(self.tags)
    
    @property
    def parsed_reviews(self) -> List[Dict]:
        """Parse reviews JSON string into list."""
        if not self.reviews:
            return []
        return json.loads(self.reviews)


# ============================================================================
# PLAN MODELS
# ============================================================================

class PlanBase(SQLModel):
    """Base model for Plan with common fields."""
    user_preferences: Optional[str] = Field(default=None, description="User preferences as JSON")
    area: Optional[str] = Field(default=None, description="Target area name")
    group_size: int = Field(default=2, description="Number of people in group")


class Plan(PlanBase, table=True):
    """Database model for Plan."""
    __tablename__ = "plans"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    venues: Optional[str] = Field(default=None, description="Venue IDs in order as JSON")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApiQueryBase(SQLModel):
    """Base model for API query tracking."""
    query: str = Field(description="Search query used")
    location: str = Field(description="Location searched")
    field_mask: str = Field(description="Field mask used in API request")
    max_venues: int = Field(description="Maximum venues requested")
    response_json: Optional[str] = Field(default=None, description="API response as JSON")
    venues_found: int = Field(default=0, description="Number of venues found in response")
    venues_stored: int = Field(default=0, description="Number of venues actually stored")


class ApiQuery(ApiQueryBase, table=True):
    """Database model for tracking API queries."""
    __tablename__ = "api_queries"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    request_time: datetime = Field(default_factory=datetime.utcnow, description="Time of API request")
    success: bool = Field(default=True, description="Whether the request was successful")


class PlanCreate(PlanBase):
    """Schema for creating a new plan."""
    venue_ids: List[int] = Field(default_factory=list, description="List of venue IDs in order")


class PlanPublic(PlanBase):
    """Public schema for Plan."""
    id: int
    venues: List[int] = Field(default_factory=list, description="List of venue IDs in order")
    created_at: datetime


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_tags(tags_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Validate tags against predefined values and ensure proper structure.
    
    Args:
        tags_dict: Dictionary of tags by category
        
    Returns:
        Validated tags dictionary with only allowed values
    """
    validated_tags = TAG_STRUCTURE.copy()
    tag_lists = {
        'category': CATEGORY_TAGS,
        'vibe': VIBE_TAGS,
        'special': SPECIAL_TAGS,
        'price': PRICE_TAGS
    }
    
    for category, tags_list in tags_dict.items():
        if category in validated_tags:
            valid_tags = [tag for tag in tags_list if tag in tag_lists.get(category, [])]
            validated_tags[category] = valid_tags
    
    return validated_tags


def tags_to_json(tags_dict: Dict[str, List[str]]) -> str:
    """
    Convert tags dictionary to JSON string for storage.
    
    Args:
        tags_dict: Dictionary of tags by category
        
    Returns:
        JSON string representation of validated tags
    """
    validated_tags = validate_tags(tags_dict)
    return json.dumps(validated_tags)


def json_to_tags(tags_json: str) -> Dict[str, List[str]]:
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
