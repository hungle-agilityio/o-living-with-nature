"""Chapters 03, 04 and 05 of `/vi/` in Vietnamese, with the owner's lines (vietnamese spec, task T3,
issue #106).

The row names (M28 to M31 and M33) are those of the "Test matrix rows" of the issue. M32 is
checked by hand in the pull request and has no test here. The rows M26 and M27 (the admin field)
are in `owner_content/tests/test_reply_time_vi.py`.
"""

import html as html_lib
import json
import re
from html.parser import HTMLParser

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

NUMBER = "0945 384 500"
CHANNELS = ("call", "whatsapp", "zalo")
PLACES = ("bar", "rent", "faq", "contact")

EN_PRICE = "From 13–14 million VND a month"
VI_PRICE = "Từ 13–14 triệu đồng mỗi tháng"
VI_GREETING = "Chào bạn, mình là Bún."
VI_REPLY = "Mình thường trả lời trong vòng một giờ."
VI_NO_PRICE = "Hỏi mình về giá thuê nhé"
VI_NO_CHANNEL = "Thông tin liên hệ sẽ sớm có."
VI_BUTTONS = ["Gọi điện", "WhatsApp", "Zalo"]
VI_TERMS = [
    "Nguyên căn, theo tháng",
    "Thuê tối thiểu một tháng",
    "Đặt cọc hai tháng",
    "Mỗi tháng đã gồm tối đa 300 kWh điện và 10 m³ nước. Phần vượt tính theo giá nhà nước.",
    "Mình lo giúp bạn thủ tục đăng ký tạm trú",
]
VI_QUOTE = "Mình muốn một căn nhà sống dễ chịu mỗi ngày, chứ không chỉ đẹp trong ảnh."
VI_QUESTIONS = [
    ("Thời gian thuê tối thiểu là bao lâu?", "Một tháng."),
    ("Có thuê riêng một phòng được không?", "Không. Nhà chỉ cho thuê nguyên căn."),
    ("Giá thuê bao nhiêu?", f"{VI_PRICE}."),
    ("Tiền cọc bao nhiêu?", "Hai tháng tiền nhà."),
    (
        "Giá đã gồm điện nước chưa?",
        "Mỗi tháng đã gồm tối đa 300 kWh điện và 10 m³ nước. Phần vượt tính theo giá nhà nước.",
    ),
    (
        "Có được nuôi thú cưng không?",
        "Mình cùng trao đổi nhé. Kể mình nghe về bé thú cưng của bạn.",
    ),
    (
        "Chủ nhà có giúp đăng ký tạm trú không?",
        "Có. Mình lo giúp bạn thủ tục đăng ký tạm trú.",
    ),
    (
        "Có thể đến xem nhà trước khi quyết định không?",
        "Được chứ. Bạn nhắn cho mình, mình hẹn giờ nhé.",
    ),
]
EN_RENT_TEXTS = [
    "03 · to stay a long while",
    "The rent",
    EN_PRICE,
    "Whole house, by the month",
    "I wanted a house that feels good to live in every day, not just in photos.",
]
EN_FAQ_TEXTS = [
    "04 · questions",
    "FAQ",
    "Hi, I'm Bún.",
    "I usually reply within an hour.",
    "What is the minimum stay?",
    "How much is the rent?",
    f"{EN_PRICE}.",
]


@pytest.fixture(autouse=True)
def owner_values() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=13,
        price_to_million=14,
        phone=NUMBER,
        whatsapp=NUMBER,
        zalo=NUMBER,
        owner_first_name="Bún",
        reply_time="within an hour",
    )


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    assert match, pattern
    return match.group(0)


def _chapter(html: str, name: str) -> str:
    return _section(html, rf'<section id="{name}".*?</section>')


def _bar(html: str) -> str:
    return _section(html, r'<nav class="contact-bar".*?</nav>')


def _plain(fragment: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def _accents(fragment: str) -> list[str]:
    return [_plain(text) for text in re.findall(r'<span class="accent">(.*?)</span>', fragment)]


def _heading(fragment: str) -> str:
    return _section(fragment, r"<h2\b.*?</h2>")


def _buttons(fragment: str) -> list[str]:
    return [_plain(text) for text in re.findall(r'<a class="button[^"]*".*?>(.*?)</a>', fragment)]


def _json_ld(html: str) -> dict[str, object]:
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    assert match, "no JSON-LD"
    data = json.loads(match.group(1))
    assert isinstance(data, dict)
    return data


class _Anchors(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[tuple[str | None, str | None, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and "data-channel" in values:
            self.buttons.append((values.get("href"), values["data-channel"], values["data-place"]))


def _button_attributes(html: str) -> list[tuple[str | None, str | None, str | None]]:
    parser = _Anchors()
    parser.feed(html)
    return parser.buttons


# M28 (AC3, AC4)


def test_m28_rent_chapter_in_vietnamese(client: Client) -> None:
    rent = _chapter(_get(client, "/vi/"), "rent")

    text = _plain(rent)
    assert "03 · thuê dài lâu" in text
    assert _plain(_heading(rent)) == "Giá thuê"
    assert _accents(_heading(rent)) == ["thuê"]
    line = _section(rent, r'<p class="rent__line big">.*?</p>')
    assert _plain(line) == VI_PRICE
    assert _accents(line) == ["triệu", "mỗi tháng"]
    assert _buttons(rent) == VI_BUTTONS
    for term in VI_TERMS:
        assert term in _plain(_section(rent, r'<ul class="rent__terms">.*?</ul>'))
    quote = _section(rent, r"<blockquote>.*?</blockquote>")
    assert _plain(quote) == VI_QUOTE
    assert _accents(quote) == ["chứ không chỉ đẹp trong ảnh."]
    signature = _section(rent, r'<figure class="rent__quote[^"]*">.*?</figure>')
    assert _plain(_section(signature, r"<figcaption\b.*?</figcaption>")) == "— Bún"


def test_m28_faq_chapter_in_vietnamese(client: Client) -> None:
    faq = _chapter(_get(client, "/vi/"), "faq")

    assert "04 · hỏi đáp" in _plain(faq)
    assert _plain(_heading(faq)) == "Hỏi đáp"
    line = _section(faq, r'<p class="faq-side__line">.*?</p>')
    assert _plain(line) == f"{VI_GREETING} {VI_REPLY}"
    assert _accents(line) == [VI_REPLY]
    items = re.findall(r'<details class="faq-item"[^>]*>(.*?)</details>', faq, re.DOTALL)
    assert [
        (_plain(_section(item, r"<summary>.*?</summary>")), _plain(_section(item, r"<p>.*?</p>")))
        for item in items
    ] == VI_QUESTIONS
    assert 'name="faq"' in faq
    assert _buttons(faq) == VI_BUTTONS


def test_m28_contact_chapter_in_vietnamese(client: Client) -> None:
    contact = _chapter(_get(client, "/vi/"), "contact")

    assert _plain(_heading(contact)) == "Bạn sẽ ở lại chứ?"
    assert _accents(_heading(contact)) == ["ở lại chứ?"]
    line = _section(contact, r'<p class="contact__line">.*?</p>')
    assert _plain(line) == f"{VI_GREETING} {VI_REPLY}"
    assert _accents(line) == [VI_REPLY]
    assert _buttons(contact) == VI_BUTTONS


def test_m28_phone_contact_bar_and_house_owner_line_in_vietnamese(client: Client) -> None:
    html = _get(client, "/vi/")

    assert _buttons(_bar(html)) == VI_BUTTONS
    house = _section(_chapter(html, "house"), r'<p class="house__owner[^"]*">.*?</p>')
    assert _plain(house).startswith(VI_GREETING)


def test_m28_price_range_of_the_vietnamese_page_is_in_vietnamese(client: Client) -> None:
    assert _json_ld(_get(client, "/vi/"))["priceRange"] == VI_PRICE


def test_m28_vietnamese_chapters_hold_no_english_text(client: Client) -> None:
    html = _get(client, "/vi/")

    for name in ("rent", "faq", "contact"):
        text = _plain(_chapter(html, name))
        for english in ("million VND", "I usually reply", "Hi, I'm", "Whole house", "FAQ"):
            assert english not in text, f"{name}: {english}"
        assert "Call" not in _buttons(_chapter(html, name))
    assert "Call" not in _buttons(_bar(html))


def test_m28_english_page_keeps_its_values(client: Client) -> None:
    html = _get(client, "/")

    rent = _plain(_chapter(html, "rent"))
    faq = _plain(_chapter(html, "faq"))
    for expected in EN_RENT_TEXTS:
        assert expected in rent
    for expected in EN_FAQ_TEXTS:
        assert expected in faq
    assert _buttons(_chapter(html, "rent")) == ["Call", "WhatsApp", "Zalo"]
    assert _buttons(_bar(html)) == ["Call", "WhatsApp", "Zalo"]
    assert _plain(_heading(_chapter(html, "contact"))) == "Will you stay?"
    assert _accents(_section(_chapter(html, "rent"), r'<p class="rent__line big">.*?</p>')) == [
        "million",
        "a month",
    ]
    assert _json_ld(html)["priceRange"] == EN_PRICE


# M29 (AC5)


def test_m29_one_price_on_the_vietnamese_page(client: Client) -> None:
    SiteSettings.objects.update(price_from_million=13, price_to_million=None)

    html = _get(client, "/vi/")

    rent_line = _section(_chapter(html, "rent"), r'<p class="rent__line big">.*?</p>')
    assert _plain(rent_line) == "Từ 13 triệu đồng mỗi tháng"
    assert _accents(rent_line) == ["triệu", "mỗi tháng"]
    assert "Từ 13 triệu đồng mỗi tháng." in _plain(_chapter(html, "faq"))
    assert _json_ld(html)["priceRange"] == "Từ 13 triệu đồng mỗi tháng"


def test_m29_no_price_on_the_vietnamese_page(client: Client) -> None:
    SiteSettings.objects.update(price_from_million=None, price_to_million=None)

    html = _get(client, "/vi/")

    rent_line = _section(_chapter(html, "rent"), r'<p class="rent__line big">.*?</p>')
    assert _plain(rent_line) == VI_NO_PRICE
    faq = _chapter(html, "faq")
    rent_answer = _plain(re.findall(r"<p>(.*?)</p>", faq, re.DOTALL)[2])
    assert rent_answer == f"{VI_NO_PRICE}."
    assert "priceRange" not in _json_ld(html)


# M30 (AC6)


def test_m30_no_channel_on_the_vietnamese_page(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    html = _get(client, "/vi/")

    assert _button_attributes(html) == []
    assert "contact-bar" not in html
    faq = _plain(_chapter(html, "faq"))
    assert f"{VI_GREETING} {VI_REPLY}" in faq
    assert _plain(_chapter(html, "contact")).endswith(VI_NO_CHANNEL)
    assert VI_NO_CHANNEL in _chapter(html, "contact")
    assert "Contact details are on their way." not in html


# M31 (AC7)


def test_m31_buttons_keep_their_link_channel_and_place_in_both_languages(client: Client) -> None:
    english = _button_attributes(_get(client, "/"))
    vietnamese = _button_attributes(_get(client, "/vi/"))

    assert len(vietnamese) == len(CHANNELS) * len(PLACES)
    assert {(channel, place) for _, channel, place in vietnamese} == {
        (channel, place) for channel in CHANNELS for place in PLACES
    }
    assert vietnamese == english
    assert ("tel:+84945384500", "call", "rent") in vietnamese
    assert ("https://wa.me/84945384500", "whatsapp", "faq") in vietnamese
    assert ("https://zalo.me/0945384500", "zalo", "contact") in vietnamese


# M33 (AC8)


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_m33_each_page_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
