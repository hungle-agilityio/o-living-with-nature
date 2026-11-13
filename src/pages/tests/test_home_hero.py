"""The home hero "Through the Ở" (AC21 to AC25): what the server sends and the files it needs.

The flight itself runs in a browser; the browser check of the issue shows it. These tests pin
what the page, the stylesheet and the script must hold for the flight and for the still hero.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import hero
from pages.daypart import THEMES

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db

REPO = Path(settings.SRC_DIR).parent
HERO_FILES = Path(settings.SRC_DIR) / "static" / "media" / "hero"
LINE = "A garden house in Hòa Xuân, Đà Nẵng. Two bedrooms, two gardens, rented whole, by the month."


class _Page(HTMLParser):
    """Collects the start tags with their attributes, and the whole text of each element."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.text: dict[str, list[str]] = {}
        self._open: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag not in {"meta", "link", "img", "source", "br"}:
            self._open.append((tag, []))

    def handle_endtag(self, tag: str) -> None:
        if tag not in [name for name, _parts in self._open]:
            return
        while True:
            name, parts = self._open.pop()
            self.text.setdefault(name, []).append(" ".join("".join(parts).split()))
            if name == tag:
                return

    def handle_data(self, data: str) -> None:
        for _name, parts in self._open:
            parts.append(data)

    def all(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == name]

    def with_class(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for _tag, attrs in self.tags if name in (attrs.get("class") or "").split()]


def _parse(html: str) -> _Page:
    page = _Page()
    page.feed(html)
    page.close()
    return page


def _html(client: Client, address: str = "/?t=day") -> str:
    response = client.get(address)
    assert response.status_code == 200
    return response.content.decode()


def _hero(client: Client, address: str = "/?t=day") -> str:
    match = re.search(r'<section id="hero".*?</section>', _html(client, address), re.DOTALL)
    assert match, "no hero section in the home page"
    return match.group(0)


def _css() -> str:
    return (Path(settings.SRC_DIR) / "static" / "css" / "site.css").read_text(encoding="utf-8")


def _script() -> str:
    return (Path(settings.SRC_DIR) / "static" / "js" / "hero.js").read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    # A rule of its own: the selector starts a line (not one under the flight class).
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _no_files(mocker: MockerFixture, *missing: str) -> None:
    """Make the named static files look missing."""
    real = finders.find

    def find(path: str) -> object:
        if path in missing:
            return None
        return real(path)

    mocker.patch("pages.hero.finders.find", side_effect=find)


# The service: which files the hero of a theme uses


@pytest.mark.parametrize("theme", THEMES)
def test_service_gives_the_three_files_of_a_theme(theme: str) -> None:
    assert hero.media_for(theme) == hero.HeroMedia(
        poster=f"media/hero/{theme}.jpg",
        mp4=f"media/hero/{theme}.mp4",
        webm=f"media/hero/{theme}.webm",
    )


@pytest.mark.parametrize("value", ["", "noon", "DAY", "../day", "day/../../css/site"])
def test_service_gives_nothing_for_a_name_that_is_not_a_theme(value: str) -> None:
    assert hero.media_for(value) is None


@pytest.mark.parametrize("extension", ["jpg", "mp4", "webm"])
def test_service_gives_nothing_when_one_file_of_the_theme_is_missing(
    mocker: MockerFixture, extension: str
) -> None:
    _no_files(mocker, f"media/hero/dusk.{extension}")

    assert hero.media_for("dusk") is None
    assert hero.media_for("day") is not None


# AC21


def test_hero_opens_with_the_letter(client: Client) -> None:
    section = _hero(client)

    assert re.search(r'<p class="hero__letter"[^>]*>\s*Ở\s*</p>', section)
    letter = _rule(_css(), ".hero__letter")
    assert "font-family: var(--font-serif)" in letter
    assert "font-weight: 500" in letter
    assert "font-size: var(--size-hero)" in letter
    # 70% of the screen height, at most 105% of its width (design.md, type scale).
    assert re.search(r"--size-hero:\s*min\(70vh,\s*105vw\)", _css())


def test_letter_is_filled_with_the_loop_of_the_theme(client: Client) -> None:
    page = _parse(_hero(client, "/?t=day"))

    (video,) = page.all("video")
    assert video["poster"] == "/static/media/hero/day.jpg"
    sources = {source["type"]: source["src"] for source in page.all("source")}
    assert sources == {
        "video/webm": "/static/media/hero/day.webm",
        "video/mp4": "/static/media/hero/day.mp4",
    }
    assert "muted" in video
    assert "loop" in video
    assert "playsinline" in video
    # The script draws the playing video through the letter shape on this canvas.
    assert len(page.all("canvas")) == 1


def test_dictionary_line_is_under_the_letter(client: Client) -> None:
    section = _hero(client)
    page = _parse(section)

    assert page.text["p"][1:3] == [
        'ở · verb · Vietnamese · say "uh?"',
        "1. to stay. 2. to live somewhere. 3. to be at home.",
    ]
    assert page.text["i"] == ["ở", "to be at home."]
    assert section.index("hero__letter") < section.index("to be at home.")


def test_hero_invites_to_scroll(client: Client) -> None:
    section = _hero(client)

    assert "Scroll, and come in ↓" in _parse(section).text["p"]
    assert section.index("to be at home.") < section.index("Scroll, and come in ↓")


def test_chip_says_the_video_is_illustrative(client: Client) -> None:
    page = _parse(_hero(client))

    assert page.text["span"].count("Illustrative video") == 1
    assert len(page.with_class("hero__chip")) == 1


@pytest.mark.parametrize("theme", THEMES)
def test_media_credits_list_every_loop_and_its_files_exist(theme: str) -> None:
    credits = (REPO / "docs" / "specs" / "site-shell" / "media-credits.md").read_text(
        encoding="utf-8"
    )

    assert re.search(
        rf"^\| `{theme}` \|[^|]+\| https://www\.pexels\.com/video/\S+ \|$", credits, re.M
    )
    for extension in ("jpg", "mp4", "webm"):
        assert (HERO_FILES / f"{theme}.{extension}").is_file()


# AC22


def test_page_loads_the_one_plain_script_deferred(client: Client) -> None:
    page = _parse(_html(client))

    # The hero's flight, the photo dialog of the floor plan (one-page AC17), then the phone
    # contact bar (one-page AC12), after the load and reveal motion that base.html links
    # (design-match AC13).
    scripts = page.all("script")
    assert [script["src"] for script in scripts] == [
        "/static/js/reveal.js",
        "/static/js/daypart.js",
        "/static/js/hero.js",
        "/static/js/floor-plan.js",
        "/static/js/area-band.js",
        "/static/js/contact-bar.js",
        "/static/js/count.js",
    ]
    for script in scripts:
        assert "defer" in script
        assert "async" not in script
    # Nothing written into the page itself: the script files are all the JavaScript there is.
    assert page.text["script"] == ["", "", "", "", "", "", ""]


def test_script_is_small_and_uses_no_library() -> None:
    script = _script()

    assert len(script.encode()) < 14_000
    for sign in ("import ", "require(", "http://", "https://", "jQuery", "eval("):
        assert sign not in script, sign


def test_script_flies_only_when_motion_is_fine() -> None:
    script = _script()

    assert "(prefers-reduced-motion: reduce)" in script
    # The flight is switched on by one class on the page; without it the hero is the still one.
    assert '"hero-flight"' in script
    # The numbers of design.md: the letter grows up to about 70 times, with no POWER any more;
    # the intro runs on time (time-of-day-live): rest to 0.6 s, grow to 5.6 s, heading in by 7.0 s.
    assert re.search(r"MAX_SCALE\s*=\s*70\b", script)
    assert "POWER" not in script
    assert re.search(r"GROW_START\s*=\s*0\.6\b", script)
    assert re.search(r"GROW_END\s*=\s*5\.6\b", script)
    assert re.search(r"INTRO_END\s*=\s*7(\.0)?\b", script)


def test_stage_is_about_three_screens_with_a_frame_that_stays() -> None:
    # design-match: the stage is now one screen, with no sticky frame.
    css = _css()

    flight = _rule(css, "html.hero-flight .hero")
    assert "height: 100svh" in flight
    assert "min-height: 560px" in flight
    assert "330vh" not in css
    assert "position: sticky" not in css.split("/* Home hero", 1)[1]
    # The header row turns Paper once the loop covers the screen.
    assert re.search(r"html\.hero-over \.site-header\s*\{[^}]*color:\s*var\(--paper\)", css)


# AC23


def test_still_hero_fills_the_letter_with_the_poster_photo(client: Client) -> None:
    page = _parse(_hero(client, "/?t=dusk"))

    (letter,) = page.with_class("hero__letter")
    assert letter["style"] == "background-image: url('/static/media/hero/dusk.jpg')"
    css = _css()
    assert re.search(r"\.hero__letter\s*\{[^}]*background-clip:\s*text", css)
    assert re.search(r"\.hero__letter\s*\{[^}]*-webkit-background-clip:\s*text", css)


def test_no_video_plays_without_the_script(client: Client) -> None:
    page = _parse(_hero(client))

    (video,) = page.all("video")
    assert "autoplay" not in video
    # Under reduced motion the browser is not even offered the files.
    for source in page.all("source"):
        assert source["media"] == "(prefers-reduced-motion: no-preference)"
    # The video and the canvas show only in the flight.
    still = _css().split("html.hero-flight", 1)[0]
    assert re.search(
        r"\.hero__video,\s*\.hero__canvas,\s*\.hero__shade\s*\{[^}]*display:\s*none", still
    )


def test_heading_and_its_line_are_in_the_page_in_every_case(client: Client) -> None:
    section = _hero(client)
    page = _parse(section)

    assert page.text["h1"] == ["Living with nature"]
    assert LINE in page.text["p"]
    assert re.search(r'<span class="accent">rented whole, by the month\.</span>', section)
    assert section.index("Scroll, and come in ↓") < section.index("<h1")
    # Nothing of the still hero is hidden: the hiding rules all need the flight class.
    for selector in (".hero__title", ".hero__foot", ".hero__gloss", ".hero__line"):
        for rule in re.findall(rf"(?m)^{re.escape(selector)}\s*\{{([^}}]*)\}}", _css()):
            assert "opacity" not in rule, selector
            assert "display: none" not in rule, selector
            assert "visibility" not in rule, selector


def test_flight_is_off_under_reduced_motion_in_the_stylesheet() -> None:
    # The script checks the preference; the stylesheet has no flight rule outside the class the
    # script sets, so a page without the script can never show a stage.
    css = _css()

    assert "330vh" not in css.split("html.hero-flight", 1)[0]
    assert "position: sticky" not in css.split("html.hero-flight", 1)[0]


# AC24


@pytest.mark.parametrize("theme", THEMES)
def test_preview_uses_the_loop_and_the_poster_of_that_theme(client: Client, theme: str) -> None:
    section = _hero(client, f"/?t={theme}")
    page = _parse(section)

    (video,) = page.all("video")
    assert video["poster"] == f"/static/media/hero/{theme}.jpg"
    assert [source["src"] for source in page.all("source")] == [
        f"/static/media/hero/{theme}.webm",
        f"/static/media/hero/{theme}.mp4",
    ]
    (letter,) = page.with_class("hero__letter")
    assert letter["style"] == f"background-image: url('/static/media/hero/{theme}.jpg')"


def test_hero_follows_the_theme_of_the_page(client: Client) -> None:
    html = _html(client, "/?t=nonsense")

    theme = re.search(r'<body data-daypart="(\w+)"', html)
    assert theme
    assert f'poster="/static/media/hero/{theme.group(1)}.jpg"' in html


def test_missing_files_give_a_sand_letter_and_no_chip(
    client: Client, mocker: MockerFixture
) -> None:
    _no_files(mocker, "media/hero/night.mp4")

    section = _hero(client, "/?t=night")
    page = _parse(section)

    assert re.search(r'<p class="hero__letter">\s*Ở\s*</p>', section)
    assert not page.all("video")
    assert not page.all("source")
    assert "Illustrative" not in section
    # The other themes' files may be listed for the live switch (time-of-day-live AC13); no
    # file of the night loop is.
    assert "media/hero/night" not in section
    # Nothing else breaks: the words and the heading are all there.
    assert "to be at home." in section
    assert page.text["h1"] == ["Living with nature"]
    letter = _rule(_css(), ".hero__letter")
    assert "background-color: var(--sand)" in letter
    assert "color: var(--sand)" in letter
    assert re.search(r"--sand:\s*#e9e2d3", _css(), re.IGNORECASE)
    # The script fills the letter with the same Sand when it has no loop and no poster.
    assert re.search(r'SAND\s*=\s*"#e9e2d3"', _script(), re.IGNORECASE)


# AC25


def test_video_loads_only_its_metadata(client: Client) -> None:
    (video,) = _parse(_hero(client)).all("video")

    assert video["preload"] == "metadata"


@pytest.mark.parametrize("theme", THEMES)
def test_only_the_loop_of_the_current_theme_is_in_the_page(client: Client, theme: str) -> None:
    # The video, its sources and the letter name only the current theme's files; the data
    # attributes of the hero section may list the other themes' files for the live switch
    # (time-of-day-live AC13).
    section = _hero(client, f"/?t={theme}")
    page = _parse(section)
    (video,) = page.all("video")
    (letter,) = page.with_class("hero__letter")
    named = [video["poster"], letter["style"]] + [source["src"] for source in page.all("source")]
    assert {name for text in named for name in re.findall(r"media/hero/(\w+)\.", text or "")} == {
        theme
    }
    # The page also holds the Hòa Xuân area loop (one-page AC14), so the count is the hero's.
    assert len(page.all("video")) == 1


@pytest.mark.django_db
@pytest.mark.parametrize("address", ["/", "/?t=dusk"])
def test_home_page_asks_the_database_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    # The one query reads the owner's site settings (one-page AC5).
    with django_assert_num_queries(1):
        response = client.get(address)

    assert response.status_code == 200


def test_nothing_of_the_hero_is_wider_than_the_screen() -> None:
    css = _css()

    # The still hero cuts what the big letter would push sideways; the frame of the flight too.
    assert re.search(r"(?m)^\.hero\s*\{[^}]*overflow-x:\s*clip", css)
    assert re.search(r"html\.hero-flight \.hero__frame\s*\{[^}]*overflow:\s*hidden", css)
    assert "100vw" not in css.split("/* Home hero", 1)[1].split("/* Phones", 1)[0]
