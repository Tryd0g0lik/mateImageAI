from django.shortcuts import render



def main_views(request):
    return render(request, "index.html", {})
