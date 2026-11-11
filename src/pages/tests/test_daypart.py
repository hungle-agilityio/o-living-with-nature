"""The time of day in Hòa Xuân: the theme of a moment, the header line, the preview links."""

import re
from datetime import UTC, datetime, timedelta, timezone

import pytest
from django.conf import settings
from django.template.loader import render_to_string
from django.test import Client
from pytest_mock import MockerFixture

from pages.daypart import DA_NANG, THEMES, Daypart, daypart_for, preview_theme, theme_for

COLOURS = {
    "dawn": ("#efe3d6", "#2b2620", "#5e5348"),
    "day": ("#f4f0e8", "#1f2a22", "#5c6358"),
    "dusk": ("#e4be97", "#2a1e16", "#4e3a2c"),
    "night": ("#151d18", "#e9e2d3", "#b9b2a2"),
}


def _at(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 11, 11, hour, minute, second, tzinfo=DA_NANG)


def _freeze(mocker: MockerFixture, moment: datetime) -> None:
    mocker.patch("pages.context_processors.timezone.now", return_value=moment)


def _get(client: Client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _css() -> str:
    return (settings.SRC_DIR / "static" / "css" / "site.css").read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


# AC8


@pytest.mark.parametrize(
    ("hour", "minute", "expected"),
    [
        (4, 59, "night"),
        (5, 0, "dawn"),
        (7, 59, "dawn"),
        (8, 0, "day"),
        (16, 59, "day"),
        (17, 0, "dusk"),
        (18, 59, "dusk"),
        (19, 0, "night"),
        (0, 0, "night"),
        (12, 0, "day"),
        (23, 59, "night"),
    ],
)
def test_theme_at_each_boundary(hour: int, minute: int, expected: str) -> None:
    assert theme_for(_at(hour, minute)) == expected


def test_last_second_before_dawn_is_night() -> None:
    assert theme_for(_at(4, 59, 59)) == "night"
    assert theme_for(_at(5, 0, 0)) == "dawn"


def test_a_utc_moment_is_read_in_da_nang_time() -> None:
    # 22:00 UTC is 05:00 the next day in Đà Nẵng (UTC+7).
    assert theme_for(datetime(2026, 11, 10, 22, 0, tzinfo=UTC)) == "dawn"
    assert theme_for(datetime(2026, 11, 10, 21, 59, tzinfo=UTC)) == "night"
    # 13:20 in New York (UTC-5) is 01:20 in Đà Nẵng.
    new_york = timezone(timedelta(hours=-5))
    assert theme_for(datetime(2026, 11, 10, 13, 20, tzinfo=new_york)) == "night"


def test_a_moment_without_a_time_zone_is_refused() -> None:
    with pytest.raises(ValueError, match="time zone"):
        theme_for(datetime(2026, 11, 11, 12, 0))  # noqa: DTZ001


def test_the_themes_are_the_four_names_in_the_order_of_a_day() -> None:
    assert THEMES == ("dawn", "day", "dusk", "night")


# AC10 and AC11, in the service


def test_daypart_has_the_theme_its_label_and_the_clock() -> None:
    moment = datetime(2026, 11, 11, 6, 20, tzinfo=UTC)  # 13:20 in Đà Nẵng

    assert daypart_for(moment, {}) == Daypart(theme="day", label="Day", clock="13:20")


def test_clock_is_a_24_hour_clock_with_leading_zeros() -> None:
    assert daypart_for(_at(5, 7), {}).clock == "05:07"
    assert daypart_for(_at(19, 0), {}).clock == "19:00"


@pytest.mark.parametrize("theme", ["dawn", "day", "dusk", "night"])
def test_preview_shows_the_asked_theme_and_keeps_the_real_clock(theme: str) -> None:
    shown = daypart_for(_at(13, 20), {"t": theme})

    assert shown == Daypart(theme=theme, label=theme.capitalize(), clock="13:20")


@pytest.mark.parametrize(
    "value", ["DAY", "Day", " day", "noon", "", "day night", "<script>", "dawn\n"]
)
def test_any_other_preview_value_is_ignored(value: str) -> None:
    assert preview_theme({"t": value}) is None
    assert daypart_for(_at(13, 20), {"t": value}).theme == "day"


def test_no_preview_value_is_no_preview() -> None:
    assert preview_theme({}) is None
    assert preview_theme({"other": "night"}) is None


# AC9


@pytest.mark.parametrize(
    ("moment", "theme"),
    [(_at(6, 30), "dawn"), (_at(13, 20), "day"), (_at(18, 0), "dusk"), (_at(2, 0), "night")],
)
def test_body_carries_the_theme_of_the_current_time(
    client: Client, mocker: MockerFixture, moment: datetime, theme: str
) -> None:
    _freeze(mocker, moment)

    assert f'<body data-daypart="{theme}">' in _get(client)


def test_server_clock_in_utc_gives_the_da_nang_theme(client: Client, mocker: MockerFixture) -> None:
    _freeze(mocker, datetime(2026, 11, 11, 11, 30, tzinfo=UTC))  # 18:30 in Đà Nẵng

    html = _get(client)

    assert '<body data-daypart="dusk">' in html
    assert "It's 18:30 in Hòa Xuân · Dusk" in html.replace("&#x27;", "'")


@pytest.mark.parametrize("theme", ["dawn", "day", "dusk", "night"])
def test_stylesheet_has_the_colours_of_each_theme(theme: str) -> None:
    rule = _rule(_css(), f'body[data-daypart="{theme}"]')
    ground, ink, muted = COLOURS[theme]

    assert re.search(rf"--ground:\s*{ground}\s*;", rule, re.IGNORECASE)
    assert re.search(rf"--ink:\s*{ink}\s*;", rule, re.IGNORECASE)
    assert re.search(rf"--muted:\s*{muted}\s*;", rule, re.IGNORECASE)


def test_line_colour_is_fixed_except_at_night() -> None:
    css = _css()

    for theme in ("dawn", "day", "dusk"):
        assert "--line" not in _rule(css, f'body[data-daypart="{theme}"]')
    night = _rule(css, 'body[data-daypart="night"]')
    assert re.search(r"--line:\s*rgba\(233,\s*226,\s*211,\s*0?\.18\)\s*;", night)


def test_footer_band_keeps_its_colours_in_every_theme() -> None:
    css = _css()

    for theme in THEMES:
        rule = _rule(css, f'body[data-daypart="{theme}"]')
        assert "--band" not in rule
        assert "--paper" not in rule


# AC10


def test_header_shows_the_time_in_hoa_xuan_and_the_theme(
    client: Client, mocker: MockerFixture
) -> None:
    _freeze(mocker, _at(13, 20))

    html = _get(client).replace("&#x27;", "'")
    header = html[html.index("<header") : html.index("</header>")]

    assert "It's 13:20 in Hòa Xuân · Day" in header


# AC11


@pytest.mark.parametrize("theme", ["dawn", "day", "dusk", "night"])
def test_query_shows_that_theme_instead(client: Client, mocker: MockerFixture, theme: str) -> None:
    _freeze(mocker, _at(13, 20))

    html = _get(client, f"/?t={theme}").replace("&#x27;", "'")

    assert f'<body data-daypart="{theme}">' in html
    assert f"It's 13:20 in Hòa Xuân · {theme.capitalize()}" in html


@pytest.mark.parametrize("value", ["DAY", "noon", "", "%3Cb%3Enight"])
def test_any_other_query_value_shows_the_real_theme_and_is_not_echoed(
    client: Client, mocker: MockerFixture, value: str
) -> None:
    _freeze(mocker, _at(20, 5))

    html = _get(client, f"/?t={value}").replace("&#x27;", "'")

    assert '<body data-daypart="night">' in html
    assert "It's 20:05 in Hòa Xuân · Night" in html
    assert "DAY" not in html
    assert "noon" not in html
    # "%3Cb%3Enight" reaches the page as "<b>night": neither that nor its escaped form shows.
    assert "<b>" not in html
    assert "&lt;b&gt;" not in html


def test_footer_has_the_preview_line_linking_to_the_current_page(
    client: Client, mocker: MockerFixture
) -> None:
    _freeze(mocker, _at(13, 20))

    html = _get(client, "/?t=dusk")
    footer = html[html.index("<footer") : html.index("</footer>")]
    line = re.search(r'<p class="site-footer__preview">(.*?)</p>', footer, re.DOTALL)

    assert line
    for theme in THEMES:
        assert f'<a href="?t={theme}">{theme}</a>' in line.group(1)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", line.group(1))).strip()
    assert text == "See Ở at dawn · day · dusk · night"


def test_preview_links_never_copy_the_address_the_visitor_typed(client: Client) -> None:
    # A link that is only a query stays on the page being shown, whatever its address, so an
    # address such as "//other.example/" can never turn the preview links into links elsewhere.
    request = client.get("//other.example/").wsgi_request
    footer = render_to_string(
        "includes/footer.html", {"request": request, "daypart_themes": THEMES}
    )

    assert "other.example" not in footer
    for theme in THEMES:
        assert f'<a href="?t={theme}">{theme}</a>' in footer


# AC12


def test_colour_change_takes_0_9_seconds() -> None:
    body = _rule(_css().split("@media", 1)[0], "body")

    assert re.search(r"transition:[^;]*background-color 0\.9s ease", body)
    assert re.search(r"transition:[^;]*[\s,]color 0\.9s ease", body)


def test_no_colour_transition_under_reduced_motion() -> None:
    reduced = _css().split("@media (prefers-reduced-motion: reduce)", 1)[1]

    assert re.search(r"body\s*\{[^}]*transition:\s*none", reduced)
