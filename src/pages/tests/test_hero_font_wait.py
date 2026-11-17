"""The hero waits for the letter's font (issue 129, AC1 to AC5 and AC8).

The wait runs in a browser; the browser check of the issue shows it. These tests pin what the
page, the stylesheet and the script must hold for it.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import Settings

pytestmark = pytest.mark.django_db

STATIC = Path(settings.SRC_DIR) / "static"

CORMORANT = (
    "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,500;1,300"
    "&display=block"
)
BE_VIETNAM = "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400&display=swap"
PRECONNECT = ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]
SERIF_STACK = '"Cormorant Garamond", "Times New Roman", Times, serif'


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "link":
            self.links.append(dict(attrs))


def _font_links(html: str) -> tuple[list[str], list[str]]:
    parser = _Links()
    parser.feed(html)
    preconnect = [link["href"] or "" for link in parser.links if link.get("rel") == "preconnect"]
    sheets = [
        link["href"] or ""
        for link in parser.links
        if link.get("rel") == "stylesheet" and "fonts.googleapis.com" in (link["href"] or "")
    ]
    return preconnect, sheets


def _css() -> str:
    return (STATIC / "css" / "site.css").read_text(encoding="utf-8")


def _script() -> str:
    return (STATIC / "js" / "hero.js").read_text(encoding="utf-8")


def _code() -> str:
    """The script without its comments, so a word in a comment never passes a test."""
    script = re.sub(r"/\*.*?\*/", "", _script(), flags=re.DOTALL)
    return re.sub(r"(?m)//.*$", "", script)


def _tail() -> str:
    """The code after choose(): where the font wait is wired."""
    code = _code()
    return code[code.rindex("function choose") :]


# M1 (AC1)


@pytest.mark.parametrize("address", ["/", "/vi/", "/no-such-page/"])
def test_every_page_has_the_two_font_stylesheets_in_order_and_two_preconnects(
    client: Client, settings: Settings, address: str
) -> None:
    settings.DEBUG = False

    html = client.get(address).content.decode()
    preconnect, sheets = _font_links(html)

    assert preconnect == PRECONNECT
    assert sheets == [CORMORANT, BE_VIETNAM]


def test_the_template_writes_the_ampersand_as_an_entity() -> None:
    template = (Path(settings.SRC_DIR) / "templates" / "base.html").read_text(encoding="utf-8")

    assert CORMORANT.replace("&", "&amp;") in template


# M2 (AC2)


def test_serif_stack_is_cormorant_then_times_in_the_css() -> None:
    match = re.search(r"--font-serif:\s*([^;]+);", _css())

    assert match
    assert match.group(1).strip() == SERIF_STACK


def test_hero_font_constant_is_cormorant_then_times() -> None:
    assert f"var FONT = '500 SIZEpx {SERIF_STACK}';" in _script()


def test_georgia_is_in_neither_the_css_nor_the_script() -> None:
    assert "Georgia" not in _css()
    assert "Georgia" not in _script()


# M3 (AC3)


def test_script_adds_and_removes_the_wait_class_and_loads_the_font_with_a_timeout() -> None:
    code = _tail()

    assert 'classList.add("hero-wait")' in code
    assert 'classList.remove("hero-wait")' in code
    assert 'document.fonts.load(font(64), LETTER + "O")' in code
    assert "window.setTimeout(go, 3000)" in code


def test_go_runs_its_work_once_through_a_ready_flag() -> None:
    code = _tail()
    match = re.search(r"function go\(\)\s*\{(.*?)\n  \}", code, re.DOTALL)

    assert match, "no go() function after choose()"
    body = match.group(1)
    assert re.search(r"if\s*\(\s*ready\s*\)\s*\{?\s*return", body)
    assert re.search(r"ready\s*=\s*true", body)
    assert 'classList.remove("hero-wait")' in body
    assert "choose();" in body


def test_flight_class_is_added_with_the_wait_unless_less_motion_before_the_font_load() -> None:
    code = _tail()
    flight = code.index('classList.add("hero-flight")')
    wait = code.index('classList.add("hero-wait")')
    load = code.index("document.fonts.load(")

    assert flight < load
    assert wait < load
    guard = code[max(0, flight - 120) : flight]
    assert re.search(r"!\s*lessMotion\.matches", guard)


def test_last_statement_of_the_script_is_not_a_bare_choose() -> None:
    code = _code().rstrip()

    assert code.endswith("})();")
    before_end = code[: -len("})();")].rstrip()
    assert not before_end.endswith("choose();")


# M4 (AC3, no document.fonts)


def test_without_document_fonts_go_runs_at_once_and_the_wait_class_is_never_added() -> None:
    code = _tail()
    start = code.index("document.fonts.load(font(64)")
    check = code.rindex("if (document.fonts", 0, start)
    block = code[check:]
    else_at = re.search(r"\}\s*else\s*\{\s*go\(\);", block)

    assert else_at, "no else branch that calls go()"
    assert 'classList.add("hero-wait")' not in block[else_at.start() :]


# M5 (AC4)


def test_late_font_remeasures_the_running_intro_before_go() -> None:
    code = _tail()
    handler = code[code.index("document.fonts.load(font(64)") :]

    assert re.search(
        r"\.then\(\s*function\s*\(\)\s*\{\s*if\s*\(\s*ready\s*&&\s*request\s*\)\s*\{\s*"
        r"measure\(\);\s*\}\s*go\(\);",
        handler,
    )


# M6 (AC5)


def test_still_letter_is_hidden_while_the_script_waits() -> None:
    match = re.search(r"(?m)^html\.hero-wait\s+\.hero__letter\s*\{([^}]*)\}", _css())

    assert match, "no html.hero-wait .hero__letter rule"
    assert re.search(r"visibility:\s*hidden", match.group(1))


# Code review: the wait must not be cut short or forget input.


def test_a_motion_change_during_the_wait_does_not_start_the_intro_early() -> None:
    code = _code()

    assert 'lessMotion.addEventListener("change", choose)' not in code
    assert re.search(
        r'lessMotion\.addEventListener\(\s*"change",\s*function\s*\(\)\s*\{\s*'
        r"ready\s*&&\s*choose\(\);?\s*\}",
        code,
    )


def test_input_during_the_wait_still_skips_the_intro() -> None:
    code = _code()

    assert re.search(
        r"skipped\s*=\s*window\.pageYOffset > 40 \|\| !!target \|\| \(skipped && !ready\);", code
    )
    # ready turns true only after go() has chosen, so a later start() forgets old input.
    body = code[code.index("function go()") :]
    assert body.index("choose();") < body.index("ready = true")


# M9 (AC8)


def test_script_stays_under_the_size_limit() -> None:
    assert len((STATIC / "js" / "hero.js").read_bytes()) < 14_000
