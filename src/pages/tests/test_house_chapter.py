"""The house chapter of the one page (one-page spec AC13; design.md, "The house")."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from pages import photos

pytestmark = pytest.mark.django_db

CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "house.css"
OWNER_LINE = (
    "I built a small garden house in Hòa Xuân, and I'd love for someone to make it home "
    "for a while."
)
WHY = (
    "I wanted a house that feels good to live in every day, not just in photos: a little "
    "garden, morning light, a veranda to sit on. Ở is that house."
)
POINTS = [
    ("01", "A private garden and a covered veranda"),
    ("02", "Light and air through a light well"),
    ("03", "Live like at home, for a month or more"),
]
LAYOUT = [
    "Two bedrooms",
    "One bathroom",
    "Living room and kitchen",
    "Mezzanine",
    "Light well",
    "Front and back gardens",
    "Covered veranda",
    "Laundry, drying and storage area",
]
INCLUDED = "Basic furniture. Garden care once a week. Cleaning can be arranged."
GALLERY = ["lightwell", "bedroom", "kitchen", "mezzanine"]


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _house(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    match = re.search(r'<section id="house"[^>]*>.*?</section>', response.content.decode(), re.S)
    assert match, "no section #house"
    return match.group(0)


def _block(html: str, css_class: str) -> str:
    match = re.search(rf'<(\w+) class="{css_class}"[^>]*>.*?</\1>', html, re.S)
    assert match, f"no .{css_class}"
    return match.group(0)


def _photo_paths(html: str) -> list[str]:
    return re.findall(r'<img src="/static/media/photos/([\w-]+)\.jpg"', html)


# AC1


def test_owner_line_starts_with_the_owners_greeting(client: Client) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(owner_first_name="Lan", price_from_million=9)

    line = _block(_house(client), "house__owner quote")

    assert _text(line) == f"Hi, I'm Lan. {OWNER_LINE}"


def test_why_paragraph_is_shown_as_written(client: Client) -> None:
    assert _text(_block(_house(client), "house__why")) == WHY


def test_three_numbered_points_in_order(client: Client) -> None:
    points = _block(_house(client), "house__points")

    assert points.startswith("<ol")
    items = re.findall(r"<li>(.*?)</li>", points, re.S)
    numbers = re.findall(r'<span class="house__number"[^>]*>(.*?)</span>', points)
    assert numbers == [number for number, _ in POINTS]
    assert [_text(item) for item in items] == [f"{number} {text}" for number, text in POINTS]


def test_veranda_photo_comes_before_the_gallery(client: Client) -> None:
    house = _house(client)

    paths = _photo_paths(house)
    assert paths == ["veranda", *GALLERY]
    assert f'alt="{photos.PHOTOS["veranda"].alt}"' in house


def test_gallery_holds_the_four_photos_in_3_by_4(client: Client) -> None:
    gallery = _block(_house(client), "house__gallery")

    assert _photo_paths(gallery) == GALLERY
    assert gallery.count("aspect-ratio: 3 / 4") == 4
    assert gallery.count("Illustrative photo") == 4


def test_gallery_scrolls_sideways_inside_its_box_on_narrow_screens() -> None:
    css = CSS.read_text(encoding="utf-8")

    narrow = re.search(r"@media \(max-width: 760px\)\s*\{(.*)\}\s*$", css, re.S)
    assert narrow, "no rule for 760px or less"
    gallery = re.search(r"\.house__gallery\s*\{([^}]*)\}", narrow.group(1))
    assert gallery, "no gallery rule at 760px or less"
    assert re.search(r"overflow-x:\s*auto", gallery.group(1))
    assert re.search(r"grid-auto-columns:\s*240px", gallery.group(1))
    assert "100vw" not in css


def test_layout_list_has_its_label_and_eight_lines(client: Client) -> None:
    layout = _block(_house(client), "house__layout")

    assert _text(_block(layout, "label muted")) == "The layout"
    assert [_text(item) for item in re.findall(r"<li>(.*?)</li>", layout, re.S)] == LAYOUT


def test_included_line_has_its_label(client: Client) -> None:
    included = _block(_house(client), "house__included")

    assert _text(_block(included, "label muted")) == "Included"
    assert _text(included) == f"Included {INCLUDED}"


def test_texts_come_in_the_order_of_the_design(client: Client) -> None:
    text = _text(_house(client))

    order = [OWNER_LINE, WHY, POINTS[0][1], "The layout", LAYOUT[-1], INCLUDED]
    positions = [text.index(part) for part in order]
    assert positions == sorted(positions)


# AC2


def test_house_chapter_adds_no_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _house(client)
