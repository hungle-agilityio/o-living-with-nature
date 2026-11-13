"""Design match T1: the frame and the chapter heads of `/` (design-match spec, AC1 to AC5;
design.md, "Frame"). The positions in the browser are checked by the verify report's screens;
these tests pin the markup and the rules that give them."""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

CSS = settings.SRC_DIR / "static" / "css"
SITE_CSS = CSS / "site.css"
CONTACT_CSS = CSS / "chapters" / "contact.css"
FAQ_CSS = CSS / "chapters" / "faq.css"
INSET = "max(var(--side), calc((100% - var(--content-max)) / 2 + var(--side)))"
# id, label after the hook, accent word of the h2 (FAQ has none), the h2 text.
HEADS = [
    ("house", "01 · at home", "house", "The house"),
    ("hoa-xuan", "02 · close by", "Xuân", "Hòa Xuân"),
    ("rent", "03 · to stay a long while", "rent", "The rent"),
    ("faq", "04 · questions", None, "FAQ"),
    ("contact", "05", "stay?", "Will you stay?"),
]


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, chapter_id: str) -> str:
    match = re.search(rf'<section id="{chapter_id}".*?</section>', html, re.DOTALL)
    assert match, f"no section {chapter_id}"
    return match.group(0)


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1]


def _site() -> str:
    return SITE_CSS.read_text(encoding="utf-8")


# AC1: the container of every chapter, the full-width hero and contact band


def test_one_page_main_is_full_width_so_each_part_sets_its_own_width(client: Client) -> None:
    html = _home(client)

    assert '<main class="site-main site-main--one-page">' in html
    rule = _rule(_site(), ".site-main--one-page")
    assert "max-width: none" in rule
    assert "padding: 0" in rule


def test_other_pages_keep_the_container_main(client: Client) -> None:
    html = client.get("/no-such-page/").content.decode()

    assert '<main class="site-main">' in html
    rule = _rule(_site(), ".site-main")
    assert "max-width: var(--content-max)" in rule
    assert "var(--side)" in rule


def test_every_chapter_sits_in_the_1360px_container_with_its_sides() -> None:
    rule = _rule(_site(), ".chapter")

    # 1440px: (1440 - 1360) / 2 + 40 = 80px; 390px: the 18px sides.
    assert "width: min(100%, var(--content-max))" in rule
    assert "margin-left: auto" in rule
    assert "margin-right: auto" in rule
    assert "padding-left: var(--side)" in rule
    assert "padding-right: var(--side)" in rule
    assert "max-width: 100%" in rule
    assert "--side: 18px" in _phone_part(_site())
    assert "--content-max: 1360px" in _site()


def test_contact_band_spans_the_width_with_its_text_in_the_container() -> None:
    rule = _rule(CONTACT_CSS.read_text(encoding="utf-8"), ".chapter--contact")

    assert "width: 100%" in rule
    assert f"padding-left: {INSET}" in rule
    assert f"padding-right: {INSET}" in rule
    # No more shadow trick: the band is as wide as the page, never wider.
    assert "100vmax" not in rule


def test_still_hero_spans_the_width_with_its_text_in_the_container() -> None:
    site = _site()
    still = site.split("html.hero-flight", 1)[0]

    hero = _rule(still, ".hero")
    assert f"padding-left: {INSET}" in hero
    assert f"padding-right: {INSET}" in hero
    flight = _rule(site, "html.hero-flight .hero")
    assert "padding: 0" in flight


def test_nothing_uses_the_screen_width_to_break_out() -> None:
    for sheet in [SITE_CSS, *sorted((CSS / "chapters").glob("*.css"))]:
        assert "100vw" not in sheet.read_text(encoding="utf-8"), sheet.name


# AC2


def test_the_flight_rule_on_the_main_is_gone() -> None:
    site = _site()

    assert "html.hero-flight .site-main" not in site
    assert not re.search(r"\.hero-flight[^{]*\.site-main", site)


# AC3


def test_home_response_shows_no_template_comment(client: Client) -> None:
    html = _home(client)

    assert "{#" not in html
    assert "#}" not in html


def test_every_short_comment_in_the_templates_fits_on_one_line() -> None:
    templates = sorted(settings.SRC_DIR.glob("**/templates/**/*.html"))
    assert templates
    for template in templates:
        for number, line in enumerate(template.read_text(encoding="utf-8").splitlines(), 1):
            if "{#" in line:
                assert "#}" in line[line.index("{#") :], f"{template.name}:{number}"


# AC4


@pytest.mark.parametrize(("chapter_id", "label", "accent", "heading"), HEADS)
def test_chapter_opens_with_label_word_then_h2_with_its_accent(
    client: Client, chapter_id: str, label: str, accent: str | None, heading: str
) -> None:
    section = _section(_home(client), chapter_id)

    marker = re.search(r'<p class="chapter-marker label\b[^"]*">(.*?)</p>', section, re.DOTALL)
    assert marker, "no label"
    assert unescape(marker.group(1)) == f" ̉ {label}"
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", section, re.DOTALL)
    assert h2
    assert _text(h2.group(1)) == heading
    if accent is None:
        assert "accent" not in h2.group(1)
        assert 'class="chapter-word"' not in section
    else:
        assert f'<span class="accent">{accent}</span>' in h2.group(1)
        word = section.index('class="chapter-word"')
        assert section.index(marker.group(0)) < word < section.index("<h2")


def test_label_is_stone_except_on_the_ink_band(client: Client) -> None:
    html = _home(client)

    for chapter_id, *_rest in HEADS[:4]:
        assert 'class="chapter-marker label muted"' in _section(html, chapter_id)
    assert 'class="chapter-marker label"' in _section(html, "contact")
    # The label rule: 11px capitals (small capitals at 11 / 0.7), 0.22em.
    label = _rule(_site(), ".label,\n.nav-links,\n.nav-menu summary,\n.site-footer__note")
    assert "font-variant-caps: all-small-caps" in label
    assert "calc(var(--size-label) * 0.22)" in label
    assert "--size-label: 11px" in _site()


def test_head_sizes_on_desktop_and_phones() -> None:
    site = _site()
    phone = _phone_part(site)

    word = _rule(site, ".chapter-word")
    assert "font-size: var(--size-chapter)" in word
    assert "line-height: 0.8" in word
    assert "font-style: italic" in word
    assert "--size-chapter: 200px" in site
    assert "--size-chapter: 96px" in phone
    assert "font-size: calc(64px / 0.7)" in _rule(site, ".chapter h2")
    assert "font-size: calc(40px / 0.7)" in phone
    # The accent word in Cormorant italic at the heading's real size (0.7 of the small caps).
    accent = _rule(site, ".chapter h2 .accent")
    assert "font-size: 0.7em" in accent
    accents = _rule(site, "h1 em,\nh2 em,\n.accent")
    assert "font-family: var(--font-serif)" in accents
    assert "font-style: italic" in accents
    faq = FAQ_CSS.read_text(encoding="utf-8")
    assert "font-size: calc(150px / 0.7)" in _rule(faq, ".chapter--faq h2")
    assert "font-size: calc(60px / 0.7)" in _phone_part(faq)


# AC5


def test_no_paper_gap_between_the_contact_band_and_the_footer(client: Client) -> None:
    html = _home(client)

    # The contact band is the last part of the main, and the main has no bottom padding.
    main = re.search(r"<main\b.*?</main>", html, re.DOTALL)
    assert main
    after_contact = main.group(0).split(_section(html, "contact"), 1)[1]
    assert "<section" not in after_contact
    assert "<p" not in after_contact
    assert "padding: 0" in _rule(_site(), ".site-main--one-page")
    assert "margin-bottom" not in _rule(
        CONTACT_CSS.read_text(encoding="utf-8"), ".chapter--contact"
    )


# AC6


def test_home_still_makes_exactly_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        _home(client)
