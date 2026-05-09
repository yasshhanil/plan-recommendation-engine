"""
Common endpoints for the Plan Recommendation Engine API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Venue, Area, Plan, VenuePublic, AreaPublic, PlanPublic, VenueCreate, PlanCreate
from functions import (
    assign_weights,
    generate_plan
)

# Create main router
router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


# Recommendation endpoint
@router.get("/")
async def recommendation(
    tags: Optional[str] = Query(None, description="Comma-separated tags for recommendation"),
    area_id: Optional[int] = Query(None, description="Area ID to filter by"),
    db: Session = Depends(get_db)
):
    """Recommendation endpoint with database integration"""
    
    input_tags = {
            "category_tags": ["cafe", "activity"],
            "vibe_tags": ["cozy", "romantic"], 
            "special_tags": ["date_spot"],
            "price_tags": ["upscale"]
        }
    area_id = 1
    weighted_tags = assign_weights(input_tags)
    print("Weighted tags:", weighted_tags)
    venue_ids = generate_plan(db, weighted_tags, input_tags, area_id, num_recommendations=3)
    
    return {
        "venue_ids": venue_ids
    }
    
  
