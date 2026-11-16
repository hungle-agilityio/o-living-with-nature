"""The Vietnamese page at `/vi/`, the EN · VI switch and the search tags of both languages
(vietnamese spec, task T1, issue #107).

The row names (M1 to M18) are those of the "Test matrix rows" of the issue. M10, M11b and M33
are checked by hand in the pull request and have no test here.
"""

import html as html_lib
import json
import re
import types
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import pytest
from django.conf import settings as django_settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings
from pytest_mock import MockerFixture

from owner_content.models import SiteSettings
from pages import seo
from pages.daypart import DA_NANG

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db

BASE = "https://o.example"
JS = Path(django_settings.SRC_DIR) / "static" / "js"

EN_TITLE = "Ở — Living with Nature · Garden house for rent in Hòa Xuân, Đà Nẵng"
VI_TITLE = "Ở — Nhà vườn cho thuê nguyên căn ở Hòa Xuân, Đà Nẵng"
VI_DESCRIPTION = (
    "Thuê nhà nguyên căn ở Hòa Xuân, Đà Nẵng: nhà vườn hai phòng ngủ cho thuê theo tháng. "
    "Từ 13–14 triệu đồng mỗi tháng, thuê tối thiểu một tháng."
)
VI_SITE_NAME = "Ở — Sống cùng thiên nhiên"
VI_404_HEADING = "Lối này không dẫn đến đâu cả — vườn ở phía này."
VI_404_LINE = "Trang bạn tìm không có ở đây. Có thể trang đã chuyển chỗ, hoặc đường dẫn bị gõ sai."

ALTERNATES = (
    f'<link rel="alternate" hreflang="en" href="{BASE}/">',
    f'<link rel="alternate" hreflang="vi" href="{BASE}/vi/">',
    f'<link rel="alternate" hreflang="x-default" href="{BASE}/">',
)


def _at(hour: int, minute: int) -> datetime:
    return datetime(2026, 11, 11, hour, minute, 5, tzinfo=DA_NANG)


def _freeze(mocker: MockerFixture, moment: datetime) -> None:
    mocker.patch("pages.context_processors.timezone.now", return_value=moment)
    mocker.patch("pages.views.timezone.now", return_value=moment)


def _get(client: Client, path: str, **extra: Any) -> str:
    response = client.get(path, **extra)
    assert response.status_code == 200
    return response.content.decode()


def _not_found(client: Client, settings: Settings, path: str) -> str:
    settings.DEBUG = False
    response = client.get(path)
    assert response.status_code == 404
    return response.content.decode()


def _section(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    assert match, pattern
    return match.group(0)


def _header(html: str) -> str:
    return _section(html, r"<header\b.*?</header>")


def _footer(html: str) -> str:
    return _section(html, r"<footer\b.*?</footer>")


def _hero(html: str) -> str:
    return _section(html, r'<section id="hero".*?</section>')


def _main(html: str) -> str:
    return _section(html, r"<main\b.*?</main>")


def _plain(fragment: str) -> str:
    """The visible text of a fragment: tags removed, entities decoded, spaces collapsed."""
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


class _Tags(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


def _tags(fragment: str, name: str) -> list[dict[str, str | None]]:
    parser = _Tags()
    parser.feed(fragment)
    return [attrs for tag, attrs in parser.tags if tag == name]


def _links(fragment: str) -> list[tuple[str, str]]:
    """(href, text) of every link in the fragment."""
    return [
        (html_lib.unescape(href), _plain(text))
        for href, text in re.findall(
            r'<a\b[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', fragment, re.DOTALL
        )
    ]


def _time_line(html: str) -> str:
    return _section(html, r'<span class="site-header__time label"[^>]*>.*?</span>')


def _data_labels(html: str) -> dict[str, str]:
    (attrs,) = _tags(_time_line(html), "span")
    raw = attrs.get("data-labels")
    assert raw, "no data-labels on the time line"
    labels = json.loads(raw)
    assert isinstance(labels, dict)
    return labels


def _json_ld(html: str) -> dict[str, object]:
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    assert match, "no JSON-LD"
    data = json.loads(match.group(1))
    assert isinstance(data, dict)
    return data


def _meta(html: str, key: str, value: str) -> str:
    for attrs in _tags(html[: html.index("</head>")], "meta"):
        if attrs.get(key) == value:
            return attrs["content"] or ""
    raise AssertionError(f"no meta {key}={value}")


def _set_owner() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=13, price_to_million=14, phone="0905 123 456", zalo=""
    )


# M1 (AC1)


def test_m1_languages_are_english_and_vietnamese_and_the_default_stays_english() -> None:
    assert django_settings.LANGUAGES == [("en", "English"), ("vi", "Tiếng Việt")]
    assert django_settings.LANGUAGE_CODE == "en"


# M2 and M3 (AC2)


def test_m2_accept_language_vi_does_not_change_the_english_address(client: Client) -> None:
    response = client.get("/", HTTP_ACCEPT_LANGUAGE="vi")

    assert response.status_code == 200
    assert '<html lang="en">' in response.content.decode()


def test_m2_vi_address_is_vietnamese(client: Client) -> None:
    html = _get(client, "/vi/", HTTP_ACCEPT_LANGUAGE="vi")

    assert '<html lang="vi">' in html


def test_m2_vi_address_is_vietnamese_whatever_the_browser_asks(client: Client) -> None:
    assert '<html lang="vi">' in _get(client, "/vi/", HTTP_ACCEPT_LANGUAGE="en")


def test_m3_language_cookie_vi_does_not_change_the_english_address(client: Client) -> None:
    client.cookies["django_language"] = "vi"

    response = client.get("/")

    assert response.status_code == 200
    assert '<html lang="en">' in response.content.decode()


# M4 (AC3)


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/vi", "/vi/"),
        ("/house/", "/#house"),
        ("/hoa-xuan/", "/#hoa-xuan"),
        ("/faq/", "/#faq"),
        ("/contact/", "/#contact"),
    ],
)
def test_m4_redirects(client: Client, path: str, target: str) -> None:
    response = client.get(path)

    assert response.status_code == 301
    assert response["Location"] == target


@pytest.mark.parametrize("path", ["/sitemap.xml", "/robots.txt", "/healthz/"])
def test_m4_technical_addresses_answer_200(client: Client, path: str) -> None:
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/vi/sitemap.xml", "/vi/house/", "/vi/owner/"])
def test_m4_no_vietnamese_version_of_the_other_addresses(
    client: Client, settings: Settings, path: str
) -> None:
    settings.DEBUG = False

    assert client.get(path).status_code == 404


# M5 and M6 (AC4)


def test_m5_vietnamese_not_found_page(client: Client, settings: Settings) -> None:
    html = _not_found(client, settings, "/vi/not-here/")
    main = _main(html)

    assert '<html lang="vi">' in html
    assert re.search(r'<p class="label[^"]*">\s*404\s*</p>', main)
    assert _plain(_section(main, r"<h1\b.*?</h1>")) == VI_404_HEADING
    assert VI_404_LINE in _plain(main)
    assert _links(main) == [("/vi/", "Về trang chủ"), ("/vi/#contact", "Liên hệ Bún")]
    robots = _meta(html, "name", "robots")
    assert robots == "noindex, nofollow"
    assert _plain(_section(html, r"<title>.*?</title>")) == VI_SITE_NAME


def test_m6_english_not_found_page_keeps_its_texts(client: Client, settings: Settings) -> None:
    html = _not_found(client, settings, "/not-here/")
    main = _main(html)

    assert '<html lang="en">' in html
    assert _plain(_section(main, r"<h1\b.*?</h1>")) == (
        "This path leads nowhere — the garden is this way."
    )
    assert _links(main) == [("/", "Back to the home page"), ("/contact/", "Contact Bún")]
    assert _plain(_section(html, r"<title>.*?</title>")) == "Ở — Living with Nature"


# M7 and M8 (AC5)


def test_m7_every_text_module_has_the_same_keys_in_both_languages() -> None:
    import importlib
    import pkgutil

    import pages.texts as package

    names = [info.name for info in pkgutil.iter_modules(package.__path__)]
    assert "shell" in names
    for name in names:
        module = importlib.import_module(f"pages.texts.{name}")
        assert set(module.EN) == set(module.VI), name
        assert all(module.EN.values()), f"{name}: an empty English text"
        assert all(module.VI.values()), f"{name}: an empty Vietnamese text"


def test_m7_shell_holds_the_texts_of_the_spec() -> None:
    from pages.texts import shell

    assert shell.VI["clock_line"] == "{clock} ở Hòa Xuân"
    assert shell.EN["clock_line"] == "It's {clock} in Hòa Xuân"
    assert shell.VI["site_name"] == VI_SITE_NAME
    assert shell.VI["seo_title"] == VI_TITLE
    assert shell.VI["seo_description"] == VI_DESCRIPTION
    assert shell.EN["seo_title"] == EN_TITLE
    assert shell.EN["site_name"] == "Ở — Living with Nature"


def test_m8_missing_keys_returns_the_key_only_in_one_dictionary() -> None:
    from pages.language import missing_keys

    made_up = types.ModuleType("made_up")
    made_up.EN = {"both": "x", "only_en": "y"}  # type: ignore[attr-defined]
    made_up.VI = {"both": "x"}  # type: ignore[attr-defined]
    assert missing_keys(made_up) == {"only_en"}

    made_up.VI = {"both": "x", "only_vi": "z"}  # type: ignore[attr-defined]
    assert missing_keys(made_up) == {"only_en", "only_vi"}

    made_up.VI = {"both": "x", "only_en": "z"}  # type: ignore[attr-defined]
    assert missing_keys(made_up) == set()


# M9 and M12 (AC6, AC8)


def _switch(html: str) -> str:
    return _section(html, r'<p class="lang-switch label"[^>]*>.*?</p>')


def _check_switch(html: str, label: str, current: str, other: str, href: str, lang: str) -> None:
    switch = _switch(html)
    (paragraph,) = _tags(switch, "p")
    assert paragraph["aria-label"] == label
    spans = re.findall(r"<span\b([^>]*)>(.*?)</span>", switch, re.DOTALL)
    current_spans = [text for attrs, text in spans if "lang-switch__current" in attrs]
    assert current_spans == [current]
    assert [_plain(text) for attrs, text in spans if "aria-hidden" in attrs] == ["·"]
    anchors = _tags(switch, "a")
    assert len(anchors) == 1
    assert anchors[0]["href"] == href
    assert anchors[0]["hreflang"] == lang
    assert anchors[0]["lang"] == lang
    assert _plain(_section(switch, r"<a\b.*?</a>")) == other
    assert "aria-current" not in html
    # The switch sits between the row of links and the phone menu.
    header = _header(html)
    assert header.index('class="nav-row"') < header.index("lang-switch") < header.index("nav-menu")


def test_m9_switch_on_the_english_page(client: Client) -> None:
    _check_switch(_get(client, "/"), "Language", "EN", "VI", "/vi/", "vi")


def test_m9_switch_on_the_vietnamese_page(client: Client) -> None:
    _check_switch(_get(client, "/vi/"), "Ngôn ngữ", "VI", "EN", "/", "en")


def test_m9_switch_on_the_english_not_found_page(client: Client, settings: Settings) -> None:
    _check_switch(_not_found(client, settings, "/not-here/"), "Language", "EN", "VI", "/vi/", "vi")


def test_m9_switch_on_the_vietnamese_not_found_page(client: Client, settings: Settings) -> None:
    _check_switch(_not_found(client, settings, "/vi/not-here/"), "Ngôn ngữ", "VI", "EN", "/", "en")


def test_m12_switch_link_is_plain_without_script(client: Client) -> None:
    # As sent, the link has no hash: the script adds it, the link works without it.
    assert 'href="/vi/" hreflang="vi" lang="vi">VI</a>' in _get(client, "/")
    assert 'href="/" hreflang="en" lang="en">EN</a>' in _get(client, "/vi/")


# M11 (AC8)


def test_m11_switch_script_is_linked_deferred_right_before_the_count_script(
    client: Client,
) -> None:
    html = _get(client, "/")

    scripts = re.findall(r"<script src=\"([^\"]+)\"[^>]*>", html)
    assert scripts[-1] == "/static/js/count.js"
    assert scripts[-2] == "/static/js/lang-switch.js"
    assert '<script src="/static/js/lang-switch.js" defer></script>' in html


def test_m11_switch_script_is_small_and_plain() -> None:
    script = (JS / "lang-switch.js").read_text(encoding="utf-8")

    assert len(script.splitlines()) < 40
    for chapter in ("house", "hoa-xuan", "rent", "faq", "contact"):
        assert chapter in script, chapter
    assert "innerHeight" in script
    for sign in ("localStorage", "sessionStorage", "fetch", "import"):
        assert sign not in script, sign


# M13 (AC9)


def test_m13_clock_line_in_vietnamese_by_day(client: Client, mocker: MockerFixture) -> None:
    _freeze(mocker, _at(14, 52))

    html = _get(client, "/vi/")

    assert _plain(_time_line(html)) == "14:52 ở Hòa Xuân · Ban ngày"
    assert _data_labels(html) == {
        "dawn": "Bình minh",
        "day": "Ban ngày",
        "dusk": "Hoàng hôn",
        "night": "Ban đêm",
    }


def test_m13_clock_line_in_vietnamese_at_dusk(client: Client, mocker: MockerFixture) -> None:
    _freeze(mocker, _at(18, 0))

    assert _plain(_time_line(_get(client, "/vi/"))) == "18:00 ở Hòa Xuân · Hoàng hôn"


def test_m13_clock_line_in_english_is_unchanged(client: Client, mocker: MockerFixture) -> None:
    _freeze(mocker, _at(14, 52))

    html = _get(client, "/")

    assert _plain(_time_line(html)) == "It's 14:52 in Hòa Xuân · Day"
    assert _data_labels(html) == {"dawn": "Dawn", "day": "Day", "dusk": "Dusk", "night": "Night"}


def test_m13_daypart_script_reads_the_labels_and_replaces_the_last_part() -> None:
    script = (JS / "daypart.js").read_text(encoding="utf-8")

    assert "data-labels" in script
    assert "· [^·]+$" in script


# M14 (AC10)


def test_m14_menus_and_wordmark_in_vietnamese(client: Client) -> None:
    header = _header(_get(client, "/vi/"))

    expected = [
        ("/vi/#house", "Căn nhà"),
        ("/vi/#hoa-xuan", "Hòa Xuân"),
        ("/vi/#rent", "Giá thuê"),
        ("/vi/#faq", "Hỏi đáp"),
        ("/vi/#contact", "Liên hệ"),
    ]
    links = _links(header)
    wordmark = [a for a in _tags(header, "a") if "wordmark" in (a.get("class") or "")]
    assert [a["href"] for a in wordmark] == ["/vi/"]
    # The wordmark, the language link, then the menu twice (row and phone menu).
    menu_links = [link for link in links if link[0].startswith("/vi/#")]
    assert menu_links == expected * 2
    navs = [attrs["aria-label"] for attrs in _tags(header, "nav")]
    assert navs == ["Chính", "Menu"]
    assert "<summary>Menu</summary>" in header


def test_m14_menus_in_english_are_unchanged(client: Client) -> None:
    header = _header(_get(client, "/"))

    menu_links = [link for link in _links(header) if link[0].startswith("/#")]
    assert (
        menu_links
        == [
            ("/#house", "The house"),
            ("/#hoa-xuan", "Hòa Xuân"),
            ("/#rent", "Rent"),
            ("/#faq", "FAQ"),
            ("/#contact", "Contact"),
        ]
        * 2
    )


def test_m14_hero_in_vietnamese(client: Client) -> None:
    hero = _plain(_hero(_get(client, "/vi/")))

    assert "ở · động từ · tiếng Việt · thanh hỏi" in hero
    assert "1. lưu lại. 2. sống ở một nơi. 3. có mặt ở nhà." in hero
    assert "Cuộn xuống, mời bạn vào nhà ↓" in hero
    assert "Sống cùng thiên nhiên" in hero
    assert (
        "Một căn nhà vườn ở Hòa Xuân, Đà Nẵng. Hai phòng ngủ, hai khoảng vườn, "
        "cho thuê nguyên căn, theo tháng." in hero
    )
    assert "Video minh hoạ" in hero


def test_m14_hero_h1_keeps_its_accent_word(client: Client) -> None:
    h1 = _section(_hero(_get(client, "/vi/")), r"<h1\b.*?</h1>")

    assert re.search(r"Sống\s*<em[^>]*>cùng</em>\s*thiên nhiên", h1)


def test_m14_footer_in_vietnamese(client: Client) -> None:
    footer = _footer(_get(client, "/vi/?t=day"))
    text = _plain(footer)

    assert "một chữ để ở lại · Hòa Xuân, Đà Nẵng" in text
    assert "Xem Ở lúc" in text
    assert [href for href, _name in _links(footer)] == [
        "?t=dawn",
        "?t=day",
        "?t=dusk",
        "?t=night",
    ]
    assert [name for _href, name in _links(footer)] == [
        "bình minh",
        "ban ngày",
        "hoàng hôn",
        "ban đêm",
    ]
    assert 'Ảnh và video có nhãn "Minh hoạ" là ảnh tạm cho đến khi nhà xây xong.' in text


def test_m14_no_english_text_remains_in_the_shell_of_the_vietnamese_page(
    client: Client,
) -> None:
    html = _get(client, "/vi/")
    shell = _plain(_header(html) + _hero(html) + _footer(html))

    for english in (
        "The house",
        "Rent",
        "FAQ",
        "Contact",
        "Scroll, and come in",
        "Living with nature",
        "verb · Vietnamese",
        "a word for staying",
        "See Ở at",
        "stand-ins",
        "Illustrative",
        "It's",
        " in Hòa Xuân",
    ):
        assert english not in shell, english


def test_m14_chips_and_credits_in_vietnamese(client: Client) -> None:
    html = _get(client, "/vi/")
    credits = re.findall(r'<figcaption class="media__credit">(.*?)</figcaption>', html, re.DOTALL)

    assert "Ảnh minh hoạ" in html
    assert 'class="media__chip">Illustrative' not in html
    assert credits
    for credit in credits:
        assert not credit.strip().startswith("Photo: ")
    assert any(credit.strip().startswith("Ảnh: ") for credit in credits)


def test_m14_chips_and_credits_in_english_are_unchanged(client: Client) -> None:
    html = _get(client, "/")
    credits = re.findall(r'<figcaption class="media__credit">(.*?)</figcaption>', html, re.DOTALL)

    assert "Illustrative photo" in html
    assert "Illustrative video" in html
    assert "Ảnh minh hoạ" not in html
    assert any(credit.strip().startswith("Photo: ") for credit in credits)
    assert not any(credit.strip().startswith("Ảnh: ") for credit in credits)


def test_m14_phone_contact_bar_label_in_vietnamese(client: Client) -> None:
    _set_owner()

    vi = _get(client, "/vi/")
    en = _get(client, "/")

    assert '<nav class="contact-bar" aria-label="Liên hệ">' in vi
    assert '<nav class="contact-bar" aria-label="Contact">' in en


# M15 (AC11)


def test_m15_head_of_the_vietnamese_page(client: Client, settings: Settings) -> None:
    settings.SITE_BASE_URL = BASE
    _set_owner()

    html = _get(client, "/vi/")

    assert _plain(_section(html, r"<title>.*?</title>")) == VI_TITLE
    assert _meta(html, "name", "description") == VI_DESCRIPTION
    assert _meta(html, "property", "og:title") == VI_TITLE
    assert _meta(html, "property", "og:description") == VI_DESCRIPTION
    assert _meta(html, "property", "og:url") == f"{BASE}/vi/"
    assert _meta(html, "property", "og:site_name") == VI_SITE_NAME
    assert f'<link rel="canonical" href="{BASE}/vi/">' in html
    data = _json_ld(html)
    assert data["name"] == VI_SITE_NAME
    assert data["description"] == VI_DESCRIPTION
    assert data["url"] == f"{BASE}/vi/"


def test_m15_head_of_the_english_page_is_unchanged(client: Client, settings: Settings) -> None:
    settings.SITE_BASE_URL = BASE
    _set_owner()

    html = _get(client, "/")

    description = seo.PAGES["home"].description
    assert description == (
        "A whole garden house with two bedrooms, rented by the month in Hòa Xuân, Đà Nẵng. "
        "From 13–14 million VND a month, minimum stay one month."
    )
    assert _plain(_section(html, r"<title>.*?</title>")) == EN_TITLE
    assert _meta(html, "name", "description") == description
    assert _meta(html, "property", "og:url") == f"{BASE}/"
    assert _meta(html, "property", "og:site_name") == "Ở — Living with Nature"
    assert f'<link rel="canonical" href="{BASE}/">' in html
    assert _json_ld(html) == {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "name": "Ở — Living with Nature",
        "description": description,
        "url": f"{BASE}/",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Hòa Xuân",
            "addressRegion": "Đà Nẵng",
            "addressCountry": "VN",
        },
        "priceRange": "From 13–14 million VND a month",
        "telephone": "+84905123456",
    }


# M16 (AC12)


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_m16_alternates_follow_the_canonical(client: Client, settings: Settings, path: str) -> None:
    settings.SITE_BASE_URL = BASE
    html = _get(client, path)

    canonical = re.search(r'<link rel="canonical" href="[^"]+">', html)
    assert canonical
    after = html[canonical.end() :]
    expected = "".join(f"\\s*{re.escape(tag)}" for tag in ALTERNATES)
    assert re.match(expected, after)
    assert html.count('rel="alternate"') == 3


@pytest.mark.parametrize("path", ["/not-here/", "/vi/not-here/"])
def test_m16_not_found_pages_have_no_alternates(
    client: Client, settings: Settings, path: str
) -> None:
    assert 'rel="alternate"' not in _not_found(client, settings, path)


# M17 (AC13)


def test_m17_sitemap_lists_both_addresses_with_their_alternates() -> None:
    xml = seo.sitemap_xml("https://example.test")

    root = ElementTree.fromstring(xml.encode())
    sm = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    xhtml = "{http://www.w3.org/1999/xhtml}"
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in xml
    urls = list(root.iter(f"{sm}url"))
    assert [url.findtext(f"{sm}loc") for url in urls] == [
        "https://example.test/",
        "https://example.test/vi/",
    ]
    for url in urls:
        links = [
            (link.get("rel"), link.get("hreflang"), link.get("href"))
            for link in url.iter(f"{xhtml}link")
        ]
        assert links == [
            ("alternate", "en", "https://example.test/"),
            ("alternate", "vi", "https://example.test/vi/"),
            ("alternate", "x-default", "https://example.test/"),
        ]


@pytest.mark.parametrize(
    ("enabled", "robots"), [(False, "noindex, nofollow"), (True, "index, follow")]
)
@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_m17_robots_value_of_both_pages(
    client: Client, settings: Settings, path: str, enabled: bool, robots: str
) -> None:
    settings.INDEXING_ENABLED = enabled

    assert _meta(_get(client, path), "name", "robots") == robots


# M18 (AC14)


def test_m18_vietnamese_page_makes_exactly_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        response = client.get("/vi/")

    assert response.status_code == 200
    assert '<html lang="vi">' in response.content.decode()
