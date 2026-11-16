"""Chapters 01 (the house) and 02 (Hòa Xuân) of `/vi/`, the walk through the house and the
Vietnamese alt texts (vietnamese spec, task T2, issue #105).

The row names (M19 to M24, M33) are those of the "Test matrix rows" of the issue. M22 has no
test (the chapter has no data that can be empty) and M25 is checked by hand.
"""

import re
from html import unescape

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from pages import floor_plan, photos
from pages.templatetags.texts import alt_text

pytestmark = pytest.mark.django_db

GREETING = "Hi, I'm Bún."
MAPS = (
    "https://www.google.com/maps/search/?api=1&query=H%C3%B2a%20Xu%C3%A2n%2C%20"
    "%C4%90%C3%A0%20N%E1%BA%B5ng"
)

VI_OWNER = (
    "Mình đã xây một căn nhà vườn nhỏ ở Hòa Xuân, và rất mong có người đến biến nó thành "
    "nhà của mình một thời gian."
)
VI_WHY = (
    "Mình muốn một căn nhà sống dễ chịu mỗi ngày, chứ không chỉ đẹp trong ảnh: một khoảnh "
    "vườn nhỏ, nắng sớm, một hiên nhà để ngồi. Ở chính là căn nhà ấy."
)
VI_ROOMS = ["Phòng ngủ · hai", "Giếng trời", "Hiên nhà", "Phòng khách & bếp", "Vườn sau"]
VI_FACTS = [
    ("2", "phòng ngủ"),
    ("2", "khoảng vườn"),
    ("1", "giếng trời"),
    ("1", "hộ thuê một lúc"),
]
VI_LAYOUT = [
    "Hai phòng ngủ",
    "Một phòng tắm",
    "Phòng khách và bếp",
    "Gác lửng",
    "Giếng trời",
    "Vườn trước và vườn sau",
    "Hiên có mái che",
    "Khu giặt, phơi và kho",
]
VI_INCLUDED = "Nội thất cơ bản. Chăm vườn mỗi tuần một lần. Có thể sắp xếp người dọn dẹp."
VI_BLOCKS = [
    "Vườn trước",
    "Phòng khách và bếp",
    "Giếng trời",
    "Phòng ngủ 1",
    "Phòng ngủ 2",
    "Phòng tắm",
    "Gác lửng",
    "Hiên có mái che",
    "Vườn sau",
    "Giặt, phơi và kho",
]
EN_BLOCKS = [
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
NO_PHOTO_VI = ["Vườn trước", "Phòng tắm", "Vườn sau", "Giặt, phơi và kho"]
VI_SCHEMATIC_NOTE = (
    "Sơ đồ tạm cho đến khi có bản vẽ của kiến trúc sư: đây là các phòng của căn nhà, "
    "chưa phải cách bố trí thật."
)

# The English texts written in house.html (the greeting is left out, it comes from the owner).
EN_HOUSE_TEXTS = [
    "01 · at home",
    "I built a small garden house in Hòa Xuân, and I'd love for someone to make it",
    "home for a while.",
    "I wanted a house that feels good to live in every day, not just in photos",
    "Bedrooms · two",
    "Light well",
    "Veranda",
    "Living & kitchen",
    "Back garden",
    "bedrooms",
    "gardens",
    "household at a time",
    "The layout",
    "Two bedrooms",
    "One bathroom",
    "Living room and kitchen",
    "Mezzanine",
    "Front and back gardens",
    "Covered veranda",
    "Laundry, drying and storage area",
    "Included",
    "Basic furniture",
    "Garden care once a week",
    "Cleaning can be arranged",
    "Walk through the house",
    "Front garden",
    "Bedroom 1",
    "Bedroom 2",
    "Bathroom",
    "Schematic",
    "Close",
]

EN_HOA_XUAN_TEXTS = [
    "02 · close by",
    "Everything you need day to day is close by.",
    "Supermarket",
    "across the road",
    "Market",
    "about 10 min",
    "Beach",
    "Airport",
    "about 15 min",
    "Hòa Xuân on Google Maps",
]

VI_ALTS = {
    "bedroom": "Phòng ngủ yên tĩnh với chiếc giường đã dọn",
    "lightwell": "Khoảng thông tầng với cây treo dưới giếng trời",
    "veranda": "Hiên sau rợp bóng với ghế mây và cây nhiệt đới",
    "kitchen": "Căn bếp đầy nắng với đồ gỗ",
    "garden-evening": "Dây đèn trong vườn lúc chiều tối",
    "mezzanine": "Cầu thang tay vịn gỗ và cây xanh trong căn nhà sáng",
    "market": "Người phụ nữ bán rau ở chợ",
    "street": "Con đường làng yên tĩnh",
    "tea": "Tách trà bên cửa sổ",
    "beach-sunset": "Người đi dạo trên biển lúc hoàng hôn",
    "corner": "Cây xanh bên cửa sổ cạnh chiếc ghế bành",
    "leaves": "Bóng lá cọ trên tường",
    "first-light": "Đi chân trần trên biển lúc bình minh",
    "lit-window": "Ngôi nhà sáng đèn cửa sổ lúc đêm",
}
VI_LOOP_LABEL = "Chạy xe máy trên đường"


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _chapter(html: str, chapter_id: str) -> str:
    match = re.search(rf'<section id="{chapter_id}".*?</section>', html, re.DOTALL)
    assert match, chapter_id
    return match.group(0)


def _text(fragment: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _block(html: str, css_class: str) -> str:
    pattern = rf'<(\w+) class="{re.escape(css_class)}[^"]*"[^>]*>(.*?)</\1>'
    match = re.search(pattern, html, re.DOTALL)
    assert match, css_class
    return match.group(2)


def _rooms(html: str) -> list[tuple[str, str]]:
    """The floor plan blocks in order: (name, tag), where tag is `a` for a link."""
    found = re.findall(r'<(a|span) class="floor-plan__room"[^>]*>(.*?)</\1>', html, re.DOTALL)
    return [(_text(name), tag) for tag, name in found]


def _attrs(html: str, name: str) -> list[str]:
    return [unescape(value) for value in re.findall(rf'\b{name}="([^"]*)"', html)]


@pytest.fixture(autouse=True)
def _owner() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(owner_first_name="Bún", price_from_million=13)


def test_vi_house_chapter_shows_every_vietnamese_text_and_no_english_one(client: Client) -> None:
    house = _chapter(_get(client, "/vi/"), "house")
    text = _text(house)

    assert "01 · căn nhà" in text
    assert re.search(r'<h2[^>]*>\s*Căn\s*<span class="accent">nhà</span>\s*</h2>', house)
    owner = _text(_block(house, "house__owner"))
    # The greeting comes from the owner's settings (Vietnamese with #106): only its place counts.
    assert owner.endswith(" " + VI_OWNER)
    assert owner[: -len(VI_OWNER)].strip()
    assert re.search(r'<span class="accent">\s*nhà của mình một thời gian\.\s*</span>', house)
    assert _text(_block(house, "house__why")) == VI_WHY
    labels = [_text(m) for m in re.findall(r'house__room-label label">(.*?)</p>', house, re.DOTALL)]
    assert labels == VI_ROOMS
    facts = re.findall(
        r'house__fact-number">(.*?)</span>\s*<span class="house__fact-label">(.*?)</span>',
        house,
        re.DOTALL,
    )
    assert [(_text(n), _text(label)) for n, label in facts] == VI_FACTS
    layout = _block(house, "house__layout")
    assert "Bố cục" in _text(layout)
    assert [_text(i) for i in re.findall(r"<li>(.*?)</li>", layout, re.DOTALL)] == VI_LAYOUT
    assert _text(_block(house, "house__included")) == f"Đã bao gồm {VI_INCLUDED}"
    for english in EN_HOUSE_TEXTS:
        assert english not in text, english


def test_vi_walk_through_the_house_in_vietnamese(client: Client) -> None:
    house = _chapter(_get(client, "/vi/"), "house")
    plan = re.search(r'<figure id="floor-plan".*?</figure>', house, re.DOTALL)
    assert plan

    assert "Đi một vòng quanh nhà" in _text(plan.group(0))
    assert [name for name, _ in _rooms(plan.group(0))] == VI_BLOCKS
    assert _text(_block(plan.group(0), "media__chip floor-plan__chip")) == "Sơ đồ"
    assert VI_SCHEMATIC_NOTE in _text(plan.group(0))
    dialog = re.search(r"<dialog.*?</dialog>", house, re.DOTALL)
    assert dialog
    assert 'aria-label="Ảnh"' in dialog.group(0)
    assert "Ảnh minh hoạ" in _text(dialog.group(0))
    assert _text(_block(dialog.group(0), "button button--secondary floor-plan__close")) == "Đóng"
    assert 'aria-label="Photo"' not in house


def test_vi_blocks_without_a_photo_keep_their_name_and_have_no_link(client: Client) -> None:
    plan = _chapter(_get(client, "/vi/"), "house")

    rooms = dict(_rooms(plan))
    for name in NO_PHOTO_VI:
        assert rooms[name] == "span", name
    for name in set(VI_BLOCKS) - set(NO_PHOTO_VI):
        assert rooms[name] == "a", name
    linked = re.findall(r'<a class="floor-plan__room" href="[^"]+"', plan)
    assert len(linked) == len(VI_BLOCKS) - len(NO_PHOTO_VI)


def test_vi_hoa_xuan_chapter_shows_every_vietnamese_text_and_the_same_maps_link(
    client: Client,
) -> None:
    chapter = _chapter(_get(client, "/vi/"), "hoa-xuan")
    text = _text(chapter)

    assert "02 · quanh nhà" in text
    assert "Mọi thứ bạn cần hằng ngày đều ở gần." in text
    travel = re.findall(
        r'hoa-xuan__place label">(.*?)</span>.*?hoa-xuan__time">(.*?)</span>', chapter, re.DOTALL
    )
    assert [(_text(p), _text(t)) for p, t in travel] == [
        ("Siêu thị", "ngay bên kia đường"),
        ("Chợ", "khoảng 10 phút"),
        ("Biển", "khoảng 10 phút"),
        ("Sân bay", "khoảng 15 phút"),
    ]
    button = re.search(
        r'<a class="button[^"]*hoa-xuan__maps[^"]*" href="([^"]+)"[^>]*>(.*?)</a>', chapter
    )
    assert button
    assert unescape(button.group(1)) == MAPS
    assert _text(button.group(2)) == "Hòa Xuân trên Google Maps ↗"
    assert re.search(r'<h2[^>]*>\s*Hòa\s*<span class="accent">Xuân</span>\s*</h2>', chapter)
    for english in EN_HOA_XUAN_TEXTS:
        assert english not in text, english


def test_en_house_and_hoa_xuan_chapters_keep_every_english_text(client: Client) -> None:
    html = _get(client, "/")
    house = _text(_chapter(html, "house"))
    area = _text(_chapter(html, "hoa-xuan"))

    for english in [*EN_HOUSE_TEXTS, "The house", GREETING]:
        assert english in house, english
    for english in EN_HOA_XUAN_TEXTS:
        assert english in area, english
    assert [n for n, _ in _rooms(_chapter(html, "house"))] == EN_BLOCKS
    assert 'aria-label="Photo"' in html
    assert "Ảnh" not in house


def test_floor_plan_blocks_default_to_english() -> None:
    assert [block.name for block in floor_plan.blocks()] == EN_BLOCKS
    assert [block.name for block in floor_plan.blocks(language="en")] == EN_BLOCKS
    assert [block.name for block in floor_plan.blocks(language="vi")] == VI_BLOCKS


def test_every_photo_has_the_vietnamese_alt_text_of_the_spec() -> None:
    assert set(photos.PHOTOS) == set(VI_ALTS)
    for key, expected in VI_ALTS.items():
        assert photos.PHOTOS[key].alt_vi == expected, key
    assert photos.AREA_LOOP.label_vi == VI_LOOP_LABEL


def test_vi_page_alts_loop_label_data_alt_and_credits_are_vietnamese(client: Client) -> None:
    html = _get(client, "/vi/")
    chapters = _chapter(html, "house") + _chapter(html, "hoa-xuan")

    alts = set(_attrs(chapters, "alt"))
    english_alts = {p.alt for p in photos.PHOTOS.values()}
    assert alts
    # The loop's poster carries the loop's label as its alt text.
    assert alts <= {*VI_ALTS.values(), VI_LOOP_LABEL}
    assert not alts & english_alts
    assert f'aria-label="{VI_LOOP_LABEL}"' in chapters
    assert photos.AREA_LOOP.label not in chapters
    data_alts = _attrs(chapters, "data-alt")
    assert data_alts
    assert set(data_alts) <= set(VI_ALTS.values())
    credits = re.findall(r'<figcaption class="media__credit">(.*?)</figcaption>', chapters)
    credits += _attrs(chapters, "data-credit")
    assert credits
    for credit in credits:
        text = _text(credit)
        assert text in ("", "Video: Pexels", VI_SCHEMATIC_NOTE) or text.startswith("Ảnh: "), text
        assert not text.startswith("Photo: "), text
    assert "Video: Pexels" in chapters


def test_en_page_alts_loop_label_data_alt_and_credits_stay_english(client: Client) -> None:
    html = _get(client, "/")
    chapters = _chapter(html, "house") + _chapter(html, "hoa-xuan")
    english_alts = {p.alt for p in photos.PHOTOS.values()}

    alts = set(_attrs(chapters, "alt"))
    assert alts
    # The loop's poster carries the loop's label as its alt text.
    assert alts <= {*english_alts, photos.AREA_LOOP.label}
    assert f'aria-label="{photos.AREA_LOOP.label}"' in chapters
    assert set(_attrs(chapters, "data-alt")) <= english_alts
    for credit in _attrs(chapters, "data-credit"):
        assert credit.startswith("Photo: ")
    assert "Ảnh: " not in chapters


def test_alt_text_gives_the_english_alt_when_the_photo_has_no_vietnamese_one() -> None:
    made_up = photos.Photo(
        key="made-up",
        width=10,
        height=10,
        alt="A made-up photo",
        credit="Photo: Pexels",
        source="https://www.pexels.com/photo/made-up/",
        alt_vi="",
    )

    assert alt_text(made_up, "vi") == "A made-up photo"
    assert alt_text(made_up, "en") == "A made-up photo"
    assert alt_text(photos.PHOTOS["bedroom"], "vi") == VI_ALTS["bedroom"]


@pytest.mark.parametrize("address", ["/", "/vi/"])
def test_home_page_makes_one_query_in_each_language(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(1):
        _get(client, address)
