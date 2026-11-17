"""What search engines read: each page's title, description and canonical address, the robots
value, `sitemap.xml` and `robots.txt`."""

import json
from dataclasses import dataclass
from xml.sax.saxutils import escape

from django.conf import settings

from owner_content.services import SiteSettingsValue
from pages import language
from pages.texts import shell

SITE_NAME = shell.EN["site_name"]
OG_TYPE = "website"

ROBOTS_INDEX = "index, follow"
ROBOTS_NOINDEX = "noindex, nofollow"

SITEMAP_PATH = "/sitemap.xml"

# The home page in each language lists the same alternates (hreflang, path); the paths come
# from `pages.language`, the one place that names the address of each language.
VI_PREFIX = language.home_path(language.VI).rstrip("/")
ALTERNATE_PATHS: tuple[tuple[str, str], ...] = (
    (language.EN, language.home_path(language.EN)),
    (language.VI, language.home_path(language.VI)),
    ("x-default", language.home_path(language.EN)),
)
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"

SCHEMA_CONTEXT = "https://schema.org"
SCHEMA_TYPE = "LodgingBusiness"
ADDRESS: dict[str, str] = {
    "@type": "PostalAddress",
    "addressLocality": "Hòa Xuân",
    "addressRegion": "Đà Nẵng",
    "addressCountry": "VN",
}
CALL_KEY = "call"
TEL_PREFIX = "tel:"


@dataclass(frozen=True)
class Page:
    """One public page: its address on the site and the texts of its search result."""

    path: str
    title: str
    description: str


@dataclass(frozen=True)
class Head:
    """The search tags of one page, ready for the `head` of `base.html`."""

    title: str
    description: str
    canonical: str
    robots: str
    site_name: str = SITE_NAME
    og_type: str = OG_TYPE
    site_verification: str = ""
    alternates: tuple[tuple[str, str], ...] = ()


# The pages of phase 1, in the order of the sitemap: the one page `/` (the old page addresses
# redirect to its chapters and are not listed). The texts change through issues.
PAGES: dict[str, Page] = {
    "home": Page(
        path="/",
        title=shell.EN["seo_title"],
        description=shell.EN["seo_description"],
    ),
}


def canonical_url(path: str, base_url: str | None = None) -> str:
    """The one public address of a path: the base URL plus the path, never a query."""
    base = settings.SITE_BASE_URL if base_url is None else base_url
    return base.rstrip("/") + path


def robots_value(indexing_enabled: bool | None = None) -> str:
    """What the robots meta tag says: out of search results unless indexing is switched on."""
    enabled = settings.INDEXING_ENABLED if indexing_enabled is None else indexing_enabled
    return ROBOTS_INDEX if enabled else ROBOTS_NOINDEX


def head_for(name: str, lang: str | None = None) -> Head:
    """The search tags of the page with this name in `lang` (default: the current language);
    an unknown name is a KeyError. Both languages list the same alternates."""
    page = PAGES[name]
    alternates = tuple((hreflang, canonical_url(path)) for hreflang, path in ALTERNATE_PATHS)
    if language.normalise(lang or language.current()) == language.VI:
        words = shell.VI
        return Head(
            title=words["seo_title"],
            description=words["seo_description"],
            canonical=canonical_url(VI_PREFIX + page.path),
            robots=robots_value(),
            site_name=words["site_name"],
            site_verification=settings.GOOGLE_SITE_VERIFICATION,
            alternates=alternates,
        )
    return Head(
        title=page.title,
        description=page.description,
        canonical=canonical_url(page.path),
        robots=robots_value(),
        site_verification=settings.GOOGLE_SITE_VERIFICATION,
        alternates=alternates,
    )


def page_head(
    lang: str,
    *,
    title: str,
    description: str,
    path: str,
    og_type: str,
    alternates: tuple[tuple[str, str], ...],
) -> Head:
    """The search tags of a page outside `PAGES` (a journal page): `path` already carries the
    `/vi` prefix in Vietnamese, and `alternates` holds full addresses (or nothing)."""
    words = shell.VI if language.normalise(lang) == language.VI else shell.EN
    return Head(
        title=title,
        description=description,
        canonical=canonical_url(path),
        robots=robots_value(),
        site_name=words["site_name"],
        og_type=og_type,
        site_verification=settings.GOOGLE_SITE_VERIFICATION,
        alternates=alternates,
    )


def structured_data(head: Head, owner: SiteSettingsValue) -> str:
    """The JSON-LD text of the page, safe to place inside a `<script>` element.

    After `json.dumps`, `<`, `>` and `&` become `\\u003c`, `\\u003e` and `\\u0026`, so no text
    (a price line, for example) can close the script element or open a tag; JSON readers decode
    the escapes back to the same characters.
    """
    data: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": SCHEMA_TYPE,
        "name": head.site_name,
        "description": head.description,
        "url": head.canonical,
        "address": ADDRESS,
    }
    if owner.price_line is not None:
        data["priceRange"] = owner.price_line
    call = next((channel for channel in owner.channels if channel.key == CALL_KEY), None)
    if call is not None:
        data["telephone"] = call.link.removeprefix(TEL_PREFIX)
    text = json.dumps(data, ensure_ascii=False)
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def sitemap_xml(base_url: str | None = None) -> str:
    """`sitemap.xml`: the canonical address of the home page in each language, each with the
    alternates of both; it does not depend on the active language."""
    links = "".join(
        f'<xhtml:link rel="alternate" hreflang="{escape(hreflang)}" '
        f'href="{escape(canonical_url(path, base_url), {chr(34): "&quot;"})}"/>'
        for hreflang, path in ALTERNATE_PATHS
    )
    urls = "".join(
        f"  <url><loc>{escape(canonical_url(prefix + page.path, base_url))}</loc>{links}</url>\n"
        for page in PAGES.values()
        for prefix in ("", VI_PREFIX)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="{XHTML_NAMESPACE}">\n'
        f"{urls}"
        "</urlset>\n"
    )


def robots_txt(indexing_enabled: bool | None = None, base_url: str | None = None) -> str:
    """`robots.txt`: everything disallowed unless indexing is on, and where the sitemap is."""
    enabled = settings.INDEXING_ENABLED if indexing_enabled is None else indexing_enabled
    rule = "Allow: /" if enabled else "Disallow: /"
    return f"User-agent: *\n{rule}\nSitemap: {canonical_url(SITEMAP_PATH, base_url)}\n"
