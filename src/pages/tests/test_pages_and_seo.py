"""The five pages, their search tags, `sitemap.xml` and `robots.txt` (AC13 to AC18)."""

import json
import os
import re
import subprocess
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from pages import seo

SRC = Path(__file__).resolve().parents[2]
BASE = "https://o.example"
SITE_NAME = "Ở — Living with Nature"

# Address, title and description of each page: the table of AC14, word for word.
PAGES = [
    (
        "/",
        "Ở — Living with Nature · Garden house for rent in Hòa Xuân, Đà Nẵng",
        "A whole garden house with two bedrooms, rented by the month in Hòa Xuân, Đà Nẵng. "
        "From 13–14 million VND a month, minimum stay one month.",
    ),
    (
        "/house/",
        "The house · Ở, a garden house for rent in Đà Nẵng",
        "Two bedrooms, a mezzanine, a light well, front and back gardens and a covered veranda. "
        "Rented whole, by the month.",
    ),
    (
        "/hoa-xuan/",
        "Hòa Xuân, Đà Nẵng · Living at Ở",
        "A supermarket across the road, the market and the beach about 10 minutes away, "
        "the airport about 15 minutes.",
    ),
    (
        "/faq/",
        "FAQ · Renting Ở in Hòa Xuân, Đà Nẵng",
        "Minimum stay, deposit, electricity and water, pets, and residence registration "
        "for foreigners.",
    ),
    (
        "/contact/",
        "Contact Bún · Ở garden house, Đà Nẵng",
        "Call, WhatsApp or Zalo. I usually reply within an hour.",
    ),
]
ADDRESSES = [address for address, _title, _description in PAGES]
# The inner pages: address, h1, chapter number, chapter word (FAQ has none in design.md).
INNER_PAGES = [
    ("/house/", "The house", "01", "ở nhà"),
    ("/hoa-xuan/", "Hòa Xuân", "02", "ở gần"),
    ("/faq/", "FAQ", "03", None),
    ("/contact/", "Contact", "04", "ở lại?"),
]
EVERY_ADDRESS = [*ADDRESSES, "/sitemap.xml", "/robots.txt"]


class _Page(HTMLParser):
    """Collects the start tags with their attributes, and the whole text of each element."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.text: dict[str, list[str]] = {}
        self._open: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag not in {"meta", "link", "img", "source", "br"}:
            self._open.append((tag, []))

    def handle_endtag(self, tag: str) -> None:
        if tag not in [name for name, _parts in self._open]:
            return
        while True:
            name, parts = self._open.pop()
            self.text.setdefault(name, []).append(" ".join("".join(parts).split()))
            if name == tag:
                return

    def handle_data(self, data: str) -> None:
        # The text of an element includes the text of the elements inside it.
        for _name, parts in self._open:
            parts.append(data)

    def all(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == name]

    def meta(self, key: str, value: str) -> list[str | None]:
        return [meta.get("content") for meta in self.all("meta") if meta.get(key) == value]


def _get(client: Client, address: str) -> str:
    response = client.get(address)
    assert response.status_code == 200, address
    return response.content.decode()


def _parse(html: str) -> _Page:
    page = _Page()
    page.feed(html)
    page.close()
    return page


def _main(html: str) -> str:
    match = re.search(r"<main\b.*?</main>", html, re.DOTALL)
    assert match, "no <main> in the page"
    return match.group(0)


def _canonical(page: _Page) -> list[str | None]:
    return [link.get("href") for link in page.all("link") if link.get("rel") == "canonical"]


# AC13


@pytest.mark.parametrize("address", ADDRESSES)
def test_page_answers_200_with_one_h1(client: Client, address: str) -> None:
    page = _parse(_get(client, address))

    assert len(page.all("h1")) == 1


def test_home_page_h1_reads_living_with_nature_with_the_accent_word_in_italic(
    client: Client,
) -> None:
    main = _main(_get(client, "/"))
    page = _parse(main)

    assert page.text["h1"] == ["Living with nature"]
    # "with" is the accent word: `h1 em` in site.css is Cormorant Garamond italic, normal case.
    assert page.text["em"] == ["with"]
    assert re.search(r"<h1[^>]*>\s*Living <em[^>]*>with</em> nature\s*</h1>", main)


def test_home_page_h1_is_under_a_plain_letter_in_sand(client: Client) -> None:
    main = _main(_get(client, "/"))

    letter = re.search(r'<p class="home-letter"[^>]*style="([^"]*)"[^>]*>\s*Ở\s*</p>', main)
    assert letter, "no plain letter Ở above the h1"
    assert "color: var(--sand)" in letter.group(1)
    assert "font-family: var(--font-serif)" in letter.group(1)
    assert main.index(letter.group(0)) < main.index("<h1")
    # Plain: no photo and no video in it until the hero of the later task.
    assert not _parse(main).all("img")
    assert not _parse(main).all("video")


@pytest.mark.parametrize(("address", "heading", "number", "word"), INNER_PAGES)
def test_inner_page_has_the_chapter_marker_the_chapter_word_and_the_h1(
    client: Client, address: str, heading: str, number: str, word: str | None
) -> None:
    main = _main(_get(client, address))
    page = _parse(main)

    assert page.text["h1"] == [heading]
    # The marker: the hook of the letter ở (U+0309, on a no-break space), then the number.
    marker = re.search(r'<p class="chapter-marker[^"]*"[^>]*>(.*?)</p>', main, re.DOTALL)
    assert marker, "no chapter marker"
    assert unescape(marker.group(1)) == f" ̉ {number}"
    assert main.index(marker.group(0)) < main.index("<h1")
    words = re.findall(r'<p class="chapter-word"[^>]*>\s*(.*?)\s*</p>', main, re.DOTALL)
    if word is None:
        assert words == []
    else:
        assert words == [word]
        assert main.index(marker.group(0)) < main.index(word) < main.index("<h1")


@pytest.mark.parametrize("address", ADDRESSES)
def test_h1_is_drawn_in_capitals_without_changing_its_text(client: Client, address: str) -> None:
    # text-transform would make a browser report "THE HOUSE", and the browser check of the
    # issue looks for the text as written (as the 404 page does).
    (h1,) = _parse(_main(_get(client, address))).all("h1")
    style = h1["style"] or ""

    assert "text-transform: none" in style
    assert "font-variant-caps: all-small-caps" in style


@pytest.mark.parametrize(("address", "heading", "_number", "_word"), INNER_PAGES)
def test_inner_page_marks_its_link_in_the_header(
    client: Client, address: str, heading: str, _number: str, _word: str | None
) -> None:
    current = [a for a in _parse(_get(client, address)).all("a") if a.get("aria-current")]

    assert current
    assert {a["href"] for a in current} == {address}


# AC14


@pytest.mark.parametrize(("address", "title", "description"), PAGES)
def test_page_has_its_title_and_description(
    client: Client, address: str, title: str, description: str
) -> None:
    page = _parse(_get(client, address))

    assert page.text["title"] == [title]
    assert page.meta("name", "description") == [description]


# AC15


@pytest.mark.parametrize("address", ADDRESSES)
@pytest.mark.parametrize("query", ["", "?t=dusk", "?t=nonsense&utm_source=x"])
def test_canonical_is_the_base_url_plus_the_path_without_any_query(
    client: Client, settings: Settings, address: str, query: str
) -> None:
    settings.SITE_BASE_URL = BASE

    page = _parse(_get(client, address + query))

    assert _canonical(page) == [BASE + address]
    assert page.meta("property", "og:url") == [BASE + address]


@pytest.mark.parametrize(("address", "title", "description"), PAGES)
def test_page_has_the_open_graph_tags(
    client: Client, address: str, title: str, description: str
) -> None:
    page = _parse(_get(client, address))

    assert page.meta("property", "og:title") == [title]
    assert page.meta("property", "og:description") == [description]
    assert page.meta("property", "og:type") == ["website"]
    assert page.meta("property", "og:site_name") == [SITE_NAME]


def test_query_is_never_echoed_into_the_search_tags(client: Client) -> None:
    html = _get(client, '/house/?t="><b>x</b>&next=//evil.example')

    assert "evil.example" not in html
    assert "<b>x</b>" not in html


def test_canonical_of_an_unknown_page_is_refused() -> None:
    with pytest.raises(KeyError):
        seo.head_for("blog")


# AC16


def test_sitemap_lists_the_five_canonical_addresses_and_nothing_else(
    client: Client, settings: Settings
) -> None:
    settings.SITE_BASE_URL = BASE

    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/xml"
    root = ElementTree.fromstring(response.content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    assert root.tag == f"{namespace}urlset"
    assert [child.tag for child in root] == [f"{namespace}url"] * 5
    assert [loc.text for loc in root.iter(f"{namespace}loc")] == [BASE + a for a in ADDRESSES]


def test_sitemap_escapes_the_base_url() -> None:
    xml = seo.sitemap_xml("https://o.example/a&b")

    assert "<loc>https://o.example/a&amp;b/house/</loc>" in xml
    ElementTree.fromstring(xml.encode())


# AC17


def _settings_from_environment(**extra: str) -> dict[str, object]:
    """The settings are read once per process, so each case loads them in a fresh one."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_")
        and key not in {"PYTHONPATH", "INDEXING_ENABLED", "SITE_BASE_URL"}
    }
    env.update({"DJANGO_SETTINGS_MODULE": "config.settings", "PYTHONPATH": str(SRC), **extra})
    probe = (
        "import json; from django.conf import settings; "
        "print(json.dumps([settings.INDEXING_ENABLED, settings.SITE_BASE_URL]))"
    )
    done = subprocess.run(
        [sys.executable, "-c", probe], env=env, capture_output=True, text=True, check=True
    )
    indexing, base_url = json.loads(done.stdout.strip().splitlines()[-1])
    return {"indexing": indexing, "base_url": base_url}


def test_indexing_is_off_and_the_base_url_is_local_by_default() -> None:
    assert _settings_from_environment() == {"indexing": False, "base_url": "http://localhost:8000"}


def test_indexing_is_on_only_when_the_environment_says_1() -> None:
    assert _settings_from_environment(INDEXING_ENABLED="1")["indexing"] is True
    for value in ("0", "", "true", "yes", "on", "11"):
        assert _settings_from_environment(INDEXING_ENABLED=value)["indexing"] is False, value


def test_base_url_comes_from_the_environment() -> None:
    result = _settings_from_environment(SITE_BASE_URL="https://o.example/")

    assert result["base_url"] == "https://o.example"


@pytest.mark.parametrize("address", ADDRESSES)
def test_indexing_off_every_page_says_noindex(
    client: Client, settings: Settings, address: str
) -> None:
    settings.INDEXING_ENABLED = False

    page = _parse(_get(client, address))

    assert page.meta("name", "robots") == ["noindex, nofollow"]


@pytest.mark.parametrize("address", ADDRESSES)
def test_indexing_on_every_page_says_index(
    client: Client, settings: Settings, address: str
) -> None:
    settings.INDEXING_ENABLED = True

    page = _parse(_get(client, address))

    assert page.meta("name", "robots") == ["index, follow"]


def test_indexing_off_robots_txt_disallows_everything(client: Client, settings: Settings) -> None:
    settings.INDEXING_ENABLED = False
    settings.SITE_BASE_URL = BASE

    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert response.content.decode().splitlines() == [
        "User-agent: *",
        "Disallow: /",
        f"Sitemap: {BASE}/sitemap.xml",
    ]


def test_indexing_on_robots_txt_allows_everything(client: Client, settings: Settings) -> None:
    settings.INDEXING_ENABLED = True
    settings.SITE_BASE_URL = BASE

    response = client.get("/robots.txt")

    assert response.content.decode().splitlines() == [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {BASE}/sitemap.xml",
    ]


def test_not_found_page_stays_out_of_search_results_when_indexing_is_on(
    client: Client, settings: Settings
) -> None:
    settings.DEBUG = False
    settings.INDEXING_ENABLED = True

    response = client.get("/this-page-does-not-exist/")

    assert response.status_code == 404
    page = _parse(response.content.decode())
    assert page.meta("name", "robots") == ["noindex, nofollow"]
    assert _canonical(page) == []


# AC18


@pytest.mark.django_db
@pytest.mark.parametrize("address", EVERY_ADDRESS)
def test_page_asks_the_database_nothing(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(0):
        response = client.get(address)

    assert response.status_code == 200
