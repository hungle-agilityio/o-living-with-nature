"""The "page not found" page of design E: an unknown address, with debug off (AC19)."""

import re
from html.parser import HTMLParser

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db

UNKNOWN_ADDRESS = "/this-page-does-not-exist/"
HEADING = "This path leads nowhere — the garden is this way."
LINE = "The page you were looking for isn't here. It may have moved, or the link has a typo."


class _Page(HTMLParser):
    """Collects the start tags with their attributes, and the text of each link and element."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.links: list[tuple[dict[str, str | None], str]] = []
        self.text: dict[str, list[str]] = {}
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag == "a":
            self.links.append((dict(attrs), ""))
        if tag not in {"meta", "link", "img", "source", "br"}:
            self._stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._stack:
            while self._stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if not self._stack or not data.strip():
            return
        self.text.setdefault(self._stack[-1], []).append(data.strip())
        if self._stack[-1] == "a":
            attrs, text = self.links[-1]
            self.links[-1] = (attrs, (text + " " + data.strip()).strip())

    def all(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == name]


def _parse(html: str) -> _Page:
    page = _Page()
    page.feed(html)
    return page


def _main(html: str) -> str:
    match = re.search(r"<main\b.*?</main>", html, re.DOTALL)
    assert match, "no <main> in the page"
    return match.group(0)


@pytest.fixture
def not_found(client: Client, settings: Settings) -> str:
    settings.DEBUG = False
    response = client.get(UNKNOWN_ADDRESS)
    assert response.status_code == 404
    return response.content.decode()


def test_unknown_address_answers_404_with_the_site_page(client: Client, settings: Settings) -> None:
    settings.DEBUG = False

    response = client.get(UNKNOWN_ADDRESS)

    assert response.status_code == 404
    assert "404.html" in [template.name for template in response.templates]
    assert "base.html" in [template.name for template in response.templates]


def test_page_has_the_header_and_the_footer(not_found: str) -> None:
    page = _parse(not_found)

    assert '<html lang="en">' in not_found
    assert len(page.all("header")) == 1
    assert len(page.all("footer")) == 1
    wordmark = [a for a in page.all("a") if "wordmark" in (a.get("class") or "")]
    assert [a["href"] for a in wordmark] == ["/"]
    assert "a word for staying · Hòa Xuân, Đà Nẵng" in not_found
    assert "aria-current" not in not_found


def test_page_has_the_label_the_heading_and_the_line(not_found: str) -> None:
    main = _main(not_found)
    page = _parse(main)

    assert re.search(r'<p class="label[^"]*">\s*404\s*</p>', main)
    assert page.text["h1"] == [HEADING]
    assert len(page.all("h1")) == 1
    assert LINE in page.text["p"]
    # The label comes first, then the heading, then the line.
    assert main.index(">404<") < main.index(HEADING) < main.index(LINE)


def test_heading_is_drawn_in_capitals_without_changing_its_text(not_found: str) -> None:
    # text-transform would make a browser report "THIS PATH LEADS NOWHERE", and the browser
    # check of the issue looks for the text as written.
    (h1,) = _parse(_main(not_found)).all("h1")
    style = h1["style"] or ""

    assert "text-transform: none" in style
    assert "font-variant-caps: all-small-caps" in style


def test_page_has_the_two_buttons(not_found: str) -> None:
    links = _parse(_main(not_found)).links

    assert [(attrs["href"], text) for attrs, text in links] == [
        ("/", "Back to the home page"),
        ("/contact/", "Contact Bún"),
    ]
    home, contact = (attrs["class"] or "" for attrs, _text in links)
    assert home.split() == ["button"]
    assert contact.split() == ["button", "button--secondary"]


def test_page_carries_noindex(not_found: str) -> None:
    robots = [meta for meta in _parse(not_found).all("meta") if meta.get("name") == "robots"]

    assert len(robots) == 1
    assert "noindex" in (robots[0]["content"] or "")
    assert not_found.index('name="robots"') < not_found.index("</head>")


def test_page_title_names_the_site(not_found: str) -> None:
    # The issue gives no title for this page, so it keeps the title of the site.
    (title,) = _parse(not_found).text["title"]

    assert title == "Ở — Living with Nature"


def test_page_uses_no_javascript(not_found: str) -> None:
    assert "<script" not in not_found
    assert "onclick" not in not_found


def test_home_page_does_not_get_the_noindex_of_the_404_page(
    client: Client, settings: Settings
) -> None:
    # Since the indexing switch (AC17) every page has a robots tag; with the switch on, the
    # home page is indexed while the 404 page keeps its noindex.
    settings.INDEXING_ENABLED = True

    response = client.get("/")

    assert response.status_code == 200
    assert "noindex" not in response.content.decode()


@pytest.mark.django_db
def test_page_asks_the_database_nothing(
    client: Client, settings: Settings, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    settings.DEBUG = False

    with django_assert_num_queries(0):
        response = client.get(UNKNOWN_ADDRESS)

    assert response.status_code == 404
