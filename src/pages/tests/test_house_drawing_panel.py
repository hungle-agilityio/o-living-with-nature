"""Open a room from the plan (house-plan-2d spec, task T2, issue #161).

The row names (M13, M15, M16, M17, M19, M21) are those of the "Test matrix rows" of the issue.
M14 and the screenshot half of M17 are browser checks, M18 is manual, M22 is the whole suite.
These tests read the script and the stylesheet as text and use the test client for the queries.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

SCRIPT = Path(settings.SRC_DIR) / "static" / "js" / "floor-plan.js"
CSS = Path(settings.SRC_DIR) / "static" / "css" / "chapters" / "house.css"


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _css() -> str:
    """The stylesheet with comments dropped and every run of white space made one space."""
    text = re.sub(r"/\*.*?\*/", " ", CSS.read_text(encoding="utf-8"), flags=re.S)
    return " ".join(text.split())


def _blocks(css: str) -> list[tuple[str, str]]:
    """Every `selector { declarations }` pair at any depth, as (selector, body)."""
    return [(s.strip(), b.strip()) for s, b in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]


def _has_rule(css: str, selector: str, declaration: str) -> bool:
    """True when one rule has this selector (in its list) and this declaration."""
    wanted = " ".join(declaration.split()).rstrip(";")
    for sel, body in _blocks(css):
        selectors = [" ".join(part.split()) for part in sel.split(",")]
        declarations = [" ".join(d.split()) for d in body.split(";") if d.strip()]
        if selector in selectors and wanted in declarations:
            return True
    return False


def _media(css: str, query: str) -> str:
    """The body of the first `@media (query) { ... }` block, with its braces balanced."""
    start = css.find("@media " + query)
    assert start != -1, f"no @media {query}"
    open_at = css.index("{", start)
    depth = 0
    for i in range(open_at, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[open_at + 1 : i]
    raise AssertionError(f"@media {query} is not closed")


# M13 (AC1)


def test_m13_click_on_a_room_link_opens_it_and_marks_its_parts() -> None:
    script = _script()

    assert "a.plan__room" in script
    assert "click" in script
    assert "preventDefault" in script
    for word in ('"js"', '"is-open"', '"is-on"', "aria-current", '"true"'):
        assert word in script, word
    # aria-current goes to the two links only: it must not be set on the item
    assert "aria-current" in script
    assert script.count("aria-current") <= 3
    # a modified click or another button keeps the link's own behaviour
    for key in ("metaKey", "ctrlKey", "shiftKey", "altKey", "button"):
        assert key in script, key
    # Space on a link calls the opening function, as an SVG link has no click()
    assert '" "' in script or "Space" in script


# M15 (AC5)


def test_m15_bar_is_hidden_until_a_room_is_open_and_hint_hides_when_open() -> None:
    css = _css()

    assert _has_rule(css, ".plan.js:not(.is-open) .plan__bar", "display: none")
    assert _has_rule(css, ".plan.js.is-open .plan__hint", "display: none")


# M16 (AC2, AC4)


def test_m16_arrows_wrap_around_the_rooms() -> None:
    script = _script()

    assert "% rooms.length" in script
    assert "ArrowRight" in script
    assert "ArrowLeft" in script


def test_m16_escape_closes_and_focus_goes_to_the_shown_link() -> None:
    script = _script()

    assert "Escape" in script
    assert "getClientRects" in script
    assert "focus(" in script


def test_m16_keys_are_ignored_in_form_fields_and_while_a_dialog_is_open() -> None:
    script = _script()

    assert "dialog[open]" in script
    assert "isContentEditable" in script
    for tag in ("INPUT", "TEXTAREA", "SELECT"):
        assert tag in script.upper(), tag


def test_m16_the_address_opens_a_room_without_motion() -> None:
    script = _script()

    assert "location.hash" in script
    assert "#room-" in script
    assert "is-instant" in script
    assert "is-revealed-now" in script
    assert "is-revealed" in script
    assert "window.PLAN_OPEN" not in script


def test_m16_phone_scroll_keeps_the_header_gap_and_honours_reduced_motion() -> None:
    script = _script()

    assert "scrollBy" in script
    assert "r.top - 84" in script
    assert "prefers-reduced-motion: reduce" in script
    assert '"smooth"' in script
    assert '"auto"' in script


def test_m16_script_returns_early_without_the_figure_or_the_close_button() -> None:
    script = _script()

    assert "#floor-plan" in script or "floor-plan" in script
    assert ".plan__close" in script


# M17 (AC3, integration part)


def test_m17_phone_sheet_is_fixed_and_at_most_76vh_high() -> None:
    narrow = " ".join(_media(_css(), "(max-width: 860px)").split())

    assert _has_rule(narrow, ".plan.js.is-open .plan__panel", "position: fixed")
    assert _has_rule(narrow, ".plan.js.is-open .plan__panel", "max-height: 76vh")


def test_m17_sheet_covers_the_contact_bar_and_the_header() -> None:
    css = _css()

    assert _has_rule(css, ".plan.js.is-open .plan__panel", "z-index: 60") or any(
        "z-index: 60" in body and ".plan__panel" in sel for sel, body in _blocks(css)
    )


# M19 (AC6)


def test_m19_script_is_small_plain_and_strict() -> None:
    script = _script()

    assert len(script.encode()) < 4_000
    for sign in (
        "import ",
        "require(",
        "innerHTML",
        "eval(",
        "localStorage",
        "sessionStorage",
        "document.cookie",
    ):
        assert sign not in script, sign
    assert '"use strict"' in script


def test_m19_reduced_motion_removes_both_animations() -> None:
    css = _css()

    assert "@keyframes plan-in" in css
    assert "@keyframes plan-up" in css
    # a block of its own, after the 860 px block, so it comes later than the rules it cancels
    wide = css.index("@media (max-width: 860px)")
    marker = "@media (prefers-reduced-motion: reduce) { .plan.js .plan-room.is-on"
    assert marker in css[wide:], "no reduced-motion block for the plan after the 860px block"
    block = _media(css[css.index(marker) :], "(prefers-reduced-motion: reduce)")
    assert ".plan.js .plan-room.is-on" in block
    assert ".plan.js.is-open .plan__panel" in block
    assert "animation: none" in block


def test_m19_instant_class_cancels_the_animations() -> None:
    css = _css()

    selectors = ".plan.js.is-instant .plan-room.is-on, .plan.js.is-open.is-instant .plan__panel"
    assert _has_rule(css, ".plan.js.is-instant .plan-room.is-on", "animation: none")
    assert selectors in css


# M21 (AC7)


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_m21_home_pages_make_exactly_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
