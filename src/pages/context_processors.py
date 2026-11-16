"""Values every template gets."""

from django.http import HttpRequest
from django.utils import timezone

from pages import language
from pages.daypart import THEMES, Daypart, daypart_for


def daypart(request: HttpRequest) -> dict[str, Daypart | tuple[str, ...]]:
    """The time of day in Hòa Xuân for this request, and the themes a visitor can preview."""
    return {
        "daypart": daypart_for(timezone.now(), request.GET.dict()),
        "daypart_themes": THEMES,
    }


def page_language(request: HttpRequest) -> dict[str, str | dict[str, str]]:
    """The language of the page (`en` or `vi`), the addresses that follow it, the switch and
    the labels of the four themes for the header clock."""
    lang = language.of_request(request)
    return {
        "lang": lang,
        "home_path": language.home_path(lang),
        "contact_path": language.contact_path(lang),
        "lang_switch": language.switch(lang),
        "daypart_labels": language.daypart_labels(lang),
    }
