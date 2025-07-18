"""
person/urls_api.py
THis's contains an api url for the person.
"""

from rest_framework.routers import DefaultRouter

from person.views_api.users_views import UserViews

router = DefaultRouter()
router.register("register", UserViews, basename="register_key")
