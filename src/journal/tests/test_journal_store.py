"""The journal notes and their admin (journal spec, task T1, issue #136). Demo data only.

Rows M1 to M13 and M15 to M18 of the issue's test matrix (M14 is looked at by the owner).
"""

import html
import re
from datetime import UTC, date, datetime
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils.safestring import SafeString
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from journal.models import COVER_CHOICES, JournalPost
from journal.services import refresh_flags
from journal.text import to_html
from owner_content.models import SiteSettings
from owner_content.services import site_settings
from pages.photos import PHOTOS

INDEX = "/owner/"
LIST_URL = "/owner/journal/journalpost/"
ADD_URL = "/owner/journal/journalpost/add/"
FIRST = "ten-minutes-from-everything"
SECOND = "staying-a-month-or-longer"
VI_ERROR = "Fill the Vietnamese title, summary and text, or leave all three empty."
EMPTY_LINE = (
    "No journal posts yet. The Journal link stays hidden on the site until you publish "
    "the first one."
)
TEXT_HELP = (
    "A blank line starts a new paragraph. A line that starts with ## is a subheading. "
    "Web addresses become links by themselves."
)
FIRST_BODY = "\n\n".join(
    [
        "People often ask me what is near the house. Here is the short version.",
        "## Every day",
        "There is a supermarket right across the road, so water, fruit and the small things "
        "are a few steps away. The market is about ten minutes away.",
        "## The sea",
        "The beach is about ten minutes away.",
        "## Arriving and leaving",
        "The airport is about fifteen minutes away.",
        "If you would like to see exactly where the house is, ask me and I will send you "
        "the location.",
    ]
)
FIRST_BODY_VI = "\n\n".join(
    [
        "Nhiều bạn hỏi mình quanh nhà có gì. Đây là bản ngắn gọn.",
        "## Hằng ngày",
        "Siêu thị ở ngay bên kia đường, nước, trái cây và đồ lặt vặt chỉ cách vài bước. "
        "Chợ cách khoảng mười phút.",
        "## Biển",
        "Biển cách khoảng mười phút.",
        "## Đi và về",
        "Sân bay cách khoảng mười lăm phút.",
        "Nếu bạn muốn biết chính xác nhà ở đâu, cứ hỏi, mình gửi vị trí cho bạn.",
    ]
)
SECOND_BODY = "\n\n".join(
    [
        "The house is rented whole, by the month. The minimum stay is one month, with two "
        "months' deposit.",
        "## Included",
        "Basic furniture. Up to 300 kWh of electricity and 10 m³ of water each month; "
        "anything above is charged at the official rate. Garden care once a week. "
        "Cleaning can be arranged.",
        "## Paperwork",
        "I take care of temporary residence registration for you.",
        "## Pets",
        "Let's talk.",
    ]
)
JOURNAL_BEFORE = [("journal", "0001_initial")]
JOURNAL_AFTER = [("journal", "0002_first_drafts")]


@pytest.fixture
def owner_client() -> Client:
    owner = User.objects.create_superuser(username="demo-owner", password="demo-password-123")
    client = Client()
    client.force_login(owner)
    return client


def make(slug: str = "demo-note", **fields: Any) -> JournalPost:
    values: dict[str, Any] = {
        "title": "Demo note",
        "slug": slug,
        "summary": "A demo summary.",
        "body": "A demo text.",
        "date": date(2026, 11, 1),
    }
    values.update(fields)
    return JournalPost.objects.create(**values)


def form_data(**fields: str) -> dict[str, str]:
    data = {
        "title": "Demo post",
        "slug": "demo-post",
        "summary": "A demo summary.",
        "body": "A demo text.",
        "title_vi": "",
        "summary_vi": "",
        "body_vi": "",
        "cover": "",
        "date": "2026-11-17",
        "status": "draft",
    }
    data.update(fields)
    return data


def flags() -> tuple[bool, bool]:
    record = SiteSettings.objects.order_by("pk").first()
    assert record is not None
    return record.journal_en, record.journal_vi


def meta_of(name: str, attribute: str) -> Any:
    return getattr(JournalPost._meta.get_field(name), attribute)


def cells(row_html: str) -> str:
    texts = re.findall(r"<(?:th|td)\b[^>]*>(.*?)</(?:th|td)>", row_html, flags=re.S)
    plain = [" ".join(re.sub(r"<[^>]+>", " ", html.unescape(cell)).split()) for cell in texts]
    return " · ".join(plain[1:] if plain and plain[0] == "" else plain)


def result_rows(page: str) -> list[str]:
    body = re.search(r"<tbody>(.*?)</tbody>", page, flags=re.S)
    assert body is not None
    return [cells(row) for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", body.group(1), flags=re.S)]


def unescaped(response: Any) -> str:
    return html.unescape(response.content.decode())


# M1 (AC1)


def test_m1_the_fields_have_their_labels_lengths_and_help_texts() -> None:
    expected = {
        "title": ("Title", 120),
        "slug": ("Address", 80),
        "summary": ("Summary", 240),
        "body": ("Text", 8000),
        "title_vi": ("Title (Vietnamese)", 120),
        "summary_vi": ("Summary (Vietnamese)", 240),
        "body_vi": ("Text (Vietnamese)", 8000),
        "cover": ("Cover photo", 40),
        "status": ("status", 9),
    }
    for name, (label, length) in expected.items():
        assert meta_of(name, "verbose_name") == label, name
        assert meta_of(name, "max_length") == length, name
    assert meta_of("date", "verbose_name") == "Date"
    assert JournalPost._meta.verbose_name == "journal post"
    assert JournalPost._meta.verbose_name_plural == "journal posts"
    assert list(JournalPost._meta.ordering or []) == ["-date", "-pk"]
    assert meta_of("slug", "unique")
    for name in ("title_vi", "summary_vi", "body_vi", "cover"):
        assert meta_of(name, "blank"), name
    assert meta_of("slug", "help_text") == (
        "The page is /journal/ followed by this address. "
        "Made from the title; change it only before you publish."
    )
    assert meta_of("summary", "help_text") == "One or two sentences, shown in the list."
    assert meta_of("body", "help_text") == TEXT_HELP
    assert meta_of("body_vi", "help_text") == TEXT_HELP
    assert meta_of("title_vi", "help_text") == (
        "Leave the Vietnamese empty and the note shows only on the English pages."
    )
    assert meta_of("cover", "help_text") == (
        "One of the site's photos (they show the Illustrative label), or none. "
        "Uploading is not possible."
    )
    assert meta_of("date", "help_text") == "Shown on the note; the list is newest first."
    assert meta_of("status", "help_text") == "Only published notes are on the site."


def test_m1_the_cover_choices_are_the_site_photos_in_alphabetical_order() -> None:
    keys = [key for key, _ in COVER_CHOICES]

    assert keys == sorted(PHOTOS)
    assert len(keys) == 14
    assert keys[0] == "beach-sunset"
    assert keys[-1] == "veranda"
    assert COVER_CHOICES[0] == ("beach-sunset", "photos/beach-sunset.jpg")


@pytest.mark.django_db
def test_m1_a_new_note_is_a_draft_dated_today_in_da_nang(mocker: MockerFixture) -> None:
    mocker.patch(
        "django.utils.timezone.now", return_value=datetime(2026, 11, 16, 23, 30, tzinfo=UTC)
    )

    note = JournalPost(title="T", slug="t", summary="S", body="B")

    assert note.status == "draft"
    assert note.date == date(2026, 11, 17)
    assert note.cover == ""


@pytest.mark.django_db
def test_m1_the_note_knows_its_address_its_name_and_whether_it_has_vietnamese() -> None:
    note = make(
        "an-address", title="Hello", title_vi="Xin chào", summary_vi="Tóm tắt", body_vi="Nội dung"
    )

    assert note.get_absolute_url() == "/journal/an-address/"
    assert str(note) == "Hello"
    assert note.has_vietnamese is True
    assert make("plain").has_vietnamese is False


# M2 (AC1)


@pytest.mark.django_db
def test_m2_a_second_note_with_the_same_slug_is_refused() -> None:
    assert JournalPost.objects.filter(slug=FIRST).exists()
    duplicate = JournalPost(title="Other", slug=FIRST, summary="S", body="B", date=date(2026, 1, 1))

    with pytest.raises(ValidationError) as error:
        duplicate.full_clean()

    assert "slug" in error.value.message_dict


@pytest.mark.django_db
def test_m2_a_cover_that_is_not_a_site_photo_is_refused() -> None:
    note = JournalPost(title="T", slug="t", summary="S", body="B", cover="pool")

    with pytest.raises(ValidationError) as error:
        note.full_clean()

    assert "cover" in error.value.message_dict


@pytest.mark.django_db
def test_m2_a_title_of_121_characters_is_refused_and_120_is_kept() -> None:
    too_long = JournalPost(title="x" * 121, slug="t", summary="S", body="B")
    fits = JournalPost(title="x" * 120, slug="t2", summary="S", body="B")

    with pytest.raises(ValidationError) as error:
        too_long.full_clean()
    fits.full_clean()

    assert "title" in error.value.message_dict


# M3, M4 (AC2)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fields",
    [
        {"title_vi": "Mười phút"},
        {"summary_vi": "Tóm tắt"},
        {"body_vi": "Nội dung"},
        {"title_vi": "Mười phút", "summary_vi": "Tóm tắt"},
        {"title_vi": "Mười phút", "summary_vi": "   ", "body_vi": "\n"},
    ],
)
def test_m3_part_of_the_vietnamese_gives_the_exact_error(fields: dict[str, str]) -> None:
    note = JournalPost(title="T", slug="t", summary="S", body="B", **fields)

    with pytest.raises(ValidationError) as error:
        note.full_clean()

    assert error.value.message_dict == {"__all__": [VI_ERROR]}


@pytest.mark.django_db
def test_m3_in_the_admin_part_of_the_vietnamese_saves_nothing(owner_client: Client) -> None:
    before = JournalPost.objects.count()

    response = owner_client.post(ADD_URL, form_data(title_vi="Mười phút"))

    assert response.status_code == 200
    assert VI_ERROR in unescaped(response)
    assert JournalPost.objects.count() == before


@pytest.mark.django_db
def test_m4_all_three_vietnamese_fields_or_none_validate() -> None:
    both = JournalPost(
        title="T",
        slug="t",
        summary="S",
        body="B",
        title_vi="Mười phút",
        summary_vi="Tóm tắt",
        body_vi="Nội dung",
    )
    none = JournalPost(title="T", slug="t2", summary="S", body="B")

    both.full_clean()
    none.full_clean()

    assert both.has_vietnamese is True
    assert none.has_vietnamese is False


# M5, M6 (AC3)


def _migrate(target: list[tuple[str, str]]) -> Any:
    executor = MigrationExecutor(connection)
    executor.migrate(target)
    executor = MigrationExecutor(connection)
    return executor.loader.project_state(target).apps


def _back_to_latest() -> None:
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_m5_after_migrate_the_two_first_drafts_exist_with_their_exact_values() -> None:
    try:
        _migrate(JOURNAL_BEFORE)
        apps = _migrate(JOURNAL_AFTER)
        model = apps.get_model("journal", "JournalPost")

        notes = list(model.objects.order_by("pk"))

        assert [note.slug for note in notes] == [FIRST, SECOND]
        first, second = notes
        assert (first.slug, first.date, first.cover, first.status) == (
            FIRST,
            date(2026, 11, 16),
            "market",
            "draft",
        )
        assert first.title == "Ten minutes from everything"
        assert first.summary == (
            "A supermarket across the road, the market and the beach about ten minutes away, "
            "the airport about fifteen."
        )
        assert first.body == FIRST_BODY
        assert first.title_vi == "Mười phút là tới mọi thứ"
        assert first.summary_vi == (
            "Siêu thị ngay bên kia đường, chợ và biển khoảng mười phút, sân bay khoảng "
            "mười lăm phút."
        )
        assert first.body_vi == FIRST_BODY_VI
        assert (second.slug, second.date, second.cover, second.status) == (
            SECOND,
            date(2026, 11, 12),
            "",
            "draft",
        )
        assert second.title == "Staying a month or longer"
        assert second.summary == "What the rent includes, and what I take care of for you."
        assert second.body == SECOND_BODY
        assert (second.title_vi, second.summary_vi, second.body_vi) == ("", "", "")
    finally:
        _back_to_latest()


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_m6_a_note_with_an_existing_slug_is_skipped() -> None:
    try:
        apps = _migrate(JOURNAL_BEFORE)
        model = apps.get_model("journal", "JournalPost")
        model.objects.all().delete()
        model.objects.create(
            title="Mine",
            slug=SECOND,
            summary="Mine.",
            body="Mine.",
            date=date(2026, 1, 1),
            status="published",
        )

        apps = _migrate(JOURNAL_AFTER)
        model = apps.get_model("journal", "JournalPost")

        assert sorted(model.objects.values_list("slug", flat=True)) == sorted([FIRST, SECOND])
        assert model.objects.get(slug=SECOND).title == "Mine"
    finally:
        _back_to_latest()


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_m6_going_back_deletes_the_two_notes_only_while_they_are_drafts() -> None:
    try:
        apps = _migrate(JOURNAL_AFTER)
        model = apps.get_model("journal", "JournalPost")
        model.objects.filter(slug=FIRST).update(status="published")

        apps = _migrate(JOURNAL_BEFORE)
        model = apps.get_model("journal", "JournalPost")

        assert list(model.objects.values_list("slug", flat=True)) == [FIRST]
    finally:
        _back_to_latest()


# M7, M8, M9 (AC4)


@pytest.mark.django_db
def test_m7_publishing_in_the_admin_creates_the_settings_record_and_sets_the_flags(
    owner_client: Client,
) -> None:
    SiteSettings.objects.all().delete()
    JournalPost.objects.all().delete()

    response = owner_client.post(ADD_URL, form_data(status="published"))

    assert response.status_code == 302
    assert SiteSettings.objects.count() == 1
    assert flags() == (True, False)


@pytest.mark.django_db
def test_m7_a_published_note_with_all_three_vietnamese_fields_sets_the_vietnamese_flag(
    owner_client: Client,
) -> None:
    JournalPost.objects.all().delete()

    response = owner_client.post(
        ADD_URL,
        form_data(
            slug="vi-note",
            status="published",
            title_vi="Mười phút",
            summary_vi="Tóm tắt",
            body_vi="Nội dung",
        ),
    )

    assert response.status_code == 302
    assert flags() == (True, True)


@pytest.mark.django_db
def test_m7_refreshing_the_flags_writes_only_the_flags(mocker: MockerFixture) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(owner_first_name="Bún")
    stale = SiteSettings.objects.order_by("pk").first()
    assert stale is not None
    SiteSettings.objects.update(owner_first_name="Lan")
    JournalPost.objects.all().delete()
    JournalPost.objects.create(title="T", slug="t", summary="S", body="B", status="published")
    queryset = mocker.MagicMock()
    queryset.first.return_value = stale
    mocker.patch.object(SiteSettings.objects, "order_by", return_value=queryset)

    refresh_flags()

    record = SiteSettings.objects.get()
    assert record.owner_first_name == "Lan"
    assert (record.journal_en, record.journal_vi) == (True, False)


@pytest.mark.django_db
def test_m7_a_draft_note_sets_no_flag(owner_client: Client) -> None:
    JournalPost.objects.all().delete()

    owner_client.post(ADD_URL, form_data(status="draft"))

    assert flags() == (False, False)


def _published_with_vietnamese(owner_client: Client) -> JournalPost:
    JournalPost.objects.all().delete()
    note = make("only-one")
    owner_client.post(
        f"{LIST_URL}{note.pk}/change/",
        form_data(
            slug="only-one",
            status="published",
            title_vi="Mười phút",
            summary_vi="Tóm tắt",
            body_vi="Nội dung",
        ),
    )
    assert flags() == (True, True)
    return note


@pytest.mark.django_db
def test_m8_setting_the_last_published_note_back_to_draft_clears_both_flags(
    owner_client: Client,
) -> None:
    note = _published_with_vietnamese(owner_client)

    owner_client.post(f"{LIST_URL}{note.pk}/change/", form_data(slug="only-one", status="draft"))

    assert flags() == (False, False)


@pytest.mark.django_db
def test_m8_deleting_the_last_published_note_from_its_page_clears_both_flags(
    owner_client: Client,
) -> None:
    note = _published_with_vietnamese(owner_client)

    response = owner_client.post(f"{LIST_URL}{note.pk}/delete/", {"post": "yes"})

    assert response.status_code == 302
    assert not JournalPost.objects.exists()
    assert flags() == (False, False)


@pytest.mark.django_db
def test_m8_the_bulk_delete_of_the_last_published_notes_clears_both_flags(
    owner_client: Client,
) -> None:
    note = _published_with_vietnamese(owner_client)

    response = owner_client.post(
        LIST_URL,
        {"action": "delete_selected", "_selected_action": [str(note.pk)], "post": "yes"},
    )

    assert response.status_code == 302
    assert not JournalPost.objects.exists()
    assert flags() == (False, False)


@pytest.mark.django_db
def test_m9_site_settings_returns_the_flags_in_one_query(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(journal_en=True, journal_vi=False)

    with django_assert_num_queries(1):
        value = site_settings("en")

    assert (value.journal_en, value.journal_vi) == (True, False)
    SiteSettings.objects.all().update(journal_vi=True)
    assert site_settings("vi").journal_vi is True


@pytest.mark.django_db
def test_m9_without_a_record_both_flags_are_false(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    SiteSettings.objects.all().delete()

    with django_assert_num_queries(1):
        value = site_settings("en")

    assert (value.journal_en, value.journal_vi) == (False, False)


@pytest.mark.django_db
def test_m9_the_site_settings_form_shows_neither_flag(owner_client: Client) -> None:
    record = SiteSettings.objects.order_by("pk").first() or SiteSettings.objects.create()

    response = owner_client.get(f"/owner/owner_content/sitesettings/{record.pk}/change/")

    page = response.content.decode()
    assert response.status_code == 200
    assert "journal_en" not in page
    assert "journal_vi" not in page


# M10, M11 (AC5)


@pytest.mark.django_db
def test_m10_the_admin_index_has_the_journal_section_with_an_add_link(
    owner_client: Client,
) -> None:
    page = owner_client.get(INDEX).content.decode()

    assert ">Journal<" in page
    assert "Journal posts" in page
    assert f'href="{ADD_URL}"' in page


@pytest.mark.django_db
def test_m10_the_list_shows_the_columns_the_two_first_notes_the_filter_and_the_search(
    owner_client: Client,
) -> None:
    response = owner_client.get(LIST_URL)

    page = response.content.decode()
    assert response.status_code == 200
    assert "<h1>Journal posts</h1>" in page
    head = re.search(r"<thead>(.*?)</thead>", page, flags=re.S)
    assert head is not None
    assert cells(head.group(1)) == "Title · Date · Status · Vietnamese · Cover photo"
    assert result_rows(page) == [
        "Ten minutes from everything · Nov. 16, 2026 · Draft · Yes · photos/market.jpg",
        "Staying a month or longer · Nov. 12, 2026 · Draft · No · —",
    ]
    assert "By status" in page
    assert 'id="searchbar"' in page


@pytest.mark.django_db
def test_m10_the_search_finds_a_note_by_its_title(owner_client: Client) -> None:
    page = owner_client.get(LIST_URL, {"q": "Staying"}).content.decode()

    assert [row.split(" · ")[0] for row in result_rows(page)] == ["Staying a month or longer"]


@pytest.mark.django_db
def test_m11_a_visitor_who_is_not_signed_in_is_sent_to_the_sign_in_page(client: Client) -> None:
    for address in (LIST_URL, ADD_URL):
        response = client.get(address)

        assert response.status_code == 302
        assert response["Location"].startswith("/owner/login/")


# M12 (AC6)


@pytest.mark.django_db
def test_m12_with_no_note_the_list_shows_the_line_and_the_add_button_and_no_table(
    owner_client: Client,
) -> None:
    JournalPost.objects.all().delete()

    response = owner_client.get(LIST_URL)

    page = response.content.decode()
    assert response.status_code == 200
    assert "<h1>Journal posts</h1>" in page
    assert EMPTY_LINE in page
    assert "Add journal post" in page
    assert 'id="result_list"' not in page
    assert "By status" not in page
    assert 'id="searchbar"' not in page


# M13 (AC7)


@pytest.mark.django_db
def test_m13_the_change_form_has_three_groups_with_their_labels_and_help_texts(
    owner_client: Client,
) -> None:
    response = owner_client.get(f"{LIST_URL}1/change/")

    page = unescaped(response)
    assert response.status_code == 200
    groups = ("English (required)", "Tiếng Việt (optional)", "Publishing")
    positions = [page.index(group) for group in groups]
    assert positions == sorted(positions)
    for label in (
        "Title:",
        "Address:",
        "Summary:",
        "Text:",
        "Title (Vietnamese):",
        "Summary (Vietnamese):",
        "Text (Vietnamese):",
        "Cover photo:",
        "Date:",
        "Status:",
    ):
        assert label in page, label
    for help_text in (
        "The page is /journal/ followed by this address. "
        "Made from the title; change it only before you publish.",
        "One or two sentences, shown in the list.",
        TEXT_HELP,
        "Leave the Vietnamese empty and the note shows only on the English pages.",
        "One of the site's photos (they show the Illustrative label), or none. "
        "Uploading is not possible.",
        "Shown on the note; the list is newest first.",
        "Only published notes are on the site.",
    ):
        assert help_text in page, help_text


@pytest.mark.django_db
def test_m13_the_cover_select_starts_with_no_cover_and_lists_the_14_photos(
    owner_client: Client,
) -> None:
    page = unescaped(owner_client.get(f"{LIST_URL}1/change/"))

    select = re.search(r'<select name="cover".*?</select>', page, flags=re.S)
    assert select is not None
    options = re.findall(r'<option value="([^"]*)"([^>]*)>(.*?)</option>', select.group(0))
    assert [(value, label) for value, _, label in options] == [
        ("", "— No cover —"),
        *COVER_CHOICES,
    ]
    assert len(options) == 15
    assert [value for value, attrs, _ in options if "selected" in attrs] == ["market"]


@pytest.mark.django_db
def test_m13_view_on_site_leads_to_the_journal_address_of_the_note(owner_client: Client) -> None:
    page = owner_client.get(f"{LIST_URL}1/change/").content.decode()

    link = re.search(r'href="(/owner/r/\d+/1/)"', page)
    assert link is not None
    assert "View on site" in page
    response = owner_client.get(link.group(1))
    assert response.status_code == 302
    assert response["Location"].endswith(f"/journal/{FIRST}/")


@pytest.mark.django_db
def test_m13_on_the_add_page_the_address_is_filled_from_the_title(owner_client: Client) -> None:
    response = owner_client.get(ADD_URL)

    page = response.content.decode()
    attribute = re.search(r'data-prepopulated-fields="([^"]*)"', page)
    assert attribute is not None
    data = html.unescape(attribute.group(1))
    assert "id_slug" in data
    assert "id_title" in data


# M15, M16, M17 (AC8)


def test_m15_paragraphs_a_subheading_and_a_link() -> None:
    result = to_html("Hi\n\n## The sea\n\nSee https://example.com/a.")

    assert result == (
        "<p>Hi</p>\n<h2>The sea</h2>\n"
        '<p>See <a href="https://example.com/a" rel="noopener" target="_blank">'
        "https://example.com/a</a>.</p>"
    )
    assert isinstance(result, SafeString)


def test_m15_a_single_line_break_is_kept_as_br() -> None:
    assert to_html("one\ntwo") == "<p>one<br>two</p>"
    assert to_html("one\r\ntwo\r\n\r\nthree") == "<p>one<br>two</p>\n<p>three</p>"


def test_m15_the_lines_after_a_subheading_in_the_same_block_make_a_paragraph() -> None:
    assert to_html("## Title\nline") == "<h2>Title</h2>\n<p>line</p>"


@pytest.mark.parametrize("trailing", [".", ",", ";", ":", "!", "?", ")"])
def test_m15_a_trailing_mark_stays_outside_the_link(trailing: str) -> None:
    assert to_html(f"go http://a.com/x{trailing}") == (
        '<p>go <a href="http://a.com/x" rel="noopener" target="_blank">http://a.com/x</a>'
        f"{trailing}</p>"
    )


def test_m16_a_script_is_escaped() -> None:
    assert to_html("<script>alert(1)</script>") == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"


def test_m16_quotes_and_ampersands_are_escaped() -> None:
    assert to_html('say "hi"') == "<p>say &quot;hi&quot;</p>"
    assert to_html("Tom & Jerry's") == "<p>Tom &amp; Jerry&#x27;s</p>"


def test_m16_javascript_is_never_linked() -> None:
    assert to_html("javascript:alert(1)") == "<p>javascript:alert(1)</p>"


def test_m16_an_address_in_quotes_is_linked_without_the_quotes() -> None:
    assert to_html('see "https://x.com"') == (
        '<p>see &quot;<a href="https://x.com" rel="noopener" target="_blank">https://x.com</a>'
        "&quot;</p>"
    )


def test_m16_an_ampersand_in_an_address_is_escaped_in_the_link() -> None:
    assert to_html("https://x.com/?a=1&b=2") == (
        '<p><a href="https://x.com/?a=1&amp;b=2" rel="noopener" target="_blank">'
        "https://x.com/?a=1&amp;b=2</a></p>"
    )


@pytest.mark.parametrize("text", ["", "\n\n", "   \n \n  "])
def test_m17_empty_text_gives_an_empty_string(text: str) -> None:
    assert to_html(text) == ""


# M18 (AC9)


@pytest.mark.django_db
def test_m18_the_list_makes_the_same_number_of_queries_with_1_and_50_notes(
    owner_client: Client,
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    JournalPost.objects.all().delete()
    make("note-0")
    owner_client.get(LIST_URL)
    with CaptureQueriesContext(connection) as captured:
        owner_client.get(LIST_URL)
    expected = len(captured)

    JournalPost.objects.bulk_create(
        [
            JournalPost(
                title=f"Note {number}",
                slug=f"note-{number}",
                summary="S",
                body="B",
                date=date(2026, 11, 1),
                cover="market",
                title_vi="V",
                summary_vi="V",
                body_vi="V",
            )
            for number in range(1, 50)
        ]
    )
    assert JournalPost.objects.count() == 50

    with django_assert_num_queries(expected):
        response = owner_client.get(LIST_URL)

    assert response.status_code == 200
