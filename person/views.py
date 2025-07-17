import os

from django.shortcuts import render

from project.settings import BASE_DIR


def main_views(request):
    files = []
    # GET JS FILES FOR LOGIN AND REGISTER PAGES
    # if "login" in request.path.lower() or "register" in request.path.lower():
    files = os.listdir(f"{BASE_DIR}/collectstatic/scripts")
    files = ["scripts/" + file for file in files]
    return render(request, "layout/index.html", {"js_files":files})
