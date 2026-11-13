"""time-of-day-live T1: a slower, even intro and the night letter (issue #75, AC1 to AC7).

The intro runs in a browser; the browser check of the issue shows it. These tests pin the
constants and the curve of the script, check the curve numerically, and pin the outline of the
letter in the night theme, in the stylesheet and on the canvas.
"""

import math
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

STATIC = Path(settings.SRC_DIR) / "static"
NIGHT = 'body[data-daypart="night"] .hero__letter'
PAPER_55 = "rgba(233, 226, 211, 0.55)"


def _script() -> str:
    return (STATIC / "js" / "hero.js").read_text(encoding="utf-8")


def _code() -> str:
    """The script without its comments, so a word in a comment never passes a test."""
    script = re.sub(r"/\*.*?\*/", "", _script(), flags=re.DOTALL)
    return re.sub(r"(?m)//.*$", "", script)


def _css() -> str:
    return (STATIC / "css" / "site.css").read_text(encoding="utf-8")


def _number(name: str) -> float:
    match = re.search(rf"\b{name}\s*=\s*([0-9.]+)(?:\s*/\s*([0-9.]+))?\s*;", _code())
    assert match, f"no {name}"
    value = float(match.group(1))
    return value / float(match.group(2)) if match.group(2) else value


def _ease(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def _size(seconds: float, max_scale: float = 70) -> float:
    start, end = _number("GROW_START"), _number("GROW_END")
    t = min(1.0, max(0.0, (seconds - start) / (end - start)))
    return float(max_scale ** _ease(t))


# AC1: the constants of the slower intro


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("GROW_START", 0.6),
        ("GROW_END", 5.6),
        ("INTRO_END", 7.0),
        ("LINE_DELAY", 0.15),
        ("LINE_TIME", 1.0),
        ("CUE_START", 6.9),
        ("FOOT_END", 1 / 6),
    ],
)
def test_intro_runs_on_the_constants_of_the_design(name: str, value: float) -> None:
    assert _number(name) == pytest.approx(value)


# AC2: the size is maxScale to the power of a sine ease


def test_size_is_max_scale_to_the_power_of_a_sine_ease() -> None:
    code = _code()

    assert "Math.pow(maxScale, e)" in code
    assert "-(Math.cos(Math.PI * t) - 1) / 2" in code
    assert re.search(r"MAX_SCALE\s*=\s*70\b", code)
    # The wide-screen rule stays.
    assert "Math.max(MAX_SCALE, (1.15 * width) / (side[1] * size))" in code


def test_power_and_cubic_ease_are_gone() -> None:
    code = _code()

    assert "POWER" not in code
    assert "4 * t * t * t" not in code
    assert "Math.pow(-2 * t + 2, 3)" not in code


def test_anchor_moves_to_the_centre_by_the_same_ease() -> None:
    code = _code()

    assert "(width / 2 - anchorX) * e" in code
    assert "(height / 2 - anchorY) * e" in code


# AC3: the curve, checked numerically on the formula of the script


@pytest.mark.parametrize(("seconds", "power"), [(1.6, 0.095), (3.1, 0.5), (4.6, 0.905)])
def test_size_at_three_moments_is_within_15_percent(seconds: float, power: float) -> None:
    expected = 70**power
    assert abs(_size(seconds) - expected) / expected < 0.15


def test_no_frame_of_the_growth_multiplies_the_size_by_more_than_1_06() -> None:
    start, end = _number("GROW_START"), _number("GROW_END")
    frames = int((end - start) * 60) + 1
    sizes = [_size(start + i / 60) for i in range(frames + 1)]

    assert max(b / a for a, b in zip(sizes, sizes[1:], strict=False)) <= 1.06
    assert sizes[-1] == pytest.approx(70)


# AC5: the still letter has a Paper outline at night only


def test_still_letter_has_the_paper_outline_at_night() -> None:
    css = _css()
    match = re.search(rf"(?m)^{re.escape(NIGHT)}\s*\{{([^}}]*)\}}", css)

    assert match, f"no {NIGHT} rule"
    assert f"-webkit-text-stroke: 1.5px {PAPER_55}" in match.group(1)
    # After the first .hero__letter rule, so it wins over it.
    assert css.index(NIGHT) > css.index(".hero__letter {")


def test_outline_is_only_in_the_night_theme() -> None:
    css = _css()

    assert css.count("-webkit-text-stroke") == 1
    # No new rule for the night body alone.
    assert len(re.findall(r'(?m)^body\[data-daypart="night"\]\s*\{', css)) == 1


# AC6: the canvas strokes the letter at night during the first fifth of the growth


def test_canvas_strokes_the_letter_at_night_only() -> None:
    code = _code()

    assert "strokeText(LETTER, originX, originY)" in code
    assert '"rgba(233, 226, 211, "' in code
    assert re.search(r"0\.55\s*\*\s*clamp\(1 - time / 0\.2\)", code)
    # 1.5 CSS px on screen at any size of the letter.
    assert "1.5 / scale" in code


def test_theme_is_read_on_every_frame() -> None:
    code = _code()
    tick = code.split("function tick()", 1)[1].split("\n  }\n", 1)[0]

    assert 'document.body.getAttribute("data-daypart") === "night"' in tick


# AC7: one small plain deferred script, one query


def test_script_stays_small_and_plain() -> None:
    script = _script()

    assert len(script.encode()) < 14_000
    for sign in ("import ", "require(", "http://", "https://", "eval("):
        assert sign not in script, sign


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        response = client.get("/")

    assert response.status_code == 200
    assert '<script src="/static/js/hero.js" defer>' in response.content.decode()
