"""Counting: add one to the daily total of a view or a contact-button press."""

from datetime import date

from django.db.models import F
from django.http import HttpRequest
from django.utils import timezone

from counter.models import DailyCount
from pages.daypart import DA_NANG


def today_in_da_nang() -> date:
    return timezone.now().astimezone(DA_NANG).date()


def is_same_origin(request: HttpRequest) -> bool:
    """True when the Origin header is absent or is the site's own scheme and host."""
    origin = request.headers.get("Origin")
    if origin is None:
        return True
    return origin == f"{request.scheme}://{request.get_host()}"


def is_owner_visit(request: HttpRequest) -> bool:
    """A logged-in staff user (the owner in /owner/) is not counted.

    For a visitor without a session cookie this reads no database and sets no cookie.
    """
    user = getattr(request, "user", None)
    return bool(user is not None and user.is_authenticated and user.is_staff)


def record_count(*, kind: str, channel: str, place: str, day: date | None = None) -> None:
    """Add 1 to the row of that day, kind, channel and place; create it at 1 the first time.

    Two queries: an INSERT of the row at 0 that does nothing when it already exists (so two
    requests racing on the first count of a day never fail), then an UPDATE that adds 1.
    """
    day = day or today_in_da_nang()
    key = {"day": day, "kind": kind, "channel": channel, "place": place}
    DailyCount.objects.bulk_create([DailyCount(**key, count=0)], ignore_conflicts=True)
    DailyCount.objects.filter(**key).update(count=F("count") + 1)
