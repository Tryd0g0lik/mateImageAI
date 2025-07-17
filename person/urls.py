from django.urls import path

from person.views import main_views

urlpatterns = [
    path("", main_views, name="main_views"),
]

