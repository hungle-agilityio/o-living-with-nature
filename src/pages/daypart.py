"""The time of day in Hòa Xuân: which colour theme a moment gets, and what a page shows for it."""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from django import forms

DA_NANG = ZoneInfo("Asia/Ho_Chi_Minh")

DAWN = "dawn"
DAY = "day"
DUSK = "dusk"
NIGHT = "night"
# In the order of a day, which is also the order of the preview links in the footer.
THEMES: tuple[str, ...] = (DAWN, DAY, DUSK, NIGHT)

# The hour each theme starts at, in Đà Nẵng time. Before the first one it is still night.
_STARTS: tuple[tuple[int, str], ...] = ((5, DAWN), (8, DAY), (17, DUSK), (19, NIGHT))


@dataclass(frozen=True)
class Daypart:
    """What a page shows: the theme name, its label and the clock in Hòa Xuân."""

    theme: str
    label: str
    clock: str


class PreviewForm(forms.Form):
    """The `?t=` query of a visitor: one of the four theme names, exactly as written."""

    t = forms.ChoiceField(choices=[(theme, theme) for theme in THEMES], required=False)


def _in_da_nang(moment: datetime) -> datetime:
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("the moment needs a time zone")
    return moment.astimezone(DA_NANG)


def theme_for(moment: datetime) -> str:
    """The theme for a moment: dawn 05:00–07:59, day 08:00–16:59, dusk 17:00–18:59, else night."""
    hour = _in_da_nang(moment).hour
    theme = NIGHT
    for start, name in _STARTS:
        if hour >= start:
            theme = name
    return theme


def preview_theme(query: dict[str, str]) -> str | None:
    """The theme a visitor asked to preview with `?t=`, or None when the value is not a theme."""
    form = PreviewForm(query)
    if not form.is_valid():
        return None
    return form.cleaned_data["t"] or None


def daypart_for(moment: datetime, query: dict[str, str]) -> Daypart:
    """The theme to show (the preview when one is asked, else the real one) and the real clock."""
    theme = preview_theme(query) or theme_for(moment)
    return Daypart(
        theme=theme,
        label=theme.capitalize(),
        clock=_in_da_nang(moment).strftime("%H:%M"),
    )
