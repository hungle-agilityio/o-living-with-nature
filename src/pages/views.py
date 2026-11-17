from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe

from counter.services import today_in_da_nang
from enquiries.forms import EnquiryForm
from enquiries.services import sent_state
from owner_content.services import site_settings
from pages import hero, language, seo
from pages.daypart import daypart_for


def home(request: HttpRequest) -> HttpResponse:
    """The whole site: the hero and the five chapters, with the owner's settings (one query)."""
    return render_home(request, enquiry_state="sent" if sent_state(request.GET) else "form")


def render_home(
    request: HttpRequest,
    *,
    enquiry_form: EnquiryForm | None = None,
    enquiry_state: str = "form",
    status: int = 200,
) -> HttpResponse:
    """The home page with the enquiry form in one of "form", "errors", "sent" or "paused"."""
    theme = daypart_for(timezone.now(), request.GET.dict()).theme
    loops = hero.loops()
    lang = language.of_request(request)
    head = seo.head_for("home", lang)
    owner = site_settings(lang)
    if enquiry_form is None:
        enquiry_form = EnquiryForm(language=lang, today=today_in_da_nang())
    context = {
        "seo": head,
        "hero": loops.get(theme),
        "hero_loops": loops,
        "owner": owner,
        # seo.structured_data already escaped <, > and & for a script element.
        "structured_data": mark_safe(seo.structured_data(head, owner)),
        "enquiry_form": enquiry_form,
        "enquiry_state": enquiry_state,
    }
    return render(request, "pages/home.html", context, status=status)


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
