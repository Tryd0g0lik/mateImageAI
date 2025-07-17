"""
project/urls_api.py
"""
from rest_framework.routers import DefaultRouter
from person.urls_api import router as person_router
from metaimage.urls_api import router as meta_image_router
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path("persons/", person_router, name="persons"),
    path("metaimages/", meta_image_router, name="metaimages"),
]
