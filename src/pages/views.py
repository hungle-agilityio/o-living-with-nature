from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe

from owner_content.services import site_settings
from pages import hero, seo
from pages.daypart import daypart_for


def home(request: HttpRequest) -> HttpResponse:
    """The whole site: the hero and the five chapters, with the owner's settings (one query)."""
    theme = daypart_for(timezone.now(), request.GET.dict()).theme
    loops = hero.loops()
    head = seo.head_for("home")
    owner = site_settings()
    context = {
        "seo": head,
        "hero": loops.get(theme),
        "hero_loops": loops,
        "owner": owner,
        # seo.structured_data already escaped <, > and & for a script element.
        "structured_data": mark_safe(seo.structured_data(head, owner)),
    }
    return render(request, "pages/home.html", context)


def chapter(request: HttpRequest, chapter_id: str) -> HttpResponse:
    """An old page address: sent for good to its chapter of the home page, with no query."""
    return HttpResponsePermanentRedirect(f"/#{chapter_id}")


def sitemap(request: HttpRequest) -> HttpResponse:
    return HttpResponse(seo.sitemap_xml(), content_type="application/xml")


def robots(request: HttpRequest) -> HttpResponse:
    return HttpResponse(seo.robots_txt(), content_type="text/plain; charset=utf-8")


def health(request: HttpRequest) -> HttpResponse:
    """For the host's health check: the app is up and serving requests."""
    return HttpResponse("ok", content_type="text/plain")
