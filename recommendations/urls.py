"""
URL configuration for recommendations app
"""

from django.urls import path
from . import views
from .auth_views import google_auth, apple_auth, set_city, me, register, login, delete_account

app_name = 'recommendations'

urlpatterns = [
    path('auth/google/', google_auth, name='auth_google'),
    path('auth/apple/', apple_auth, name='auth_apple'),
    path('auth/register/', register, name='auth_register'),
    path('auth/login/', login, name='auth_login'),
    path('auth/delete-account/', delete_account, name='auth_delete_account'),
    path('auth/set-city/', set_city, name='auth_set_city'),
    path('auth/me/', me, name='auth_me'),
    path('', views.recommendation, name='recommendation'),
    path('template/', views.template_recommendation, name='template_recommendation'),
    path('save-plan/', views.save_plan, name='save_plan'),
    path('get-plans/', views.get_plans, name='get_plans'),
    path('get-venues/', views.get_venues_by_ids, name='get_venues_by_ids'),
    path('get-areas/', views.get_areas_by_city, name='get_areas_by_city'),
    path('get-cities/', views.get_cities, name='get_cities'),
    path('preview-card/', views.preview_share_card, name='preview_share_card'),
    path('plan/<uuid:token>/', views.plan_landing_page, name='plan_landing_page_legacy'),
    path('intent/', views.intent_recommendation, name='intent_recommendation'),
    path('join-waitlist/', views.join_waitlist, name='join_waitlist'),
]
