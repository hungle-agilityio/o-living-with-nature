"""The Journal link in the menus and the footer (journal spec, task T3, issue #138).

Rows M34 to M36 of the issue's test matrix (M37 is looked at by the owner).
Demo data only, no network. The desktop row and the phone "Menu" both use
`includes/nav_links.html`, so each test counts both.
"""

import html as html_lib
import re
from datetime import date

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from journal.models import JournalPost
from journal.services import refresh_flags

pytestmark = pytest.mark.django_db

FIRST = "ten-minutes-from-everything"
NOT_FOUND = "/this-page-does-not-exist/"

MENU_EN = ["The house", "Hòa Xuân", "Rent", "FAQ", "Journal", "Contact"]
MENU_VI = ["Căn nhà", "Hòa Xuân", "Giá thuê", "Hỏi đáp", "Nhật ký", "Liên hệ"]


@pytest.fixture(autouse=True)
def site(settings: Settings) -> None:
    settings.DEBUG = False
    settings.SITE_BASE_URL = "https://example.test"
    settings.INDEXING_ENABLED = False


def note(slug: str, *, vietnamese: bool = False, status: str = "published") -> None:
    JournalPost.objects.create(
        title=f"Demo note {slug}",
        slug=f"demo-{slug}",
        summary="Demo summary.",
        body="Demo text.",
        title_vi="Ghi chép mẫu" if vietnamese else "",
        summary_vi="Tóm tắt mẫu." if vietnamese else "",
        body_vi="Nội dung mẫu." if vietnamese else "",
        date=date(2026, 11, 1),
        status=status,
    )
    refresh_flags()


def publish_first_notes() -> None:
    """Publish the first stored note (it has all three Vietnamese fields)."""
    JournalPost.objects.filter(slug=FIRST).update(status="published")
    refresh_flags()


def fetch(client: Client, url: str, status: int = 200) -> str:
    response = client.get(url)
    assert response.status_code == status
    return response.content.decode()


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def href_of(attrs: str) -> str:
    found = re.search(r'href="([^"]*)"', attrs)
    assert found
    return html_lib.unescape(found.group(1))


def menus(body: str) -> list[list[tuple[str, str, str]]]:
    """For each `ul.nav-links` (desktop row, phone Menu): (label, href, attrs) of its links."""
    result = []
    for ul in re.findall(r'<ul class="nav-links">(.*?)</ul>', body, re.DOTALL):
        result.append(
            [
                (text_of(inner), href_of(attrs), attrs)
                for attrs, inner in re.findall(r"<a\b([^>]*)>(.*?)</a>", ul, re.DOTALL)
            ]
        )
    return result


def footer_first_link(body: str) -> tuple[str, str] | None:
    """The (label, href) of the footer's first child if it is a link paragraph, else None."""
    inner = re.search(
        r'<div class="site-footer__inner">\s*(.*?)</div>\s*</footer>', body, re.DOTALL
    )
    assert inner
    first = re.match(r"<p class=\"([^\"]*)\">(.*?)</p>", inner.group(1).strip(), re.DOTALL)
    assert first
    link = re.search(r'<a href="([^"]*)"[^>]*>(.*?)</a>', first.group(2), re.DOTALL)
    if "site-footer__journal" not in first.group(1) or not link:
        return None
    return text_of(link.group(2)), link.group(1)


def has_journal_text(body: str) -> bool:
    return "Journal" in " ".join(
        label for menu in menus(body) for label, _, _ in menu
    ) or "Nhật ký" in " ".join(label for menu in menus(body) for label, _, _ in menu)


def journal_links(body: str) -> list[str]:
    return re.findall(r'<a href="(/(?:vi/)?journal/)"', body)


# M34 (AC1)


def test_m34_published_note_with_vietnamese_puts_the_link_in_both_menus_and_the_footer(
    client: Client,
) -> None:
    publish_first_notes()

    english = fetch(client, "/")
    en_menus = menus(english)
    assert len(en_menus) == 2
    for menu in en_menus:
        assert [label for label, _, _ in menu] == MENU_EN
        assert dict((label, href) for label, href, _ in menu)["Journal"] == "/journal/"
    assert footer_first_link(english) == ("Journal", "/journal/")

    vietnamese = fetch(client, "/vi/")
    vi_menus = menus(vietnamese)
    assert len(vi_menus) == 2
    for menu in vi_menus:
        assert [label for label, _, _ in menu] == MENU_VI
        assert dict((label, href) for label, href, _ in menu)["Nhật ký"] == "/vi/journal/"
    assert footer_first_link(vietnamese) == ("Nhật ký", "/vi/journal/")


# M35 (AC2)


def test_m35_only_drafts_show_no_link_on_either_page(client: Client) -> None:
    note("draft", vietnamese=True, status="draft")

    for url in ("/", "/vi/"):
        body = fetch(client, url)
        assert not has_journal_text(body)
        assert footer_first_link(body) is None
        assert "journal/" not in " ".join(href for m in menus(body) for _, href, _ in m)
        assert "/journal/" not in " ".join(journal_links(body))


def test_m35_english_only_note_shows_the_link_on_en_and_none_on_vi(client: Client) -> None:
    note("english-only", vietnamese=False)

    english = fetch(client, "/")
    assert all([label for label, _, _ in menu] == MENU_EN for menu in menus(english)), (
        "English menu lists Journal"
    )
    assert footer_first_link(english) == ("Journal", "/journal/")

    vietnamese = fetch(client, "/vi/")
    for menu in menus(vietnamese):
        assert "Nhật ký" not in [label for label, _, _ in menu]
    assert footer_first_link(vietnamese) is None


# M36 (AC3, AC4)


@pytest.mark.parametrize(
    ("url", "label", "href", "menu_labels"),
    [
        ("/journal/", "Journal", "/journal/", MENU_EN),
        (f"/journal/{FIRST}/", "Journal", "/journal/", MENU_EN),
        ("/vi/journal/", "Nhật ký", "/vi/journal/", MENU_VI),
        (f"/vi/journal/{FIRST}/", "Nhật ký", "/vi/journal/", MENU_VI),
    ],
)
def test_m36_journal_pages_mark_the_menu_link_current_in_both_menus(
    client: Client, url: str, label: str, href: str, menu_labels: list[str]
) -> None:
    publish_first_notes()

    body = fetch(client, url)

    found = menus(body)
    assert len(found) == 2
    for menu in found:
        assert [name for name, _, _ in menu] == menu_labels
        for name, link, attrs in menu:
            if name == label:
                assert link == href
                assert 'aria-current="page"' in attrs
            else:
                assert "aria-current" not in attrs
    assert footer_first_link(body) == (label, href)


def test_m36_home_menu_link_is_not_marked_current(client: Client) -> None:
    publish_first_notes()

    for menu in menus(fetch(client, "/")):
        assert all("aria-current" not in attrs for _, _, attrs in menu)


def test_m36_page_not_found_has_no_journal_link_and_asks_the_database_nothing(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    publish_first_notes()

    with django_assert_num_queries(0):
        response = client.get(NOT_FOUND)

    assert response.status_code == 404
    body = response.content.decode()
    assert not has_journal_text(body)
    assert footer_first_link(body) is None
    assert 'href="/journal/"' not in body


@pytest.mark.parametrize("url", ["/", "/vi/"])
@pytest.mark.parametrize("published", [False, True])
def test_m36_home_pages_still_make_exactly_one_query(
    client: Client,
    django_assert_num_queries: DjangoAssertNumQueries,
    url: str,
    published: bool,
) -> None:
    if published:
        publish_first_notes()

    with django_assert_num_queries(1):
        response = client.get(url)

    assert response.status_code == 200
