"""The walk through the house: the drawn plan and the room list of the house chapter.

One-page spec AC16 and AC17 (issue #42), reworked by the house-plan-2d spec (issue #160). The
browser check of the issue shows the plan. These tests pin what the server sends, the service
that lists the rooms, and what the script must hold.
"""

import re
from html import unescape
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import floor_plan, photos

pytestmark = pytest.mark.django_db

SCRIPT = Path(settings.SRC_DIR) / "static" / "js" / "floor-plan.js"
CSS = Path(settings.SRC_DIR) / "static" / "css" / "chapters" / "house.css"
CAPTION = "A hand sketch of the 6 × 18 m plan, not the architect's drawing."
BLOCKS = [
    "Front garden",
    "Kitchen",
    "Bathroom",
    "Laundry and drying",
    "Bedroom 1",
    "Bedroom 2",
    "Back garden",
]


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _house(client: Client) -> str:
    match = re.search(r'<section id="house"[^>]*>.*?</section>', _home(client), re.S)
    assert match, "no section #house"
    return match.group(0)


def _plan(html: str) -> str:
    match = re.search(
        r'<figure id="floor-plan".*</figure>(?=\s*<script src="/static/js/floor-plan.js")',
        html,
        re.S,
    )
    assert match, 'no figure id="floor-plan"'
    return match.group(0)


def _blocks(plan: str) -> list[str]:
    """The name of each room of the list, in page order."""
    rooms = re.search(r'<ol class="plan__rooms">(.*?)</ol>', plan, re.S)
    assert rooms, "no list of rooms"
    names = re.findall(r'<h4 class="plan-room__name">(.*?)</h4>', rooms.group(1), re.S)
    return [_text(name) for name in names]


# AC1


def test_plan_comes_after_the_included_line_in_the_house_chapter(client: Client) -> None:
    house = _house(client)

    assert house.index('class="house__included reveal"') < house.index('id="floor-plan"')


def test_plan_has_its_heading_chip_and_caption(client: Client) -> None:
    plan = _plan(_house(client))

    heading = re.search(r"<h3\b[^>]*>(.*?)</h3>", plan, re.S)
    assert heading
    assert _text(heading.group(1)) == "Walk through the house"
    assert '<span class="media__chip plan__chip">Sketch · not to scale</span>' in plan
    caption = re.search(
        r'<figcaption class="media__credit plan__note-line">(.*?)</figcaption>', plan, re.S
    )
    assert caption
    assert _text(caption.group(1)) == CAPTION


def test_plan_shows_the_parts_of_the_house_from_front_to_back(client: Client) -> None:
    assert _blocks(_plan(_house(client))) == BLOCKS


def test_plan_is_drawn_without_an_image_file(client: Client) -> None:
    plan = _plan(_house(client))

    paper = re.search(
        r'<div class="plan__paper">.*?<span class="media__chip plan__chip">', plan, re.S
    )
    assert paper, "no div.plan__paper"
    assert "<img" not in paper.group(0)
    assert "url(" not in CSS.read_text(encoding="utf-8")


def test_plan_claims_no_floor_or_wall(client: Client) -> None:
    words = _text(_plan(_house(client))).lower()

    for claim in ("floor", "upstairs", "downstairs", "storey", "wall", "north", "south"):
        assert claim not in words, claim


def test_plan_runs_across_the_chapter_on_wide_screens() -> None:
    css = CSS.read_text(encoding="utf-8")

    rule = re.search(r"\.house__plan\s*\{([^}]*)\}", css)
    assert rule, "no .house__plan rule"
    assert re.search(r"grid-column:\s*1\s*/\s*-1", rule.group(1))
    assert "100vw" not in css


# AC2


def test_a_missing_photo_file_gives_its_room_the_empty_block(
    client: Client, mocker: MockerFixture
) -> None:
    real = photos.photo
    mocker.patch.object(
        photos, "photo", side_effect=lambda key: None if key == "kitchen" else real(key)
    )

    plan = _plan(_house(client))

    item = re.search(r'<li class="plan-room" id="room-kitchen".*?</li>', plan, re.S)
    assert item
    assert "plan-room__box--empty" in item.group(0)
    assert "No photo of this room yet" in item.group(0)
    assert plan.count('href="#room-kitchen"') == 2


def test_service_lists_the_blocks_with_their_photos() -> None:
    rooms = floor_plan.rooms()
    expected = {
        "Kitchen": "kitchen",
        "Bedroom 1": "bedroom",
        "Bedroom 2": "bedroom",
        "Back garden": "garden-evening",
    }

    assert [room.name for room in rooms] == BLOCKS
    for room in rooms:
        assert (room.photo.key if room.photo else None) == expected.get(room.name), room.name


def test_service_drops_the_photo_of_a_missing_file(mocker: MockerFixture) -> None:
    mocker.patch.object(photos, "photo", return_value=None)

    assert all(room.photo is None for room in floor_plan.rooms())


def test_page_loads_the_floor_plan_script_deferred(client: Client) -> None:
    html = _home(client)

    assert '<script src="/static/js/floor-plan.js" defer></script>' in html


def test_script_is_plain_and_opens_a_room() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert len(script.encode()) < 4_000
    for sign in ("import ", "require(", "http://", "https://", "jQuery", "eval(", "innerHTML"):
        assert sign not in script, sign
    assert '"use strict"' in script
    assert "plan__room" in script
    assert "preventDefault" in script
    assert "floor-plan" in script


# AC3


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
