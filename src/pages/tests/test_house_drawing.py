"""The walk through the house as a hand-drawn plan (house-plan-2d spec, task T1, issue #160).

The row names (M1 to M12b, M20) are those of the "Test matrix rows" of the issue. M4 is n/a, M6
and the screenshot half of M7 are browser checks, M22 is the whole suite. These tests pin what the
server sends, the room service, the drawing's markup and the CSS rules the layout relies on.
"""

import re
from html import unescape
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import floor_plan, photos
from pages.texts import house as house_texts

pytestmark = pytest.mark.django_db

CSS = Path(settings.SRC_DIR) / "static" / "css" / "chapters" / "house.css"

KEYS = [
    "front-garden",
    "kitchen",
    "bathroom",
    "laundry",
    "bedroom-1",
    "bedroom-2",
    "back-garden",
]
KINDS = ["garden", "room", "wet", "wet", "room", "room", "garden"]
SHAPES = [
    ((0, 0), (90, 0), (90, 35), (0, 35)),
    ((0, 35), (90, 35), (90, 60), (0, 60)),
    ((90, 0), (112, 0), (112, 25), (90, 25)),
    ((90, 35), (112, 35), (112, 60), (90, 60)),
    ((112, 0), (180, 0), (180, 15), (168, 30), (112, 30)),
    ((112, 30), (168, 30), (145, 60), (112, 60)),
    ((180, 15), (180, 60), (145, 60)),
]
PHOTO_KEYS = [None, "kitchen", None, None, "bedroom", "bedroom", "garden-evening"]
EN_NAMES = [
    "Front garden",
    "Kitchen",
    "Bathroom",
    "Laundry and drying",
    "Bedroom 1",
    "Bedroom 2",
    "Back garden",
]
VI_NAMES = [
    "Vườn trước",
    "Bếp",
    "Phòng vệ sinh",
    "Giặt và phơi",
    "Phòng ngủ 1",
    "Phòng ngủ 2",
    "Vườn sau",
]
EN_TEXTS = [
    "The way in from the gate: a garden 3.5 m wide and 9 m deep, beside the kitchen.",
    "A long kitchen, 2.5 m wide and 9 m deep, along the garden: a real kitchen for everyday "
    "cooking and a table to eat together.",
    "The bathroom, off the corridor that leads to the two bedrooms.",
    "A corner to wash and dry clothes, across the corridor from the bathroom.",
    "A calm bedroom at the back of the house, away from the gate.",
    "The second bedroom, next to the first, opening onto the back garden.",
    "A small triangle of garden at the back corner, easy to look after. Garden care once a week "
    "is included.",
]
VI_TEXTS = [
    "Lối vào từ cổng: khu vườn rộng 3,5 m, sâu 9 m, nằm cạnh gian bếp.",
    "Gian bếp dài, rộng 2,5 m, sâu 9 m, chạy dọc khu vườn: bếp thật để nấu mỗi ngày và bàn để "
    "cùng ăn.",
    "Phòng vệ sinh, mở ra hành lang dẫn vào hai phòng ngủ.",
    "Góc giặt và phơi đồ, đối diện phòng vệ sinh qua hành lang.",
    "Phòng ngủ yên tĩnh ở phía sau nhà, xa cổng.",
    "Phòng ngủ thứ hai, cạnh phòng thứ nhất, nhìn ra vườn sau.",
    "Mảnh vườn tam giác nhỏ ở góc sau nhà, dễ chăm. Đã bao gồm chăm vườn mỗi tuần một lần.",
]
NO_PHOTO_KEYS = ["front-garden", "bathroom", "laundry"]
REMOVED_KEYS = [
    "layout",
    "layout_bedrooms",
    "layout_bathroom",
    "layout_living",
    "layout_mezzanine",
    "layout_light_well",
    "layout_gardens",
    "layout_veranda",
    "layout_laundry",
    "schematic",
    "schematic_note",
    "dialog_label",
]
LANGS: dict[str, dict[str, Any]] = {
    "en": {
        "path": "/",
        "heading": "Walk through the house",
        "chip": "Sketch · not to scale",
        "note": "A hand sketch of the 6 × 18 m plan, not the architect's drawing.",
        "label": "Plan of the house: tap a room",
        "empty": "No photo of this room yet",
        "names": EN_NAMES,
        "texts": EN_TEXTS,
        "kitchen_count": "02 of 07",
        "included": "Included",
        "removed": ["The layout", "Two bedrooms"],
        "schematic": "Schematic",
    },
    "vi": {
        "path": "/vi/",
        "heading": "Đi một vòng quanh nhà",
        "chip": "Phác thảo · không theo tỉ lệ",
        "note": "Phác tay mặt bằng 6 × 18 m, chưa phải bản vẽ của kiến trúc sư.",
        "label": "Mặt bằng căn nhà: chạm vào một phòng",
        "empty": "Chưa có ảnh phòng này",
        "names": VI_NAMES,
        "texts": VI_TEXTS,
        "kitchen_count": "02 / 07",
        "included": "Đã bao gồm",
        "removed": ["Bố cục", "Hai phòng ngủ"],
        "schematic": "Sơ đồ",
    },
}
BOTH = pytest.mark.parametrize("lang", ["en", "vi"])


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _house(client: Client, path: str = "/") -> str:
    match = re.search(r'<section id="house"[^>]*>.*?</section>', _get(client, path), re.S)
    assert match, "no section #house"
    return match.group(0)


def _plan(html: str) -> str:
    match = re.search(
        r'<figure id="floor-plan".*</figure>(?=\s*<script src="/static/js/floor-plan.js")',
        html,
        re.S,
    )
    assert match, 'no figure id="floor-plan" before the floor-plan script'
    return match.group(0)


def _svg(plan: str, orient: str) -> str:
    match = re.search(rf'<svg class="plan__svg plan__svg--{orient}"[^>]*>.*?</svg>', plan, re.S)
    assert match, f"no svg.plan__svg--{orient}"
    return match.group(0)


def _links(svg: str) -> list[str]:
    return re.findall(r'<a class="plan__room"[^>]*>.*?</a>', svg, re.S)


def _items(plan: str) -> list[str]:
    ol = re.search(r'<ol class="plan__rooms">(.*)</ol>', plan, re.S)
    assert ol, "no ol.plan__rooms"
    return re.findall(r'<li class="plan-room"[^>]*>.*?</li>', ol.group(1), re.S)


def _item(plan: str, key: str) -> str:
    for item in _items(plan):
        if f'id="room-{key}"' in item:
            return item
    raise AssertionError(f"no li#room-{key}")


def _bbox(points: str) -> tuple[float, float]:
    pairs = [tuple(float(n) for n in pair.split(",")) for pair in points.split()]
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    return max(xs) - min(xs), max(ys) - min(ys)


# M1: the seven rooms (AC1)


def test_m1_rooms_come_in_walking_order_with_kind_shape_name_and_text_in_english() -> None:
    rooms = floor_plan.rooms()

    assert [room.key for room in rooms] == KEYS
    assert [room.kind for room in rooms] == KINDS
    assert [tuple(tuple(point) for point in room.shape) for room in rooms] == SHAPES
    assert [room.name for room in rooms] == EN_NAMES
    assert [room.text for room in rooms] == EN_TEXTS
    assert [room.photo.key if room.photo else None for room in rooms] == PHOTO_KEYS
    assert [room.name for room in floor_plan.rooms("en")] == EN_NAMES


def test_m1_rooms_come_with_vietnamese_names_and_texts_for_vi() -> None:
    rooms = floor_plan.rooms(language="vi")

    assert [room.key for room in rooms] == KEYS
    assert [room.name for room in rooms] == VI_NAMES
    assert [room.text for room in rooms] == VI_TEXTS


def test_m1_plot_is_6_by_18_metres_in_decimetres() -> None:
    assert floor_plan.LENGTH == 180
    assert floor_plan.WIDTH == 60


# M2: rooms without a photo (AC1)


def test_m2_a_missing_bedroom_photo_file_leaves_both_bedrooms_without_a_photo(
    mocker: MockerFixture,
) -> None:
    real = photos.photo
    mocker.patch.object(
        photos, "photo", side_effect=lambda key: None if key == "bedroom" else real(key)
    )

    by_key = {room.key: room for room in floor_plan.rooms()}

    assert by_key["bedroom-1"].photo is None
    assert by_key["bedroom-2"].photo is None
    assert by_key["kitchen"].photo is not None


def test_m2_front_garden_bathroom_and_laundry_never_have_a_photo() -> None:
    by_key = {room.key: room for room in floor_plan.rooms()}

    for key in NO_PHOTO_KEYS:
        assert by_key[key].photo is None, key


def test_m2_no_photo_file_at_all_leaves_every_room_without_a_photo(mocker: MockerFixture) -> None:
    mocker.patch.object(photos, "photo", return_value=None)

    assert all(room.photo is None for room in floor_plan.rooms())


# M3: the layout rules of the stylesheet (AC2)


def test_m3_plan_runs_across_the_chapter_width() -> None:
    css = CSS.read_text(encoding="utf-8")

    rule = re.search(r"\.house__plan\s*\{([^}]*)\}", css)
    assert rule, "no .house__plan rule"
    assert re.search(r"grid-column:\s*1\s*/\s*-1", rule.group(1))
    assert re.search(r"grid-row:\s*auto", rule.group(1))


def test_m3_plan_body_has_the_8fr_and_4fr_columns() -> None:
    css = CSS.read_text(encoding="utf-8")

    rule = re.search(r"\.plan__body\s*\{([^}]*)\}", css)
    assert rule, "no .plan__body rule"
    columns = re.search(r"grid-template-columns:([^;]*);", rule.group(1))
    assert columns
    assert re.search(r"\b8fr\b.*\b4fr\b", columns.group(1))


# M5: the drawing (AC3)


def test_m5_each_plan_has_seven_room_links_each_with_one_hit_polygon_and_no_hall_link(
    client: Client,
) -> None:
    plan = _plan(_house(client))

    for orient in ("h", "v"):
        svg = _svg(plan, orient)
        assert plan.count(f"plan__svg--{orient}") == 1
        links = _links(svg)
        assert len(links) == 7
        for link in links:
            assert link.count('class="plan__hit"') == 1
        assert svg.count("<a ") == 7
        assert "#room-hall" not in svg
        assert "hall" in _text(svg)


def test_m5_the_two_washes_are_defined_once_each(client: Client) -> None:
    plan = _plan(_house(client))

    assert plan.count('id="plan-wash"') == 1
    assert plan.count('id="plan-hatch"') == 1
    assert re.search(r'<svg class="plan__defs"[^>]*aria-hidden="true"', plan)


def test_m5_the_section_is_hidden_from_assistive_technology(client: Client) -> None:
    plan = _plan(_house(client))

    assert re.search(r'<svg class="plan__section"[^>]*aria-hidden="true"', plan)


def test_m5_the_paper_holds_no_image(client: Client) -> None:
    plan = _plan(_house(client))

    paper = re.search(
        r'<div class="plan__paper">.*?<span class="media__chip plan__chip">', plan, re.S
    )
    assert paper, "no div.plan__paper"
    assert "<img" not in paper.group(0)
    assert "<svg" in paper.group(0)


def test_m5_two_renders_give_the_same_plan(client: Client) -> None:
    assert _plan(_house(client)) == _plan(_house(client))


# M7: tap areas on a phone (AC4), the unit part


def test_m7_bathroom_and_laundry_tap_areas_are_at_least_44_px_on_a_390_px_phone(
    client: Client,
) -> None:
    svg = _svg(_plan(_house(client)), "v")
    view_box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    assert view_box
    scale = 332 / 394  # card inner width at 390 px over the upright viewBox width
    assert abs(float(view_box.group(1)) - 394) < 1

    for key in ("bathroom", "laundry"):
        link = next(link for link in _links(svg) if f'data-room="{key}"' in link)
        points = re.search(r'<polygon class="plan__hit" points="([^"]+)"', link)
        assert points, key
        width, height = _bbox(points.group(1))
        assert width * scale >= 44, (key, width * scale)
        assert height * scale >= 44, (key, height * scale)


def test_m7_the_upright_plan_shows_on_narrow_screens_and_the_sideways_one_hides() -> None:
    css = CSS.read_text(encoding="utf-8")

    assert re.search(r"\.plan__svg--v\s*\{[^}]*display:\s*none", css)
    start = css.find("@media (max-width: 860px)")
    assert start >= 0, "no rule for 860px or less"
    narrow = css[start:]
    assert re.search(r"\.plan__svg--h\s*\{[^}]*display:\s*none", narrow)
    assert re.search(r"\.plan__svg--v\s*\{[^}]*display:\s*block", narrow)


# M8: the links and the group label (AC6)


@BOTH
def test_m8_each_room_link_goes_to_its_item_with_its_name(client: Client, lang: str) -> None:
    data = LANGS[lang]
    plan = _plan(_house(client, data["path"]))

    for orient in ("h", "v"):
        links = _links(_svg(plan, orient))
        assert len(links) == 7
        for link, key, name in zip(links, KEYS, data["names"], strict=True):
            tag = link.split(">", 1)[0]
            assert f'href="#room-{key}"' in tag
            assert f'data-room="{key}"' in tag
            assert f'aria-label="{name}"' in tag


@BOTH
def test_m8_each_plan_is_a_group_labelled_tap_a_room(client: Client, lang: str) -> None:
    data = LANGS[lang]
    plan = _plan(_house(client, data["path"]))

    for orient in ("h", "v"):
        tag = _svg(plan, orient).split(">", 1)[0]
        assert 'role="group"' in tag
        assert f'aria-label="{data["label"]}"' in tag


# M9: heading, chip and caption (AC5)


@BOTH
def test_m9_heading_chip_and_caption(client: Client, lang: str) -> None:
    data = LANGS[lang]
    plan = _plan(_house(client, data["path"]))

    heading = re.search(r'<h3 id="floor-plan-heading"[^>]*>(.*?)</h3>', plan, re.S)
    assert heading
    assert _text(heading.group(1)) == data["heading"]
    chip = re.search(r'<span class="media__chip plan__chip">(.*?)</span>', plan, re.S)
    assert chip
    assert _text(chip.group(1)) == data["chip"]
    note = re.search(
        r'<figcaption class="media__credit plan__note-line">(.*?)</figcaption>', plan, re.S
    )
    assert note
    assert _text(note.group(1)) == data["note"]


@BOTH
def test_m9_page_has_no_schematic_word(client: Client, lang: str) -> None:
    data = LANGS[lang]

    assert data["schematic"] not in _text(_house(client, data["path"]))


# M10: the room list (AC7)


@BOTH
def test_m10_room_list_has_seven_items_in_order(client: Client, lang: str) -> None:
    data = LANGS[lang]
    plan = _plan(_house(client, data["path"]))

    items = _items(plan)
    assert len(items) == 7
    for item, key, name, text in zip(items, KEYS, data["names"], data["texts"], strict=True):
        assert f'id="room-{key}"' in item
        assert f'data-room="{key}"' in item
        assert 'tabindex="-1"' in item
        name_tag = re.search(r'<h4 class="plan-room__name">(.*?)</h4>', item, re.S)
        assert name_tag
        assert _text(name_tag.group(1)) == name
        body = re.search(r'<p class="plan-room__text">(.*?)</p>', item, re.S)
        assert body
        assert _text(body.group(1)) == text


@BOTH
def test_m10_each_item_is_numbered_out_of_seven(client: Client, lang: str) -> None:
    data = LANGS[lang]
    plan = _plan(_house(client, data["path"]))
    word = "of" if lang == "en" else "/"

    for number, item in enumerate(_items(plan), 1):
        count = re.search(r'<p class="label muted plan-room__count">(.*?)</p>', item, re.S)
        assert count
        assert _text(count.group(1)) == f"{number:02d} {word} 07"
    kitchen = re.search(
        r'<p class="label muted plan-room__count">(.*?)</p>', _item(plan, "kitchen"), re.S
    )
    assert kitchen
    assert _text(kitchen.group(1)) == data["kitchen_count"]


@BOTH
def test_m10_kitchen_shows_its_photo_chip_and_credit(client: Client, lang: str) -> None:
    plan = _plan(_house(client, LANGS[lang]["path"]))
    kitchen = _item(plan, "kitchen")
    entry = photos.PHOTOS["kitchen"]

    assert '<figure class="media plan-room__media">' in kitchen
    assert '<div class="media__box plan-room__box">' in kitchen
    image = re.search(r"<img [^>]*>", kitchen)
    assert image
    assert f'src="/static/{entry.path}"' in image.group(0)
    assert 'loading="lazy"' in image.group(0)
    assert f'width="{entry.width}"' in image.group(0)
    assert f'height="{entry.height}"' in image.group(0)
    chip = "Illustrative photo" if lang == "en" else "Ảnh minh hoạ"
    assert f'<span class="media__chip">{chip}</span>' in kitchen
    credit = re.search(r'<figcaption class="media__credit">(.*?)</figcaption>', kitchen, re.S)
    assert credit
    assert _text(credit.group(1)) == ("Photo: Pexels" if lang == "en" else "Ảnh: Pexels")
    alt = entry.alt if lang == "en" else entry.alt_vi
    assert f'alt="{alt}"' in image.group(0)


# M11: rooms without a photo (AC8)


@BOTH
@pytest.mark.parametrize("key", NO_PHOTO_KEYS)
def test_m11_room_without_a_photo_shows_the_sand_block_with_o_and_the_caption(
    client: Client, lang: str, key: str
) -> None:
    empty = LANGS[lang]["empty"]
    item = _item(_plan(_house(client, LANGS[lang]["path"])), key)

    assert '<div class="media__box plan-room__box plan-room__box--empty">' in item
    assert "role=" not in item
    assert re.search(r'<span class="plan-room__mark" aria-hidden="true">Ở</span>', item)
    credit = re.search(r'<figcaption class="media__credit">(.*?)</figcaption>', item, re.S)
    assert credit
    assert _text(credit.group(1)) == empty
    assert "<img" not in item


def test_m11_a_room_whose_photo_file_is_missing_shows_the_sand_block(
    client: Client, mocker: MockerFixture
) -> None:
    real = photos.photo
    mocker.patch.object(
        photos, "photo", side_effect=lambda key: None if key == "kitchen" else real(key)
    )

    plan = _plan(_house(client))

    kitchen = _item(plan, "kitchen")
    assert "plan-room__box--empty" in kitchen
    assert "No photo of this room yet" in kitchen
    assert len(_links(_svg(plan, "h"))) == 7


# M12: nothing of the old dialog is left (AC9)


def test_m12_no_dialog_and_no_photo_link_inside_the_plan(client: Client) -> None:
    html = _get(client, "/")
    plan = _plan(html)

    assert "<dialog" not in plan
    assert "floor-plan__dialog" not in html
    assert 'href="/static/media/photos/' not in plan
    assert not re.search(r'\bdata-(?:alt|credit|width|height)="', plan)


def test_m12_figure_keeps_its_id_and_the_script_is_linked_once_with_defer(client: Client) -> None:
    html = _get(client, "/")

    assert html.count('id="floor-plan"') == 1
    assert html.count("js/floor-plan.js") == 1
    assert '<script src="/static/js/floor-plan.js" defer></script>' in html


# M12b: the layout list and its texts are gone (AC9)


@BOTH
def test_m12b_house_chapter_has_no_layout_list_but_keeps_included(
    client: Client, lang: str
) -> None:
    data = LANGS[lang]
    house = _house(client, data["path"])
    text = _text(house)

    assert "house__layout" not in house
    for word in data["removed"]:
        assert word not in text, word
    included = re.search(r'<div class="house__included[^"]*"[^>]*>(.*?)</div>', house, re.S)
    assert included
    assert _text(included.group(1)).startswith(data["included"])


@pytest.mark.parametrize("key", REMOVED_KEYS)
def test_m12b_removed_text_keys_are_gone_in_both_languages(key: str) -> None:
    assert key not in house_texts.EN
    assert key not in house_texts.VI


def test_m12b_texts_keep_the_same_keys_in_both_languages() -> None:
    assert set(house_texts.EN) == set(house_texts.VI)


# M20: the query budget (AC10)


@pytest.mark.parametrize("address", ["/", "/vi/"])
def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(1):
        _get(client, address)
