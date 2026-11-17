"""The phone photo carousel of the house chapter (mobile-smoothness spec AC1 to AC6, AC17, AC18;
issue #141).

The swipe itself is checked in a browser. These tests pin what the stylesheet says at 760 px or
less and above it, what the server sends, and what the script file must hold.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db

CSS = Path(settings.SRC_DIR) / "static" / "css" / "chapters" / "house.css"
SCRIPT = Path(settings.SRC_DIR) / "static" / "js" / "house-carousel.js"
ADDRESSES = ["/", "/vi/"]
FORBIDDEN = ["import", "require(", "http", "eval(", "localStorage", "sessionStorage"]
# key, height, shift (positive: lower, negative: higher) of the desktop collage on main
DESKTOP_ROOMS = [
    ("bedroom", 620, 0),
    ("lightwell", 460, 160),
    ("veranda", 340, 60),
    ("kitchen", 380, 0),
    ("garden-evening", 460, -120),
]


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _desktop_css() -> str:
    return _css().split("@media (max-width: 760px)")[0]


def _narrow_css() -> str:
    narrow = re.search(r"@media \(max-width: 760px\)\s*\{(.*?)\n\}", _css(), re.S)
    assert narrow, "no rule for 760px or less"
    return narrow.group(1)


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no rule {selector}"
    return match.group(1)


def _script() -> str:
    assert SCRIPT.is_file(), "no src/static/js/house-carousel.js"
    return SCRIPT.read_text(encoding="utf-8")


def _script_srcs(html: str) -> list[str]:
    return re.findall(r'<script src="([^"]+)"', html)


# M1 (AC1)


def test_phone_collage_is_a_snapping_row_that_runs_to_the_screen_edges() -> None:
    """M1: the collage at 760 px or less."""
    collage = _rule(_narrow_css(), ".house__collage")

    assert re.search(r"overflow-x:\s*auto", collage)
    assert re.search(r"scroll-snap-type:\s*x mandatory", collage)
    assert re.search(r"margin:[^;]*calc\(-1 \* var\(--side\)\)", collage)
    assert re.search(r"scroll-padding:\s*0 var\(--side\)", collage)


def test_phone_card_is_84_percent_of_the_row_with_a_4_5_photo_box() -> None:
    """M1: the card and its photo box at 760 px or less."""
    narrow = _narrow_css()

    assert re.search(r"flex:\s*0 0 84%", _rule(narrow, ".house__room"))
    assert re.search(r"aspect-ratio:\s*4 / 5", _rule(narrow, ".house__room .media__box"))


def test_pager_is_hidden_above_760px_and_a_flex_row_inside_it() -> None:
    """M1: `.house__pager` is `display: none` before the 760 px block, `display: flex` inside."""
    assert re.search(r"display:\s*none", _rule(_desktop_css(), ".house__pager"))
    assert re.search(r"display:\s*flex", _rule(_narrow_css(), ".house__pager"))


# M3 (AC1, empty)


def test_collage_still_has_five_cards_when_a_photo_file_is_missing(
    client: Client, mocker: MockerFixture
) -> None:
    """M3: with the bedroom photo missing, five `li.house__room` remain for the script to count."""
    mocker.patch(
        "pages.photos.finders.find",
        side_effect=lambda path: None if path.endswith("bedroom.jpg") else f"/found/{path}",
    )

    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()
    collage = re.search(r'<ul class="house__collage">.*?</ul>', html, re.S)
    assert collage, "no .house__collage"
    assert len(re.findall(r'<li class="house__room\b', collage.group(0))) == 5
    assert "/static/media/photos/bedroom.jpg" not in collage.group(0)


# M4 (AC2)


def test_phone_card_snaps_to_its_centre_and_stops_at_every_card() -> None:
    """M4: one swipe moves one card."""
    room = _rule(_narrow_css(), ".house__room")

    assert re.search(r"scroll-snap-align:\s*center", room)
    assert re.search(r"scroll-snap-stop:\s*always", room)


def test_script_listens_to_scroll_passively_once_per_frame() -> None:
    """M4: a passive scroll listener that asks for one animation frame at a time."""
    script = _script()

    assert '"scroll"' in script
    assert re.search(r"passive:\s*true", script)
    assert "requestAnimationFrame" in script
    assert script.lstrip().startswith(("(function", "(() =>", '"use strict"'))
    assert '"use strict"' in script


# M5 (AC3)


def test_script_builds_labelled_dots_with_state_and_a_polite_count() -> None:
    """M5: the words the script holds."""
    script = _script()

    for word in (
        '"button"',
        '"Photo "',
        '"Ảnh "',
        "aria-current",
        "aria-live",
        '"polite"',
        '"smooth"',
        "prefers-reduced-motion: reduce",
    ):
        assert word in script, word


def test_dot_button_is_28_by_28_pixels() -> None:
    """M5: the `.house__dots button` rule."""
    dot = _rule(_narrow_css(), ".house__dots button")

    assert re.search(r"width:\s*28px", dot)
    assert re.search(r"height:\s*28px", dot)


def test_dots_take_the_page_colour_and_the_count_has_no_paragraph_margin() -> None:
    """Code review: the dot is `currentColor`, so the button inherits the ink of the daypart
    (a button's own colour is near-black, lost at night); the count `p` sits 14 px under the row."""
    narrow = _narrow_css()

    assert re.search(r"color:\s*inherit", _rule(narrow, ".house__dots button"))
    assert re.search(r"margin:\s*0", _rule(narrow, ".house__count"))


# M6 (AC4)


def test_phone_cards_do_not_rise_fade_or_zoom_inside_the_carousel() -> None:
    """M6: motion switched off inside the carousel at 760 px or less."""
    narrow = _narrow_css()

    card = _rule(narrow, "html.motion .house__collage .house__room.reveal")
    assert re.search(r"opacity:\s*1", card)
    assert re.search(r"transform:\s*none", card)
    assert re.search(r"transition:\s*none", card)
    photo = _rule(narrow, "html.motion .house__collage .media__box img")
    assert re.search(r"animation:\s*none", photo)


# M7 (AC5)


def test_desktop_collage_keeps_its_heights_and_shifts() -> None:
    """M7: the part of house.css before the 760 px block keeps the collage of main."""
    css = _desktop_css()

    collage = _rule(css, ".house__collage")
    assert re.search(r"grid-template-columns:\s*repeat\(12,", collage)
    assert re.search(r"gap:\s*18px", collage)
    for key, height, shift in DESKTOP_ROOMS:
        room = _rule(css, f".house__room--{key}")
        if shift:
            assert re.search(rf"margin-top:\s*{shift}px", room), key
        else:
            assert "margin-top" not in room, key
        assert re.search(rf"height:\s*{height}px", _rule(css, f".house__room--{key} .media__box"))


def test_html_holds_no_pager_because_the_script_builds_it(client: Client) -> None:
    """M7: without JavaScript there is no count line and no dot."""
    html = client.get("/").content.decode()

    assert "house__pager" not in html


# M8 (AC6)


@pytest.mark.parametrize("address", ADDRESSES)
def test_page_links_the_carousel_script_once_between_floor_plan_and_area_band(
    client: Client, address: str
) -> None:
    """M8: script order and `defer`."""
    html = client.get(address).content.decode()

    srcs = _script_srcs(html)
    assert srcs.count("/static/js/house-carousel.js") == 1
    at = srcs.index("/static/js/house-carousel.js")
    assert srcs[at - 1] == "/static/js/floor-plan.js"
    assert srcs[at + 1] == "/static/js/area-band.js"
    assert '<script src="/static/js/house-carousel.js" defer>' in html


def test_script_is_small_plain_and_reads_the_page_language() -> None:
    """M8: under 3,000 bytes, no forbidden word, reads `document.documentElement.lang`."""
    script = _script()

    assert len(script.encode("utf-8")) < 3000
    for word in FORBIDDEN:
        assert word not in script, word
    assert "document.cookie" not in script
    assert "document.documentElement.lang" in script


# M21 (AC7)


@pytest.mark.parametrize("address", ADDRESSES)
def test_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    """M21: the carousel adds no query."""
    with django_assert_num_queries(1):
        response = client.get(address)

    assert response.status_code == 200
