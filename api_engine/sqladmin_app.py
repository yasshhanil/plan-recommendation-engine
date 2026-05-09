"""
SQLAdmin configuration for the Plan Recommendation Engine
A modern admin interface for SQLModel/SQLAlchemy
"""

from fastapi import FastAPI, Request, Response
from sqladmin import Admin, ModelView, action
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import timedelta
from markupsafe import Markup
import json

from models import Venue, Area, Plan, ApiQuery
from database import engine

# Create FastAPI app
app = FastAPI(title="Plan Recommendation Engine")

# Create SQLAdmin instance
admin = Admin(app, engine, title="Plan Recommendation Engine Admin")

# Area Admin View
class AreaAdmin(ModelView, model=Area):
    column_list = [
        Area.id,
        Area.name,
        Area.country,
        Area.state,
        Area.is_active,
        Area.lat,
        Area.lng
    ]
    
    column_searchable_list = [Area.name, Area.country, Area.state]
    column_sortable_list = [Area.name]
    column_default_sort = [(Area.name, True)]
    
    form_columns = [
        Area.name,
        Area.country,
        Area.state,
        Area.is_active,
        Area.lat,
        Area.lng
    ]
    
    column_details_list = [
        Area.id,
        Area.name,
        Area.country,
        Area.state,
        Area.is_active,
        Area.lat,
        Area.lng
    ]
    
    column_labels = {
        "name": "Area Name",
        "country": "Country",
        "state": "State",
        "is_active": "Active Status",
        "lat": "Latitude",
        "lng": "Longitude"
    }
    
    page_size = 20
    page_size_options = [10, 20, 50, 100]

# Venue Admin View
class VenueAdmin(ModelView, model=Venue):
    column_list = [
        Venue.id,
        Venue.name,
        Venue.summary,
        Venue.rating,
        Venue.price_level,
        Venue.area,
        Venue.created_at
    ]
    
        
    column_searchable_list = [Venue.name, Venue.summary]
    column_sortable_list = [Venue.id, Venue.name, Venue.rating, Venue.price_level]
    column_default_sort = [(Venue.id, True)]
    
    form_columns = [
        Venue.name,
        Venue.place_id,
        Venue.lat,
        Venue.lng,
        Venue.rating,
        Venue.user_rating_count,
        Venue.price_level,
        Venue.area,
        Venue.tags,
        Venue.raw_types,
        Venue.reviews,
        Venue.photo_reference,
        Venue.google_maps_uri,
        Venue.summary
    ]
    
    column_details_list = [
        Venue.id,
        Venue.name,
        Venue.place_id,
        Venue.lat,
        Venue.lng,
        Venue.rating,
        Venue.user_rating_count,
        Venue.price_level,
        Venue.area,
        Venue.tags,
        Venue.raw_types,
        Venue.reviews,
        Venue.photo_reference,
        Venue.google_maps_uri,
        Venue.formatted_address,
        Venue.summary,
        Venue.created_at,
        Venue.updated_at
    ]
    
    column_labels = {
        "name": "Venue Name",
        "place_id": "Google Place ID",
        "rating": "Rating",
        "user_rating_count": "User Rating Count",
        "price_level": "Price Level",
        "area": "Area",
        "tags": "Tags",
        "raw_types": "Google Types",
        "reviews": "Reviews",
        "photo_reference": "Photo Reference",
        "google_maps_uri": "Google Maps URL",
        "formatted_address": "Address",
        "summary": "Summary",
        "created_at": "Created",
        "updated_at": "Last Updated"
    }
    
    column_formatters = {
        "rating": lambda m, a: f"⭐ {m.rating}" if m.rating else "N/A",
        "price_level": lambda m, a: {
            1: "💰 Inexpensive",
            2: "💰💰 Moderate", 
            3: "💰💰💰 Expensive",
            4: "💰💰💰💰 Very Expensive"
        }.get(m.price_level, "N/A"),
        "tags": lambda m, a: self._format_tags(m.tags) if m.tags else "No tags",
        "area": lambda m, a: m.area.name if m.area else "No Area"
    }
    
    column_formatters_detail = {
        "google_maps_uri": lambda m, a: Markup(f'<a href="{m.google_maps_uri}" target="_blank" rel="noopener noreferrer" style="color: #1e40af; text-decoration: underline;">🗺️ View on Google Maps</a>') if m.google_maps_uri else "No URL"
    }
    
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    
    def _format_tags(self, tags_json):
        """Format tags for display"""
        try:
            tags = json.loads(tags_json) if tags_json else {}
            tag_html = ""
            for category, tag_list in tags.items():
                for tag in tag_list:
                    tag_html += f'<span class="tag">{tag}</span> '
            return tag_html
        except:
            return "Invalid tags format"

# Plan Admin View
class PlanAdmin(ModelView, model=Plan):
    column_list = [
        Plan.id,
        Plan.area,
        Plan.group_size,
        Plan.created_at
    ]
    
    column_searchable_list = [Plan.area]
    column_sortable_list = [Plan.area, Plan.group_size, Plan.created_at]
    column_default_sort = [(Plan.created_at, False)]
    
    form_columns = [
        Plan.area,
        Plan.group_size,
        Plan.user_preferences,
        Plan.venues
    ]
    
    column_details_list = [
        Plan.id,
        Plan.area,
        Plan.group_size,
        Plan.user_preferences,
        Plan.venues,
        Plan.created_at
    ]
    
    column_labels = {
        "area": "Area",
        "group_size": "Group Size",
        "user_preferences": "User Preferences",
        "venues": "Selected Venues",
        "created_at": "Created"
    }
    
    column_formatters = {
        "group_size": lambda m, a: f"{m.group_size} people",
        "venues": lambda m, a: self._count_venues(m.venues) if m.venues else "0 venues"
    }
    
    page_size = 20
    page_size_options = [10, 20, 50, 100]
    
    def _count_venues(self, venues_json):
        """Count venues in the plan"""
        try:
            venues = json.loads(venues_json) if venues_json else []
            return f"{len(venues)} venues"
        except:
            return "Invalid venues data"

# API Query Admin View
class ApiQueryAdmin(ModelView, model=ApiQuery):
    column_list = [
        ApiQuery.id,
        ApiQuery.query,
        ApiQuery.location,
        ApiQuery.venues_found,
        ApiQuery.venues_stored,
        ApiQuery.max_venues,
        ApiQuery.success,
        ApiQuery.request_time
    ]
    
    column_sortable_list = ["request_time", "venues_found", "venues_stored"]
    column_default_sort = [("request_time", True)]  # True = descending (latest first)
    
    form_columns = [
        ApiQuery.query,
        ApiQuery.location,
        ApiQuery.field_mask,
        ApiQuery.max_venues,
        ApiQuery.response_json,
        ApiQuery.venues_found,
        ApiQuery.venues_stored,
        ApiQuery.success
    ]
    
    column_details_list = [
        ApiQuery.id,
        ApiQuery.query,
        ApiQuery.location,
        ApiQuery.field_mask,
        ApiQuery.max_venues,
        ApiQuery.venues_found,
        ApiQuery.venues_stored,
        ApiQuery.success,
        ApiQuery.request_time,
        ApiQuery.response_json
    ]
    
    column_labels = {
        "query": "Search Query",
        "location": "Location",
        "field_mask": "Field Mask",
        "max_venues": "Max Venues",
        "response_json": "API Response",
        "venues_found": "Venues Found",
        "venues_stored": "Venues Stored",
        "success": "Success",
        "request_time": "Request Time (IST)"
    }
    
    column_formatters = {
        "request_time": lambda m, a: (m.request_time + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S IST") if m.request_time else "N/A"
    }
    
    page_size = 20
    page_size_options = [10, 20, 50, 100]

# Add admin views
admin.add_view(AreaAdmin)
admin.add_view(VenueAdmin)
admin.add_view(PlanAdmin)
admin.add_view(ApiQueryAdmin)


# Custom CSS for better tag display and navigation
@app.get("/admin/static/custom.css")
async def custom_css():
    return """
    .tag {
        display: inline-block;
        padding: 2px 8px;
        margin: 2px;
        background: #e0e7ff;
        color: #3730a3;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .nav-btn {
        display: inline-block;
        padding: 8px 16px;
        margin: 0 8px;
        background: #3b82f6;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .nav-btn:hover {
        background: #2563eb;
        text-decoration: none;
        color: white;
    }
    
    .nav-btn-prev {
        background: #6b7280;
    }
    
    .nav-btn-prev:hover {
        background: #4b5563;
    }
    
    .nav-btn-next {
        background: #10b981;
    }
    
    .nav-btn-next:hover {
        background: #059669;
    }
    
    .nav-btn-disabled {
        display: inline-block;
        padding: 8px 16px;
        margin: 0 8px;
        background: #e5e7eb;
        color: #9ca3af;
        border-radius: 6px;
        font-weight: 500;
        cursor: not-allowed;
    }
    
    .nav-counter {
        display: inline-block;
        padding: 8px 16px;
        margin: 0 8px;
        background: #f3f4f6;
        color: #374151;
        border-radius: 6px;
        font-weight: 600;
        min-width: 120px;
        text-align: center;
    }
    
    .navigation-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    """

@app.get("/")
async def root():
    return {
        "message": "Plan Recommendation Engine Admin", 
        "admin": "/admin",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SQLAdmin on http://localhost:8003")
    print("📊 Admin Panel: http://localhost:8003/admin")
    print("📚 API Docs: http://localhost:8003/docs")
    uvicorn.run(app, host="0.0.0.0", port=8003)
