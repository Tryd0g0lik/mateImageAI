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
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from project.urls_api import urlpatterns as api_urls
from project import settings
from rest_framework.permissions import AllowAny

from project.views import CSRFTokenView

# from project.views import csrf_token

# SWAGGER DOC
# https://drf-yasg.readthedocs.io/en/stable/readme.html#configuration
# https://www.django-rest-framework.org/api-guide/schemas/
schema_view = get_schema_view(
    openapi.Info(
        title="MateImageAI API",
        default_version="v1",
        description="API Documentation",
        contact=openapi.Contact(email="work@80mail.ru"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    urlconf="project.urls",
)


urlpatterns = [
    path("", include(("person.urls", "person_app"), namespace="person_app")),
    path("admin/", admin.site.urls),
    path("api/", include((api_urls, "api_keys"), namespace="api_keys")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),  # Swagger UI
    path(
        "swagger<format>/", schema_view.with_ui("swagger", cache_timeout=0)
    ),  # Swagger UI
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),  # ReDoc
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
