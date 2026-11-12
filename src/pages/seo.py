"""What search engines read: each page's title, description and canonical address, the robots
value, `sitemap.xml` and `robots.txt`."""

from dataclasses import dataclass
from xml.sax.saxutils import escape

from django.conf import settings

SITE_NAME = "Ở — Living with Nature"
OG_TYPE = "website"

ROBOTS_INDEX = "index, follow"
ROBOTS_NOINDEX = "noindex, nofollow"

SITEMAP_PATH = "/sitemap.xml"


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


# The five pages of phase 1, in the order of the sitemap. The texts change through issues.
PAGES: dict[str, Page] = {
    "home": Page(
        path="/",
        title="Ở — Living with Nature · Garden house for rent in Hòa Xuân, Đà Nẵng",
        description=(
            "A whole garden house with two bedrooms, rented by the month in Hòa Xuân, Đà Nẵng. "
            "From 13–14 million VND a month, minimum stay one month."
        ),
    ),
    "house": Page(
        path="/house/",
        title="The house · Ở, a garden house for rent in Đà Nẵng",
        description=(
            "Two bedrooms, a mezzanine, a light well, front and back gardens and a covered "
            "veranda. Rented whole, by the month."
        ),
    ),
    "hoa_xuan": Page(
        path="/hoa-xuan/",
        title="Hòa Xuân, Đà Nẵng · Living at Ở",
        description=(
            "A supermarket across the road, the market and the beach about 10 minutes away, "
            "the airport about 15 minutes."
        ),
    ),
    "faq": Page(
        path="/faq/",
        title="FAQ · Renting Ở in Hòa Xuân, Đà Nẵng",
        description=(
            "Minimum stay, deposit, electricity and water, pets, and residence registration "
            "for foreigners."
        ),
    ),
    "contact": Page(
        path="/contact/",
        title="Contact Bún · Ở garden house, Đà Nẵng",
        description="Call, WhatsApp or Zalo. I usually reply within an hour.",
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


def head_for(name: str) -> Head:
    """The search tags of the page with this name; an unknown name is a KeyError."""
    page = PAGES[name]
    return Head(
        title=page.title,
        description=page.description,
        canonical=canonical_url(page.path),
        robots=robots_value(),
    )


def sitemap_xml(base_url: str | None = None) -> str:
    """`sitemap.xml`: the canonical addresses of the five pages and nothing else."""
    urls = "".join(
        f"  <url><loc>{escape(canonical_url(page.path, base_url))}</loc></url>\n"
        for page in PAGES.values()
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}"
        "</urlset>\n"
    )


def robots_txt(indexing_enabled: bool | None = None, base_url: str | None = None) -> str:
    """`robots.txt`: everything disallowed unless indexing is on, and where the sitemap is."""
    enabled = settings.INDEXING_ENABLED if indexing_enabled is None else indexing_enabled
    rule = "Allow: /" if enabled else "Disallow: /"
    return f"User-agent: *\n{rule}\nSitemap: {canonical_url(SITEMAP_PATH, base_url)}\n"
