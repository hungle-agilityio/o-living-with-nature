"""The journal pages at /journal/ and /vi/journal/ (journal spec, task T2, issue #137).

Rows M19, M21 to M32 of the issue's test matrix (M20 and M33 are looked at by the owner).
Demo data only, no network. The two first notes are the drafts the #136 migration stores
(pk 1 `ten-minutes-from-everything`, pk 2 `staying-a-month-or-longer`); a test that publishes
notes through the ORM calls `refresh_flags()` afterwards.
"""

import html as html_lib
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from counter.models import DailyCount
from journal.models import JournalPost
from journal.services import refresh_flags
from owner_content.models import SiteSettings
from owner_content.services import site_settings

pytestmark = pytest.mark.django_db

FIRST = "ten-minutes-from-everything"
SECOND = "staying-a-month-or-longer"
BASE_URL = "https://example.test"
CSS = Path(__file__).resolve().parents[2] / "static" / "css" / "journal.css"

LEAD_EN = (
    "I write here now and then about the house, the neighbourhood and what staying a while "
    "is like. — Bún"
)
LEAD_VI = "Thỉnh thoảng mình viết ở đây về căn nhà, khu xung quanh và chuyện ở lâu. — Bún"
FIRST_SUMMARY = (
    "A supermarket across the road, the market and the beach about ten minutes away, "
    "the airport about fifteen."
)
FIRST_SUMMARY_VI = (
    "Siêu thị ngay bên kia đường, chợ và biển khoảng mười phút, sân bay khoảng mười lăm phút."
)
NOT_FOUND_HEADING = {
    "en": "This path leads nowhere — the garden is this way.",
    "vi": "Lối này không dẫn đến đâu cả — vườn ở phía này.",
}


# helpers


@pytest.fixture(autouse=True)
def site(settings: Settings) -> None:
    settings.DEBUG = False
    settings.SITE_BASE_URL = BASE_URL
    settings.INDEXING_ENABLED = False


def set_owner(**values: Any) -> None:
    record = SiteSettings.objects.order_by("pk").first() or SiteSettings()
    for name, value in values.items():
        setattr(record, name, value)
    record.save()


def publish(*slugs: str) -> None:
    JournalPost.objects.filter(slug__in=slugs).update(status="published")
    refresh_flags()


def make_note(
    slug: str,
    day: date,
    *,
    vietnamese: bool = False,
    status: str = "published",
    title: str = "",
) -> JournalPost:
    post = JournalPost.objects.create(
        title=title or f"Note {slug}",
        slug=slug,
        summary=f"Summary of {slug}.",
        body=f"Text of {slug}.",
        title_vi=f"Ghi chép {slug}" if vietnamese else "",
        summary_vi=f"Tóm tắt {slug}." if vietnamese else "",
        body_vi=f"Nội dung {slug}." if vietnamese else "",
        date=day,
        status=status,
    )
    refresh_flags()
    return post


def fetch(client: Client, url: str, status: int = 200) -> str:
    response = client.get(url)
    assert response.status_code == status
    return response.content.decode()


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def part(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    assert match, f"{pattern!r} not found"
    return match.group(1)


def links(fragment: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for attrs, inner in re.findall(r"<a\b([^>]*)>(.*?)</a>", fragment, re.DOTALL):
        href = re.search(r'href="([^"]*)"', attrs)
        assert href
        found.append((html_lib.unescape(href.group(1)), text_of(inner)))
    return found


def cards(html: str) -> list[tuple[str, str]]:
    """The (class, inner html) of each `<li class="note-card...">` of the list."""
    ol = part(html, r'<ol class="journal__list">(.*?)</ol>')
    return re.findall(r'<li class="(note-card[^"]*)">(.*?)</li>', ol, re.DOTALL)


def head_meta(html: str, attr: str, name: str) -> str:
    match = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', html)
    assert match, f"meta {name} not found"
    return html_lib.unescape(match.group(1))


def canonical(html: str) -> str:
    return part(html, r'<link rel="canonical" href="([^"]*)"')


def alternates(html: str) -> list[tuple[str, str]]:
    return re.findall(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)"', html)


def switch_href(html: str) -> str:
    return part(html, r'<p class="lang-switch[^"]*"[^>]*>.*?<a href="([^"]*)"')


def assert_not_found(client: Client, url: str, lang: str) -> None:
    response = client.get(url)
    assert response.status_code == 404
    assert "404.html" in [template.name for template in response.templates]
    body = response.content.decode()
    assert f'<html lang="{lang}">' in body
    assert NOT_FOUND_HEADING[lang] in body


def configure_owner() -> None:
    set_owner(
        price_from_million=13,
        price_to_million=14,
        phone="0945 384 500",
        whatsapp="0945 384 500",
        zalo="0945 384 500",
        owner_first_name="Bún",
        reply_time="within an hour",
    )


# M19 (AC1)


def test_m19_list_shows_texts_order_dates_links_and_cover_with_label_and_credit(
    client: Client,
) -> None:
    """M19, AC1: the English list with the two first notes published."""
    set_owner(owner_first_name="Bún")
    publish(FIRST, SECOND)

    body = fetch(client, "/journal/")

    head = part(body, r'<header class="journal__head">(.*?)</header>')
    paragraphs = [
        (cls, text_of(inner)) for cls, inner in re.findall(r'<p class="([^"]*)">(.*?)</p>', head)
    ]
    assert paragraphs == [("label muted", "Journal"), ("journal__lead", LEAD_EN)]
    assert text_of(part(head, r'<h1 class="journal__title">(.*?)</h1>')) == "Notes from Hòa Xuân"

    items = cards(body)
    assert len(items) == 2
    (first_class, first), (second_class, second) = items
    assert first_class == "note-card"
    assert second_class == "note-card note-card--plain"

    assert '<time datetime="2026-11-16">16 November 2026</time>' in first
    assert f'<h2><a href="/journal/{FIRST}/">Ten minutes from everything</a></h2>' in first
    assert FIRST_SUMMARY in text_of(first)
    assert f'<a class="more" href="/journal/{FIRST}/">Read →</a>' in first
    cover = part(first, r'<div class="note-card__cover">(.*?)</div>\s*<div')
    assert "market" in cover
    assert "Illustrative photo" in cover
    assert "Photo: Pexels" in cover

    assert '<time datetime="2026-11-12">12 November 2026</time>' in second
    assert f'<h2><a href="/journal/{SECOND}/">Staying a month or longer</a></h2>' in second
    assert "What the rent includes, and what I take care of for you." in second
    assert f'<a class="more" href="/journal/{SECOND}/">Read →</a>' in second
    assert "note-card__cover" not in second
    assert "<figure" not in second

    assert body.index(FIRST) < body.index(SECOND)
    assert "journal__pages" not in body  # two notes: one page


# M21 (AC2)


def test_m21_thirteen_notes_make_two_pages_and_bad_pages_answer_404(client: Client) -> None:
    """M21, AC2: 12 on page 1 with Older, 1 on page 2 with Newer; pages 3, 0, x are 404."""
    for n in range(1, 14):
        make_note(f"note-{n:02d}", date(2026, 10, 1) + timedelta(days=n))

    page_one = fetch(client, "/journal/")
    assert len(cards(page_one)) == 12
    assert "/journal/note-13/" in cards(page_one)[0][1]
    assert "/journal/note-02/" in cards(page_one)[-1][1]
    nav_one = part(page_one, r'<nav class="journal__pages">(.*?)</nav>')
    older = [(href, text) for href, text in links(nav_one) if text == "Older notes →"]
    assert len(older) == 1
    assert older[0][0].endswith("?page=2")
    assert "Newer notes" not in nav_one

    page_two = fetch(client, "/journal/?page=2")
    assert len(cards(page_two)) == 1
    assert "/journal/note-01/" in cards(page_two)[0][1]
    nav_two = part(page_two, r'<nav class="journal__pages">(.*?)</nav>')
    assert ("/journal/", "← Newer notes") in links(nav_two)
    assert "Older notes" not in nav_two

    for bad in ("3", "0", "x", "-1"):
        assert_not_found(client, f"/journal/?page={bad}", "en")


def test_m21_two_notes_with_the_same_date_show_the_higher_pk_first(client: Client) -> None:
    """M21, AC2: same date, the note created last (higher pk) comes first."""
    make_note("older-pk", date(2026, 11, 5))
    make_note("newer-pk", date(2026, 11, 5))

    items = cards(fetch(client, "/journal/"))

    assert ["/journal/newer-pk/" in inner for _, inner in items] == [True, False]
    assert "/journal/older-pk/" in items[1][1]


# M22 (AC3)


def test_m22_vietnamese_list_shows_only_the_note_with_vietnamese(client: Client) -> None:
    """M22, AC3: /vi/journal/ lists only the note with all three Vietnamese fields."""
    set_owner(owner_first_name="Bún")
    publish(FIRST, SECOND)

    body = fetch(client, "/vi/journal/")

    assert '<html lang="vi">' in body
    head = part(body, r'<header class="journal__head">(.*?)</header>')
    paragraphs = [
        (cls, text_of(inner)) for cls, inner in re.findall(r'<p class="([^"]*)">(.*?)</p>', head)
    ]
    assert paragraphs == [("label muted", "Nhật ký"), ("journal__lead", LEAD_VI)]
    assert text_of(part(head, r'<h1 class="journal__title">(.*?)</h1>')) == "Ghi chép từ Hòa Xuân"
    items = cards(body)
    assert len(items) == 1
    inner = items[0][1]
    assert f'<a href="/vi/journal/{FIRST}/">Mười phút là tới mọi thứ</a>' in inner
    assert '<time datetime="2026-11-16">16/11/2026</time>' in inner
    assert FIRST_SUMMARY_VI in text_of(inner)
    assert f'<a class="more" href="/vi/journal/{FIRST}/">Đọc →</a>' in inner
    assert "Ảnh minh hoạ" in inner
    assert "Ảnh: Pexels" in inner
    assert "Staying a month" not in body
    assert SECOND not in body


# M23 (AC4)


def test_m23_only_drafts_answer_404_with_the_page_not_found_page(client: Client) -> None:
    """M23, AC4: the state right after #136 (two drafts) has no journal list."""
    assert_not_found(client, "/journal/", "en")
    assert_not_found(client, "/vi/journal/", "vi")


def test_m23_published_notes_without_vietnamese_make_the_vietnamese_list_404(
    client: Client,
) -> None:
    """M23, AC4: a note with only some Vietnamese fields does not count."""
    JournalPost.objects.filter(slug=FIRST).update(summary_vi="")
    publish(FIRST, SECOND)

    assert fetch(client, "/journal/")
    assert_not_found(client, "/vi/journal/", "vi")


# M24 (AC5)


def test_m24_note_page_has_its_parts_contact_block_and_another_note(client: Client) -> None:
    """M24, AC5: the English note page of the first note."""
    configure_owner()
    publish(FIRST, SECOND)

    body = fetch(client, f"/journal/{FIRST}/")

    article = part(body, r'<article class="note">(.*?)</article>')
    assert ("/journal/", "← All notes") in links(article)
    assert 'class="note__back"' in article
    assert '<time datetime="2026-11-16">16 November 2026</time>' in article
    assert text_of(part(article, r'<h1 class="note__title">(.*?)</h1>')) == (
        "Ten minutes from everything"
    )
    cover = part(article, r'<div class="note__cover">(.*?)</figure>')
    assert "market" in cover
    assert "Illustrative photo" in cover
    assert "Photo: Pexels" in cover
    text = part(article, r'<div class="note__body">(.*?)</div>\s*<aside')
    assert "<p>" in text
    for heading in ("Every day", "The sea", "Arriving and leaving"):
        assert f"<h2>{heading}</h2>" in text

    aside = part(article, r'<aside class="note-contact">(.*?)</aside>')
    assert text_of(part(aside, r'<p class="note-contact__line">(.*?)</p>')) == (
        "Like the sound of it?"
    )
    assert text_of(part(aside, r'<p class="note-contact__price">(.*?)</p>')) == (
        "From 13–14 million VND a month. I usually reply within an hour."
    )
    buttons = re.findall(r"<a\b[^>]*data-channel[^>]*>(.*?)</a>", aside, re.DOTALL)
    assert [text_of(label) for label in buttons] == ["Call", "WhatsApp", "Zalo"]
    assert aside.count('data-place="journal"') == 3
    assert ("/#enquiry", "Or leave me a message →") in links(
        part(aside, r'<p class="note-contact__form">(.*?)</p>')
    )

    more = part(article, r'<p class="note__more[^"]*">(.*?)</p>')
    assert text_of(more) == "Another note: Staying a month or longer"
    assert links(more) == [(f"/journal/{SECOND}/", "Staying a month or longer")]


# M25 (AC6)


def test_m25_vietnamese_note_page_and_a_note_without_cover_has_no_figure(
    client: Client,
) -> None:
    """M25, AC6: the Vietnamese note page; the second note has no `<figure>`."""
    configure_owner()
    publish(FIRST, SECOND)

    body = fetch(client, f"/vi/journal/{FIRST}/")

    assert '<html lang="vi">' in body
    article = part(body, r'<article class="note">(.*?)</article>')
    assert ("/vi/journal/", "← Tất cả ghi chép") in links(article)
    assert '<time datetime="2026-11-16">16/11/2026</time>' in article
    assert text_of(part(article, r'<h1 class="note__title">(.*?)</h1>')) == (
        "Mười phút là tới mọi thứ"
    )
    for heading in ("Hằng ngày", "Biển", "Đi và về"):
        assert f"<h2>{heading}</h2>" in article
    aside = part(article, r'<aside class="note-contact">(.*?)</aside>')
    assert text_of(part(aside, r'<p class="note-contact__line">(.*?)</p>')) == "Bạn thấy hợp chứ?"
    expected_price = "Từ 13–14 triệu đồng mỗi tháng. " + site_settings("vi").reply_line
    assert text_of(part(aside, r'<p class="note-contact__price">(.*?)</p>')) == expected_price
    buttons = re.findall(r"<a\b[^>]*data-channel[^>]*>(.*?)</a>", aside, re.DOTALL)
    assert [text_of(label) for label in buttons] == ["Gọi điện", "WhatsApp", "Zalo"]
    assert ("/vi/#enquiry", "Hoặc để lại lời nhắn cho mình →") in links(aside)
    assert "Ghi chép khác" not in body  # only one note has Vietnamese

    plain = fetch(client, f"/journal/{SECOND}/")
    assert "<figure" not in part(plain, r'<article class="note">(.*?)</article>')


# M26 (AC7)


def test_m26_no_price_no_channel_and_one_note(client: Client) -> None:
    """M26, AC7: the contact block without a price, without channels, with one note."""
    set_owner(
        price_from_million=None,
        price_to_million=None,
        phone="",
        whatsapp="",
        zalo="",
        reply_time="within an hour",
    )
    publish(FIRST)

    body = fetch(client, f"/journal/{FIRST}/")

    aside = part(body, r'<aside class="note-contact">(.*?)</aside>')
    assert text_of(part(aside, r'<p class="note-contact__price">(.*?)</p>')) == (
        "I usually reply within an hour."
    )
    assert "data-channel" not in aside
    assert "contact-buttons" not in aside
    assert ("/#enquiry", "Or leave me a message →") in links(aside)
    assert "Another note" not in body  # one published note only


# M27 (AC7)


def test_m27_another_note_is_the_next_older_and_the_newest_for_the_oldest(
    client: Client,
) -> None:
    """M27, AC7: notes dated 16, 12 and 10 November point 16 -> 12 -> 10 -> 16."""
    make_note("third-note", date(2026, 11, 10), title="Third note")
    publish(FIRST, SECOND)

    def another(slug: str) -> list[tuple[str, str]]:
        body = fetch(client, f"/journal/{slug}/")
        return links(part(body, r'<p class="note__more[^"]*">(.*?)</p>'))

    assert another(FIRST) == [(f"/journal/{SECOND}/", "Staying a month or longer")]
    assert another(SECOND) == [("/journal/third-note/", "Third note")]
    assert another("third-note") == [(f"/journal/{FIRST}/", "Ten minutes from everything")]


# M28 (AC8)


def test_m28_draft_unknown_and_no_vietnamese_answer_404_in_their_language(
    client: Client,
) -> None:
    """M28, AC8: a draft, an unknown address and a note without Vietnamese in /vi/."""
    publish(SECOND)  # the first note stays a draft

    # The published note itself is there, so a 404 below is the journal's own answer.
    assert fetch(client, f"/journal/{SECOND}/")
    assert_not_found(client, f"/journal/{FIRST}/", "en")
    assert_not_found(client, "/journal/no-such-note/", "en")
    assert_not_found(client, "/vi/journal/no-such-note/", "vi")
    assert_not_found(client, f"/vi/journal/{SECOND}/", "vi")
    assert_not_found(client, f"/vi/journal/{FIRST}/", "vi")


# M29 (AC9)


def test_m29_titles_descriptions_canonical_robots_and_og_type(
    client: Client, settings: Settings
) -> None:
    """M29, AC9: the head of the lists and of a note."""
    set_owner(owner_first_name="Bún")
    publish(FIRST, SECOND)

    english = fetch(client, "/journal/")
    assert part(english, r"<title>(.*?)</title>") == "Journal · Ở"
    assert head_meta(english, "name", "description") == LEAD_EN
    assert canonical(english) == f"{BASE_URL}/journal/"
    assert head_meta(english, "name", "robots") == "noindex, nofollow"
    assert head_meta(english, "property", "og:type") == "website"

    vietnamese = fetch(client, "/vi/journal/")
    assert part(vietnamese, r"<title>(.*?)</title>") == "Nhật ký · Ở"
    assert head_meta(vietnamese, "name", "description") == LEAD_VI
    assert canonical(vietnamese) == f"{BASE_URL}/vi/journal/"
    assert head_meta(vietnamese, "property", "og:type") == "website"

    note = fetch(client, f"/journal/{FIRST}/")
    assert part(note, r"<title>(.*?)</title>") == "Ten minutes from everything · Ở"
    assert head_meta(note, "name", "description") == FIRST_SUMMARY
    assert canonical(note) == f"{BASE_URL}/journal/{FIRST}/"
    assert head_meta(note, "property", "og:type") == "article"

    vi_note = fetch(client, f"/vi/journal/{FIRST}/")
    assert part(vi_note, r"<title>(.*?)</title>") == "Mười phút là tới mọi thứ · Ở"
    assert head_meta(vi_note, "name", "description") == FIRST_SUMMARY_VI
    assert canonical(vi_note) == f"{BASE_URL}/vi/journal/{FIRST}/"
    assert head_meta(vi_note, "property", "og:type") == "article"

    settings.INDEXING_ENABLED = True
    assert head_meta(fetch(client, "/journal/"), "name", "robots") == "index, follow"


def test_m29_hreflang_alternates_only_where_both_languages_exist(client: Client) -> None:
    """M29, AC9: the first note and the lists have alternates; the second note has none."""
    publish(FIRST, SECOND)
    expected = [
        ("en", f"{BASE_URL}/journal/{FIRST}/"),
        ("vi", f"{BASE_URL}/vi/journal/{FIRST}/"),
        ("x-default", f"{BASE_URL}/journal/{FIRST}/"),
    ]

    assert alternates(fetch(client, f"/journal/{FIRST}/")) == expected
    assert alternates(fetch(client, f"/vi/journal/{FIRST}/")) == expected
    assert alternates(fetch(client, f"/journal/{SECOND}/")) == []
    assert alternates(fetch(client, "/journal/")) == [
        ("en", f"{BASE_URL}/journal/"),
        ("vi", f"{BASE_URL}/vi/journal/"),
        ("x-default", f"{BASE_URL}/journal/"),
    ]


def test_m29_language_switch_goes_to_the_same_page_or_the_nearest_one(client: Client) -> None:
    """M29, AC9: same page when it exists, else the other list, else the other home page."""
    publish(FIRST, SECOND)

    assert switch_href(fetch(client, f"/journal/{FIRST}/")) == f"/vi/journal/{FIRST}/"
    assert switch_href(fetch(client, f"/vi/journal/{FIRST}/")) == f"/journal/{FIRST}/"
    assert switch_href(fetch(client, f"/journal/{SECOND}/")) == "/vi/journal/"
    assert switch_href(fetch(client, "/journal/")) == "/vi/journal/"
    assert switch_href(fetch(client, "/vi/journal/")) == "/journal/"


def test_m29_language_switch_goes_to_the_vietnamese_home_without_a_vietnamese_note(
    client: Client,
) -> None:
    """M29, AC9: no note has Vietnamese, so /journal/ switches to /vi/."""
    publish(SECOND)

    body = fetch(client, "/journal/")

    assert switch_href(body) == "/vi/"
    assert alternates(body) == []


# M30 (AC10)


def test_m30_place_journal_is_counted_shown_in_the_report_and_count_js_is_loaded(
    client: Client,
) -> None:
    """M30, AC10: POST /count/ with place=journal, the report row, count.js on every page."""
    response = client.post("/count/", {"kind": "click", "channel": "zalo", "place": "journal"})
    assert response.status_code == 204
    assert DailyCount.objects.get(kind="click", channel="zalo", place="journal").count == 1

    owner = User.objects.create_superuser(username="demo-owner", password="demo-password-123")
    admin = Client()
    admin.force_login(owner)
    assert "Journal notes" in fetch(admin, "/owner/counter/dailycount/")

    publish(FIRST, SECOND)
    for url in ("/journal/", "/vi/journal/", f"/journal/{FIRST}/", f"/vi/journal/{FIRST}/"):
        body = fetch(client, url)
        assert re.search(r'<script src="[^"]*js/count\.js[^"]*" defer></script>', body), url


# M31 (AC11)


@pytest.mark.parametrize("extra_notes", [0, 28])
def test_m31_journal_pages_stay_within_three_queries(
    client: Client,
    django_assert_max_num_queries: DjangoAssertNumQueries,
    extra_notes: int,
) -> None:
    """M31, AC11: lists and note page make at most 3 queries with 1 (here 2) and 30 notes."""
    publish(FIRST, SECOND)
    for n in range(extra_notes):
        make_note(f"extra-{n:02d}", date(2026, 9, 1) + timedelta(days=n), vietnamese=True)

    for url in ("/journal/", "/vi/journal/", f"/journal/{FIRST}/", f"/vi/journal/{FIRST}/"):
        with django_assert_max_num_queries(3):
            assert client.get(url).status_code == 200


def test_m31_home_keeps_one_query_and_sitemap_and_robots_none(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    """M31, AC11: `/` and `/vi/` 1 query; sitemap and robots 0; sitemap lists only / and /vi/."""
    publish(FIRST, SECOND)

    for url in ("/", "/vi/"):
        with django_assert_num_queries(1):
            assert client.get(url).status_code == 200
    with django_assert_num_queries(0):
        sitemap = client.get("/sitemap.xml").content.decode()
        assert client.get("/robots.txt").status_code == 200

    assert re.findall(r"<loc>(.*?)</loc>", sitemap) == [f"{BASE_URL}/", f"{BASE_URL}/vi/"]


# M32 (AC12)


def test_m32_no_cookie_and_no_script_but_the_sites_own_static_files(
    client: Client, settings: Settings
) -> None:
    """M32, AC12: no Set-Cookie, and every script is a static file of the site."""
    publish(FIRST, SECOND)

    for url in ("/journal/", "/vi/journal/", f"/journal/{FIRST}/", f"/vi/journal/{FIRST}/"):
        response = client.get(url)
        assert response.status_code == 200, url
        assert not response.cookies, url
        body = response.content.decode()
        tags = re.findall(r"<script\b[^>]*>", body)
        assert tags, url
        for tag in tags:
            src = re.search(r'src="([^"]*)"', tag)
            assert src, f"inline script on {url}"
            assert src.group(1).startswith(settings.STATIC_URL), src.group(1)
        assert "onclick" not in body


def test_m32_journal_css_keeps_the_line_heights_that_clear_vietnamese_marks() -> None:
    """M32, AC12: `.journal__title` >= .9, `.note__title` >= 1.05, none below .9."""
    assert CSS.exists()
    source = CSS.read_text()

    values = [float(v) for v in re.findall(r"line-height\s*:\s*(\d*\.?\d+)\s*[;}]", source)]
    assert values, "no unitless line-height in journal.css"
    assert min(values) >= 0.9

    def declared(selector: str) -> list[float]:
        found: list[float] = []
        for names, block in re.findall(r"([^{}]+)\{([^{}]*)\}", source):
            if selector in [name.strip() for name in names.split(",")]:
                found += [
                    float(v) for v in re.findall(r"line-height\s*:\s*(\d*\.?\d+)\s*;?", block)
                ]
        return found

    assert declared(".journal__title") and min(declared(".journal__title")) >= 0.9
    assert declared(".note__title") and min(declared(".note__title")) >= 1.05
