"""The FAQ chapter of `/`: the eight questions of design.md as `details` elements, the first
open, no script, and the rent answer that follows the owner's price (one-page spec, AC15)."""

import re
from html import unescape
from html.parser import HTMLParser

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

PRICE_ANSWER = "{price}"
QUESTIONS = [
    ("What is the minimum stay?", "One month."),
    ("Can I rent a room, not the whole house?", "No. The house is rented whole."),
    ("How much is the rent?", PRICE_ANSWER),
    ("How much is the deposit?", "Two months' rent."),
    (
        "Are electricity and water included?",
        "Up to 300 kWh of electricity and 10 m³ of water each month. "
        "Anything above is charged at the official rate.",
    ),
    ("Can I bring a pet?", "Let's talk. Tell me about your pet."),
    (
        "Do you help with temporary residence registration?",
        "Yes. I take care of temporary residence registration for you.",
    ),
    ("Can I visit before I decide?", "Yes. Send me a message and we'll find a time."),
]
FAQ_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "faq.css"


class _Details(HTMLParser):
    """Collects each `details` element: its `open` attribute, its summary text and the rest."""

    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict[str, object]] = []
        self._in_details = False
        self._in_summary = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "details":
            self._in_details = True
            self.items.append({"open": "open" in dict(attrs), "summary": "", "answer": ""})
        elif tag == "summary" and self._in_details:
            self._in_summary = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "details":
            self._in_details = False
        elif tag == "summary":
            self._in_summary = False

    def handle_data(self, data: str) -> None:
        if not self._in_details:
            return
        key = "summary" if self._in_summary else "answer"
        self.items[-1][key] = str(self.items[-1][key]) + data


def _faq(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    match = re.search(r'<section id="faq"[^>]*>.*?</section>', response.content.decode(), re.DOTALL)
    assert match, "no section #faq"
    return match.group(0)


def _items(section: str) -> list[dict[str, object]]:
    parser = _Details()
    parser.feed(section)
    return parser.items


def _clean(text: object) -> str:
    return " ".join(unescape(str(text)).split())


def _settings(price_from: int | None, price_to: int | None) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(price_from_million=price_from, price_to_million=price_to)


# AC1


def test_faq_shows_the_eight_questions_in_order_as_details(client: Client) -> None:
    _settings(13, 14)

    items = _items(_faq(client))

    assert [_clean(item["summary"]) for item in items] == [q for q, _ in QUESTIONS]


def test_each_answer_is_the_text_of_design(client: Client) -> None:
    _settings(13, 14)

    items = _items(_faq(client))

    expected = [
        "From 13–14 million VND a month." if answer == PRICE_ANSWER else answer
        for _, answer in QUESTIONS
    ]
    assert [_clean(item["answer"]) for item in items] == expected


def test_only_the_first_question_is_open(client: Client) -> None:
    _settings(13, 14)

    items = _items(_faq(client))

    assert [item["open"] for item in items] == [True] + [False] * 7


def test_rent_answer_asks_when_there_is_no_price(client: Client) -> None:
    _settings(None, None)

    items = _items(_faq(client))

    assert _clean(items[2]["answer"]) == "Ask me about the rent."


def test_rent_answer_follows_a_single_price(client: Client) -> None:
    _settings(9, None)

    items = _items(_faq(client))

    assert _clean(items[2]["answer"]) == "From 9 million VND a month."


def test_faq_uses_no_script(client: Client) -> None:
    section = _faq(client)

    assert "<script" not in section
    assert not re.search(r"\son[a-z]+\s*=", section)


def test_faq_keeps_one_query_for_the_page(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    _settings(13, 14)

    with django_assert_num_queries(1):
        assert client.get("/").status_code == 200


def test_faq_rows_show_plus_when_closed_and_dash_when_open() -> None:
    css = FAQ_CSS.read_text(encoding="utf-8")

    assert re.search(r"max-width:\s*880px", css)
    assert re.search(r"summary::after\s*\{[^}]*content:\s*\"\+\"", css)
    assert re.search(r"\[open\]\s*>?\s*summary::after\s*\{[^}]*content:\s*\"–\"", css)
    assert re.search(r"summary::after\s*\{[^}]*font-family:\s*var\(--font-serif\)", css)
