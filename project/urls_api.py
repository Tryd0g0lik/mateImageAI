"""
project/urls_api.py
"""

from rest_framework_simplejwt.views import TokenObtainPairView

from person.urls_api import router as person_router

# from metaimage.urls_api import router as meta_image_router
from django.urls import path, include
from person.views_api.users_views import UserViews
from project.views import CSRFTokenView

# from project.views import csrf_token

urlpatterns = [
    # path("auth/", include(person_router.urls), name="auth_key"),
    path("auth/", include(person_router.urls), name="auth_key"),
    path(
        "auth/register/0/login/",
        UserViews.as_view({"post": "login"}),
        name="register_login",
    ),
    path(
        "auth/register/<int:pk>/logout/",
        UserViews.as_view({"patch": "logout"}),
        name="register_logout",
    ),
    # path("metaimages/", meta_image_router, name="metaimages"),
    path("auth/csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
