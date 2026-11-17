"""Storing an enquiry: the trap, the daily limit and the 12-month keep.

Nothing here logs: a name, a reply-to or a message never reaches a log record.
"""

from datetime import datetime, time, timedelta
from enum import StrEnum

from django.http import QueryDict

from enquiries.forms import EnquiryForm, EnquiryStateForm
from enquiries.models import Enquiry
from pages.daypart import DA_NANG

DAILY_LIMIT = 20
KEEP_DAYS = 365


class Outcome(StrEnum):
    STORED = "stored"
    TRAPPED = "trapped"
    PAUSED = "paused"


def is_trapped(form: EnquiryForm) -> bool:
    """True when the hidden trap field was filled; it always cleans, even on a wrong post."""
    return bool(form.cleaned_data.get("website"))


def delete_expired(now: datetime) -> None:
    """One DELETE of every enquiry older than `KEEP_DAYS` days."""
    Enquiry.objects.filter(created_at__lt=now - timedelta(days=KEEP_DAYS)).delete()


def start_of_day(now: datetime) -> datetime:
    """Midnight of `now`'s day in Đà Nẵng."""
    return datetime.combine(now.astimezone(DA_NANG).date(), time.min, tzinfo=DA_NANG)


def store_enquiry(form: EnquiryForm, *, language: str, from_owner: bool, now: datetime) -> Outcome:
    """Store a valid form, unless it is a trap or today's limit is reached.

    `from_owner` is not used yet: the count of #119 leaves the owner's own tests out.
    """
    if is_trapped(form):
        return Outcome.TRAPPED
    if Enquiry.objects.filter(created_at__gte=start_of_day(now)).count() >= DAILY_LIMIT:
        return Outcome.PAUSED
    delete_expired(now)
    data = form.cleaned_data
    Enquiry.objects.create(
        name=data["name"],
        reply_to=data["reply_to"],
        move_in=data["move_in"],
        stay=data["stay"],
        message=data["message"],
        language=language,
    )
    return Outcome.STORED


def sent_state(query: QueryDict) -> bool:
    """True only for `?enquiry=sent`."""
    form = EnquiryStateForm(query)
    return form.is_valid() and form.cleaned_data["enquiry"] == "sent"
