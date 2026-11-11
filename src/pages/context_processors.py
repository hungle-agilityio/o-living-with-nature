"""Values every template gets."""

from django.http import HttpRequest
from django.utils import timezone

from pages.daypart import THEMES, Daypart, daypart_for


def daypart(request: HttpRequest) -> dict[str, Daypart | tuple[str, ...]]:
    """The time of day in Hòa Xuân for this request, and the themes a visitor can preview."""
    return {
        "daypart": daypart_for(timezone.now(), request.GET.dict()),
        "daypart_themes": THEMES,
    }
