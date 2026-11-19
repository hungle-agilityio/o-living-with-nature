"""The enquiry form on its own Paper panel with one filled button (issue #171).

Spec: contact-one-place AC9 to AC14.

M14 (browser) and M22 (check.sh) have no test here.
"""

import re

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

CONTACT_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "contact.css"
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
REDUCED = "@media (prefers-reduced-motion: reduce)"

SEND_EN = (
    '<button class="button button--send" type="submit">Send message '
    '<span class="button--send__arrow" aria-hidden="true">→</span></button>'
)
SEND_VI = (
    '<button class="button button--send" type="submit">Gửi lời nhắn '
    '<span class="button--send__arrow" aria-hidden="true">→</span></button>'
)


@pytest.fixture(autouse=True)
def owner_values() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=13,
        price_to_million=14,
        phone="0945 384 500",
        whatsapp="0945 384 500",
        zalo="0945 384 500",
        owner_first_name="Bún",
        reply_time="within an hour",
    )


def _css() -> str:
    return re.sub(r"/\*.*?\*/", "", CONTACT_CSS.read_text(encoding="utf-8"), flags=re.DOTALL)


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _rules(css: str) -> list[tuple[set[str], str]]:
    """Every rule of the text as (its comma-separated selectors, its declarations)."""
    found: list[tuple[set[str], str]] = []
    for match in RULE.finditer(css):
        selectors = {_squash(part) for part in match.group(1).split(",")}
        found.append((selectors, _squash(match.group(2))))
    return found


def _body(css: str, *selectors: str) -> str:
    """The declarations of the rule that lists all the given selectors."""
    for parts, body in _rules(css):
        if set(selectors) <= parts:
            return body
    pytest.fail(f"no rule for {', '.join(selectors)}")


def _second_760_block(css: str) -> str:
    starts = [m.start() for m in re.finditer(r"@media \(max-width: 760px\) \{", css)]
    assert len(starts) >= 2, "no second 760px block in contact.css"
    block = css[starts[1] :]
    nxt = block.find("@media", 1)
    return block if nxt == -1 else block[:nxt]


def _page(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


# M13 (AC1): the panel


def test_m13_enquiry_is_a_paper_panel_with_ink_text_and_no_top_border() -> None:
    body = _body(_css(), ".enquiry")

    assert "background: var(--paper)" in body
    assert "color: var(--band)" in body
    assert "padding: var(--space-5)" in body
    assert "border-radius: 4px" in body
    assert "border-top" not in body
    assert "padding-top" not in body


def test_m13_phone_panel_padding_is_smaller() -> None:
    body = _body(_second_760_block(_css()), ".enquiry")

    assert "padding: var(--space-4) var(--space-3)" in body


def test_m13_fields_use_ink_text_and_an_ink_line_at_35_percent() -> None:
    body = _body(_css(), ".enquiry input", ".enquiry select", ".enquiry textarea")

    assert "color: var(--band)" in body
    assert "border-bottom: 1px solid rgba(31, 42, 34, 0.35)" in body
    assert "var(--paper)" not in body
    assert "rgba(244, 240, 232" not in body


def test_m13_no_enquiry_or_send_button_rule_uses_the_theme_ink() -> None:
    checked = 0
    for selectors, body in _rules(_css()):
        if any(s.startswith((".enquiry", ".button--send")) for s in selectors):
            checked += 1
            assert "var(--ink)" not in body, f"{sorted(selectors)} uses var(--ink)"
    assert checked > 0


# M15 (AC1, AC4): the thanks sits on the same panel


def test_m15_sent_state_is_on_the_same_panel(client: Client) -> None:
    html = _page(client, "/?enquiry=sent")

    assert '<div class="enquiry enquiry--sent"' in html


# M16 (AC2): the button markup


def test_m16_english_button_has_the_arrow_span(client: Client) -> None:
    assert SEND_EN in _page(client, "/")


def test_m16_vietnamese_button_has_the_arrow_span(client: Client) -> None:
    assert SEND_VI in _page(client, "/vi/")


# M17 (AC2): the button styles


def test_m17_send_button_is_full_width_ink_filled_and_56px_high() -> None:
    body = _body(_css(), ".enquiry .button--send")

    assert "width: 100%" in body
    assert "min-height: 56px" in body
    assert "background: var(--band)" in body
    assert "color: var(--paper)" in body


def test_m17_hover_and_focus_fill_and_arrow_move() -> None:
    css = _css()

    hover = _body(css, ".enquiry .button--send:hover", ".enquiry .button--send:focus-visible")
    assert "#2f3d33" in hover
    arrow = _body(
        css,
        ".button--send:hover .button--send__arrow",
        ".button--send:focus-visible .button--send__arrow",
    )
    assert "translateX(5px)" in arrow


def test_m17_last_reduced_motion_block_stops_the_arrow() -> None:
    css = _css()
    last = css.rfind("@media")
    assert css[last:].startswith(REDUCED), "the last @media is not the reduced-motion block"
    last_arrow = [m.start() for m in re.finditer(r"^\.button--send__arrow\s*\{", css, re.MULTILINE)]
    assert last_arrow, "no top-level .button--send__arrow rule"
    assert last_arrow[-1] < last, "the reduced-motion block is not after the arrow rule"

    block = css[last:]
    assert "transition: none" in _body(block, ".button--send__arrow")
    still = _body(
        block,
        ".button--send:hover .button--send__arrow",
        ".button--send:focus-visible .button--send__arrow",
    )
    assert "transform: none" in still


def test_m17_first_reduced_motion_block_still_holds_only_the_contact_bar() -> None:
    css = _css()
    first = css.index(REDUCED)
    block = css[first : css.index("\n}\n", first)]

    assert ".contact-bar" in block
    assert "button--send" not in block
    assert ".enquiry" not in block


# M18 (AC3): chapter 05's buttons are outlines


def test_m18_chapter_buttons_are_outlines_and_the_phone_bar_call_stays_filled() -> None:
    css = _css()

    row = _body(css, ".chapter--contact .contact__row .button")
    assert "background: transparent" in row
    assert "color: var(--paper)" in row
    bar = _body(css, ".contact-bar .button:not(.button--secondary)")
    assert "background: var(--paper)" in bar


# M19 (AC4): errors on Paper


def test_m19_errors_use_the_terracotta_on_paper() -> None:
    css = _css()

    summary = _body(css, ".enquiry__summary")
    assert summary.count("#a4502a") >= 2
    assert "#a4502a" in _body(css, ".enquiry .field__error")
    underline = _body(
        css,
        ".enquiry .field--error input",
        ".enquiry .field--error select",
        ".enquiry .field--error textarea",
    )
    assert "border-bottom-color: #a4502a" in underline
    focused = _body(
        css,
        ".enquiry .field--error input:focus",
        ".enquiry .field--error select:focus",
        ".enquiry .field--error textarea:focus",
    )
    assert "border-bottom-color: #a4502a" in focused


def test_m19_no_light_error_colours_are_left() -> None:
    css = CONTACT_CSS.read_text(encoding="utf-8").lower()

    assert "#f0b48c" not in css
    assert "#e8a87c" not in css


# M21 (AC5): one query each


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_m21_one_query_each(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
