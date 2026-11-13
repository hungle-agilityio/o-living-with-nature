"""The FAQ chapter in two columns (issue #83): the head, the owner's line and the contact
buttons on the left, sticky on desktop; the eight questions on the right, one open at a time."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

FAQ_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "faq.css"
QUESTIONS = [
    "What is the minimum stay?",
    "Can I rent a room, not the whole house?",
    "How much is the rent?",
    "How much is the deposit?",
    "Are electricity and water included?",
    "Can I bring a pet?",
    "Do you help with temporary residence registration?",
    "Can I visit before I decide?",
]


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _faq(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    match = re.search(r'<section id="faq"[^>]*>.*?</section>', response.content.decode(), re.S)
    assert match, "no section #faq"
    return match.group(0)


def _element(html: str, tag: str, css_class: str) -> str:
    """The first `tag` whose class list holds `css_class`, up to its matching closing tag."""
    start = re.search(rf'<{tag} class="(?:[^"]* )?{re.escape(css_class)}(?: [^"]*)?"', html)
    assert start, f"no <{tag} class=…{css_class}…>"
    depth = 0
    for tag_match in re.finditer(rf"<(/?){tag}\b[^>]*>", html[start.start() :]):
        depth += -1 if tag_match.group(1) else 1
        if depth == 0:
            return html[start.start() : start.start() + tag_match.end()]
    raise AssertionError(f"<{tag} class=…{css_class}…> is not closed")


def _classes(html: str, tag: str, css_class: str) -> list[str]:
    match = re.search(rf'<{tag} class="((?:[^"]* )?{re.escape(css_class)}(?: [^"]*)?)"', html)
    assert match, f"no <{tag} class=…{css_class}…>"
    return match.group(1).split()


def _css() -> str:
    return FAQ_CSS.read_text(encoding="utf-8")


def _desktop_part(css: str) -> str:
    return css.split("@media (max-width: 760px)", 1)[0]


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1]


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return " ".join(match.group(1).split())


# AC1: a 12-column grid, the side block sticky in columns 1–4, the list in columns 6–12


def test_faq_is_a_12_column_grid_with_40px_gap_on_desktop() -> None:
    rule = _rule(_desktop_part(_css()), ".chapter--faq")

    assert "display: grid" in rule
    assert "grid-template-columns: repeat(12, minmax(0, 1fr))" in rule
    assert "column-gap: 40px" in rule or "gap: 40px" in rule


def test_side_block_spans_columns_1_to_4_and_is_sticky_at_96px() -> None:
    rule = _rule(_desktop_part(_css()), ".faq-side")

    assert "grid-column: 1 / 5" in rule
    assert "position: sticky" in rule
    assert "top: 96px" in rule


def test_list_spans_columns_6_to_12() -> None:
    rule = _rule(_desktop_part(_css()), ".faq-list")

    assert "grid-column: 6 / 13" in rule
    assert "max-width: 880px" not in rule


def test_side_block_comes_before_the_list(client: Client) -> None:
    faq = _faq(client)

    side = _element(faq, "div", "faq-side")
    assert faq.index(side) < faq.index('class="faq-list')


# AC2: head, rule, the owner's line, the buttons with place="faq"


def test_side_block_holds_the_head_the_line_and_the_buttons(client: Client) -> None:
    side = _element(_faq(client), "div", "faq-side")

    assert "04 · questions" in _text(side)
    assert '<h2 id="faq-heading">FAQ</h2>' in side
    line = re.search(r'<p class="faq-side__line">(.*?)</p>', side, re.S)
    assert line
    assert line.group(1) == (
        'Hi, I&#x27;m Bún. <span class="accent">I usually reply within an hour.</span>'
    )
    links = re.findall(r"<a [^>]*data-channel=[^>]*>", side)
    assert links
    assert all('data-place="faq"' in link for link in links)
    assert side.index("<h2") < side.index("faq-side__line") < side.index("contact-buttons")


def test_owner_line_follows_the_owner_values(client: Client) -> None:
    SiteSettings.objects.update(owner_first_name="Lan", reply_time="within a day")

    side = _element(_faq(client), "div", "faq-side")

    line = re.search(r'<p class="faq-side__line">(.*?)</p>', side, re.S)
    assert line
    assert "Lan" in _text(line.group(1))
    assert "within a day" in _text(line.group(1))


def test_owner_line_is_cormorant_300_at_26px_under_a_1px_line_rule() -> None:
    css = _css()

    line = _rule(css, ".faq-side__line")
    assert "font-family: var(--font-serif)" in line
    assert "font-weight: 300" in line
    assert "font-size: 26px" in line
    invite = _rule(css, ".faq-side__invite")
    assert "border-top: 1px solid var(--line)" in invite


def test_head_sizes_stay_150px_and_60px() -> None:
    css = _css()

    assert "font-size: calc(150px / 0.7)" in _rule(css, ".chapter--faq h2")
    assert "font-size: calc(60px / 0.7)" in _phone_part(css)


# AC3: no contact channel


def test_without_a_channel_the_side_block_keeps_only_the_line(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    side = _element(_faq(client), "div", "faq-side")

    assert "faq-side__line" in side
    assert "contact-buttons" not in side
    assert "data-channel" not in side
    invite = _element(side, "div", "faq-side__invite")
    assert _text(invite) == "Hi, I'm Bún. I usually reply within an hour."


# AC4: eight details, the first open, one open at a time, Cormorant summaries


def test_list_keeps_the_eight_questions_in_order_with_name_faq(client: Client) -> None:
    faq_list = _element(_faq(client), "div", "faq-list")

    details = re.findall(r"<details\b[^>]*>", faq_list)
    assert len(details) == 8
    assert all('name="faq"' in tag for tag in details)
    assert [" open" in tag or tag.endswith("open>") for tag in details] == [True] + [False] * 7
    summaries = [_text(s) for s in re.findall(r"<summary>(.*?)</summary>", faq_list, re.S)]
    assert summaries == QUESTIONS


def test_summaries_are_cormorant_300_at_30px_and_22px_on_phones() -> None:
    css = _css()

    summary = _rule(css, ".faq-item summary")
    assert "font-family: var(--font-serif)" in summary
    assert "font-weight: 300" in summary
    assert "font-size: 30px" in summary
    assert "font-size: 22px" in _rule(_phone_part(css), ".faq-item summary")


def test_answers_stay_stone_at_most_56ch() -> None:
    answer = _rule(_css(), ".faq-item p")

    assert "max-width: 56ch" in answer
    assert "color: var(--muted)" in answer


# AC5: one column on phones, head, list, then the line and the buttons


def test_phone_is_one_column_with_head_list_then_line() -> None:
    phone = _phone_part(_css())

    section = _rule(phone, ".chapter--faq")
    assert "display: flex" in section
    assert "flex-direction: column" in section
    assert "display: contents" in _rule(phone, ".faq-side")
    assert "order: 2" in _rule(phone, ".faq-list")
    assert "order: 3" in _rule(phone, ".faq-side__invite")
    assert "min-width: 0" in _rule(phone, ".faq-list")


# AC6: reveal, no script


def test_list_and_side_block_carry_reveal(client: Client) -> None:
    faq = _faq(client)

    assert "reveal" in _classes(faq, "div", "faq-side")
    assert "reveal" in _classes(faq, "div", "faq-list")


def test_faq_has_no_script_and_no_inline_event(client: Client) -> None:
    faq = _faq(client)

    assert "<script" not in faq
    assert not re.search(r"\son[a-z]+\s*=", faq)


# AC7: still one query


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        assert client.get("/").status_code == 200
