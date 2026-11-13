"""The site as one page: the chapters of `/`, the menu, the old addresses and the photo tag
(one-page spec, AC1 to AC8)."""

import re
from html import unescape
from html.parser import HTMLParser
from xml.etree import ElementTree

import pytest
from django.conf import settings
from django.template import Context, Template
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings
from pytest_mock import MockerFixture

from owner_content.models import SiteSettings
from owner_content.services import site_settings
from pages import photos

pytestmark = pytest.mark.django_db

BASE = "https://o.example"
# id, marker label after the hook, chapter word (FAQ has none), heading: the table of the
# spec (the label with its gloss: design-match AC4).
CHAPTERS = [
    ("house", "01 · at home", "ở nhà", "The house"),
    ("hoa-xuan", "02 · close by", "ở gần", "Hòa Xuân"),
    ("rent", "03 · to stay a long while", "ở lâu", "The rent"),
    ("faq", "04 · questions", None, "FAQ"),
    ("contact", "05", "ở lại?", "Will you stay?"),
]
NAV_LINKS = [
    ("The house", "/#house"),
    ("Hòa Xuân", "/#hoa-xuan"),
    ("Rent", "/#rent"),
    ("FAQ", "/#faq"),
    ("Contact", "/#contact"),
]
OLD_ADDRESSES = [
    ("/house/", "/#house"),
    ("/hoa-xuan/", "/#hoa-xuan"),
    ("/faq/", "/#faq"),
    ("/contact/", "/#contact"),
]
TEMPLATES = settings.SRC_DIR / "pages" / "templates" / "pages"
CSS = settings.SRC_DIR / "static" / "css"


class _Tags(HTMLParser):
    """Collects every start tag with its attributes."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))

    def all(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == name]


def _parse(html: str) -> _Tags:
    parser = _Tags()
    parser.feed(html)
    return parser


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, chapter_id: str) -> str:
    match = re.search(rf'<section id="{chapter_id}"[^>]*>.*?</section>', html, re.DOTALL)
    assert match, f"no section #{chapter_id}"
    return match.group(0)


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _photo(source: str, **context: object) -> str:
    return Template("{% load photos %}" + source).render(Context(context))


# AC1


def test_chapters_follow_the_hero_in_order(client: Client) -> None:
    html = _home(client)

    ids = re.findall(r'<section id="([\w-]+)"', html)
    assert ids == ["hero", *[chapter_id for chapter_id, *_rest in CHAPTERS]]


@pytest.mark.parametrize(("chapter_id", "number", "word", "heading"), CHAPTERS)
def test_chapter_has_its_marker_word_and_h2(
    client: Client, chapter_id: str, number: str, word: str | None, heading: str
) -> None:
    section = _section(_home(client), chapter_id)

    # The marker: the hook of the letter ở (U+0309, on a no-break space), then the label.
    marker = re.search(r'<p class="chapter-marker[^"]*"[^>]*>(.*?)</p>', section, re.DOTALL)
    assert marker, "no chapter marker"
    assert unescape(marker.group(1)) == f" ̉ {number}"
    words = re.findall(r'<p class="chapter-word"[^>]*>\s*(.*?)\s*</p>', section, re.DOTALL)
    assert words == ([] if word is None else [word])
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", section, re.DOTALL)
    assert [_text(part) for part in h2] == [heading]
    assert section.index(marker.group(0)) < section.index("<h2")
    if word is not None:
        assert section.index(marker.group(0)) < section.index(word) < section.index("<h2")


def test_page_has_one_h1_the_heros(client: Client) -> None:
    html = _home(client)

    assert len(_parse(html).all("h1")) == 1
    hero = re.search(r'<section id="hero".*?</section>', html, re.DOTALL)
    assert hero and "<h1" in hero.group(0)


# AC2


@pytest.mark.parametrize("tag", ["nav", "details"])
def test_menu_links_jump_to_the_chapters(client: Client, tag: str) -> None:
    header = re.search(r"<header\b.*?</header>", _home(client), re.DOTALL)
    assert header
    block = re.search(rf"<{tag}\b.*?</{tag}>", header.group(0), re.DOTALL)
    assert block

    links = [
        (_text(text), href)
        for href, text in re.findall(r'<a href="([^"]*)"[^>]*>(.*?)</a>', block.group(0))
    ]
    assert links == NAV_LINKS


def test_no_link_carries_aria_current(client: Client) -> None:
    assert "aria-current" not in _home(client)


# AC3


@pytest.mark.parametrize(("address", "location"), OLD_ADDRESSES)
def test_old_address_redirects_for_good_to_its_chapter(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str, location: str
) -> None:
    with django_assert_num_queries(0):
        response = client.get(address)

    assert response.status_code == 301
    assert response["Location"] == location


# AC4


def test_sitemap_lists_only_the_home_page(client: Client, settings: Settings) -> None:
    settings.SITE_BASE_URL = BASE

    root = ElementTree.fromstring(client.get("/sitemap.xml").content)

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    assert [loc.text for loc in root.iter(f"{namespace}loc")] == [f"{BASE}/"]


# AC5


def test_home_page_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        response = client.get("/")

    assert response.status_code == 200


def test_home_page_has_the_site_settings_as_owner(client: Client) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(owner_first_name="Lan", price_from_million=9)

    response = client.get("/")

    assert response.context["owner"] == site_settings()
    assert response.context["owner"].greeting == "Hi, I'm Lan."


@pytest.mark.parametrize("address", ["/sitemap.xml", "/robots.txt", "/healthz/"])
def test_other_addresses_make_no_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(0):
        assert client.get(address).status_code == 200


# AC6


def test_photo_tag_renders_the_media_slot_of_the_photo() -> None:
    entry = photos.PHOTOS["veranda"]

    html = _photo('{% photo "veranda" ratio="4 / 3" %}')

    (img,) = _parse(html).all("img")
    assert img["src"] == f"/static/{entry.path}"
    assert img["alt"] == entry.alt
    assert img["width"] == str(entry.width)
    assert img["height"] == str(entry.height)
    assert "aspect-ratio: 4 / 3" in html
    assert "Illustrative photo" in html
    assert f'<figcaption class="media__credit">{entry.credit}</figcaption>' in html


def test_first_photo_of_the_page_is_not_lazy_and_the_next_ones_are() -> None:
    html = _photo('{% photo "veranda" %}{% photo "kitchen" %}{% photo "bedroom" %}')

    loading = [img.get("loading") for img in _parse(html).all("img")]
    assert loading == [None, "lazy", "lazy"]


def test_first_photo_counts_across_included_templates() -> None:
    # Each chapter is an included template: only the first photo of the whole page is eager.
    chapter = Template('{% load photos %}{% photo "tea" %}{% photo "kitchen" %}')

    html = _photo(
        '{% include chapter %}{% photo "veranda" %}{% include chapter %}', chapter=chapter
    )

    loading = [img.get("loading") for img in _parse(html).all("img")]
    assert loading == [None, "lazy", "lazy", "lazy", "lazy"]


def test_each_page_render_starts_with_an_eager_photo() -> None:
    template = Template('{% load photos %}{% photo "tea" %}')

    first = template.render(Context({}))
    second = template.render(Context({}))

    assert 'loading="lazy"' not in first
    assert 'loading="lazy"' not in second


def test_unknown_photo_gives_the_empty_state() -> None:
    html = _photo('{% photo "no-such-photo" ratio="4 / 3" %}')

    assert "media--empty" in html
    assert "<img" not in html
    assert "aspect-ratio: 4 / 3" in html


def test_missing_photo_file_gives_the_empty_state(mocker: MockerFixture) -> None:
    mocker.patch("pages.photos.finders.find", return_value=None)

    html = _photo('{% photo "veranda" %}')

    assert "media--empty" in html
    assert "<img" not in html


def test_photo_key_can_come_from_a_variable() -> None:
    html = _photo("{% photo key %}", key="tea")

    assert "/static/media/photos/tea.jpg" in html


def test_accent_word_of_a_chapter_heading_stays_lower_case(client: Client) -> None:
    site = (CSS / "site.css").read_text(encoding="utf-8")

    assert '<span class="accent">stay?</span>' in _section(_home(client), "contact")
    assert re.search(r"\.chapter h2 \.accent\s*\{[^}]*font-variant-caps:\s*normal", site)


# AC7


@pytest.mark.parametrize("name", ["house", "hoa_xuan", "rent", "faq", "contact"])
def test_each_chapter_has_its_template_and_stylesheet(client: Client, name: str) -> None:
    home = (TEMPLATES / "home.html").read_text(encoding="utf-8")

    assert (TEMPLATES / "chapters" / f"{name}.html").is_file()
    assert (CSS / "chapters" / f"{name}.css").is_file()
    assert f'{{% include "pages/chapters/{name}.html" %}}' in home
    assert f"css/chapters/{name}.css" in home
    assert f'href="/static/css/chapters/{name}.css"' in _home(client)


@pytest.mark.parametrize("name", ["house", "hoa_xuan", "faq", "contact"])
def test_old_page_templates_are_removed(name: str) -> None:
    assert not (TEMPLATES / f"{name}.html").exists()


# AC8


def test_nothing_of_the_chapters_is_wider_than_the_screen() -> None:
    site = (CSS / "site.css").read_text(encoding="utf-8")

    # The chapter word is the widest text; it wraps instead of pushing the page sideways.
    assert re.search(r"\.chapter\s*\{[^}]*overflow-wrap:\s*anywhere", site)
    assert re.search(r"\.chapter\s*\{[^}]*max-width:\s*100%", site)
    for sheet in sorted((CSS / "chapters").glob("*.css")):
        assert "100vw" not in sheet.read_text(encoding="utf-8"), sheet.name
