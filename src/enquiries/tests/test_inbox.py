"""The owner's enquiries inbox in the admin (issue #120, AC1 to AC9). Demo data only."""

import html
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from django.contrib.auth.models import Permission, User
from django.db import connection
from django.http import HttpResponse
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import translation
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from enquiries.inbox import (
    deleted_on,
    is_email,
    move_in_long,
    move_in_short,
    page_language,
    received,
    stay_label,
)
from enquiries.models import Enquiry
from pages.daypart import DA_NANG

pytestmark = pytest.mark.django_db

INDEX = "/owner/"
LIST_URL = "/owner/enquiries/enquiry/"
ADD_URL = "/owner/enquiries/enquiry/add/"
NOW = datetime(2026, 11, 17, 12, 0, tzinfo=DA_NANG)
EMPTY_LINE = "No enquiries yet. They appear here when someone sends the form on the site."
SHORT_NOTE = "Each enquiry is deleted 12 months after it arrived."
LONG_NOTE = (
    "Newest first. Each enquiry is deleted 12 months after it arrived. "
    "The site never sends a reply for you: answer by email, WhatsApp or Zalo, "
    "then mark it as replied."
)
MESSAGE = "Hello Bún,\nwe work remotely."


@pytest.fixture(autouse=True)
def fixed_now(mocker: MockerFixture) -> None:
    mocker.patch("django.utils.timezone.now", return_value=NOW)


@pytest.fixture
def owner_client() -> Client:
    owner = User.objects.create_superuser(username="demo-owner", password="demo-password-123")
    client = Client()
    client.force_login(owner)
    return client


def make(
    name: str,
    reply_to: str,
    created_at: datetime,
    *,
    move_in: str = "",
    stay: str = "",
    status: str = "new",
    message: str = "Hello",
    language: str = "en",
) -> Enquiry:
    enquiry = Enquiry.objects.create(
        name=name,
        reply_to=reply_to,
        move_in=move_in,
        stay=stay,
        message=message,
        language=language,
        status=status,
    )
    Enquiry.objects.filter(pk=enquiry.pk).update(created_at=created_at)
    enquiry.refresh_from_db()
    return enquiry


def demo_three() -> tuple[Enquiry, Enquiry, Enquiry]:
    anna = make(
        "Anna K.",
        "anna.k@example.com",
        datetime(2026, 11, 16, 9, 12, tzinfo=DA_NANG),
        move_in="2027-01",
        stay="6-12",
        message=MESSAGE,
    )
    minh = make(
        "Minh T.",
        "+84 905 000 111",
        datetime(2026, 11, 14, 21, 40, tzinfo=DA_NANG),
        move_in="2026-12",
        stay="3-6",
        language="vi",
    )
    lukas = make(
        "Lukas & Mai",
        "lukas.m@example.com",
        datetime(2026, 10, 28, 15, 5, tzinfo=DA_NANG),
        stay="12+",
        status="replied",
    )
    return anna, minh, lukas


def text_of(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def page_text(response: HttpResponse) -> str:
    return text_of(response.content.decode())


def rows_of(response: HttpResponse) -> list[list[str]]:
    body = response.content.decode()
    if 'id="result_list"' not in body:
        return []  # Django draws no table for zero rows (AC4)
    start = body.index("<tbody", body.index('id="result_list"'))
    table = body[start : body.index("</tbody>", start)]
    rows = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S):
        cells = [text_of(cell) for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        rows.append([cell for cell in cells if cell])
    return rows


def get(client: Client, url: str, **extra: Any) -> HttpResponse:
    response = client.get(url, **extra)
    assert isinstance(response, HttpResponse)
    return response


# M38: the index entry, the three rows, the filter, the actions and the note (AC1, AC2).


def test_m38_index_lists_enquiries_with_a_link_and_no_add_link(owner_client: Client) -> None:
    """M38"""
    response = get(owner_client, INDEX)
    body = response.content.decode()
    assert response.status_code == 200
    assert "Enquiries" in page_text(response)
    assert f'href="{LIST_URL}"' in body
    assert f'href="{ADD_URL}"' not in body


def test_m38_list_shows_three_rows_newest_first_with_their_labels(owner_client: Client) -> None:
    """M38"""
    demo_three()
    response = get(owner_client, LIST_URL)
    assert response.status_code == 200
    assert rows_of(response) == [
        [
            "16 Nov 2026, 09:12",
            "Anna K.",
            "anna.k@example.com",
            "Jan 2027",
            "6–12 months",
            "New",
        ],
        [
            "14 Nov 2026, 21:40",
            "Minh T.",
            "+84 905 000 111",
            "Dec 2026",
            "3–6 months",
            "New",
        ],
        [
            "28 Oct 2026, 15:05",
            "Lukas & Mai",
            "lukas.m@example.com",
            "Not sure yet",
            "A year or more",
            "Replied",
        ],
    ]


def test_m38_list_has_heading_filter_panel_actions_and_note(owner_client: Client) -> None:
    """M38"""
    demo_three()
    response = get(owner_client, LIST_URL)
    body = response.content.decode()
    text = page_text(response)
    assert "<h1>Enquiries</h1>" in body
    assert "Select enquiry to change" not in text
    assert "By status" in text
    assert "All" in text
    assert re.search(r"New\s*\(2\)", text)
    assert re.search(r"Replied\s*\(1\)", text)
    assert "Mark as replied" in text
    assert "Mark as new" in text
    assert LONG_NOTE in text
    assert 'class="enq-note"' in body


def test_m38_status_is_a_badge_and_the_received_cell_links_to_the_change_page(
    owner_client: Client,
) -> None:
    """M38"""
    anna, _, _ = demo_three()
    body = get(owner_client, LIST_URL).content.decode()
    assert '<span class="enq-badge enq-badge--new">New</span>' in body
    assert '<span class="enq-badge enq-badge--replied">Replied</span>' in body
    assert f"{LIST_URL}{anna.pk}/change/" in body


def test_m38_list_shows_english_dates_for_a_vietnamese_browser(owner_client: Client) -> None:
    """M38 (AC5): the date stays English with a Vietnamese browser."""
    demo_three()
    response = get(owner_client, LIST_URL, HTTP_ACCEPT_LANGUAGE="vi")
    assert "16 Nov 2026, 09:12" in page_text(response)


# M39: the action "Mark as replied" (AC3).


def test_m39_mark_as_replied_changes_two_and_the_new_filter_is_empty(
    owner_client: Client,
) -> None:
    """M39"""
    anna, minh, lukas = demo_three()
    response = owner_client.post(
        LIST_URL,
        {"action": "mark_replied", "_selected_action": [anna.pk, minh.pk]},
    )
    assert response.status_code == 302
    for enquiry in (anna, minh, lukas):
        enquiry.refresh_from_db()
    assert (anna.status, minh.status, lukas.status) == ("replied", "replied", "replied")
    filtered = get(owner_client, LIST_URL + "?status__exact=new")
    assert filtered.status_code == 200
    assert rows_of(filtered) == []


def test_m39_mark_as_new_puts_a_replied_enquiry_back(owner_client: Client) -> None:
    """M39"""
    _, _, lukas = demo_three()
    owner_client.post(LIST_URL, {"action": "mark_new", "_selected_action": [lukas.pk]})
    lukas.refresh_from_db()
    assert lukas.status == "new"


# M40: the empty list and a filter that matches nothing (AC4).


def test_m40_empty_list_shows_two_lines_and_no_actions_or_filter(owner_client: Client) -> None:
    """M40"""
    response = get(owner_client, LIST_URL)
    body = response.content.decode()
    text = page_text(response)
    assert response.status_code == 200
    assert "<h1>Enquiries</h1>" in body
    assert EMPTY_LINE in text
    assert SHORT_NOTE in text
    assert "By status" not in text
    assert "Mark as replied" not in text
    assert "Newest first." not in text
    assert 'id="result_list"' not in body


def test_m40_a_filter_matching_nothing_keeps_the_normal_list(owner_client: Client) -> None:
    """M40"""
    make("Lukas & Mai", "lukas.m@example.com", NOW - timedelta(days=3), status="replied")
    response = get(owner_client, LIST_URL + "?status__exact=new")
    text = page_text(response)
    assert response.status_code == 200
    assert "By status" in text
    assert "Mark as replied" in text
    assert LONG_NOTE in text
    assert "No enquiries yet" not in text


# M41: the change page (AC5).


def test_m41_change_page_reads_the_enquiry_whole(owner_client: Client) -> None:
    """M41"""
    anna, _, _ = demo_three()
    response = get(owner_client, f"{LIST_URL}{anna.pk}/change/")
    body = response.content.decode()
    text = page_text(response)
    assert response.status_code == 200
    assert "<title>Enquiry from Anna K." in body
    assert f"Enquiry {anna.pk}" not in text
    assert "16 Nov 2026, 09:12 (English page)" in text
    assert "Anna K." in text
    assert 'href="mailto:anna.k@example.com"' in body
    assert "January 2027" in text
    assert "6–12 months" in text
    assert "Hello Bún,<br>we work remotely." in body
    assert "Deleted on" in text
    assert "16 Nov 2027" in text
    assert '<select name="status"' in body


def test_m41_change_page_rows_come_in_the_given_order(owner_client: Client) -> None:
    """M41"""
    anna, _, _ = demo_three()
    text = page_text(get(owner_client, f"{LIST_URL}{anna.pk}/change/"))
    labels = ["Received", "Name", "Reply to", "Move in", "Stay", "Message", "Deleted on", "Status"]
    positions = [text.index(label + " ") for label in labels]
    assert positions == sorted(positions)


def test_m41_change_page_has_no_history_link_and_no_extra_save_buttons(
    owner_client: Client,
) -> None:
    """M41"""
    anna, _, _ = demo_three()
    body = get(owner_client, f"{LIST_URL}{anna.pk}/change/").content.decode()
    assert "historylink" not in body
    assert "_addanother" not in body
    assert "_continue" not in body
    assert 'name="_save"' in body
    assert "deletelink" in body


def test_m41_a_phone_number_is_plain_text_not_a_link(owner_client: Client) -> None:
    """M41"""
    _, minh, _ = demo_three()
    response = get(owner_client, f"{LIST_URL}{minh.pk}/change/")
    assert "+84 905 000 111" in page_text(response)
    assert "mailto:" not in response.content.decode()
    assert "Vietnamese page" in page_text(response)


def test_m41_saving_the_status_changes_only_the_status(owner_client: Client) -> None:
    """M41"""
    anna, _, _ = demo_three()
    response = owner_client.post(f"{LIST_URL}{anna.pk}/change/", {"status": "replied"})
    assert response.status_code == 302
    saved = Enquiry.objects.get(pk=anna.pk)
    assert saved.status == "replied"
    assert saved.name == "Anna K."
    assert saved.reply_to == "anna.k@example.com"
    assert saved.message == MESSAGE
    assert saved.created_at == anna.created_at


def test_m41_other_fields_cannot_be_edited_through_a_post(owner_client: Client) -> None:
    """M41"""
    anna, _, _ = demo_three()
    owner_client.post(
        f"{LIST_URL}{anna.pk}/change/",
        {"status": "new", "name": "Someone Else", "reply_to": "x@example.com", "message": "x"},
    )
    saved = Enquiry.objects.get(pk=anna.pk)
    assert (saved.name, saved.reply_to, saved.message) == ("Anna K.", "anna.k@example.com", MESSAGE)


def test_m41_the_add_page_is_refused(owner_client: Client) -> None:
    """M41"""
    assert owner_client.get(ADD_URL).status_code == 403


# M42: login and data-sensitive (AC6).


def test_m42_a_visitor_is_sent_to_the_admin_login() -> None:
    """M42"""
    demo_three()
    response = Client().get(LIST_URL)
    assert response.status_code == 302
    assert str(response["Location"]).startswith("/owner/login/")


def test_m42_a_visitor_is_sent_to_the_admin_login_from_the_change_page() -> None:
    """M42"""
    anna, _, _ = demo_three()
    response = Client().get(f"{LIST_URL}{anna.pk}/change/")
    assert response.status_code == 302
    assert str(response["Location"]).startswith("/owner/login/")


def test_m42_list_marks_name_and_reply_to_as_sensitive(owner_client: Client) -> None:
    """M42"""
    demo_three()
    body = get(owner_client, LIST_URL).content.decode()
    assert "<span data-sensitive>Anna K.</span>" in body
    assert "<span data-sensitive>anna.k@example.com</span>" in body
    assert "<span data-sensitive>Minh T.</span>" in body
    assert "<span data-sensitive>+84 905 000 111</span>" in body
    assert "<span data-sensitive>Lukas &amp; Mai</span>" in body


def test_m42_change_page_marks_name_reply_to_message_heading_and_breadcrumb(
    owner_client: Client,
) -> None:
    """M42"""
    anna, _, _ = demo_three()
    body = get(owner_client, f"{LIST_URL}{anna.pk}/change/").content.decode()
    assert "<h1>Enquiry from <span data-sensitive>Anna K.</span></h1>" in body
    # The heading, the last breadcrumb and the Name row.
    assert body.count("<span data-sensitive>Anna K.</span>") >= 3
    assert "anna.k@example.com</a>" in body
    assert re.search(r"data-sensitive[^>]*>\s*<a href=\"mailto:anna.k@example.com\"", body)
    assert '<div class="enq-msg" data-sensitive>' in body


# M43: expiry on opening the list (AC7).


def test_m43_an_enquiry_366_days_old_is_gone_when_the_list_opens(owner_client: Client) -> None:
    """M43"""
    old = make("Old Demo", "old@example.com", NOW - timedelta(days=366))
    fresh = make("Fresh Demo", "fresh@example.com", NOW - timedelta(days=364))
    response = get(owner_client, LIST_URL)
    assert not Enquiry.objects.filter(pk=old.pk).exists()
    assert Enquiry.objects.filter(pk=fresh.pk).exists()
    text = page_text(response)
    assert "Old Demo" not in text
    assert "Fresh Demo" in text


def test_m43_when_only_expired_enquiries_exist_the_empty_list_shows(
    owner_client: Client,
) -> None:
    """M43"""
    make("Old Demo", "old@example.com", NOW - timedelta(days=400))
    assert EMPTY_LINE in page_text(get(owner_client, LIST_URL))


# M44: the table scrolls inside its own box (AC8, the HTML check only).


def test_m44_result_list_sits_inside_the_scroll_box(owner_client: Client) -> None:
    """M44"""
    demo_three()
    body = get(owner_client, LIST_URL).content.decode()
    box = body.index('class="enq-scroll"')
    table = body.index('id="result_list"')
    assert box < table
    # The box is still open when the table starts.
    assert "</div>" not in body[box:table]


def test_m44_the_scroll_rule_is_on_the_page(owner_client: Client) -> None:
    """M44"""
    demo_three()
    body = " ".join(get(owner_client, LIST_URL).content.decode().split())
    assert ".enq-scroll { max-width: 100%; overflow-x: auto }" in body


# M45: the query count does not grow with the rows (AC9).


def test_m45_query_count_is_the_same_with_one_and_with_300_enquiries(
    owner_client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    """M45"""
    make("Anna K.", "anna.k@example.com", NOW - timedelta(days=1), move_in="2027-01", stay="6-12")
    get(owner_client, LIST_URL)  # warm up
    with CaptureQueriesContext(connection) as captured:
        get(owner_client, LIST_URL)
    baseline = len(captured)
    Enquiry.objects.bulk_create(
        Enquiry(
            name=f"Demo {number}",
            reply_to=f"demo{number}@example.com",
            move_in="2027-01",
            stay="3-6",
            message="Hello",
            language="en",
            status="replied" if number % 2 else "new",
        )
        for number in range(299)
    )
    assert Enquiry.objects.count() == 300
    with django_assert_num_queries(baseline):
        get(owner_client, LIST_URL)


# The labels of inbox.py, with no database.


def test_received_is_in_da_nang_time_with_the_day_unpadded() -> None:
    """M38"""
    assert received(datetime(2026, 11, 16, 9, 12, tzinfo=DA_NANG)) == "16 Nov 2026, 09:12"
    assert received(datetime(2026, 11, 6, 7, 5, tzinfo=DA_NANG)) == "6 Nov 2026, 07:05"


def test_received_converts_utc_to_da_nang() -> None:
    """M38"""
    utc = datetime(2026, 11, 15, 20, 30, tzinfo=UTC)
    assert received(utc) == "16 Nov 2026, 03:30"


def test_received_keeps_english_month_names_for_a_vietnamese_browser() -> None:
    """M38"""
    with translation.override("vi"):
        assert received(datetime(2026, 11, 16, 9, 12, tzinfo=DA_NANG)) == "16 Nov 2026, 09:12"


def test_move_in_labels() -> None:
    """M38"""
    assert move_in_short("2027-01") == "Jan 2027"
    assert move_in_long("2027-01") == "January 2027"
    assert move_in_short("") == "Not sure yet"
    assert move_in_long("") == "Not sure yet"


def test_stay_label_is_english_or_not_sure() -> None:
    """M38"""
    assert stay_label("1-3") == "1–3 months"
    assert stay_label("6-12") == "6–12 months"
    assert stay_label("12+") == "A year or more"
    assert stay_label("") == "Not sure yet"


def test_deleted_on_is_the_created_day_plus_365_days_in_da_nang() -> None:
    """M41"""
    assert deleted_on(datetime(2026, 11, 16, 9, 12, tzinfo=DA_NANG)) == "16 Nov 2027"
    assert deleted_on(datetime(2026, 11, 3, 9, 12, tzinfo=DA_NANG)) == "3 Nov 2027"
    # 18:00 UTC is already the next day in Đà Nẵng.
    assert deleted_on(datetime(2026, 11, 16, 18, 0, tzinfo=UTC)) == "17 Nov 2027"
    with translation.override("vi"):
        assert deleted_on(datetime(2026, 11, 16, 9, 12, tzinfo=DA_NANG)) == "16 Nov 2027"


def test_page_language_names_the_page() -> None:
    """M41"""
    assert page_language("en") == "English page"
    assert page_language("vi") == "Vietnamese page"


def test_is_email_tells_an_address_from_a_phone_number() -> None:
    """M41"""
    assert is_email("anna.k@example.com") is True
    assert is_email("+84 905 000 111") is False
    assert is_email("") is False
    assert is_email("not an@address") is False


# Review round 1: permissions, an unexpected status, escaping, the message style.


def staff_client(*codenames: str) -> Client:
    user = User.objects.create_user(username="demo-staff", password="demo-password-123")
    user.is_staff = True
    user.save()
    user.user_permissions.set(Permission.objects.filter(codename__in=codenames))
    client = Client()
    client.force_login(user)
    return client


def test_a_view_only_staff_user_cannot_run_the_actions() -> None:
    """M42: the actions need the change permission."""
    anna, _, _ = demo_three()
    client = staff_client("view_enquiry")
    client.post(LIST_URL, {"action": "mark_replied", "_selected_action": [anna.pk]})
    anna.refresh_from_db()
    assert anna.status == "new"


def test_a_staff_user_without_permission_is_refused_and_deletes_nothing() -> None:
    """M42, M43: the cleanup runs only for someone who may view the list."""
    old = make("Old Demo", "old@example.com", NOW - timedelta(days=400))
    response = staff_client().get(LIST_URL)
    assert response.status_code == 403
    assert Enquiry.objects.filter(pk=old.pk).exists()


def test_an_unexpected_status_does_not_break_the_list(owner_client: Client) -> None:
    """M38"""
    anna, _, _ = demo_three()
    Enquiry.objects.filter(pk=anna.pk).update(status="odd")
    response = get(owner_client, LIST_URL)
    assert response.status_code == 200
    assert "Anna K." in page_text(response)


def test_visitor_text_is_escaped_in_the_list_and_the_change_page(owner_client: Client) -> None:
    """M42"""
    odd = make(
        "<b>X</b>",
        "x@example.com",
        NOW - timedelta(days=1),
        message="<script>alert(1)</script>\nhi",
    )
    listed = get(owner_client, LIST_URL).content.decode()
    changed = get(owner_client, f"{LIST_URL}{odd.pk}/change/").content.decode()
    assert "<span data-sensitive>&lt;b&gt;X&lt;/b&gt;</span>" in listed
    assert "<b>X</b>" not in listed
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>hi" in changed
    assert "<script>alert(1)" not in changed


def test_the_message_keeps_its_spaces(owner_client: Client) -> None:
    """M41: white-space kept on the message."""
    anna, _, _ = demo_three()
    body = get(owner_client, f"{LIST_URL}{anna.pk}/change/").content.decode()
    assert "white-space: pre-wrap" in body
