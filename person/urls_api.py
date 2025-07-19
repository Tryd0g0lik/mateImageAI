"""
person/urls_api.py
THis's contains an api url for the person.
All from  paths generated wea can to the 'project/urls_api.py' of this project tree.
"""

from rest_framework.routers import DefaultRouter

from person.views_api.users_views import UserViews

router = DefaultRouter()
router.register(r"register", UserViews, basename="register_create")
