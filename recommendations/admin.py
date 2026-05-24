"""
Django admin configuration for recommendations app
"""

from django.contrib import admin
from .models import Area, Venue, Plan, ApiQuery


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin configuration for Area model"""
    list_display = ['name', 'country', 'state', 'is_active', 'connected_areas', 'created_at', 'updated_at']
    list_filter = ['is_active', 'country', 'state']
    search_fields = ['name', 'country', 'state']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'country', 'state', 'is_active')
        }),
        ('Location', {
            'fields': ('lat', 'lng')
        }),
        ('Connections', {
            'fields': ('connected_areas',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Admin configuration for Venue model"""
    list_display = ['name', 'area', 'rating', 'price_level', 'user_rating_count', 'image_url', 'formatted_address', 'created_at', 'updated_at']
    list_filter = ['area', 'price_level', 'rating']
    search_fields = ['name', 'place_id', 'formatted_address']
    readonly_fields = ['created_at', 'updated_at', 'place_id']
    ordering = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('area')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin configuration for Plan model"""
    list_display = ['id', 'area', 'group_size', 'venues_display', 'created_at']
    list_filter = ['area', 'group_size']
    search_fields = ['area', 'user_preferences']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def venues_display(self, obj):
        """Display venues in a readable format"""
        if obj.venues:
            try:
                import json
                venue_ids = json.loads(obj.venues) if isinstance(obj.venues, str) else obj.venues
                return f"{len(venue_ids)} venues" if venue_ids else "No venues"
            except:
                return str(obj.venues)[:50] + "..." if obj.venues else "No venues"
        return "No venues"
    venues_display.short_description = 'Venues'
    
    fieldsets = (
        ('Plan Info', {
            'fields': ('area', 'group_size')
        }),
        ('Data', {
            'fields': ('user_preferences', 'venues'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApiQuery)
class ApiQueryAdmin(admin.ModelAdmin):
    """Admin configuration for ApiQuery model"""
    list_display = ['query', 'location', 'field_mask', 'max_venues', 'venues_found', 'venues_stored', 'success', 'request_time']
    list_filter = ['success', 'location', 'max_venues']
    search_fields = ['query', 'location', 'field_mask']
    readonly_fields = ['request_time', 'response_json']
    ordering = ['-request_time']
    
    def response_preview(self, obj):
        """Show preview of response JSON"""
        if obj.response_json:
            return str(obj.response_json)[:100] + "..." if len(str(obj.response_json)) > 100 else obj.response_json
        return "No response"
    response_preview.short_description = 'Response Preview'
    
    fieldsets = (
        ('Query Info', {
            'fields': ('query', 'location', 'field_mask', 'max_venues')
        }),
        ('Results', {
            'fields': ('venues_found', 'venues_stored', 'success')
        }),
        ('Response Data', {
            'fields': ('response_json',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('request_time',),
            'classes': ('collapse',)
        }),
    )
