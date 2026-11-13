"""Load and reveal motion (design-match T3, spec AC13 to AC17).

The motion runs in a browser; the browser check of the issue shows the chapters after it. These
tests pin what the page links, what the script does and that every hiding rule of the stylesheet
needs the class the script sets, so without the script or under reduced motion all shows at once.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

STATIC = Path(settings.SRC_DIR) / "static"
SCRIPT = STATIC / "js" / "reveal.js"
MOTION_CSS = STATIC / "css" / "motion.css"
BASE = Path(settings.SRC_DIR) / "templates" / "base.html"
EASE = "cubic-bezier(0.2,0.7,0.2,1)"  # cubic-bezier(.2,.7,.2,1), as the formatter writes it


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _css() -> str:
    return MOTION_CSS.read_text(encoding="utf-8")


def _compact(css: str) -> str:
    """The stylesheet without comments and white space, so rules compare as written."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", "", css)


def _rules(css: str) -> list[tuple[str, str]]:
    """Every innermost rule as (selector, body), with @media wrappers left out."""
    return [
        (selector, body)
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", _compact(css))
        if not selector.startswith("@")
    ]


def _keyframes(css: str, name: str) -> str:
    match = re.search(
        r"@keyframes" + re.escape(name) + r"\{((?:[^{}]*\{[^{}]*\})*)\}", _compact(css)
    )
    assert match, name
    return match.group(1)


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


# AC1 (spec AC13): the files, linked from base.html, the class on <html>


def test_base_links_the_motion_stylesheet_and_the_deferred_script(client: Client) -> None:
    html = _home(client)

    assert '<link rel="stylesheet" href="/static/css/motion.css">' in html
    assert '<script src="/static/js/reveal.js" defer></script>' in html
    base = BASE.read_text(encoding="utf-8")
    assert "{% static 'css/motion.css' %}" in base
    assert "{% static 'js/reveal.js' %}" in base


def test_motion_files_are_found_as_static_files() -> None:
    assert finders.find("js/reveal.js")
    assert finders.find("css/motion.css")


def test_script_is_small_and_uses_no_library() -> None:
    script = _script()

    assert len(script.encode()) < 6_000
    for sign in ("import ", "require(", "http://", "https://", "jQuery", "eval("):
        assert sign not in script, sign


def test_script_sets_the_class_only_when_motion_is_welcome() -> None:
    script = _script()

    assert "document.documentElement" in script
    assert 'classList.add("motion")' in script
    assert "(prefers-reduced-motion: reduce)" in script
    # The class is set after the check, never before it.
    assert script.index("prefers-reduced-motion") < script.index('classList.add("motion")')


def test_every_hiding_rule_needs_the_class_set_by_the_script() -> None:
    rules = _rules(_css())

    assert rules
    for selector, body in rules:
        if selector.startswith(("from", "to")) or re.fullmatch(r"[\d.]+%", selector):
            continue  # a keyframe step, only used by a rule below
        for part in selector.split(","):
            assert part.startswith("html.motion"), part
        # A rule that hides, moves or animates is only ever under the class.
        assert body


def test_motion_rules_also_need_no_reduced_motion_preference() -> None:
    css = _compact(_css())

    assert css.startswith("@media(prefers-reduced-motion:no-preference){")
    assert css.endswith("}")
    assert css.count("@media") == 1


# AC2 (spec AC14): the header


def test_header_fades_in_and_moves_down_into_place() -> None:
    rules = dict(_rules(_css()))

    header = rules["html.motion.site-header"]
    assert "animation:motion-header-in0.9sease-out0.2sbackwards" in header
    steps = _keyframes(_css(), "motion-header-in")
    assert "from{opacity:0;transform:translateY(-12px);}" in steps
    assert "to{opacity:1;transform:none;}" in steps


# AC3 (spec AC15): the reveal of each block


def test_reveal_blocks_start_42px_lower_and_hidden() -> None:
    rules = dict(_rules(_css()))

    hidden = rules["html.motion.reveal"]
    assert "opacity:0" in hidden
    assert "transform:translateY(42px)" in hidden
    assert f"transition:opacity1.1s{EASE},transform1.1s{EASE}" in hidden
    shown = rules["html.motion.reveal.is-revealed"]
    assert "opacity:1" in shown
    assert "transform:none" in shown


def test_blocks_on_screen_at_load_show_at_once() -> None:
    rules = dict(_rules(_css()))

    assert "transition:none" in rules["html.motion.reveal.is-revealed-now"]
    script = _script()
    assert "getBoundingClientRect" in script
    assert "is-revealed-now" in script


def test_script_reveals_at_12_percent_and_then_stops_watching() -> None:
    script = _script()

    assert "IntersectionObserver" in script
    assert "threshold: 0.12" in script
    assert "unobserve" in script
    assert 'querySelectorAll(".reveal")' in script


def test_siblings_start_012s_apart_with_at_most_5_steps() -> None:
    script = _script()

    assert "STEP = 0.12" in script
    assert "MAX_STEPS = 5" in script
    assert "Math.min(" in script
    assert "transitionDelay" in script


# AC4 (spec AC16): the slow zoom of photos in media slots


def test_photos_in_media_slots_zoom_slowly_back_and_forth() -> None:
    rules = dict(_rules(_css()))

    zoom = rules["html.motion.media__boximg"]
    assert "animation:motion-zoom22sease-in-outinfinitealternate" in zoom
    steps = _keyframes(_css(), "motion-zoom")
    assert "from{transform:scale(1.02);}" in steps
    assert "to{transform:scale(1.09);}" in steps


def test_media_slot_clips_the_zoom_and_the_empty_slot_has_no_photo() -> None:
    site = _compact((STATIC / "css" / "site.css").read_text(encoding="utf-8"))

    box = re.search(r"\.media__box\{([^}]*)\}", site)
    assert box and "overflow:hidden" in box.group(1)
    # The Sand empty slot holds no image, and no motion rule names it.
    assert "media--empty" not in _css()
    media = (Path(settings.SRC_DIR) / "templates" / "includes" / "media.html").read_text(
        encoding="utf-8"
    )
    # The last {% else %} is the empty state (the first ones choose the video sources).
    empty = media.rsplit("{% else %}", 1)[1]
    assert "<img" not in empty


# AC5 (spec AC17): no script, or reduced motion, shows everything at once


def test_page_without_the_script_has_no_class_that_hides(client: Client) -> None:
    html = _home(client)

    opening = re.search(r"<html[^>]*>", html)
    assert opening and "motion" not in opening.group(0)


def test_script_shows_everything_when_the_observer_is_missing() -> None:
    script = _script()

    # Without IntersectionObserver the script stops before it sets the class.
    assert script.index('"IntersectionObserver" in window') < script.index(
        'classList.add("motion")'
    )


def test_not_found_page_keeps_no_script(client: Client) -> None:
    response = client.get("/no-such-page/")

    assert response.status_code == 404
    assert "<script" not in response.content.decode()


# AC6 (spec AC13 to AC17): one query


def test_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        client.get("/")
