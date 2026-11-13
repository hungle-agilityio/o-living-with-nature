"""The theme follows the clock while the page is open (time-of-day-live T2, issue #76).

The switch itself runs in a browser; the browser check of the issue shows it. These tests pin
what the server sends for it (the time, the preview flag, the files of every loop) and what the
two scripts must hold.
"""

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import hero
from pages.daypart import DA_NANG, THEMES, Daypart, daypart_for

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db

JS = Path(settings.SRC_DIR) / "static" / "js"
MOMENT = datetime(2026, 11, 11, 13, 20, 5, tzinfo=DA_NANG)
MOMENT_MS = int(MOMENT.timestamp() * 1000)


def _freeze(mocker: MockerFixture, moment: datetime = MOMENT) -> None:
    mocker.patch("pages.context_processors.timezone.now", return_value=moment)
    mocker.patch("pages.views.timezone.now", return_value=moment)


def _get(client: Client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _time_line(html: str) -> str:
    match = re.search(r'<span class="site-header__time label"[^>]*>', html)
    assert match, "no time line in the header"
    return match.group(0)


def _hero_tag(html: str) -> str:
    match = re.search(r'<section id="hero"[^>]*>', html)
    assert match, "no hero section"
    return match.group(0)


def _no_files(mocker: MockerFixture, *missing: str) -> None:
    real = finders.find

    def find(path: str) -> object:
        return None if path in missing else real(path)

    mocker.patch("pages.hero.finders.find", side_effect=find)


def _daypart_js() -> str:
    return (JS / "daypart.js").read_text(encoding="utf-8")


def _hero_js() -> str:
    return (JS / "hero.js").read_text(encoding="utf-8")


# AC1: the time and the preview flag in the header line


def test_service_gives_the_time_in_milliseconds_since_1970() -> None:
    shown = daypart_for(MOMENT, {})

    assert shown.now_ms == MOMENT_MS
    assert shown.preview is False
    # The values of the page are unchanged (test_daypart compares whole Dayparts).
    assert shown == Daypart(theme="day", label="Day", clock="13:20")


def test_service_flags_a_valid_preview_only() -> None:
    assert daypart_for(MOMENT, {"t": "dusk"}).preview is True
    assert daypart_for(MOMENT, {"t": "noon"}).preview is False
    assert daypart_for(MOMENT, {"t": ""}).preview is False


def test_service_time_is_the_same_whatever_the_time_zone_of_the_moment() -> None:
    assert daypart_for(MOMENT.astimezone(UTC), {}).now_ms == MOMENT_MS


def test_header_line_carries_the_time_of_the_response(
    client: Client, mocker: MockerFixture
) -> None:
    _freeze(mocker)

    html = _get(client)
    line = _time_line(html)

    assert f'data-now="{MOMENT_MS}"' in line
    assert "data-preview" not in line
    # The text the server sends and the body tag stay as they were.
    assert "It's 13:20 in Hòa Xuân · Day</span>" in html.replace("&#x27;", "'")
    assert '<body data-daypart="day">' in html


@pytest.mark.parametrize("theme", THEMES)
def test_header_line_flags_a_preview(client: Client, mocker: MockerFixture, theme: str) -> None:
    _freeze(mocker)

    html = _get(client, f"/?t={theme}")
    line = _time_line(html)

    assert "data-preview" in line
    assert f'data-now="{MOMENT_MS}"' in line
    assert f'<body data-daypart="{theme}">' in html


@pytest.mark.parametrize("value", ["DAY", "noon", "%3Cb%3Enight"])
def test_a_query_that_is_not_a_theme_is_no_preview(
    client: Client, mocker: MockerFixture, value: str
) -> None:
    _freeze(mocker)

    assert "data-preview" not in _time_line(_get(client, f"/?t={value}"))


@pytest.mark.parametrize("address", ["/", "/?t=dusk"])
def test_home_page_still_asks_the_database_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(address)

    assert response.status_code == 200


# AC2: the script that keeps the time


def test_daypart_script_is_loaded_right_after_the_reveal_script(client: Client) -> None:
    html = _get(client)

    scripts = re.findall(r'<script src="([^"]+)"[^>]*>', html)
    assert scripts[:2] == ["/static/js/reveal.js", "/static/js/daypart.js"]
    assert '<script src="/static/js/daypart.js" defer></script>' in html
    head = html[: html.index("</head>")]
    assert "/static/js/daypart.js" in head


def test_not_found_page_still_has_no_script(client: Client) -> None:
    response = client.get("/no-such-page/")

    assert response.status_code == 404
    assert "<script" not in response.content.decode()


def test_daypart_script_is_small_plain_and_private() -> None:
    script = _daypart_js()

    assert len(script.encode()) < 4_000
    for sign in (
        "import ",
        "require(",
        "http://",
        "https://",
        "eval(",
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.cookie",
        "fetch(",
        "XMLHttpRequest",
        "sendBeacon",
        "WebSocket",
    ):
        assert sign not in script, sign


def test_daypart_script_keeps_da_nang_time_from_the_server() -> None:
    script = _daypart_js()

    assert "data-now" in script
    assert "data-preview" in script
    # UTC+7 with no daylight saving: seven hours in milliseconds, then the UTC hour and minute.
    assert re.search(r"7\s*\*\s*3600(e3|000|\s*\*\s*1000)", script)
    assert "getUTCHours" in script
    assert "getUTCMinutes" in script


# AC3: the boundaries, the moments the script checks, and the event


def test_daypart_script_uses_the_hours_of_theme_for() -> None:
    script = _daypart_js()

    for hour, theme in ((5, "dawn"), (8, "day"), (17, "dusk"), (19, "night")):
        assert re.search(rf"\[\s*{hour}\s*,\s*\"{theme}\"\s*\]", script), theme


def test_daypart_script_catches_up_when_the_page_shows_again() -> None:
    script = _daypart_js()

    assert '"visibilitychange"' in script
    assert '"pageshow"' in script


def test_daypart_script_tells_the_page_of_a_new_theme() -> None:
    script = _daypart_js()

    assert '"data-daypart"' in script
    assert re.search(r'new CustomEvent\(\s*"daypart"\s*,\s*\{\s*detail:\s*\{\s*theme', script)
    assert "document.dispatchEvent" in script


# AC4 and AC5: the header line moves on the minute, and a preview keeps its theme


def test_daypart_script_wakes_on_every_minute() -> None:
    script = _daypart_js()

    assert "60000" in script
    assert "setTimeout" in script
    assert "textContent" in script


# AC6: the files of every loop on the hero, and the switch in hero.js


@pytest.mark.parametrize("theme", THEMES)
def test_hero_lists_the_files_of_every_loop(client: Client, theme: str) -> None:
    tag = _hero_tag(_get(client, f"/?t={theme}"))

    for name in THEMES:
        files = re.search(rf'data-loop-{name}="([^"]+)"', tag)
        assert files, name
        assert files.group(1).split(" ") == [
            f"/static/media/hero/{name}.jpg",
            f"/static/media/hero/{name}.webm",
            f"/static/media/hero/{name}.mp4",
        ]


def test_hero_leaves_out_a_loop_with_a_missing_file(client: Client, mocker: MockerFixture) -> None:
    _no_files(mocker, "media/hero/dusk.webm")

    tag = _hero_tag(_get(client, "/?t=day"))

    assert "data-loop-dusk" not in tag
    assert "media/hero/dusk" not in tag
    for name in ("dawn", "day", "night"):
        assert f"data-loop-{name}=" in tag


def test_service_lists_only_the_loops_with_all_their_files(mocker: MockerFixture) -> None:
    assert list(hero.loops()) == list(THEMES)
    assert hero.loops()["night"] == hero.media_for("night")

    _no_files(mocker, "media/hero/dawn.jpg")
    assert list(hero.loops()) == ["day", "dusk", "night"]


def test_files_are_hashed_static_urls(client: Client, mocker: MockerFixture) -> None:
    # The template goes through {% static %}, so with the manifest storage of production the
    # hashed names are used.
    mocker.patch(
        "django.templatetags.static.StaticNode.handle_simple",
        side_effect=lambda path: f"/static/{path.replace('.', '.abc123.', 1)}",
    )

    tag = _hero_tag(_get(client, "/?t=day"))

    assert "/static/media/hero/night.abc123.jpg" in tag
    assert "/static/media/hero/night.abc123.webm" in tag


def test_hero_has_no_inline_script(client: Client) -> None:
    html = _get(client)
    section = html[html.index('<section id="hero"') : html.index("</section>")]

    assert "<script" not in section


def test_hero_script_follows_the_daypart_event() -> None:
    script = _hero_js()

    assert re.search(r'document\.addEventListener\(\s*"daypart"', script)
    assert '"data-loop-"' in script
    # The new poster is loaded before the sources change, and a missing theme hides the chip.
    assert "onload" in script
    # A poster that cannot load is treated as a theme with no files (Sand, no chip).
    assert "onerror" in script
    assert ".hero__chip" in script
    assert "backgroundImage" in script
    assert len(script.encode()) < 14_000
