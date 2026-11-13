"""The house chapter: owner line, room collage and facts row (design-match T4, spec AC18 to AC21;
design.md, "01 ở nhà")."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

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
# key, columns (first / last), height, shift (positive: lower, negative: higher), label
COLLAGE = [
    ("bedroom", 1, 5, 620, 0, "Bedrooms · two"),
    ("lightwell", 6, 9, 460, 160, "Light well"),
    ("veranda", 10, 12, 340, 60, "Veranda"),
    ("kitchen", 2, 6, 380, 0, "Living & kitchen"),
    ("garden-evening", 8, 12, 460, -120, "Back garden"),
]
FACTS = [
    ("2", "bedrooms"),
    ("2", "gardens"),
    ("1", "light well"),
    ("1", "household at a time"),
]


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


def _collage(html: str) -> str:
    match = re.search(r'<ul class="house__collage">.*?</ul>', html, re.S)
    assert match, "no .house__collage"
    return match.group(0)


def _rooms(html: str) -> list[str]:
    return re.findall(r"<li\b[^>]*>.*?</li>", _collage(html), re.S)


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _desktop_css() -> str:
    return _css().split("@media (max-width: 760px)")[0]


def _narrow_css() -> str:
    narrow = re.search(r"@media \(max-width: 760px\)\s*\{(.*)\}\s*$", _css(), re.S)
    assert narrow, "no rule for 760px or less"
    return narrow.group(1)


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no rule {selector}"
    return match.group(1)


# AC1


def test_owner_line_sits_beside_the_head_with_its_accent(client: Client) -> None:
    house = _house(client)

    line = _block(house, "house__owner quote reveal")
    assert _text(line).endswith(OWNER_LINE)
    assert '<span class="accent">home for a while.</span>' in line
    assert house.index("<h2") < house.index('class="house__owner') < house.index("house__why")
    intro = _rule(_desktop_css(), ".house__intro")
    assert re.search(r"grid-column:\s*8\s*/\s*span 5", intro)
    assert re.search(r"align-self:\s*end", intro)


def test_chapter_parts_come_in_order(client: Client) -> None:
    house = _house(client)

    parts = [
        'class="chapter-marker',
        'class="house__owner',
        'class="house__why',
        'class="house__collage"',
        'class="house__facts',
        'class="house__layout',
        'class="house__included',
        'id="floor-plan"',
    ]
    positions = [house.index(part) for part in parts]
    assert positions == sorted(positions)
    assert _text(_block(house, "house__why reveal")) == WHY


# AC2


def test_collage_holds_the_five_rooms_with_their_labels(client: Client) -> None:
    rooms = _rooms(_house(client))

    assert len(rooms) == len(COLLAGE)
    for room, (key, *_, label) in zip(rooms, COLLAGE, strict=True):
        assert f'src="/static/media/photos/{key}.jpg"' in room
        caption = re.search(r'<p class="house__room-label label">(.*?)</p>', room, re.S)
        assert caption, f"no label for {key}"
        assert _text(caption.group(1)) == label
        assert room.index('class="media"') < room.index("house__room-label")


def test_collage_is_a_12_column_grid_with_18px_gaps() -> None:
    collage = _rule(_desktop_css(), ".house__collage")

    assert re.search(r"grid-template-columns:\s*repeat\(12,", collage)
    assert re.search(r"gap:\s*18px", collage)


@pytest.mark.parametrize(("key", "first", "last", "height", "shift", "label"), COLLAGE)
def test_each_room_has_its_columns_height_and_shift(
    key: str, first: int, last: int, height: int, shift: int, label: str
) -> None:
    css = _desktop_css()
    room = _rule(css, f".house__room--{key}")

    assert re.search(rf"grid-column:\s*{first}\s*/\s*{last + 1}\b", room)
    if shift:
        assert re.search(rf"margin-top:\s*{shift}px", room)
    else:
        assert "margin-top" not in room
    box = _rule(css, f".house__room--{key} .media__box")
    assert re.search(rf"height:\s*{height}px", box)


def test_room_label_uses_the_11px_capitals_of_the_site_label(client: Client) -> None:
    """The site draws its 11px capitals with the class `label` (small capitals in site.css)."""
    site = (settings.SRC_DIR / "static" / "css" / "site.css").read_text(encoding="utf-8")

    assert re.search(r"--size-label:\s*11px", site)
    assert all('class="house__room-label label"' in room for room in _rooms(_house(client)))
    assert "font-size" not in _rule(_desktop_css(), ".house__room-label")


# AC3


def test_facts_row_shows_four_numbers_over_labels(client: Client) -> None:
    facts = _block(_house(client), "house__facts reveal")

    pairs = re.findall(
        r'<li>\s*<span class="house__fact-number">(.*?)</span>\s*'
        r'<span class="house__fact-label">(.*?)</span>\s*</li>',
        facts,
        re.S,
    )
    assert [(_text(number), _text(label)) for number, label in pairs] == FACTS


def test_facts_row_has_an_ink_rule_four_columns_and_80px_numbers() -> None:
    css = _desktop_css()

    facts = _rule(css, ".house__facts")
    assert re.search(r"border-top:\s*1px solid var\(--ink\)", facts)
    assert re.search(r"grid-template-columns:\s*repeat\(4,", facts)
    number = _rule(css, ".house__fact-number")
    assert re.search(r"font-family:\s*var\(--font-serif\)", number)
    assert re.search(r"font-size:\s*80px", number)


# AC4


def test_points_veranda_slot_and_mezzanine_photo_are_gone(client: Client) -> None:
    house = _house(client)

    assert "house__points" not in house
    assert "house__veranda" not in house
    assert "house__gallery" not in house
    assert "/static/media/photos/mezzanine.jpg" not in _collage(house)
    photos_before_plan = house[: house.index('id="floor-plan"')]
    assert "mezzanine.jpg" not in photos_before_plan
    assert "A private garden and a covered veranda" not in house


# AC5


def test_collage_scrolls_sideways_in_cards_on_narrow_screens() -> None:
    narrow = _narrow_css()

    collage = _rule(narrow, ".house__collage")
    assert re.search(r"overflow-x:\s*auto", collage)
    assert re.search(r"scroll-snap-type:\s*x mandatory", collage)
    assert re.search(r"max-width:\s*100%", collage)
    room = _rule(narrow, ".house__room")
    assert re.search(r"240px", room)
    assert re.search(r"margin-top:\s*0", room)
    assert re.search(r"scroll-snap-align:\s*start", room)
    box = _rule(narrow, ".house__room .media__box")
    assert re.search(r"height:\s*320px", box)


def test_facts_row_has_two_columns_and_56px_numbers_on_narrow_screens() -> None:
    narrow = _narrow_css()

    assert re.search(r"grid-template-columns:\s*repeat\(2,", _rule(narrow, ".house__facts"))
    assert re.search(r"font-size:\s*56px", _rule(narrow, ".house__fact-number"))


def test_nothing_is_wider_than_the_screen() -> None:
    assert "100vw" not in _css()


# AC6


def test_blocks_of_the_chapter_carry_reveal(client: Client) -> None:
    house = _house(client)

    for css_class in (
        "house__owner quote reveal",
        "house__why reveal",
        "house__facts reveal",
        "house__layout reveal",
        "house__included reveal",
    ):
        assert f'class="{css_class}"' in house, css_class
    for room in _rooms(house):
        assert re.match(r'<li class="house__room house__room--[\w-]+ reveal"', room)
    assert re.search(r'<figure id="floor-plan" class="[^"]*\breveal\b', house)


# AC7


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _house(client)
