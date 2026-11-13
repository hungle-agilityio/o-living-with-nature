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
FACTS = [
    ("2", "bedrooms"),
    ("2", "gardens"),
    ("1", "light well"),
    ("1", "household at a time"),
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
COLLAGE = ["bedroom", "lightwell", "veranda", "kitchen", "garden-evening"]
LABELS = ["Bedrooms · two", "Light well", "Veranda", "Living & kitchen", "Back garden"]


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

    line = _block(_house(client), "house__owner quote reveal")

    assert _text(line) == f"Hi, I'm Lan. {OWNER_LINE}"


def test_why_paragraph_is_shown_as_written(client: Client) -> None:
    assert _text(_block(_house(client), "house__why reveal")) == WHY


def test_facts_row_takes_the_place_of_the_three_points(client: Client) -> None:
    house = _house(client)
    facts = _block(house, "house__facts reveal")

    assert "house__points" not in house
    assert facts.startswith("<ul")
    items = re.findall(r"<li>(.*?)</li>", facts, re.S)
    assert [_text(item) for item in items] == [f"{number} {label}" for number, label in FACTS]


def test_collage_holds_the_five_rooms_in_order(client: Client) -> None:
    house = _house(client)

    assert _photo_paths(house[: house.index('id="floor-plan"')]) == COLLAGE
    assert f'alt="{photos.PHOTOS["veranda"].alt}"' in house


def test_collage_holds_the_five_photos_with_their_labels(client: Client) -> None:
    collage = _block(_house(client), "house__collage")

    assert _photo_paths(collage) == COLLAGE
    labels = re.findall(r'<p class="house__room-label label">(.*?)</p>', collage, re.S)
    assert [_text(label) for label in labels] == LABELS
    assert collage.count("Illustrative photo") == 5


def test_collage_scrolls_sideways_inside_its_box_on_narrow_screens() -> None:
    css = CSS.read_text(encoding="utf-8")

    narrow = re.search(r"@media \(max-width: 760px\)\s*\{(.*)\}\s*$", css, re.S)
    assert narrow, "no rule for 760px or less"
    collage = re.search(r"\.house__collage\s*\{([^}]*)\}", narrow.group(1))
    assert collage, "no collage rule at 760px or less"
    assert re.search(r"overflow-x:\s*auto", collage.group(1))
    assert re.search(r"scroll-snap-type:\s*x mandatory", collage.group(1))
    room = re.search(r"\.house__room\s*\{([^}]*)\}", narrow.group(1))
    assert room, "no card rule at 760px or less"
    assert re.search(r"240px", room.group(1))
    box = re.search(r"\.house__room \.media__box\s*\{([^}]*)\}", narrow.group(1))
    assert box, "no card height at 760px or less"
    assert re.search(r"height:\s*320px", box.group(1))
    assert "100vw" not in css


def test_layout_list_has_its_label_and_eight_lines(client: Client) -> None:
    layout = _block(_house(client), "house__layout reveal")

    assert _text(_block(layout, "label muted")) == "The layout"
    assert [_text(item) for item in re.findall(r"<li>(.*?)</li>", layout, re.S)] == LAYOUT


def test_included_line_has_its_label(client: Client) -> None:
    included = _block(_house(client), "house__included reveal")

    assert _text(_block(included, "label muted")) == "Included"
    assert _text(included) == f"Included {INCLUDED}"


def test_texts_come_in_the_order_of_the_design(client: Client) -> None:
    text = _text(_house(client))

    order = [OWNER_LINE, WHY, f"{FACTS[0][0]} {FACTS[0][1]}", "The layout", LAYOUT[-1], INCLUDED]
    positions = [text.index(part) for part in order]
    assert positions == sorted(positions)


# AC2


def test_house_chapter_adds_no_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _house(client)
