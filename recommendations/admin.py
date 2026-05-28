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
    list_display = ['name', 'area', 'rating', 'price_level', 'user_rating_count', 'shown_count', 'saved_count_this_month', 'image_url', 'formatted_address', 'created_at', 'updated_at']
    list_filter = ['area', 'price_level', 'rating']
    search_fields = ['name', 'place_id', 'formatted_address']
    readonly_fields = ['created_at', 'updated_at', 'place_id']
    ordering = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('area')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin configuration for Plan model"""
    list_display = ['id', 'city', 'area', 'template_id', 'headline_display', 'ids_display', 'user_tags_display', 'share_image_url_display', 'share_token', 'created_at', 'updated_at']
    list_filter = ['city', 'area', 'template_id']
    search_fields = ['city', 'area', 'headline', 'description', 'template_id']
    readonly_fields = ['created_at', 'updated_at', 'share_token']
    ordering = ['-created_at']

    def ids_display(self, obj):
        """Display venue IDs in a readable format"""
        if obj.ids:
            return f"{len(obj.ids)} venues" if isinstance(obj.ids, list) else str(obj.ids)[:50]
        return "No venues"
    ids_display.short_description = 'Venues'

    def user_tags_display(self, obj):
        """Display user tags in a readable format"""
        if obj.user_tags:
            return str(obj.user_tags)[:100] + "..." if len(str(obj.user_tags)) > 100 else str(obj.user_tags)
        return "No tags"
    user_tags_display.short_description = 'User Tags'

    def share_image_url_display(self, obj):
        """Display share image URL"""
        if obj.share_image_url:
            return "✓ Generated"
        return "Not generated"
    share_image_url_display.short_description = 'Share Image'

    def headline_display(self, obj):
        """Display headline in a readable format"""
        if obj.headline:
            return obj.headline[:80] + "..." if len(obj.headline) > 80 else obj.headline
        return "No headline"
    headline_display.short_description = 'Headline'

    fieldsets = (
        ('Plan Info', {
            'fields': ('city', 'area')
        }),
        ('Template & Content', {
            'fields': ('template_id', 'headline', 'description')
        }),
        ('Data', {
            'fields': ('ids', 'user_tags', 'share_image_url', 'share_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
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
