"""Messages sent through the enquiry form in the contact counts (issue #119, AC1 to AC6).

Demo data only. Posts go through /enquiry/ with the clock fixed on 16 Nov 2026 in Đà Nẵng.
"""

import re
from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from counter.models import DailyCount
from counter.report import build_report
from enquiries.models import Enquiry

pytestmark = pytest.mark.django_db

REPORT = "/owner/counter/dailycount/"
ENQUIRY = "/enquiry/"
COUNT = "/count/"
TODAY = date(2026, 11, 16)
# 12:00 on 16 Nov 2026 in Đà Nẵng (UTC+7).
NOON = datetime(2026, 11, 16, 5, 0, tzinfo=UTC)
# 00:00 on 16 Nov 2026 in Đà Nẵng.
MIDNIGHT = datetime(2026, 11, 15, 17, 0, tzinfo=UTC)
EMPTY_LINE = "Nothing counted yet. Counts start when someone opens the site."
PRIVACY_LINE = (
    "Daily totals only: no IP address, no cookie. "
    "Your own visits while you are logged in are not counted."
)
VALID = {
    "name": "Anna K.",
    "reply_to": "anna.k@example.com",
    "move_in": "2027-01",
    "stay": "6-12",
    "message": "Hello Bún, we work remotely.",
}


@pytest.fixture(autouse=True)
def fixed_today(mocker: MockerFixture) -> None:
    mocker.patch("counter.report.today_in_da_nang", return_value=TODAY)


@pytest.fixture(autouse=True)
def clock(mocker: MockerFixture) -> MagicMock:
    """Freeze "now" at noon on 16 Nov 2026 in Đà Nẵng."""
    mock: MagicMock = mocker.patch("django.utils.timezone.now")
    mock.return_value = NOON
    return mock


@pytest.fixture(autouse=True)
def no_push(mocker: MockerFixture) -> MagicMock:
    """The push to the owner's phone never reaches the network."""
    mock: MagicMock = mocker.patch("enquiries.services.push_new_enquiry")
    return mock


@pytest.fixture
def owner_client() -> Client:
    owner = User.objects.create_superuser(username="demo-owner", password="demo-password-123")
    client = Client()
    client.force_login(owner)
    return client


def view(day: date, count: int) -> None:
    DailyCount.objects.create(day=day, kind="view", channel="", place="", count=count)


def click(day: date, channel: str, place: str, count: int) -> None:
    DailyCount.objects.create(day=day, kind="click", channel=channel, place=place, count=count)


def message(day: date, count: int) -> None:
    DailyCount.objects.create(day=day, kind="message", channel="", place="contact", count=count)


def demo_counts() -> None:
    # Same demo counts as test_report.py.
    view(date(2026, 11, 1), 200)
    view(date(2026, 11, 13), 14)
    click(date(2026, 11, 2), "call", "bar", 5)
    click(date(2026, 11, 3), "zalo", "contact", 4)
    view(date(2026, 10, 31), 50)
    click(date(2026, 10, 1), "whatsapp", "rent", 2)
    view(date(2026, 1, 5), 10)
    click(date(2026, 1, 5), "call", "rent", 1)


def demo_with_messages() -> None:
    demo_counts()
    message(date(2026, 11, 5), 2)
    message(date(2026, 10, 20), 1)


def page(client: Client) -> str:
    response = client.get(REPORT)
    assert response.status_code == 200
    return response.content.decode()


def section(html: str, start: str, end: str) -> str:
    begin = html.index(start)
    return html[begin : html.index(end, begin)]


def message_rows() -> list[DailyCount]:
    return list(DailyCount.objects.filter(kind="message"))


def make_enquiries(count: int) -> None:
    Enquiry.objects.bulk_create(
        [
            Enquiry(name=f"N{i}", reply_to="old@example.com", message="Hi", language="en")
            for i in range(count)
        ]
    )
    Enquiry.objects.update(created_at=MIDNIGHT + timedelta(minutes=1))


# M32 (AC1): a stored enquiry adds 1 to the message row of the Đà Nẵng day


def test_stored_enquiry_counts_one_message_then_two() -> None:
    client = Client()
    assert client.post(ENQUIRY, VALID).status_code == 303
    row = DailyCount.objects.get(kind="message")
    assert (row.day, row.channel, row.place, row.count) == (TODAY, "", "contact", 1)
    assert client.post(ENQUIRY, VALID).status_code == 303
    row = DailyCount.objects.get(kind="message")
    assert (row.day, row.channel, row.place, row.count) == (TODAY, "", "contact", 2)
    assert Enquiry.objects.count() == 2


def test_message_day_is_the_da_nang_day_not_the_utc_day(clock: MagicMock) -> None:
    clock.return_value = datetime(2026, 11, 15, 18, 0, tzinfo=UTC)  # 01:00 on 16 Nov in Đà Nẵng
    assert Client().post(ENQUIRY, VALID).status_code == 303
    assert DailyCount.objects.get(kind="message").day == TODAY


def test_vietnamese_enquiry_is_counted_too() -> None:
    assert Client().post("/vi/enquiry/", VALID).status_code == 303
    assert DailyCount.objects.get(kind="message").count == 1


def test_stored_post_with_the_message_count_makes_at_most_five_queries(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    with django_assert_max_num_queries(5):
        assert client.post(ENQUIRY, VALID).status_code == 303
    assert DailyCount.objects.get(kind="message").count == 1


# M33 (AC2): trap, refused, paused and staff posts add nothing


def test_trap_post_adds_no_message() -> None:
    response = Client().post(ENQUIRY, {**VALID, "website": "http://spam.example"})
    assert response.status_code == 303
    assert message_rows() == []


def test_refused_post_adds_no_message() -> None:
    assert Client().post(ENQUIRY, {**VALID, "name": ""}).status_code == 400
    assert message_rows() == []


def test_paused_post_adds_no_message() -> None:
    make_enquiries(20)
    assert Client().post(ENQUIRY, VALID).status_code == 429
    assert message_rows() == []


def test_staff_post_is_stored_but_adds_no_message(owner_client: Client) -> None:
    assert owner_client.post(ENQUIRY, VALID).status_code == 303
    assert Enquiry.objects.count() == 1
    assert message_rows() == []


def test_staff_post_leaves_a_visitor_count_as_it_was(owner_client: Client) -> None:
    assert Client().post(ENQUIRY, VALID).status_code == 303
    assert owner_client.post(ENQUIRY, VALID).status_code == 303
    assert Enquiry.objects.count() == 2
    assert DailyCount.objects.get(kind="message").count == 1


# M34 (AC3): /count/ refuses kind=message


def test_count_address_refuses_a_message() -> None:
    assert Client().post(COUNT, {"kind": "message"}).status_code == 400
    assert DailyCount.objects.count() == 0


def test_count_address_refuses_a_message_with_channel_and_place() -> None:
    data = {"kind": "message", "channel": "", "place": "contact"}
    assert Client().post(COUNT, data).status_code == 400
    assert DailyCount.objects.count() == 0


def test_count_address_still_accepts_a_view_and_a_click() -> None:
    client = Client()
    assert client.post(COUNT, {"kind": "view"}).status_code == 204
    click_data = {"kind": "click", "channel": "call", "place": "bar"}
    assert client.post(COUNT, click_data).status_code == 204
    assert sorted(DailyCount.objects.values_list("kind", flat=True)) == ["click", "view"]


# M35 (AC4): the summary, the row and the column


def test_summary_has_messages_sent_and_unchanged_clicks_and_rate() -> None:
    demo_with_messages()
    this, last, total = build_report().summary
    assert (this.messages, last.messages, total.messages) == (2, 1, 3)
    assert (this.views, this.clicks, this.rate) == (214, 9, "4.2")
    assert (last.views, last.clicks, last.rate) == (50, 2, "4.0")
    assert (total.views, total.clicks, total.rate) == (274, 12, "4.4")


def test_summary_shows_messages_sent_after_contact_clicks(owner_client: Client) -> None:
    demo_with_messages()
    html = page(owner_client)
    summary = section(html, 'class="counter-summary"', "By channel")
    assert re.findall(r"<dt>Messages sent</dt>\s*<dd>(\d+)</dd>", summary) == ["2", "1", "3"]
    assert summary.index("Contact clicks") < summary.index("Messages sent")
    assert re.findall(r"<dt>Contact clicks</dt>\s*<dd>(\d+)</dd>", summary) == ["9", "2", "12"]
    assert re.findall(r"<dt>clicks per 100 views</dt>\s*<dd>([^<]+)</dd>", summary) == [
        "4.2",
        "4.0",
        "4.4",
    ]


def test_by_channel_stays_three_channels_and_has_the_messages_row() -> None:
    demo_with_messages()
    report = build_report()
    assert [r.label for r in report.by_channel] == ["Call", "WhatsApp", "Zalo"]
    row = report.messages
    assert (row.label, row.this_month, row.last_month, row.all_time) == (
        "Form (messages sent)",
        2,
        1,
        3,
    )


def test_by_channel_table_ends_with_the_form_row(owner_client: Client) -> None:
    demo_with_messages()
    html = page(owner_client)
    table = section(html, "By channel", "By place")
    rows = re.findall(r"<tr><th scope=\"row\">(.*?)</th>(.*?)</tr>", table)
    assert [label for label, _ in rows] == ["Call", "WhatsApp", "Zalo", "Form (messages sent)"]
    assert re.findall(r"<td[^>]*>(\d+)</td>", rows[-1][1]) == ["2", "1", "3"]


def test_by_month_has_a_messages_column_after_total_clicks(owner_client: Client) -> None:
    demo_with_messages()
    months = {m.month: m.messages for m in build_report().by_month}
    assert months == {"Nov 2026": 2, "Oct 2026": 1, "Jan 2026": 0}
    html = page(owner_client)
    table = section(html, "By month", PRIVACY_LINE)
    headers = re.findall(r"<th scope=\"col\"[^>]*>(.*?)</th>", table)
    assert headers[-2:] == ["Total clicks", "Messages"]
    rows = {
        month: re.findall(r"<td[^>]*>(\d+)</td>", cells)
        for month, cells in re.findall(r"<tr><th scope=\"row\">(.*?)</th>(.*?)</tr>", table)
    }
    assert rows["Nov 2026"] == ["214", "5", "0", "4", "9", "2"]
    assert rows["Oct 2026"] == ["50", "0", "2", "0", "2", "1"]
    assert rows["Jan 2026"][-1] == "0"


# M36 (AC5): empty, zeros and a lone message


def test_nothing_counted_shows_only_the_empty_line(owner_client: Client) -> None:
    assert build_report().is_empty
    html = page(owner_client)
    assert EMPTY_LINE in html
    assert PRIVACY_LINE in html
    assert "Messages sent" not in html
    assert "Form (messages sent)" not in html


def test_views_and_clicks_without_a_message_show_zeros(owner_client: Client) -> None:
    demo_counts()
    report = build_report()
    assert not report.is_empty
    assert [t.messages for t in report.summary] == [0, 0, 0]
    html = page(owner_client)
    summary = section(html, 'class="counter-summary"', "By channel")
    assert re.findall(r"<dt>Messages sent</dt>\s*<dd>(\d+)</dd>", summary) == ["0", "0", "0"]
    table = section(html, "By channel", "By place")
    form_row = table[table.index("Form (messages sent)") :]
    assert re.findall(r"<td[^>]*>(\d+)</td>", form_row) == ["0", "0", "0"]
    assert "Messages" in section(html, "By month", PRIVACY_LINE)


def test_one_message_alone_is_not_an_empty_report(owner_client: Client) -> None:
    message(date(2026, 11, 5), 1)
    assert not build_report().is_empty
    html = page(owner_client)
    assert EMPTY_LINE not in html
    assert "Form (messages sent)" in html
    summary = section(html, 'class="counter-summary"', "By channel")
    assert re.findall(r"<dt>Messages sent</dt>\s*<dd>(\d+)</dd>", summary) == ["1", "0", "1"]


# M37 (AC6): the same number of queries with 1 row and with 400 rows


def test_report_query_count_does_not_grow_with_messages(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    message(date(2026, 11, 1), 1)
    with django_assert_num_queries(2):
        build_report()
    DailyCount.objects.bulk_create(
        DailyCount(
            day=date.fromordinal(date(2025, 1, 1).toordinal() + n),
            kind="message" if n % 2 else "view",
            channel="",
            place="contact" if n % 2 else "",
            count=1,
        )
        for n in range(1, 400)
    )
    assert DailyCount.objects.count() == 400
    with django_assert_num_queries(2):
        build_report()


def test_page_query_count_does_not_grow_with_messages(owner_client: Client) -> None:
    message(date(2026, 11, 1), 1)
    with CaptureQueriesContext(connection) as small:
        page(owner_client)
    DailyCount.objects.bulk_create(
        DailyCount(
            day=date.fromordinal(date(2025, 1, 1).toordinal() + n),
            kind="message" if n % 2 else "click",
            channel="" if n % 2 else "call",
            place="contact" if n % 2 else "bar",
            count=2,
        )
        for n in range(399)
    )
    with CaptureQueriesContext(connection) as large:
        page(owner_client)
    assert len(large.captured_queries) == len(small.captured_queries)
