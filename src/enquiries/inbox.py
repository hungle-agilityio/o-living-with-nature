"""The labels of the owner's enquiries inbox: Đà Nẵng time, English words, no database."""

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import translation
from django.utils.dateformat import format as format_date

from enquiries.months import NOT_SURE, STAY_LABELS, month_label, short_month_label
from enquiries.services import KEEP_DAYS
from pages.daypart import DA_NANG


def received(created_at: datetime) -> str:
    """`16 Nov 2026, 09:12` in Đà Nẵng time, with English month names."""
    with translation.override("en"):
        return format_date(created_at.astimezone(DA_NANG), "j M Y, H:i")


def deleted_on(created_at: datetime) -> str:
    """The day the enquiry is deleted: `KEEP_DAYS` days after it arrived, in Đà Nẵng."""
    day = (created_at + timedelta(days=KEEP_DAYS)).astimezone(DA_NANG)
    with translation.override("en"):
        return format_date(day, "j M Y")


def move_in_short(value: str) -> str:
    return short_month_label(value) if value else NOT_SURE["en"]


def move_in_long(value: str) -> str:
    return month_label(value, "en") if value else NOT_SURE["en"]


def stay_label(value: str) -> str:
    return STAY_LABELS["en"].get(value, NOT_SURE["en"])


def page_language(code: str) -> str:
    return "English page" if code == "en" else "Vietnamese page"


def is_email(value: str) -> bool:
    try:
        validate_email(value)
    except ValidationError:
        return False
    return True
