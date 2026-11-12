from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from pages import hero, seo
from pages.daypart import daypart_for


def _page(request: HttpRequest, name: str) -> HttpResponse:
    """One of the five pages: its template with its search tags."""
    return render(request, f"pages/{name}.html", {"seo": seo.head_for(name)})


def home(request: HttpRequest) -> HttpResponse:
    theme = daypart_for(timezone.now(), request.GET.dict()).theme
    context = {"seo": seo.head_for("home"), "hero": hero.media_for(theme)}
    return render(request, "pages/home.html", context)


def house(request: HttpRequest) -> HttpResponse:
    return _page(request, "house")


def hoa_xuan(request: HttpRequest) -> HttpResponse:
    return _page(request, "hoa_xuan")


def faq(request: HttpRequest) -> HttpResponse:
    return _page(request, "faq")


def contact(request: HttpRequest) -> HttpResponse:
    return _page(request, "contact")


def sitemap(request: HttpRequest) -> HttpResponse:
    return HttpResponse(seo.sitemap_xml(), content_type="application/xml")


def robots(request: HttpRequest) -> HttpResponse:
    return HttpResponse(seo.robots_txt(), content_type="text/plain; charset=utf-8")


def health(request: HttpRequest) -> HttpResponse:
    """For the host's health check: the app is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")
