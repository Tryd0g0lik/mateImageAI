"""
project/urls_api.py
"""

from person.urls_api import router as person_router

# from metaimage.urls_api import router as meta_image_router
from django.urls import path, include


urlpatterns = [
    path("auth/", include(person_router.urls), name="auth_key"),
    # path("metaimages/", meta_image_router, name="metaimages"),
]
