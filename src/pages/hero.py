"""The home hero: which loop and poster fill the letter Ở for a theme."""

from dataclasses import dataclass

from django.contrib.staticfiles import finders

from pages.daypart import THEMES

_FOLDER = "media/hero"


@dataclass(frozen=True)
class HeroMedia:
    """The static files of one theme's loop: the poster photo and the two video formats."""

    poster: str
    mp4: str
    webm: str


def media_for(theme: str) -> HeroMedia | None:
    """The files of a theme's loop, or None when it is not a theme or any file is missing.

    With None the hero shows the letter in Sand and no "Illustrative video" chip.
    """
    if theme not in THEMES:
        return None
    media = HeroMedia(
        poster=f"{_FOLDER}/{theme}.jpg",
        mp4=f"{_FOLDER}/{theme}.mp4",
        webm=f"{_FOLDER}/{theme}.webm",
    )
    if any(finders.find(path) is None for path in (media.poster, media.mp4, media.webm)):
        return None
    return media


def loops() -> dict[str, HeroMedia]:
    """The files of every theme that has all three, in the order of a day, for the live switch."""
    found = {theme: media_for(theme) for theme in THEMES}
    return {theme: media for theme, media in found.items() if media is not None}
