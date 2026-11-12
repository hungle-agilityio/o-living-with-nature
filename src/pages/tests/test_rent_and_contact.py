"""The rent and contact chapters and the phone contact bar (issue #38; one-page AC9 to AC12)."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.template.loader import render_to_string
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from owner_content.services import Channel, SiteSettingsValue

pytestmark = pytest.mark.django_db

CONTACT_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "contact.css"
RENT_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "rent.css"
SCRIPT = settings.SRC_DIR / "static" / "js" / "contact-bar.js"
CHANNELS = (
    Channel(key="call", label="Call", link="tel:+84945384500"),
    Channel(key="whatsapp", label="WhatsApp", link="https://wa.me/84945384500"),
    Channel(key="zalo", label="Zalo", link="https://zalo.me/0945384500"),
)
TERMS = [
    "Whole house, by the month",
    "Minimum stay one month",
    "Two months' deposit",
    "Included each month: up to 300 kWh of electricity and 10 m³ of water. "
    "Anything above is charged at the official rate.",
    "I take care of temporary residence registration for you",
]
BAR_SCRIPT = '<script src="/static/js/contact-bar.js" defer></script>'


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


def _bar(html: str) -> str:
    match = re.search(r'<nav class="contact-bar" aria-label="Contact">.*?</nav>', html, re.S)
    assert match, "no contact bar"
    return match.group(0)


def _links(html: str) -> list[str]:
    return re.findall(r"<a [^>]*>.*?</a>", html, re.S)


def _owner(channels: tuple[Channel, ...] = CHANNELS) -> SiteSettingsValue:
    return SiteSettingsValue(
        price_line="From 13–14 million VND a month",
        channels=channels,
        greeting="Hi, I'm Bún.",
        reply_line="I usually reply within an hour.",
    )


def _no_channels() -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1].split("@media (prefers-reduced-motion", 1)[0]


# AC1: the reusable contact buttons


def test_buttons_follow_the_channels_in_order_with_label_and_link() -> None:
    html = render_to_string("includes/contact_buttons.html", {"owner": _owner(), "place": "rent"})

    links = _links(html)
    assert [_text(link) for link in links] == ["Call", "WhatsApp", "Zalo"]
    for link, channel in zip(links, CHANNELS, strict=True):
        assert f'href="{channel.link}"' in link
        assert f'data-channel="{channel.key}"' in link
        assert 'data-place="rent"' in link


def test_first_button_is_the_primary_one() -> None:
    html = render_to_string("includes/contact_buttons.html", {"owner": _owner(), "place": "bar"})

    classes = [re.search(r'class="([^"]*)"', link).group(1) for link in _links(html)]  # type: ignore[union-attr]
    assert classes == ["button", "button button--secondary", "button button--secondary"]


def test_whatsapp_and_zalo_open_in_a_new_tab_and_call_does_not() -> None:
    html = render_to_string(
        "includes/contact_buttons.html", {"owner": _owner(), "place": "contact"}
    )

    call, whatsapp, zalo = _links(html)
    assert "target=" not in call
    assert "rel=" not in call
    for link in (whatsapp, zalo):
        assert 'target="_blank"' in link
        rel = re.search(r'rel="([^"]*)"', link)
        assert rel and "noopener" in rel.group(1).split()


def test_buttons_show_only_the_channels_there_are() -> None:
    owner = _owner(channels=(CHANNELS[2],))
    html = render_to_string("includes/contact_buttons.html", {"owner": owner, "place": "rent"})

    assert [_text(link) for link in _links(html)] == ["Zalo"]


def test_buttons_render_nothing_without_a_channel() -> None:
    html = render_to_string("includes/contact_buttons.html", {"owner": _owner(()), "place": "rent"})

    assert html.strip() == ""


# AC2: the rent chapter


def test_rent_shows_the_price_line_in_the_big_size(client: Client) -> None:
    rent = _section(_home(client), "rent")

    line = re.search(r'<p class="rent__line big">(.*?)</p>', rent, re.S)
    assert line and _text(line.group(1)) == "From 13–14 million VND a month"


def test_rent_asks_about_the_rent_without_a_price(client: Client) -> None:
    SiteSettings.objects.update(price_from_million=None, price_to_million=None)

    rent = _section(_home(client), "rent")

    line = re.search(r'<p class="rent__line big">(.*?)</p>', rent, re.S)
    assert line and _text(line.group(1)) == "Ask me about the rent"
    assert "million VND" not in rent


def test_rent_shows_the_buttons_under_the_price_then_the_terms(client: Client) -> None:
    rent = _section(_home(client), "rent")

    links = _links(rent)
    assert [_text(link) for link in links] == ["Call", "WhatsApp", "Zalo"]
    assert all('data-place="rent"' in link for link in links)
    assert rent.index("rent__line") < rent.index(links[0]) < rent.index("rent__terms")


def test_rent_terms_are_listed_as_written(client: Client) -> None:
    rent = _section(_home(client), "rent")

    terms = re.search(r'<ul class="rent__terms">(.*?)</ul>', rent, re.S)
    assert terms
    items = re.findall(r"<li>(.*?)</li>", terms.group(1), re.S)
    assert [_text(item) for item in items] == TERMS


def test_rent_without_a_channel_shows_no_button(client: Client) -> None:
    _no_channels()

    rent = _section(_home(client), "rent")

    assert _links(rent) == []
    assert _text(rent).endswith(TERMS[-1])


def test_rent_grid_follows_the_design() -> None:
    css = RENT_CSS.read_text(encoding="utf-8")

    assert "repeat(12, minmax(0, 1fr))" in _rule(css, ".rent__grid")
    assert "1 / span 6" in _rule(css, ".rent__price")
    assert "8 / span 5" in _rule(css, ".rent__terms")
    assert "minmax(0, 1fr)" in _phone_part(css)


# AC3: the contact chapter


def test_contact_is_the_ink_band(client: Client) -> None:
    contact = _section(_home(client), "contact")

    assert re.match(r'<section id="contact" class="[^"]*\bband\b', contact)
    rule = _rule(CONTACT_CSS.read_text(encoding="utf-8"), ".chapter--contact")
    assert "background: var(--band)" in rule
    assert "color: var(--paper)" in rule


def test_contact_shows_the_heading_the_owner_line_then_the_buttons(client: Client) -> None:
    contact = _section(_home(client), "contact")

    text = _text(contact)
    line = "Hi, I'm Bún. I usually reply within an hour."
    assert "Will you stay?" in text
    assert line in text
    assert text.index("Will you stay?") < text.index(line) < text.index("Call")
    links = _links(contact)
    assert [_text(link) for link in links] == ["Call", "WhatsApp", "Zalo"]
    assert all('data-place="contact"' in link for link in links)
    assert "Contact details are on their way." not in text


def test_contact_line_follows_the_owner_values(client: Client) -> None:
    SiteSettings.objects.update(owner_first_name="Lan", reply_time="the same day")

    text = _text(_section(_home(client), "contact"))

    assert "Hi, I'm Lan. I usually reply the same day." in text


def test_contact_without_a_channel_says_details_are_on_their_way(client: Client) -> None:
    _no_channels()

    contact = _section(_home(client), "contact")

    assert "Contact details are on their way." in _text(contact)
    assert _links(contact) == []


# AC4: the phone contact bar


def test_bar_holds_the_buttons_for_the_bar(client: Client) -> None:
    bar = _bar(_home(client))

    links = _links(bar)
    assert [_text(link) for link in links] == ["Call", "WhatsApp", "Zalo"]
    assert all('data-place="bar"' in link for link in links)


def test_bar_comes_with_its_deferred_script(client: Client) -> None:
    html = _home(client)

    assert html.count(BAR_SCRIPT) == 1
    assert html.index(_bar(html)) < html.index(BAR_SCRIPT)


def test_no_channel_means_no_bar_and_no_script(client: Client) -> None:
    _no_channels()

    html = _home(client)

    assert 'aria-label="Contact"' not in html
    assert "contact-bar" not in html


def test_bar_is_fixed_to_the_bottom_on_phones_only() -> None:
    css = CONTACT_CSS.read_text(encoding="utf-8")

    # Hidden above 760px; fixed to the bottom at 760px or less, where it shows without a script.
    assert "display: none" in _rule(css.split("@media", 1)[0], ".contact-bar")
    phone = _rule(_phone_part(css), ".contact-bar")
    assert "position: fixed" in phone
    assert "bottom: 0" in phone
    assert "display: block" in phone
    assert "contact-bar--away" in _phone_part(css)


def test_script_hides_the_bar_over_the_hero_and_the_contact_chapter() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "IntersectionObserver" in script
    assert 'getElementById("hero")' in script
    assert 'getElementById("contact")' in script
    assert "contact-bar--away" in script


def test_script_is_small_and_uses_no_library() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert len(script.encode()) < 4_000
    for sign in ("import ", "require(", "http://", "https://", "jQuery", "eval("):
        assert sign not in script


# AC5: still one query


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
