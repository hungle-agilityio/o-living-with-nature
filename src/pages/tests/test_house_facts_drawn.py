"""The facts row of chapter 01 drawn in the style of the owner's sketch (house-plan-2d spec, task
T3, issue #162).

The row names (M23, M26, M27) are those of the "Test matrix rows" of the issue. M24 and the
screenshot half of M26 are browser checks, M25 is n/a, M22 is the whole suite.
"""

import re
from html import unescape

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

pytestmark = pytest.mark.django_db

CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "house.css"
NIGHT_INK = "#e9e2d3"
PATHS = {"en": "/", "vi": "/vi/"}
FACTS = {
    "en": [
        ("2", "bedrooms"),
        ("2", "gardens"),
        ("1", "real kitchen"),
        ("1", "household at a time"),
    ],
    "vi": [
        ("2", "phòng ngủ"),
        ("2", "khoảng vườn"),
        ("1", "gian bếp thật"),
        ("1", "hộ thuê một lúc"),
    ],
}
GONE = {"en": ["light well", "Light well"], "vi": ["giếng trời"]}
BOTH = pytest.mark.parametrize("lang", ["en", "vi"])


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _drawn(html: str) -> str:
    match = re.search(r'<div class="house__facts-drawn reveal">.*?</ul>\s*</div>', html, re.S)
    assert match, "no div.house__facts-drawn"
    return match.group(0)


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _final_narrow_block(css: str) -> str:
    """The body of the last `@media (max-width: 760px)` block, which must end the file."""
    start = css.rfind("@media (max-width: 760px)")
    assert start >= 0, "no rule for 760px or less"
    tail = css[start:].rstrip()
    assert tail.endswith("}"), "the file does not end with the 760px block"
    return tail[tail.index("{") + 1 : -1]


# M23: the markup (AC1, AC2)


@BOTH
def test_m23_facts_row_has_one_ink_rule_and_four_items_each_with_an_icon(
    client: Client, lang: str
) -> None:
    drawn = _drawn(_get(client, PATHS[lang]))

    assert drawn.count('class="house__facts-rule"') == 1
    rule = re.search(r'<svg class="house__facts-rule"[^>]*>', drawn)
    assert rule
    assert 'viewBox="0 0 1000 14"' in rule.group(0)
    assert 'aria-hidden="true"' in rule.group(0)
    assert '<ul class="house__facts house__facts--drawn">' in drawn
    items = re.findall(r"<li>.*?</li>", drawn, re.S)
    assert len(items) == 4
    for item in items:
        icon = re.search(r'<svg class="house__fact-icon"[^>]*>', item)
        assert icon, item
        assert 'viewBox="0 0 98 64"' in icon.group(0)
        assert 'aria-hidden="true"' in icon.group(0)
        assert item.count("<svg") == 1


@BOTH
def test_m23_facts_row_shows_the_numbers_and_labels_in_the_language(
    client: Client, lang: str
) -> None:
    drawn = _drawn(_get(client, PATHS[lang]))

    pairs = re.findall(
        r'<span class="house__fact-number">(.*?)</span>\s*'
        r'<span class="house__fact-label">(.*?)</span>',
        drawn,
        re.S,
    )
    assert [(_text(n), _text(label)) for n, label in pairs] == FACTS[lang]
    for word in GONE[lang]:
        assert word not in _text(drawn)


def test_m23_the_rule_has_a_group_of_two_ink_paths(client: Client) -> None:
    drawn = _drawn(_get(client, "/"))

    rule = re.search(r'<svg class="house__facts-rule".*?</svg>', drawn, re.S)
    assert rule
    group = re.search(r'<g class="fact-ink">(.*?)</g>', rule.group(0), re.S)
    assert group, "no g.fact-ink in the rule"
    assert group.group(1).count("<path") == 2


def test_m23_the_icons_use_the_plan_wash_and_the_page_defines_it_once(client: Client) -> None:
    html = _get(client, "/")
    drawn = _drawn(html)

    assert 'filter="url(#plan-wash)"' in drawn
    assert html.count('id="plan-wash"') == 1


def test_m23_vi_page_defines_the_plan_wash_once(client: Client) -> None:
    html = _get(client, "/vi/")

    assert html.count('id="plan-wash"') == 1
    assert 'filter="url(#plan-wash)"' in _drawn(html)


def test_m23_the_drawings_are_inline_and_add_no_image(client: Client) -> None:
    drawn = _drawn(_get(client, "/"))

    assert "<img" not in drawn
    assert ".png" not in drawn
    assert ".jpg" not in drawn


# M26: the stylesheet half (AC3, AC4)


def test_m26_night_theme_gives_the_ink_lines_the_sand_hex() -> None:
    css = _css()

    night = re.findall(r'body\[data-daypart="night"\][^{]*\{([^}]*)\}', css)
    assert any(NIGHT_INK in body.lower() for body in night), (
        'house.css sets no #e9e2d3 under body[data-daypart="night"]'
    )


def test_m26_phone_sizes_sit_in_the_final_760px_block() -> None:
    narrow = _final_narrow_block(_css())

    icon = re.search(r"(?<![\w-])\.house__fact-icon\s*\{([^}]*)\}", narrow)
    assert icon, "no phone rule for the drawing"
    assert re.search(r"width:\s*78px", icon.group(1))
    assert re.search(r"height:\s*51px", icon.group(1))
    number = re.search(r"\.house__facts--drawn \.house__fact-number\s*\{([^}]*)\}", narrow)
    assert number, "no phone rule for the number"
    assert re.search(r"font-size:\s*52px", number.group(1))
    label = re.search(r"\.house__facts--drawn \.house__fact-label\s*\{([^}]*)\}", narrow)
    assert label, "no phone rule for the label"
    assert re.search(r"font-size:\s*17px", label.group(1))


# M27: the query budget (AC5)


@pytest.mark.parametrize("address", ["/", "/vi/"])
def test_m27_home_page_still_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(1):
        _get(client, address)
