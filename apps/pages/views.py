from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/home.html")


def health(request: HttpRequest) -> HttpResponse:
    """For the host's health check: the app is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")
