"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from project.urls_api import urlpatterns as api_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# from person.urls import  urlpatterns as person_urls
from project import settings

from rest_framework.routers import DefaultRouter
from person.views_api.users_views import UserViews

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
)


urlpatterns = [
    path("", include(("person.urls", "person_app"), namespace="person_app")),
    path("admin/", admin.site.urls),
    path("api/", include((api_urls, "api_keys"), namespace="api_keys")),
    # path("api/", include((router.urls, "api_keys"), namespace="api_keys")),
    # path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0)
    ),  # для .json/.yaml
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),  # Swagger UI
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),  # ReDoc
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
