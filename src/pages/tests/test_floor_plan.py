"""The walk through the house: the schematic floor plan of the house chapter.

One-page spec AC16 and AC17 (issue #42: AC1 and AC2). The dialog itself opens in a browser; the
browser check of the issue shows the plan. These tests pin what the server sends, the service
that lists the blocks, and what the script must hold.
"""

import re
from html import unescape
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from django.utils.html import escape
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import floor_plan, photos

pytestmark = pytest.mark.django_db

SCRIPT = Path(settings.SRC_DIR) / "static" / "js" / "floor-plan.js"
CSS = Path(settings.SRC_DIR) / "static" / "css" / "chapters" / "house.css"
CAPTION = "Schematic until the architect's plan: the rooms of the house, not their real layout."
BLOCKS = [
    "Front garden",
    "Living room and kitchen",
    "Light well",
    "Bedroom 1",
    "Bedroom 2",
    "Bathroom",
    "Mezzanine",
    "Covered veranda",
    "Back garden",
    "Laundry, drying and storage",
]
LINKED = {
    "Living room and kitchen": "kitchen",
    "Light well": "lightwell",
    "Bedroom 1": "bedroom",
    "Bedroom 2": "bedroom",
    "Mezzanine": "mezzanine",
    "Covered veranda": "veranda",
}


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
    match = re.search(r'<figure id="floor-plan"[^>]*>.*?</figure>', html, re.S)
    assert match, 'no figure id="floor-plan"'
    return match.group(0)


def _dialog(html: str) -> str:
    match = re.search(r"<dialog\b[^>]*>.*?</dialog>", html, re.S)
    assert match, "no dialog"
    return match.group(0)


def _blocks(plan: str) -> list[tuple[str, str]]:
    """Each block of the plan: its tag (`a` or `span`) and its text, in page order."""
    rooms = re.search(r'<ol class="floor-plan__rooms">(.*?)</ol>', plan, re.S)
    assert rooms, "no list of rooms"
    items = re.findall(r"<li\b[^>]*>(.*?)</li>", rooms.group(1), re.S)
    blocks = []
    for item in items:
        tag = re.match(r"\s*<(\w+)", item)
        assert tag, item
        blocks.append((tag.group(1), _text(item)))
    return blocks


def _links(plan: str) -> dict[str, str]:
    return {
        _text(text): href
        for href, text in re.findall(r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>', plan, re.S)
    }


# AC1


def test_plan_comes_after_the_layout_list_in_the_house_chapter(client: Client) -> None:
    house = _house(client)

    assert house.index('class="house__layout"') < house.index('id="floor-plan"')


def test_plan_has_its_heading_chip_and_caption(client: Client) -> None:
    plan = _plan(_house(client))

    heading = re.search(r"<h3\b[^>]*>(.*?)</h3>", plan, re.S)
    assert heading
    assert _text(heading.group(1)) == "Walk through the house"
    assert re.search(r'<span class="media__chip floor-plan__chip">\s*Schematic\s*</span>', plan)
    caption = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", plan, re.S)
    assert caption
    assert _text(caption.group(1)) == CAPTION


def test_plan_shows_the_parts_of_the_house_from_front_to_back(client: Client) -> None:
    blocks = _blocks(_plan(_house(client)))

    assert [text for _tag, text in blocks] == BLOCKS


def test_plan_is_drawn_without_an_image_file(client: Client) -> None:
    plan = _plan(_house(client))

    assert "<img" not in plan
    assert "<svg" not in plan
    assert "url(" not in plan
    assert "url(" not in CSS.read_text(encoding="utf-8")


def test_plan_claims_no_floor_or_wall(client: Client) -> None:
    words = _text(_plan(_house(client))).lower()

    for claim in ("floor", "upstairs", "downstairs", "storey", "wall", "north", "south"):
        assert claim not in words, claim


def test_plan_sits_beside_the_layout_list_on_wide_screens() -> None:
    css = CSS.read_text(encoding="utf-8")

    rule = re.search(r"\.house__plan\s*\{([^}]*)\}", css)
    assert rule, "no .house__plan rule"
    assert re.search(r"grid-column:\s*7\s*/\s*span 6", rule.group(1))
    assert "100vw" not in css


# AC2


def test_blocks_with_a_photo_link_to_it_and_the_others_do_not(client: Client) -> None:
    plan = _plan(_house(client))

    links = _links(plan)
    assert links == {name: f"/static/{photos.PHOTOS[key].path}" for name, key in LINKED.items()}
    for tag, text in _blocks(plan):
        assert tag == ("a" if text in LINKED else "span"), text


def test_each_link_carries_what_the_dialog_shows(client: Client) -> None:
    plan = _plan(_house(client))

    for name, key in LINKED.items():
        entry = photos.PHOTOS[key]
        link = re.search(rf"<a [^>]*>\s*{re.escape(name)}\s*</a>", plan)
        assert link, name
        tag = link.group(0)
        assert f'data-alt="{escape(entry.alt)}"' in tag
        assert f'data-credit="{escape(entry.credit)}"' in tag
        assert f'data-width="{entry.width}"' in tag
        assert f'data-height="{entry.height}"' in tag
        assert "data-illustrative" in tag
        assert "onclick" not in tag


def test_page_holds_one_closed_dialog_with_chip_credit_and_close_button(client: Client) -> None:
    house = _house(client)

    assert house.count("<dialog") == 1
    dialog = _dialog(house)
    assert " open" not in dialog.split(">", 1)[0]
    assert '<span class="media__chip">Illustrative photo</span>' in dialog
    assert '<figcaption class="media__credit">' in dialog
    assert re.search(r'<form method="dialog">\s*<button[^>]*>Close</button>\s*</form>', dialog)
    # The photo is placed by the script: without one the page sends no extra image.
    assert "<img" not in dialog


def test_a_missing_photo_file_leaves_its_block_without_a_link(
    client: Client, mocker: MockerFixture
) -> None:
    real = photos.photo
    mocker.patch.object(
        photos, "photo", side_effect=lambda key: None if key == "kitchen" else real(key)
    )

    plan = _plan(_house(client))

    assert "Living room and kitchen" not in _links(plan)
    assert ("span", "Living room and kitchen") in _blocks(plan)


def test_service_lists_the_blocks_with_their_photos() -> None:
    blocks = floor_plan.blocks()

    assert [block.name for block in blocks] == BLOCKS
    for block in blocks:
        expected = LINKED.get(block.name)
        assert (block.photo.key if block.photo else None) == expected, block.name


def test_service_drops_the_photo_of_a_missing_file(mocker: MockerFixture) -> None:
    mocker.patch.object(photos, "photo", return_value=None)

    assert all(block.photo is None for block in floor_plan.blocks())


def test_page_loads_the_floor_plan_script_deferred(client: Client) -> None:
    html = _home(client)

    assert '<script src="/static/js/floor-plan.js" defer></script>' in html


def test_script_is_plain_and_opens_the_photo_in_the_dialog() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert len(script.encode()) < 6_000
    for sign in ("import ", "require(", "http://", "https://", "jQuery", "eval(", "innerHTML"):
        assert sign not in script, sign
    assert '"use strict"' in script
    assert "showModal" in script
    assert "preventDefault" in script
    assert "floor-plan" in script


# AC3


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
