"""The contact counts report in the admin (issue #89, AC1 to AC9). Demo counts only."""

from datetime import date

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import translation
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from counter.models import DailyCount
from counter.report import Report, build_report, clicks_per_100, month_label

pytestmark = pytest.mark.django_db

REPORT = "/owner/counter/dailycount/"
TODAY = date(2026, 11, 13)
EMPTY_LINE = "Nothing counted yet. Counts start when someone opens the site."
PRIVACY_LINE = (
    "Daily totals only: no IP address, no cookie. "
    "Your own visits while you are logged in are not counted."
)


@pytest.fixture(autouse=True)
def fixed_today(mocker: MockerFixture) -> None:
    mocker.patch("counter.report.today_in_da_nang", return_value=TODAY)


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


def demo_counts() -> None:
    # This month (Nov 2026), last month (Oct 2026) and an older month (Jan 2026).
    view(date(2026, 11, 1), 200)
    view(date(2026, 11, 13), 14)
    click(date(2026, 11, 2), "call", "bar", 5)
    click(date(2026, 11, 3), "zalo", "contact", 4)
    view(date(2026, 10, 31), 50)
    click(date(2026, 10, 1), "whatsapp", "rent", 2)
    view(date(2026, 1, 5), 10)
    click(date(2026, 1, 5), "call", "rent", 1)


def page(client: Client) -> str:
    response = client.get(REPORT)
    assert response.status_code == 200
    return response.content.decode()


def report_block(html: str) -> str:
    """The report itself, without the admin's side menu (which has tables of its own)."""
    start = html.index('id="content-main"')
    return html[start : html.index(PRIVACY_LINE, start)]


# AC1: listed in the admin index, read-only, behind the login


def test_admin_index_lists_contact_counts_under_counter(owner_client: Client) -> None:
    html = owner_client.get("/owner/").content.decode()
    assert "Counter" in html
    assert "Contact counts" in html
    assert REPORT in html


def test_report_uses_its_own_template(owner_client: Client) -> None:
    response = owner_client.get(REPORT)
    names = [template.name for template in response.templates]
    assert "admin/counter/report.html" in names
    assert "admin/base_site.html" in names


def test_no_add_change_or_delete(owner_client: Client) -> None:
    demo_counts()
    row = DailyCount.objects.first()
    assert row is not None
    assert owner_client.get(REPORT + "add/").status_code in (403, 404)
    assert owner_client.post(REPORT + "add/", {"kind": "view"}).status_code in (403, 404)
    assert owner_client.get(f"{REPORT}{row.pk}/change/").status_code in (403, 404)
    assert owner_client.get(f"{REPORT}{row.pk}/delete/").status_code in (403, 404)
    html = page(owner_client)
    assert REPORT + "add/" not in html
    assert DailyCount.objects.count() == 8


def test_visitor_not_logged_in_is_sent_to_login() -> None:
    response = Client().get(REPORT)
    assert response.status_code == 302
    assert response["Location"].startswith("/owner/login/")


def test_staff_without_view_permission_is_refused() -> None:
    staff = User.objects.create_user(
        username="demo-staff", password="demo-password-123", is_staff=True
    )
    client = Client()
    client.force_login(staff)
    assert client.get(REPORT).status_code == 403


# AC2: the three summary columns


def test_clicks_per_100_has_one_decimal() -> None:
    assert clicks_per_100(clicks=9, views=214) == "4.2"
    assert clicks_per_100(clicks=0, views=10) == "0.0"
    assert clicks_per_100(clicks=1, views=8) == "12.5"
    # 6.25 rounds half up to 6.3 (round() would give 6.2).
    assert clicks_per_100(clicks=1, views=16) == "6.3"


def test_clicks_per_100_without_views_is_a_dash() -> None:
    assert clicks_per_100(clicks=3, views=0) == "–"


def test_summary_has_this_month_last_month_and_all_time() -> None:
    demo_counts()
    report = build_report()
    this, last, total = report.summary
    assert (this.label, this.views, this.clicks, this.rate) == ("This month", 214, 9, "4.2")
    assert (last.label, last.views, last.clicks, last.rate) == ("Last month", 50, 2, "4.0")
    assert (total.label, total.views, total.clicks) == ("All time", 274, 12)
    assert total.rate == "4.4"


def test_last_month_in_january_is_december(mocker: MockerFixture) -> None:
    mocker.patch("counter.report.today_in_da_nang", return_value=date(2027, 1, 2))
    view(date(2026, 12, 31), 7)
    view(date(2027, 1, 1), 3)
    this, last, _ = build_report().summary
    assert (this.views, last.views) == (3, 7)


def test_a_row_after_this_month_is_not_in_this_month() -> None:
    view(date(2026, 11, 30), 4)
    view(date(2026, 12, 1), 6)
    this, _, total = build_report().summary
    assert (this.views, total.views) == (4, 10)


def test_summary_shows_in_the_page(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    for text in ("This month", "Last month", "All time", "clicks per 100 views", "4.2"):
        assert text in html


# AC3: by channel and by place


def test_by_channel_and_by_place_rows_in_order_with_zeros() -> None:
    demo_counts()
    report = build_report()
    channels = [(r.label, r.this_month, r.last_month, r.all_time) for r in report.by_channel]
    assert channels == [("Call", 5, 0, 6), ("WhatsApp", 0, 2, 2), ("Zalo", 4, 0, 4)]
    places = [(r.label, r.this_month, r.last_month, r.all_time) for r in report.by_place]
    assert places == [
        ("Phone bar", 5, 0, 5),
        ("Rent chapter", 0, 2, 3),
        ("Contact chapter", 4, 0, 4),
    ]


def test_by_channel_and_by_place_tables_show(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    for text in ("By channel", "By place", "WhatsApp", "Phone bar", "Rent chapter"):
        assert text in html


# AC4: by month


def test_by_month_newest_first() -> None:
    demo_counts()
    months = [
        (m.month, m.views, m.call, m.whatsapp, m.zalo, m.clicks) for m in build_report().by_month
    ]
    assert months == [
        ("Nov 2026", 214, 5, 0, 4, 9),
        ("Oct 2026", 50, 0, 2, 0, 2),
        ("Jan 2026", 10, 1, 0, 0, 1),
    ]


def test_month_label_stays_english_in_another_language() -> None:
    with translation.override("vi"):
        assert month_label(date(2026, 11, 1)) == "Nov 2026"


def test_by_month_keeps_the_last_12_months_with_counts() -> None:
    for month in range(1, 13):
        view(date(2025, month, 1), month)
    view(date(2026, 3, 1), 99)
    months = [m.month for m in build_report().by_month]
    assert len(months) == 12
    assert months[0] == "Mar 2026"
    assert months[-1] == "Feb 2025"
    assert "Jan 2025" not in months


def test_by_month_shows_in_the_page(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    assert "By month" in html
    assert "Nov 2026" in html


# AC5: nothing counted


def test_empty_report() -> None:
    report = build_report()
    assert isinstance(report, Report)
    assert report.is_empty


def test_empty_page_shows_only_the_empty_line(owner_client: Client) -> None:
    html = page(owner_client)
    assert EMPTY_LINE in html
    assert PRIVACY_LINE in html
    block = report_block(html)
    assert "<table" not in block
    assert "By channel" not in block
    assert "This month" not in block


def test_page_with_counts_has_no_empty_line(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    assert EMPTY_LINE not in html
    assert "<table" in html


# AC6: the privacy line


def test_privacy_line_under_the_report(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    assert PRIVACY_LINE in html
    assert html.index(PRIVACY_LINE) > html.index("By month")


# AC7: wide tables scroll inside their own box


def test_tables_are_in_a_scroll_box(owner_client: Client) -> None:
    demo_counts()
    html = page(owner_client)
    block = report_block(html)
    assert block.count("<table") == 3
    assert block.count('class="counter-scroll"') == 3
    assert "overflow-x: auto" in html


# AC8: the same number of queries with 1 row and with 400 rows


def test_report_query_count_does_not_grow(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    view(date(2026, 11, 1), 1)
    with django_assert_num_queries(2):
        build_report()
    rows = [
        DailyCount(
            day=date.fromordinal(date(2025, 1, 1).toordinal() + n),
            kind="view",
            channel="",
            place="",
            count=1,
        )
        for n in range(1, 400)
    ]
    DailyCount.objects.bulk_create(rows)
    assert DailyCount.objects.count() == 400
    with django_assert_num_queries(2):
        build_report()


def test_page_query_count_does_not_grow(owner_client: Client) -> None:
    view(date(2026, 11, 1), 1)
    with CaptureQueriesContext(connection) as small:
        page(owner_client)
    DailyCount.objects.bulk_create(
        DailyCount(
            day=date.fromordinal(date(2025, 1, 1).toordinal() + n),
            kind="click",
            channel="call",
            place="bar",
            count=2,
        )
        for n in range(399)
    )
    with CaptureQueriesContext(connection) as large:
        page(owner_client)
    assert len(large.captured_queries) == len(small.captured_queries)
