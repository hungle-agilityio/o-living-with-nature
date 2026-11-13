"""design-match T2: the "Ở" intro plays by itself, and the fixed header (issue AC1 to AC7).

The intro runs in a browser; the browser check of the issue shows it. These tests pin what the
page, the stylesheet and the script must hold for it, and for the still hero and solid header
that show without it.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db

STATIC = Path(settings.SRC_DIR) / "static"


def _css() -> str:
    return (STATIC / "css" / "site.css").read_text(encoding="utf-8")


def _script() -> str:
    return (STATIC / "js" / "hero.js").read_text(encoding="utf-8")


def _code() -> str:
    """The script without its comments, so a word in a comment never passes a test."""
    script = re.sub(r"/\*.*?\*/", "", _script(), flags=re.DOTALL)
    return re.sub(r"(?m)//.*$", "", script)


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


def _still(css: str) -> str:
    """Every rule that holds before the script sets the intro class."""
    return css.split("html.hero-flight", 1)[0]


def _phones(css: str) -> str:
    match = re.search(r"@media \(max-width: 760px\) \{(.*?)\n\}", css, re.DOTALL)
    assert match
    return match.group(1)


def _hero(client: Client, address: str = "/?t=day") -> str:
    response = client.get(address)
    assert response.status_code == 200
    match = re.search(r'<section id="hero".*?</section>', response.content.decode(), re.DOTALL)
    assert match
    return match.group(0)


# AC1: the intro plays once on load, driven by time


def test_intro_is_driven_by_time_not_by_scroll() -> None:
    code = _code()

    assert "requestAnimationFrame" in code
    assert "performance.now" in code
    # No progress read from the scroll position of the hero any more.
    assert "travel" not in code
    assert "TITLE_START" not in code


def test_intro_has_the_timings_of_the_design() -> None:
    code = _code()

    assert re.search(r"GROW_START\s*=\s*0\.6\b", code)
    assert re.search(r"GROW_END\s*=\s*5\.6\b", code)
    assert re.search(r"INTRO_END\s*=\s*7\.0\b", code)
    assert re.search(r"LINE_DELAY\s*=\s*0\.15\b", code)
    # The dictionary line fades out in the first sixth of the growth.
    assert re.search(r"FOOT_END\s*=\s*1\s*/\s*6\b", code)


def test_letter_grows_with_the_epic_one_curve_on_an_ease_in_out() -> None:
    code = _code()

    assert re.search(r"MAX_SCALE\s*=\s*70\b", code)
    assert "Math.pow(maxScale, e)" in code
    # The sine ease-in-out over the time of the growth.
    assert "Math.cos(Math.PI * t)" in code
    assert "easeInOut(time)" in code


def test_heading_rises_line_by_line() -> None:
    code = _code()
    css = _css()

    assert '"hero__ln"' in code
    assert "LINE_DELAY * index" in code
    assert "translateY(" in code
    # Each line is clipped so it moves up from hidden; the second sits on the right.
    assert "overflow: hidden" in _rule(css, "html.hero-flight .hero__ln")
    assert "align-self: flex-end" in _rule(css, "html.hero-flight .hero__ln:last-child")
    # The shade fades in with the heading.
    shade = re.findall(r"(?m)^html\.hero-flight \.hero__shade\s*\{([^}]*)\}", css)
    assert any("opacity: var(--hero-title)" in rule for rule in shade)


# AC2: one screen, the end state


def test_hero_is_one_screen_with_no_stage_and_no_sticky_frame() -> None:
    css = _css()

    flight = _rule(css, "html.hero-flight .hero")
    assert "height: 100svh" in flight
    assert "min-height: 560px" in flight
    assert "330vh" not in css
    assert "sticky" not in _rule(css, "html.hero-flight .hero__frame")


def test_heading_is_150px_capitals_and_60px_on_phones() -> None:
    css = _css()

    assert "font-size: calc(var(--size-headline) / 0.7)" in _rule(
        css, "html.hero-flight .hero__title h1"
    )
    assert re.search(r"--size-headline:\s*150px", css)
    assert re.search(r"--size-headline:\s*60px", _phones(css))


def test_line_is_cormorant_26px_and_20px_on_phones() -> None:
    css = _css()

    line = _rule(css, ".hero__line")
    assert "font-family: var(--font-serif)" in line
    assert "font-size: var(--size-hero-line)" in line
    assert re.search(r"--size-hero-line:\s*26px", css)
    assert re.search(r"--size-hero-line:\s*20px", _phones(css))


def test_cue_shows_bottom_right_in_paper_after_the_intro(client: Client) -> None:
    css = _css()

    cue = _rule(css, "html.hero-flight .hero__cue")
    assert "position: absolute" in cue
    assert "right:" in cue
    assert "color: var(--paper)" in cue
    assert "opacity: var(--hero-cue)" in cue
    assert "CUE_START" in _code()
    # The cue is its own element, no longer inside the dictionary line that fades out.
    foot = re.search(r'<div class="hero__foot">.*?</div>\s*</div>', _hero(client), re.DOTALL)
    assert foot and "Scroll, and come in" not in foot.group(0)


def test_loop_pauses_while_the_hero_is_off_screen() -> None:
    code = _code()

    assert "video.pause()" in code
    assert "video.play()" in code
    assert 'show("playing", onScreen' in code


# AC3: input skips, nothing blocks, nothing stored


def test_any_input_jumps_to_the_end_state() -> None:
    code = _code()

    for name in ("wheel", "touchstart", "keydown", "pointerdown", "scroll"):
        assert f'"{name}"' in code, name
    assert "passive: true" in code


def test_scrolling_is_never_blocked() -> None:
    code = _code()
    css = _css()

    assert "preventDefault" not in code
    assert "passive: false" not in code
    assert "overflow: hidden" not in _rule(css, "body")
    assert not re.search(r"html\.hero-flight\s*(body)?\s*\{[^}]*overflow", css)


def test_page_opened_lower_or_at_a_chapter_shows_the_end_state() -> None:
    code = _code()

    assert "location.hash" in code
    assert "pageYOffset" in code
    assert re.search(r"skipped\s*=\s*window\.pageYOffset > 40 \|\| !!target", code)


def test_no_storage_of_any_kind() -> None:
    code = _script()

    for sign in ("localStorage", "sessionStorage", "document.cookie", "indexedDB", "caches"):
        assert sign not in code, sign


# AC4: the still hero


def test_no_hero_files_means_no_intro() -> None:
    # The script returns before the intro class when there is no video.
    code = _code()

    guard = code.index("if (!frame || !video")
    assert guard < code.index('"hero-flight"')


def test_still_hero_has_no_video_and_keeps_the_heading(
    client: Client, mocker: MockerFixture
) -> None:
    css = _still(_css())

    assert re.search(
        r"\.hero__video,\s*\.hero__canvas,\s*\.hero__shade\s*\{[^}]*display:\s*none", css
    )
    real = finders.find
    mocker.patch(
        "pages.hero.finders.find",
        side_effect=lambda path: None if path == "media/hero/day.mp4" else real(path),
    )
    section = _hero(client)
    assert "<video" not in section
    assert "<h1" in section
    assert "rented whole, by the month." in section


# AC5: the header


def test_header_is_a_fixed_solid_bar_without_the_script() -> None:
    css = _css()

    header = _rule(_still(css), ".site-header")
    assert "position: fixed" in header
    assert "top: 0" in header
    assert "border-bottom: 1px solid var(--line)" in header
    assert "color-mix(in srgb, var(--ground) 94%, transparent)" in header
    assert "color: var(--ink)" in header
    # The page starts under the bar.
    body = re.findall(r"(?m)^body\s*\{([^}]*)\}", _still(css))
    assert any("padding-top: var(--header-height)" in rule for rule in body)
    assert re.search(r"--header-height:\s*64px", css)


def test_header_is_clear_over_the_hero_and_solid_once_it_has_left() -> None:
    css = _css()
    code = _code()

    clear = _rule(css, "html.hero-flight:not(.hero-past) .site-header")
    assert "background: transparent" in clear
    assert "border-bottom-color: transparent" in clear
    assert re.search(r"html\.hero-over \.site-header\s*\{[^}]*color:\s*var\(--paper\)", css)
    assert '"hero-past"' in code
    assert '"hero-over"' in code
    # The old header lift that followed the stage is gone.
    assert "header.style.transform" not in code


def test_phone_menu_still_needs_no_script(client: Client) -> None:
    html = client.get("/").content.decode()
    header = html[html.index("<header") : html.index("</header>")]

    assert "<details" in header
    assert "<summary>Menu</summary>" in header
    assert "<script" not in header


def test_menu_jump_lands_under_the_fixed_header() -> None:
    chapter = _rule(_css(), ".chapter")

    assert "scroll-margin-top: calc(var(--header-height) + var(--space-4))" in chapter


# AC6: the chip


def test_chip_sits_top_right_under_the_header_in_every_state(client: Client) -> None:
    css = _css()

    still = _rule(_still(css), ".hero__chip")
    assert "top: calc(84px - var(--header-height))" in still
    assert "right: var(--space-2)" in still
    assert "bottom: auto" in still
    assert "top: 84px" in _rule(css, "html.hero-flight .hero__chip")
    assert "Illustrative video" in _hero(client)


# AC7: small script, one query


def test_script_is_small_plain_and_deferred(client: Client) -> None:
    script = _script()

    assert len(script.encode()) < 14_000
    for sign in ("import ", "require(", "http://", "https://", "eval("):
        assert sign not in script, sign
    assert '<script src="/static/js/hero.js" defer></script>' in client.get("/").content.decode()


@pytest.mark.parametrize("address", ["/", "/?t=night"])
def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(address)

    assert response.status_code == 200
