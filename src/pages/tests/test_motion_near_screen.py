"""mobile-smoothness T4: motion only near the screen (issue #144, AC1 to AC4).

The motion runs in a browser; the browser check of the issue shows it. These tests pin what the
stylesheet and the three scripts hold: the zoom of a photo paused unless its box is near the
screen, the hero's frame loop stopped while the hero is off screen, and the language switch
measuring once per frame at most.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

STATIC = Path(settings.SRC_DIR) / "static"


def _read(*parts: str) -> str:
    return STATIC.joinpath(*parts).read_text(encoding="utf-8")


def _code(name: str) -> str:
    """A script without its comments, so a word in a comment never passes a test."""
    script = re.sub(r"/\*.*?\*/", "", _read("js", name), flags=re.DOTALL)
    return re.sub(r"(?m)//.*$", "", script)


def _compact(css: str) -> str:
    """The stylesheet without comments and white space, so rules compare as written."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", "", css)


def _rules() -> list[tuple[str, str]]:
    """Every innermost rule of motion.css as (selector, body), with @media wrappers left out."""
    return [
        (selector, body)
        for selector, body in re.findall(
            r"([^{}]+)\{([^{}]*)\}", _compact(_read("css", "motion.css"))
        )
        if not selector.startswith("@")
    ]


ZOOM = "html.motion.media__boximg"
NEAR = "html.motion.media__box.is-nearimg"


# AC1 (M17): the zoom is paused, and runs while the box is near the screen


def test_zoom_rule_keeps_its_animation_line_and_is_paused() -> None:
    rules = _rules()
    bodies = [body for selector, body in rules if selector == ZOOM]

    # One rule only with this selector: the animation shorthand and the pause live together.
    assert len(bodies) == 1
    body = bodies[0]
    assert "animation:motion-zoom22sease-in-outinfinitealternate;" in body
    assert "animation-play-state:paused;" in body
    # The pause comes after the shorthand, which would reset it.
    assert body.index("animation-play-state") > body.index("animation:motion-zoom")


def test_zoom_runs_again_in_a_box_that_is_near_the_screen() -> None:
    rules = _rules()
    bodies = [body for selector, body in rules if selector == NEAR]

    assert len(bodies) == 1
    assert "animation-play-state:running" in bodies[0]
    # After the paused rule, so it wins over it; both inside the one media block.
    selectors = [selector for selector, _ in rules]
    assert selectors.index(NEAR) > selectors.index(ZOOM)
    assert _compact(_read("css", "motion.css")).count("@media") == 1


def test_zoom_keyframes_stay_as_they_were() -> None:
    css = _compact(_read("css", "motion.css"))

    assert "@keyframesmotion-zoom{from{transform:scale(1.02);}to{transform:scale(1.09);}}" in css


def test_reveal_script_marks_boxes_near_the_screen_with_one_observer() -> None:
    code = _code("reveal.js")

    assert 'rootMargin: "10% 0px"' in code
    assert '"is-near"' in code
    assert 'querySelectorAll(".media__box")' in code
    assert code.count("rootMargin") == 1
    # The observer is created after the class "motion" is set.
    assert code.index('classList.add("motion")') < code.index("rootMargin")


def test_reveal_script_toggles_the_class_from_what_the_observer_reports() -> None:
    code = _code("reveal.js")

    assert "isIntersecting" in code
    assert "classList.toggle(" in code


# AC2 (M18): the hero's loop stops while the hero is off screen once the intro is over


def test_hero_script_watches_the_hero_with_an_observer() -> None:
    assert "IntersectionObserver" in _code("hero.js")


def test_hero_tick_cancels_its_frame_and_goes_idle_when_off_screen_after_the_intro() -> None:
    code = _code("hero.js")
    tick = code.split("function tick()", 1)[1].split("\n  }\n", 1)[0]

    assert "cancelAnimationFrame" in tick
    assert "idle" in tick
    assert "skipped" in tick
    assert "onScreen" in tick


def test_hero_resize_handler_does_not_measure_while_idle() -> None:
    code = _code("hero.js")
    handler = code.split('addEventListener("resize"', 1)[1].split("measure();", 1)[0]

    assert "request" in handler
    assert "idle" in handler


def test_hero_script_stays_under_14000_bytes() -> None:
    assert len(_read("js", "hero.js").encode()) < 14_000


# AC3 (M19): the language switch asks for one frame at a time


def test_language_switch_updates_in_an_animation_frame_on_scroll() -> None:
    code = _code("lang-switch.js")

    assert "requestAnimationFrame" in code
    assert "passive: true" in code
    assert re.search(r'addEventListener\(\s*"scroll"\s*,\s*(?!update\b)', code)


def test_language_switch_still_updates_at_once_on_the_link_events() -> None:
    code = _code("lang-switch.js")

    for name in ("pointerdown", "focus", "click"):
        assert f'"{name}"' in code, name


def test_language_switch_stays_under_40_lines() -> None:
    assert len(_read("js", "lang-switch.js").splitlines()) < 40


# AC1 (M20): under reduced motion the script returns before any observer


def test_reveal_script_returns_under_reduced_motion_before_any_observer() -> None:
    code = _code("reveal.js")

    assert "prefers-reduced-motion: reduce" in code
    assert code.index("prefers-reduced-motion: reduce") < code.index("rootMargin")


# AC4 (M21): one query for each page


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_page_still_makes_one_query(
    path: str, client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
