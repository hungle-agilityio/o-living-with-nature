"""The contact counts report the owner reads in the admin.

Every sum is made in the database, in two queries whatever the number of rows: one aggregate
for the summary, the channels and the places, and one grouped by month. Months are Đà Nẵng
months: the stored day is already the date in Đà Nẵng.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth

from counter.models import DailyCount
from counter.services import today_in_da_nang

MONTH_NAMES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTHS_SHOWN = 12
NO_VIEWS = "–"

VIEW = Q(kind=DailyCount.Kind.VIEW)
CLICK = Q(kind=DailyCount.Kind.CLICK)


@dataclass(frozen=True)
class Totals:
    label: str
    views: int
    clicks: int

    @property
    def rate(self) -> str:
        return clicks_per_100(clicks=self.clicks, views=self.views)


@dataclass(frozen=True)
class PeriodRow:
    label: str
    this_month: int
    last_month: int
    all_time: int


@dataclass(frozen=True)
class MonthRow:
    month: str
    views: int
    call: int
    whatsapp: int
    zalo: int
    clicks: int


@dataclass(frozen=True)
class Report:
    summary: tuple[Totals, Totals, Totals]
    by_channel: tuple[PeriodRow, ...]
    by_place: tuple[PeriodRow, ...]
    by_month: tuple[MonthRow, ...]

    @property
    def is_empty(self) -> bool:
        total = self.summary[2]
        return total.views == 0 and total.clicks == 0


def clicks_per_100(*, clicks: int, views: int) -> str:
    """Clicks per 100 views with one decimal (half up), or "–" when there are no views."""
    if views == 0:
        return NO_VIEWS
    value = Decimal(clicks * 100) / Decimal(views)
    return str(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def month_label(month: date) -> str:
    """For example "Nov 2026", in English whatever language is active."""
    return f"{MONTH_NAMES[month.month - 1]} {month.year}"


def month_starts(today: date) -> tuple[date, date, date]:
    """The first day of last month, of this month and of next month."""
    this_start = today.replace(day=1)
    last_start = (this_start - timedelta(days=1)).replace(day=1)
    next_start = (this_start + timedelta(days=31)).replace(day=1)
    return last_start, this_start, next_start


def _count(condition: Q) -> Sum:
    return Sum("count", filter=condition, default=0)


def build_report() -> Report:
    last_start, this_start, next_start = month_starts(today_in_da_nang())
    periods = {
        "this": Q(day__gte=this_start, day__lt=next_start),
        "last": Q(day__gte=last_start, day__lt=this_start),
        "all": Q(),
    }
    channels = DailyCount.Channel.choices
    places = DailyCount.Place.choices
    sums: dict[str, Sum] = {}
    for period, in_period in periods.items():
        sums[f"{period}_views"] = _count(in_period & VIEW)
        sums[f"{period}_clicks"] = _count(in_period & CLICK)
        for value, _ in channels:
            sums[f"{period}_channel_{value}"] = _count(in_period & CLICK & Q(channel=value))
        for value, _ in places:
            sums[f"{period}_place_{value}"] = _count(in_period & CLICK & Q(place=value))
    totals: dict[str, Any] = DailyCount.objects.aggregate(**sums)

    def row(label: str, key: str) -> PeriodRow:
        return PeriodRow(label, totals[f"this_{key}"], totals[f"last_{key}"], totals[f"all_{key}"])

    summary = (
        Totals("This month", totals["this_views"], totals["this_clicks"]),
        Totals("Last month", totals["last_views"], totals["last_clicks"]),
        Totals("All time", totals["all_views"], totals["all_clicks"]),
    )
    return Report(
        summary=summary,
        by_channel=tuple(row(str(label), f"channel_{value}") for value, label in channels),
        by_place=tuple(row(str(label), f"place_{value}") for value, label in places),
        by_month=_by_month(),
    )


def _by_month() -> tuple[MonthRow, ...]:
    channel = DailyCount.Channel
    rows = (
        DailyCount.objects.annotate(month=TruncMonth("day"))
        .values("month")
        .annotate(
            total=Sum("count"),
            views=_count(VIEW),
            call=_count(CLICK & Q(channel=channel.CALL)),
            whatsapp=_count(CLICK & Q(channel=channel.WHATSAPP)),
            zalo=_count(CLICK & Q(channel=channel.ZALO)),
            clicks=_count(CLICK),
        )
        .filter(total__gt=0)
        .order_by("-month")[:MONTHS_SHOWN]
    )
    return tuple(
        MonthRow(
            month_label(r["month"]), r["views"], r["call"], r["whatsapp"], r["zalo"], r["clicks"]
        )
        for r in rows
    )
