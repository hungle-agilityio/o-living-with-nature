"""The short header clock line for phones (mobile-smoothness spec, task T3, issue #143).

The row names (M13, M15, M16, M21) are those of the "Test matrix rows" of the issue. M14 is a
browser row and M22 is run by hand; they have no test here.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import language
from pages.daypart import DA_NANG

pytestmark = pytest.mark.django_db

STATIC = Path(django_settings.SRC_DIR) / "static"
SPAN_END = "</span>"


def _at(hour: int, minute: int) -> datetime:
    return datetime(2026, 11, 11, hour, minute, 5, tzinfo=DA_NANG)


def _freeze(mocker: MockerFixture, moment: datetime) -> None:
    mocker.patch("pages.context_processors.timezone.now", return_value=moment)
    mocker.patch("pages.views.timezone.now", return_value=moment)


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _header(html: str) -> str:
    match = re.search(r"<header\b.*?</header>", html, re.DOTALL)
    assert match
    return match.group(0)


def _rule_body(css: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert match, selector
    return match.group(1)


def _phone_block(css: str) -> str:
    start = css.index("@media (max-width: 760px)")
    depth = 0
    for index in range(css.index("{", start), len(css)):
        if css[index] == "{":
            depth += 1
        elif css[index] == "}":
            depth -= 1
            if depth == 0:
                return css[start : index + 1]
    raise AssertionError("unterminated phone block")


# M13


def test_home_header_holds_the_short_clock_right_after_the_long_one(
    client: Client, mocker: MockerFixture
) -> None:
    _freeze(mocker, _at(14, 52))

    header = _header(_get(client, "/"))

    assert '<span class="site-header__short label">14:52 · Day</span>' in header
    long_start = header.index('<span class="site-header__time label"')
    long_end = header.index(SPAN_END, long_start) + len(SPAN_END)
    assert "It's 14:52 in Hòa Xuân · Day" in header[long_start:long_end]
    assert header[long_end:].lstrip().startswith('<span class="site-header__short label">')


def test_vietnamese_header_holds_the_short_clock_with_the_vietnamese_label(
    client: Client, mocker: MockerFixture
) -> None:
    _freeze(mocker, _at(14, 52))

    header = _header(_get(client, "/vi/"))

    assert '<span class="site-header__short label">14:52 · Ban ngày</span>' in header


def test_css_hides_the_short_line_by_default_and_shows_it_on_phones() -> None:
    css = (STATIC / "css" / "site.css").read_text(encoding="utf-8")
    phone = _phone_block(css)
    outside = css.replace(phone, "")

    assert re.search(r"display:\s*none", _rule_body(outside, ".site-header__short"))
    assert re.search(r"display:\s*none", _rule_body(phone, ".site-header__time"))
    short = _rule_body(phone, ".site-header__short")
    assert re.search(r"display:\s*inline\b", short)
    assert re.search(r"white-space:\s*nowrap", short)
    assert re.search(r"align-items:\s*center", _rule_body(phone, ".site-header__left"))


# M15


def test_daypart_script_keeps_the_short_line_up_to_date() -> None:
    script = (STATIC / "js" / "daypart.js").read_text(encoding="utf-8")

    assert ".site-header__short" in script
    assert re.search(r"short\w*\.textContent", script)
    assert "clock" in script and "label" in script and "·" in script
    assert len(script.encode("utf-8")) < 4000


# M16


@pytest.mark.parametrize("lang", ["en", "vi"])
def test_header_without_a_daypart_has_neither_clock_span(lang: str) -> None:
    context: dict[str, Any] = {
        "lang": lang,
        "home_path": language.home_path(lang),
        "contact_path": language.contact_path(lang),
        "lang_switch": language.switch(lang),
        "daypart_labels": language.daypart_labels(lang),
    }

    html = render_to_string("includes/header.html", context)

    assert "site-header__time" not in html
    assert "site-header__short" not in html


# M21


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_home_pages_make_exactly_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
    assert "site-header__short" in response.content.decode()
