"""Rent, FAQ and contact of design E (design-match T6, issue #63; spec AC26 to AC30)."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.template import Context, Template
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from owner_content.services import site_settings

pytestmark = pytest.mark.django_db

CHAPTERS = settings.SRC_DIR / "static" / "css" / "chapters"
RENT_CSS = CHAPTERS / "rent.css"
FAQ_CSS = CHAPTERS / "faq.css"
CONTACT_CSS = CHAPTERS / "contact.css"
QUOTE = "I wanted a house that feels good to live in every day, not just in photos."


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, chapter_id: str) -> str:
    match = re.search(rf'<section id="{chapter_id}"[^>]*>.*?</section>', html, re.S)
    assert match, f"no section #{chapter_id}"
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


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1].split("@media (prefers-reduced-motion", 1)[0]


def _render_price(line: str | None) -> str:
    template = Template("{% load price %}{{ line|price_accents }}")
    return template.render(Context({"line": line}))


# AC1: the caps price line in columns 1–6


def test_price_line_wraps_million_and_a_month_in_the_accent(client: Client) -> None:
    rent = _section(_home(client), "rent")

    line = re.search(r'<p class="rent__line big">(.*?)</p>', rent, re.S)
    assert line
    assert line.group(1) == (
        'From 13–14 <span class="accent">million</span> VND <span class="accent">a month</span>'
    )
    assert _text(line.group(1)) == "From 13–14 million VND a month"


def test_price_line_without_a_price_asks_and_has_no_accent(client: Client) -> None:
    SiteSettings.objects.update(price_from_million=None, price_to_million=None)

    rent = _section(_home(client), "rent")

    line = re.search(r'<p class="rent__line big">(.*?)</p>', rent, re.S)
    assert line and line.group(1) == "Ask me about the rent"


def test_price_filter_handles_a_single_price_and_escapes_the_text() -> None:
    assert _render_price("From 9 million VND a month") == (
        'From 9 <span class="accent">million</span> VND <span class="accent">a month</span>'
    )
    assert (
        _render_price("<b>a month</b>") == '&lt;b&gt;<span class="accent">a month</span>&lt;/b&gt;'
    )
    assert _render_price(None) == ""


def test_price_line_is_caps_at_84px_and_44px_on_phones_with_line_height_095() -> None:
    css = RENT_CSS.read_text(encoding="utf-8")
    rule = _rule(css, ".rent__line")

    # Be Vietnam Pro 300 in small capitals, so 84px capitals need 84 / 0.7.
    assert "font-family: var(--font-sans)" in rule
    assert "font-weight: 300" in rule
    assert "font-variant-caps: all-small-caps" in rule
    assert "font-size: calc(var(--size-big) / 0.7)" in rule
    assert "line-height: calc(var(--size-big) * 0.95)" in rule
    accent = _rule(css, ".rent__line .accent")
    assert "font-variant-caps: normal" in accent
    assert "font-size: 0.7em" in accent
    site = (settings.SRC_DIR / "static" / "css" / "site.css").read_text(encoding="utf-8")
    assert "--size-big: 84px" in site
    assert "--size-big: 44px" in _phone_part(site)


def test_rent_left_column_holds_head_price_buttons_then_terms(client: Client) -> None:
    rent = _section(_home(client), "rent")

    left = _element(rent, "div", "rent__price")
    for part in ("chapter-marker", "chapter-word", "<h2", "rent__line", "contact-buttons"):
        assert part in left
    order = [left.index(p) for p in ("<h2", "rent__line", "contact-buttons", "rent__terms")]
    assert order == sorted(order)
    css = RENT_CSS.read_text(encoding="utf-8")
    assert "1 / span 6" in _rule(css, ".rent__price")


# AC2: the tea photo and the owner's quote in columns 8–12


def test_rent_shows_the_tea_photo_then_the_quote(client: Client) -> None:
    rent = _section(_home(client), "rent")

    aside = _element(rent, "div", "rent__aside")
    assert re.search(r'<img src="/static/media/photos/tea[^"]*"', aside)
    assert "aspect-ratio: 4 / 5" in aside
    quote = _element(aside, "figure", "rent__quote")
    assert aside.index("<img") < aside.index(quote)
    assert _text(quote) == f"{QUOTE} — Bún"
    assert '<span class="accent">not just in photos.</span>' in quote
    assert re.search(r'<figcaption class="label muted">— Bún</figcaption>', quote)


def test_quote_follows_the_owners_first_name(client: Client) -> None:
    SiteSettings.objects.update(owner_first_name="Lan")

    rent = _section(_home(client), "rent")

    assert "— Lan" in _text(_element(rent, "figure", "rent__quote"))


def test_photo_is_560px_high_and_4_by_5_on_phones_in_columns_8_to_12() -> None:
    css = RENT_CSS.read_text(encoding="utf-8")

    assert "8 / span 5" in _rule(css, ".rent__aside")
    assert "height: 560px" in _rule(css, ".rent__photo .media__box")
    phone = _phone_part(css)
    assert "height: auto" in _rule(phone, ".rent__photo .media__box")
    quote = _rule(css, ".rent__quote blockquote")
    assert "font-family: var(--font-serif)" in quote
    assert "font-size: 24px" in quote


# AC3: the owner's first name in the site settings


def test_site_settings_give_the_first_name() -> None:
    SiteSettings.objects.update(owner_first_name="Hưng")

    assert site_settings().first_name == "Hưng"


def test_site_settings_first_name_has_the_model_default_without_a_record() -> None:
    SiteSettings.objects.all().delete()

    assert site_settings().first_name == SiteSettings().owner_first_name


# AC4: the FAQ column


def test_faq_list_is_at_most_880px_under_the_head(client: Client) -> None:
    faq = _section(_home(client), "faq")

    assert faq.index("<h2") < faq.index("faq-list")
    assert faq.count("<details") == 8
    assert "max-width: 880px" in _rule(FAQ_CSS.read_text(encoding="utf-8"), ".faq-list")


# AC5: the contact row


def test_contact_band_has_128px_top_and_112px_bottom() -> None:
    rule = _rule(CONTACT_CSS.read_text(encoding="utf-8"), ".chapter--contact")

    assert "padding-top: 128px" in rule
    assert "padding-bottom: 112px" in rule
    assert "background: var(--band)" in rule


def test_contact_row_has_heading_and_line_left_and_buttons_right(client: Client) -> None:
    contact = _section(_home(client), "contact")

    row = _element(contact, "div", "contact__row")
    lead = _element(row, "div", "contact__lead")
    assert "<h2" in lead
    line = re.search(r'<p class="contact__line">(.*?)</p>', lead, re.S)
    assert line
    assert line.group(1) == (
        'Hi, I&#x27;m Bún. <span class="accent">I usually reply within an hour.</span>'
    )
    assert row.index(lead) < row.index("contact-buttons")
    assert contact.index("chapter-word") < contact.index(row)
    css = CONTACT_CSS.read_text(encoding="utf-8")
    flex = _rule(css, ".contact__row")
    assert "display: flex" in flex
    assert "flex-wrap: wrap" in flex
    assert "justify-content: space-between" in flex
    text = _rule(css, ".contact__line")
    assert "font-family: var(--font-serif)" in text
    assert "font-size: 30px" in text


def test_contact_without_a_channel_keeps_the_empty_state(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    html = _home(client)
    contact = _section(html, "contact")

    assert "Contact details are on their way." in _text(contact)
    assert "contact-buttons" not in contact
    assert "contact-bar" not in html


# AC6: the reveal blocks


@pytest.mark.parametrize(
    ("chapter_id", "tag", "css_class"),
    [
        ("rent", "div", "rent__line-block"),
        ("rent", "div", "rent__buttons"),
        ("rent", "div", "rent__terms-block"),
        ("rent", "div", "rent__photo"),
        ("rent", "figure", "rent__quote"),
        ("faq", "div", "faq-list"),
        ("contact", "div", "contact__row"),
    ],
)
def test_blocks_carry_reveal(client: Client, chapter_id: str, tag: str, css_class: str) -> None:
    section = _section(_home(client), chapter_id)

    assert "reveal" in _classes(section, tag, css_class)


def test_reveal_blocks_hold_the_price_line_the_buttons_and_the_terms(client: Client) -> None:
    rent = _section(_home(client), "rent")

    assert "rent__line big" in _element(rent, "div", "rent__line-block")
    assert "contact-buttons" in _element(rent, "div", "rent__buttons")
    assert "rent__terms" in _element(rent, "div", "rent__terms-block")


# AC7: still one query


def test_home_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
