"""
URL configuration for recommendations app
"""

from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendation, name='recommendation'),
    path('template/', views.template_recommendation, name='template_recommendation'),
    path('save-plan/', views.save_plan, name='save_plan'),
    path('get-plans/', views.get_plans, name='get_plans'),
    path('get-venues/', views.get_venues_by_ids, name='get_venues_by_ids'),
    path('plan/<uuid:token>/', views.plan_landing_page, name='plan_landing_page'),
    path('preview-card/', views.preview_share_card, name='preview_share_card'),
]
