"""Design match T5: the Hòa Xuân band (design-match spec AC22 to AC25; design.md, "02 ở gần").
The positions in the browser are checked by the verify report's screens; these tests pin the
markup, the rules that give them and the script that plays the loop only while it is seen."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db

CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "hoa_xuan.css"
SCRIPT = settings.SRC_DIR / "static" / "js" / "area-band.js"
LINE = "Everything you need day to day is close by."
TRAVEL = [
    ("Supermarket", "across the road"),
    ("Market", "about 10 min"),
    ("Beach", "about 10 min"),
    ("Airport", "about 15 min"),
]
INSET = "max(var(--side), calc((100% - var(--content-max)) / 2 + var(--side)))"


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _chapter(client: Client) -> str:
    match = re.search(r'<section id="hoa-xuan"[^>]*>.*?</section>', _home(client), re.S)
    assert match, "no section #hoa-xuan"
    return match.group(0)


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _phone() -> str:
    parts = _css().split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no rules for 760px or less"
    return parts[1]


def _travel(chapter: str) -> str:
    match = re.search(r'<ul class="hoa-xuan__travel">.*?</ul>', chapter, re.S)
    assert match, "no travel list"
    return match.group(0)


# AC1: the band and its loop


def test_band_is_full_width_and_100vh_with_at_least_680px() -> None:
    css = _css()

    chapter = _rule(css, ".chapter--hoa-xuan")
    assert "width: 100%" in chapter
    assert "padding-left: 0" in chapter
    assert "padding-right: 0" in chapter
    band = _rule(css, ".hoa-xuan__band")
    assert "height: 100vh" in band
    assert "min-height: 680px" in band
    assert "color: var(--paper)" in band
    # The text keeps the container: the sides, or centred past 1360px.
    assert f"padding-left: {INSET}" in band
    assert f"padding-right: {INSET}" in band
    assert "100vw" not in css


def test_loop_covers_the_band_under_the_veil() -> None:
    css = _css()

    loop = _rule(css, ".hoa-xuan__loop")
    assert "position: absolute" in loop
    assert "inset: 0" in loop
    assert "height: 100%" in _rule(css, ".hoa-xuan__loop .media__box")
    veil = _rule(css, ".hoa-xuan__loop .media__box::after")
    assert (
        "linear-gradient(to bottom, rgba(31, 42, 34, 0.55) 0%, rgba(31, 42, 34, 0.15) 40%, "
        "rgba(31, 42, 34, 0.72) 100%)" in " ".join(veil.split())
    )


def test_band_holds_the_area_loop_without_a_fixed_ratio(client: Client) -> None:
    band = re.search(r'<div class="hoa-xuan__band">.*?</figure>', _chapter(client), re.S)

    assert band, "no loop in the band"
    assert band.group(0).count("<video") == 1
    assert "aspect-ratio: 16 / 9" not in band.group(0)


def test_chip_sits_bottom_right_and_the_credit_stays_in_the_page(client: Client) -> None:
    css = _css()
    chapter = _chapter(client)

    chip = _rule(css, ".hoa-xuan__loop .media__chip")
    assert "left: auto" in chip
    assert "right:" in chip
    assert "Illustrative video" in chapter
    assert '<figcaption class="media__credit">' in chapter
    assert "display: none" not in _rule(css, ".hoa-xuan__loop .media__credit")


def test_empty_loop_fills_the_band_too(client: Client, mocker: MockerFixture) -> None:
    mocker.patch("pages.photos.area_loop", return_value=None)

    chapter = _chapter(client)

    assert "media--empty" in chapter
    assert "aspect-ratio: 16 / 9" not in chapter.split("hoa-xuan__photos", 1)[0]


def test_page_loads_the_band_script_deferred(client: Client) -> None:
    html = _home(client)

    assert '<script src="/static/js/area-band.js" defer></script>' in html


def test_script_plays_the_loop_only_while_the_band_is_on_screen() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "IntersectionObserver" in script
    assert "isIntersecting" in script
    assert ".play()" in script
    assert ".pause()" in script
    assert "prefers-reduced-motion: reduce" in script
    assert len(script.encode()) < 4_000
    for sign in ("import ", "require(", "http://", "https://", "eval("):
        assert sign not in script, sign


# AC2: the head at the top, the line and the travel facts at the bottom


def test_head_sits_at_the_top_and_the_foot_at_the_bottom() -> None:
    css = _css()

    band = _rule(css, ".hoa-xuan__band")
    assert "padding-top: 72px" in band
    assert "padding-bottom: 56px" in band
    assert "justify-content: space-between" in band


def test_line_and_travel_facts_in_their_type() -> None:
    css = _css()

    line = _rule(css, ".hoa-xuan__line")
    assert "font-size: 28px" in line
    travel = _rule(css, ".hoa-xuan__travel")
    assert "grid-template-columns: repeat(4, minmax(0, 1fr))" in travel
    row = _rule(css, ".hoa-xuan__travel li")
    assert "border-top: 1px solid rgba(244, 240, 232, 0.6)" in row
    assert "padding-top: 14px" in row
    time = _rule(css, ".hoa-xuan__time")
    assert "font-family: var(--font-serif)" in time
    assert "font-style: italic" in time
    assert "font-size: 32px" in time


def test_two_travel_columns_and_24px_times_at_760px_or_less() -> None:
    phone = _phone()

    assert re.search(
        r"\.hoa-xuan__travel\s*\{[^}]*grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\)",
        phone,
    )
    assert re.search(r"\.hoa-xuan__time\s*\{[^}]*font-size:\s*24px", phone)


def test_head_comes_before_the_line_and_the_facts(client: Client) -> None:
    chapter = _chapter(client)

    head = chapter.index("hoa-xuan__head")
    line = chapter.index(LINE)
    travel = chapter.index("hoa-xuan__travel")
    assert head < line < travel
    assert "hoa-xuan-heading" in chapter[head:line]


# AC3: the travel list stays a plain list with its rows as written


def test_travel_rows_keep_their_text_with_a_hidden_dot(client: Client) -> None:
    travel = _travel(_chapter(client))

    items = re.findall(r"<li>(.*?)</li>", travel, re.S)
    assert [_text(item) for item in items] == [f"{place} · {time}" for place, time in TRAVEL]
    assert "<li " not in travel
    for item, (place, time) in zip(items, TRAVEL, strict=True):
        assert re.search(rf'<span class="hoa-xuan__place label">{place}</span>', item)
        assert '<span class="hoa-xuan__dot" aria-hidden="true"> · </span>' in item
        assert re.search(rf'<span class="hoa-xuan__time">{time}</span>', item)
    assert "display: none" in _rule(_css(), ".hoa-xuan__dot")


# AC4: the photos and the Maps button under the band


def test_photos_then_maps_button_come_under_the_band_in_the_container(client: Client) -> None:
    chapter = _chapter(client)
    css = _css()

    band_end = chapter.index("</figure>", chapter.index("hoa-xuan__band"))
    after = chapter.index('class="hoa-xuan__after"')
    photos = chapter.index("hoa-xuan__photos")
    maps = chapter.index("hoa-xuan__maps")
    assert band_end < after < photos < maps
    rule = _rule(css, ".hoa-xuan__after")
    assert "width: min(100%, var(--content-max))" in rule
    assert "margin: 48px auto 0" in rule
    assert "padding: 0 var(--side)" in rule
    assert "grid-column: span 4" in _rule(css, ".hoa-xuan__photos li")
    assert chapter.count("aspect-ratio: 4 / 3") == 3


# AC5: the reveal


def test_head_line_facts_photos_and_button_reveal(client: Client) -> None:
    chapter = _chapter(client)

    assert re.search(r'<div class="hoa-xuan__head reveal">', chapter)
    # The line and the facts keep their own class (pinned by test_hoa_xuan_chapter.py); each
    # rises in a wrapper of its own.
    assert '<div class="reveal"><p class="hoa-xuan__line quote">' in chapter
    assert '<div class="reveal"><ul class="hoa-xuan__travel">' in chapter
    gallery = re.search(r'<ul class="hoa-xuan__photos">(.*?)</ul>', chapter, re.S)
    assert gallery
    assert gallery.group(1).count('<li class="reveal">') == 3
    assert re.search(r'<a class="button button--secondary hoa-xuan__maps reveal"', chapter)


# AC6


def test_home_still_makes_exactly_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
