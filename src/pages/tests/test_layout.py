"""The shared layout of design E: language, header, footer, design tokens and the media slot."""

import re
from html.parser import HTMLParser

import pytest
from django.conf import settings
from django.template.loader import render_to_string
from django.test import Client

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db

# The menu jumps to the chapters of the one page (one-page AC2).
NAV_LINKS = [
    ("The house", "/#house"),
    ("Hòa Xuân", "/#hoa-xuan"),
    ("Rent", "/#rent"),
    ("FAQ", "/#faq"),
    ("Contact", "/#contact"),
]
STAND_IN_LINE = (
    "Photos and videos marked &quot;Illustrative&quot; are stand-ins until the house is finished."
)


class _Tags(HTMLParser):
    """Collects every start tag with its attributes, and the text inside chosen elements."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.stack: list[str] = []
        self.text: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))
        if tag not in {"meta", "link", "img", "source", "br"}:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.stack:
            while self.stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if self.stack and data.strip():
            self.text.setdefault(self.stack[-1], []).append(data.strip())

    def all(self, name: str) -> list[dict[str, str | None]]:
        return [attrs for tag, attrs in self.tags if tag == name]


def _parse(html: str) -> _Tags:
    parser = _Tags()
    parser.feed(html)
    return parser


def _home(client: Client, **headers: str) -> str:
    response = client.get("/", **headers)  # type: ignore[arg-type]
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b.*?</{tag}>", html, re.DOTALL)
    assert match, f"no <{tag}> in the page"
    return match.group(0)


def _css() -> str:
    return (settings.SRC_DIR / "static" / "css" / "site.css").read_text(encoding="utf-8")


def _media(**context: object) -> str:
    return render_to_string("includes/media.html", context)


# AC1


def test_settings_are_english_only() -> None:
    assert settings.LANGUAGE_CODE == "en"
    assert [code for code, _name in settings.LANGUAGES] == ["en"]


def test_page_is_english_whatever_the_browser_asks(client: Client) -> None:
    html = _home(client, HTTP_ACCEPT_LANGUAGE="vi")

    assert '<html lang="en">' in html


# AC2


def test_header_has_the_wordmark_linking_home(client: Client) -> None:
    header = _section(_home(client), "header")

    wordmark = [a for a in _parse(header).all("a") if "wordmark" in (a.get("class") or "")]
    assert len(wordmark) == 1
    assert wordmark[0]["href"] == "/"
    assert re.search(r'class="wordmark"[^>]*>\s*Ở\s*</a>', header)


def test_header_row_has_the_five_chapter_links(client: Client) -> None:
    header = _section(_home(client), "header")
    row = _section(header, "nav")

    for label, href in NAV_LINKS:
        assert re.search(rf'<a href="{href}"[^>]*>{label}</a>', row), label


def test_no_link_is_current_on_the_home_page(client: Client) -> None:
    header = _section(_home(client), "header")

    assert "aria-current" not in header


# AC3


def test_phone_menu_is_a_details_element_with_the_five_chapter_links(client: Client) -> None:
    header = _section(_home(client), "header")
    details = _section(header, "details")

    assert re.search(r"<summary[^>]*>\s*Menu\s*</summary>", details)
    assert "<ul" in details
    for label, href in NAV_LINKS:
        assert re.search(rf'<li><a href="{href}"[^>]*>{label}</a></li>', details), label


def test_menu_swaps_with_the_row_at_760px_in_the_stylesheet() -> None:
    css = _css()

    assert "@media (max-width: 760px)" in css
    phone = css.split("@media (max-width: 760px)", 1)[1]
    assert re.search(r"\.nav-row\s*\{[^}]*display:\s*none", phone)
    assert re.search(r"\.nav-menu\s*\{[^}]*display:\s*block", phone)
    # Outside the phone rule the menu is hidden and the row shows.
    assert re.search(r"\.nav-menu\s*\{[^}]*display:\s*none", css.split("@media", 1)[0])


def test_page_uses_no_javascript(client: Client) -> None:
    html = _home(client)

    # The menu needs no script. The scripts of the home page are the hero's flight (AC22), the
    # photo dialog of the floor plan (one-page AC17) and the phone contact bar (one-page AC12,
    # with the owner's channels, as in the test database), after the load and reveal motion that
    # base.html links (design-match AC13).
    assert "<script" not in _section(html, "header")
    assert re.findall(r"<script[^>]*>", html) == [
        '<script src="/static/js/reveal.js" defer>',
        '<script src="/static/js/hero.js" defer>',
        '<script src="/static/js/floor-plan.js" defer>',
        '<script src="/static/js/contact-bar.js" defer>',
    ]
    assert "onclick" not in html


# AC4


def test_footer_has_the_lines_of_the_design(client: Client) -> None:
    footer = _section(_home(client), "footer")

    assert "a word for staying · Hòa Xuân, Đà Nẵng" in footer
    assert re.search(r">\s*Ở\s*<", footer)
    assert STAND_IN_LINE in footer


# AC5


def test_stylesheet_defines_the_design_tokens() -> None:
    css = _css()
    root = _section_css(css, ":root")

    expected = {
        "--ground": "#f4f0e8",
        "--ink": "#1f2a22",
        "--muted": "#5c6358",
        "--line": "#d9d2c3",
        "--paper": "#f4f0e8",
        "--sand": "#e9e2d3",
        "--band": "#1f2a22",
        "--size-headline": "150px",
        "--size-chapter": "200px",
        "--size-big": "84px",
        "--size-gloss": "26px",
        "--size-body": "16px",
        "--size-label": "11px",
        "--space-1": "8px",
        "--space-2": "16px",
        "--space-3": "24px",
        "--space-4": "32px",
        "--space-5": "48px",
        "--space-6": "64px",
        "--space-7": "136px",
        "--content-max": "1360px",
        "--side": "40px",
        "--button-height": "48px",
        "--button-radius": "999px",
        "--button-size": "13px",
        "--button-spacing": "0.16em",
    }
    for name, value in expected.items():
        assert re.search(rf"{name}:\s*{re.escape(value)}\s*;", root, re.IGNORECASE), name
    assert re.search(r'--font-sans:\s*"Be Vietnam Pro"', root)
    assert re.search(r'--font-serif:\s*"Cormorant Garamond"', root)


def test_stylesheet_has_the_phone_sizes() -> None:
    phone = _css().split("@media (max-width: 760px)", 1)[1]

    for name, value in {
        "--size-headline": "60px",
        "--size-chapter": "96px",
        "--size-big": "44px",
        "--size-gloss": "22px",
        "--side": "18px",
    }.items():
        assert re.search(rf"{name}:\s*{value}\s*;", phone), name


def test_stylesheet_has_the_two_buttons() -> None:
    css = _css()

    assert re.search(r"\.button\s*\{[^}]*min-height:\s*var\(--button-height\)", css)
    assert re.search(r"\.button\s*\{[^}]*border-radius:\s*var\(--button-radius\)", css)
    assert ".button--secondary" in css


def test_labels_are_capitals_without_changing_the_text_of_the_page() -> None:
    # text-transform would change the text a browser reports ("THE HOUSE"), so the labels,
    # the navigation and the buttons use small capitals instead.
    css = _css()

    for selector in (".site-footer__note", ".button", ".media__chip"):
        rule = _section_css(css, selector)
        assert "font-variant-caps: all-small-caps" in rule, selector
        assert "text-transform" not in rule, selector


def test_pages_load_the_two_fonts_from_google_fonts(client: Client) -> None:
    links = _parse(_home(client)).all("link")

    preconnect = [link["href"] for link in links if link.get("rel") == "preconnect"]
    assert preconnect == ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]
    fonts = [
        link["href"] or ""
        for link in links
        if link.get("rel") == "stylesheet" and "fonts.googleapis.com" in (link["href"] or "")
    ]
    assert len(fonts) == 1
    assert fonts[0].startswith("https://fonts.googleapis.com/css2?")
    assert "family=Be+Vietnam+Pro" in fonts[0]
    assert "family=Cormorant+Garamond" in fonts[0]
    assert "display=swap" in fonts[0]


def _section_css(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no {selector} rule"
    return match.group(1)


# AC6


def test_media_slot_with_an_illustrative_photo() -> None:
    html = _media(
        ratio="4 / 3",
        photo="/static/media/hero/day.jpg",
        alt="Morning light in the leaves",
        width=1280,
        height=720,
        illustrative=True,
        credit="Photo: Pexels",
    )
    parsed = _parse(html)

    assert "aspect-ratio: 4 / 3" in html
    (img,) = parsed.all("img")
    assert img["src"] == "/static/media/hero/day.jpg"
    assert img["alt"] == "Morning light in the leaves"
    assert img["width"] == "1280"
    assert img["height"] == "720"
    assert img["loading"] == "lazy"
    assert parsed.text["span"] == ["Illustrative photo"]
    assert parsed.text["figcaption"] == ["Photo: Pexels"]
    assert not parsed.all("video")


def test_media_slot_photo_without_the_flag_has_no_chip_and_no_caption() -> None:
    html = _media(ratio="4 / 3", photo="/static/media/hero/day.jpg", alt="Leaves", credit="Pexels")

    assert "Illustrative" not in html
    assert "<figcaption" not in html


def test_media_slot_first_photo_of_a_page_is_not_lazy() -> None:
    html = _media(ratio="4 / 3", photo="/static/media/hero/day.jpg", alt="Leaves", eager=True)

    (img,) = _parse(html).all("img")
    assert "loading" not in img


def test_media_slot_with_a_video() -> None:
    html = _media(
        ratio="16 / 9",
        video="/static/media/hero/day.mp4",
        photo="/static/media/hero/day.jpg",
        alt="Morning light in the leaves",
        illustrative=True,
        credit="Video: Pexels",
    )
    parsed = _parse(html)

    assert "aspect-ratio: 16 / 9" in html
    assert re.search(r'<video muted loop playsinline autoplay preload="metadata" poster="', html)
    (video,) = parsed.all("video")
    assert video["poster"] == "/static/media/hero/day.jpg"
    (source,) = parsed.all("source")
    assert source["src"] == "/static/media/hero/day.mp4"
    assert parsed.text["span"] == ["Illustrative video"]
    assert parsed.text["figcaption"] == ["Video: Pexels"]


def test_media_slot_video_shows_only_the_poster_under_reduced_motion() -> None:
    html = _media(
        ratio="16 / 9",
        video="/static/media/hero/day.mp4",
        photo="/static/media/hero/day.jpg",
        alt="Morning light in the leaves",
    )
    parsed = _parse(html)

    # The poster is in the page as a photo, and the video file is only offered when motion is fine.
    (img,) = parsed.all("img")
    assert img["src"] == "/static/media/hero/day.jpg"
    assert "media__poster" in (img["class"] or "")
    (source,) = parsed.all("source")
    assert source["media"] == "(prefers-reduced-motion: no-preference)"
    css = _css()
    assert re.search(r"\.media__poster\s*\{[^}]*display:\s*none", css)
    reduced = css.split("@media (prefers-reduced-motion: reduce)", 1)[1]
    assert re.search(r"\.media video\s*\{[^}]*display:\s*none", reduced)
    assert re.search(r"\.media__poster\s*\{[^}]*display:\s*block", reduced)


def test_media_slot_with_no_file_shows_the_empty_state() -> None:
    html = _media(ratio="4 / 3", alt="The veranda", illustrative=True, credit="Photo: Pexels")
    parsed = _parse(html)

    assert "aspect-ratio: 4 / 3" in html
    assert "media--empty" in html
    assert parsed.text["div"] == ["Ở"]
    assert not parsed.all("img")
    assert not parsed.all("video")
    assert "Illustrative" not in html
    assert "<figcaption" not in html
    assert "Photo: Pexels" not in html
    empty = _section_css(_css(), ".media--empty")
    assert "var(--sand)" in empty


# AC7


def test_page_is_laid_out_for_a_narrow_screen(client: Client) -> None:
    html = _home(client)

    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html
    assert re.search(r"img,\s*video\s*\{[^}]*max-width:\s*100%", _css())
