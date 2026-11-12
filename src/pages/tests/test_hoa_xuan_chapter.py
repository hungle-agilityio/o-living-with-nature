"""The Hòa Xuân chapter of the one page (one-page spec AC14; design.md, "Hòa Xuân")."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import photos

pytestmark = pytest.mark.django_db

CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "hoa_xuan.css"
SITE_CSS = settings.SRC_DIR / "static" / "css" / "site.css"
LINE = "Everything you need day to day is close by."
TRAVEL = [
    "Supermarket · across the road",
    "Market · about 10 min",
    "Beach · about 10 min",
    "Airport · about 15 min",
]
PHOTOS = ["market", "street", "beach-sunset"]
MAPS_TEXT = "Hòa Xuân on Google Maps ↗"
MAPS_URL = (
    "https://www.google.com/maps/search/?api=1&query="
    "H%C3%B2a%20Xu%C3%A2n%2C%20%C4%90%C3%A0%20N%E1%BA%B5ng"
)
REDUCED_MOTION_OFF = 'media="(prefers-reduced-motion: no-preference)"'


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _chapter(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    match = re.search(r'<section id="hoa-xuan"[^>]*>.*?</section>', response.content.decode(), re.S)
    assert match, "no section #hoa-xuan"
    return match.group(0)


def _block(html: str, css_class: str) -> str:
    match = re.search(rf'<(\w+) class="{css_class}"[^>]*>.*?</\1>', html, re.S)
    assert match, f"no .{css_class}"
    return match.group(0)


def _loop(html: str) -> str:
    # The slot is one <figure>; its box is a nested <div>, so the block ends at </figure>.
    match = re.search(r'<div class="hoa-xuan__loop">.*?</figure>', html, re.S)
    assert match, "no .hoa-xuan__loop"
    return match.group(0)


# AC1: the area loop


def test_area_loop_is_a_16_by_9_video_of_the_area_files(client: Client) -> None:
    loop = _loop(_chapter(client))

    assert loop.count("<video") == 1
    assert "aspect-ratio: 16 / 9" in loop
    assert '<source src="/static/media/area/area.webm" type="video/webm"' in loop
    assert '<source src="/static/media/area/area.mp4" type="video/mp4"' in loop
    assert 'poster="/static/media/area/area.jpg"' in loop
    assert f'aria-label="{photos.AREA_LOOP.label}"' in loop


def test_area_loop_shows_the_chip_and_the_credit(client: Client) -> None:
    loop = _loop(_chapter(client))

    assert _text(_block(loop, "media__chip")) == "Illustrative video"
    assert _text(_block(loop, "media__credit")) == photos.AREA_LOOP.credit


def test_area_loop_shows_only_its_poster_under_reduced_motion(client: Client) -> None:
    loop = _loop(_chapter(client))

    # The sources play only when motion is fine; the poster photo stands in otherwise.
    assert loop.count("<source") == 2
    assert loop.count(REDUCED_MOTION_OFF) == 2
    assert re.search(r'<img class="media__poster" src="/static/media/area/area\.jpg"', loop)
    reduce = SITE_CSS.read_text(encoding="utf-8").split("(prefers-reduced-motion: reduce)", 1)[1]
    assert re.search(r"\.media video\s*\{\s*display:\s*none", reduce)
    assert re.search(r"\.media__poster\s*\{\s*display:\s*block", reduce)


def test_area_loop_shows_the_empty_state_when_a_file_is_missing(
    client: Client, mocker: MockerFixture
) -> None:
    mocker.patch("pages.photos.area_loop", return_value=None)

    loop = _loop(_chapter(client))

    assert "<video" not in loop
    assert "media--empty" in loop
    assert "aspect-ratio: 16 / 9" in loop


# AC1: the line, the travel list and the link


def test_line_is_shown_as_written(client: Client) -> None:
    assert _text(_block(_chapter(client), "hoa-xuan__line quote")) == LINE


def test_travel_list_holds_the_four_places_in_order(client: Client) -> None:
    travel = _block(_chapter(client), "hoa-xuan__travel")

    assert travel.startswith("<ul")
    items = re.findall(r"<li>(.*?)</li>", travel, re.S)
    assert [_text(item) for item in items] == TRAVEL


def test_maps_link_opens_google_maps_in_a_new_tab(client: Client) -> None:
    chapter = _chapter(client)

    links = re.findall(r"<a [^>]*>.*?</a>", chapter, re.S)
    maps = [link for link in links if MAPS_TEXT in _text(link)]
    assert len(maps) == 1
    link = maps[0]
    assert f'href="{MAPS_URL}"' in link.replace("&amp;", "&")
    assert 'target="_blank"' in link
    rel = re.search(r'rel="([^"]*)"', link)
    assert rel and "noopener" in rel.group(1).split()


def test_no_map_is_embedded(client: Client) -> None:
    chapter = _chapter(client)

    assert "<iframe" not in chapter
    assert "<embed" not in chapter
    assert "<object" not in chapter


# AC1: the three photos


def test_three_area_photos_in_order(client: Client) -> None:
    gallery = _block(_chapter(client), "hoa-xuan__photos")

    paths = re.findall(r'<img src="/static/media/photos/([\w-]+)\.jpg"', gallery)
    assert paths == PHOTOS
    assert gallery.count("aspect-ratio: 4 / 3") == 3
    assert gallery.count("Illustrative photo") == 3
    for key in PHOTOS:
        assert f'alt="{photos.PHOTOS[key].alt}"' in gallery


def test_texts_come_in_the_order_of_the_design(client: Client) -> None:
    text = _text(_chapter(client))

    order = ["Illustrative video", LINE, TRAVEL[0], TRAVEL[-1], MAPS_TEXT]
    positions = [text.index(part) for part in order]
    assert positions == sorted(positions)


def test_chapter_is_one_column_on_narrow_screens() -> None:
    css = CSS.read_text(encoding="utf-8")

    narrow = re.search(r"@media \(max-width: 760px\)\s*\{(.*)\}\s*$", css, re.S)
    assert narrow, "no rule for 760px or less"
    assert re.search(r"grid-template-columns:\s*minmax\(0, 1fr\)", narrow.group(1))
    assert "100vw" not in css


# AC2


def test_hoa_xuan_chapter_adds_no_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _chapter(client)
