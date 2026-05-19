"""
URL configuration for recommendations app
"""

from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendation, name='recommendation'),
    path('template/', views.template_recommendation, name='template_recommendation'),
]
