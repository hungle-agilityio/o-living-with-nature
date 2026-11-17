"""The FAQ chapter as a fourth place for contact-button counts (issue #101, AC1 to AC9)."""

import re
from datetime import date
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from counter.models import DailyCount
from counter.report import build_report
from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

COUNT = "/count/"
REPORT = "/owner/counter/dailycount/"
TODAY = date(2026, 11, 13)
EMPTY_LINE = "Nothing counted yet. Counts start when someone opens the site."
PLACES = ["bar", "rent", "faq", "contact"]
MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "0002_daily_count_faq_place.py"


@pytest.fixture(autouse=True)
def fixed_today(mocker: MockerFixture) -> None:
    mocker.patch("counter.report.today_in_da_nang", return_value=TODAY)
    mocker.patch("counter.services.today_in_da_nang", return_value=TODAY)


@pytest.fixture
def owner_client() -> Client:
    owner = User.objects.create_superuser(username="demo-owner", password="demo-password-123")
    client = Client()
    client.force_login(owner)
    return client


def click(day: date, channel: str, place: str, count: int) -> None:
    DailyCount.objects.create(day=day, kind="click", channel=channel, place=place, count=count)


def view(day: date, count: int) -> None:
    DailyCount.objects.create(day=day, kind="view", channel="", place="", count=count)


def report_html(client: Client) -> str:
    response = client.get(REPORT)
    assert response.status_code == 200
    return response.content.decode()


# M1 (AC1)


def test_place_has_four_values_in_order_and_keeps_max_length_7() -> None:
    assert [(v, str(label)) for v, label in DailyCount.Place.choices] == [
        ("bar", "Phone bar"),
        ("rent", "Rent chapter"),
        ("faq", "FAQ chapter"),
        ("contact", "Contact chapter"),
        ("journal", "Journal notes"),
    ]
    assert DailyCount._meta.get_field("place").max_length == 7


# M2 (AC2)


def test_migration_0002_alters_place_only_and_models_have_no_pending_change() -> None:
    assert MIGRATION.exists()
    source = MIGRATION.read_text()
    assert '("counter", "0001_initial")' in source
    assert source.count("migrations.AlterField(") == 1
    assert source.count("migrations.") == 2  # Migration base class + the one AlterField
    assert 'model_name="dailycount"' in source
    assert 'name="place"' in source
    call_command("makemigrations", "counter", check=True, dry_run=True, verbosity=0)


# M3 (AC3)


@pytest.mark.parametrize("channel", ["call", "whatsapp", "zalo"])
def test_faq_click_is_counted_and_adds_up(client: Client, channel: str) -> None:
    data = {"kind": "click", "channel": channel, "place": "faq"}
    for expected in (1, 2):
        response = client.post(COUNT, data)
        assert response.status_code == 204
        assert response.content == b""
        row = DailyCount.objects.get(day=TODAY, kind="click", channel=channel, place="faq")
        assert row.count == expected


# M4 (AC4)


@pytest.mark.parametrize("place", ["hero", "FAQ", ""])
def test_unknown_place_is_refused_and_nothing_is_stored(client: Client, place: str) -> None:
    response = client.post(COUNT, {"kind": "click", "channel": "call", "place": place})
    assert response.status_code == 400
    assert DailyCount.objects.count() == 0


# M5 (AC5)


def test_every_contact_link_has_a_known_place_and_can_be_posted(client: Client) -> None:
    SiteSettings.objects.update(phone="0901234567", whatsapp="0901234568", zalo="0901234569")
    html = client.get("/").content.decode()
    links = re.findall(r"<a [^>]*data-channel=[^>]*>", html)
    assert links
    faq = re.search(r'<section id="faq"[^>]*>.*?</section>', html, re.S)
    assert faq
    faq_links = re.findall(r"<a [^>]*data-channel=[^>]*>", faq.group(0))
    assert faq_links
    assert all('data-place="faq"' in link for link in faq_links)
    channels_seen: set[str] = set()
    for link in links:
        channel = re.search(r'data-channel="([^"]*)"', link)
        place = re.search(r'data-place="([^"]*)"', link)
        assert channel
        assert place
        assert place.group(1) in PLACES
        channels_seen.add(channel.group(1))
        response = client.post(
            COUNT, {"kind": "click", "channel": channel.group(1), "place": place.group(1)}
        )
        assert response.status_code == 204
    assert channels_seen == {"call", "whatsapp", "zalo"}


# M6 (AC5, empty)


def test_without_any_channel_the_home_page_has_no_contact_link(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")
    html = client.get("/").content.decode()
    assert "data-channel" not in html


# M7 (AC6)


def test_report_has_the_faq_chapter_row_between_rent_and_contact(owner_client: Client) -> None:
    click(date(2026, 11, 2), "call", "bar", 5)
    click(date(2026, 11, 3), "zalo", "contact", 4)
    click(date(2026, 11, 4), "whatsapp", "faq", 3)
    report = build_report()
    assert [r.label for r in report.by_place] == [
        "Phone bar",
        "Rent chapter",
        "FAQ chapter",
        "Contact chapter",
        "Journal notes",
    ]
    assert [r.this_month for r in report.by_place] == [5, 0, 3, 4, 0]
    assert report.summary[0].clicks == 12
    assert "FAQ chapter" in report_html(owner_client)


# M8 (AC7)


def test_faq_row_is_zero_when_no_faq_press_was_counted() -> None:
    view(date(2026, 11, 1), 200)
    click(date(2026, 11, 2), "call", "bar", 5)
    click(date(2026, 11, 3), "zalo", "contact", 4)
    click(date(2026, 10, 1), "whatsapp", "rent", 2)
    click(date(2026, 1, 5), "call", "rent", 1)
    rows = {r.label: r for r in build_report().by_place}
    faq = rows["FAQ chapter"]
    assert (faq.this_month, faq.last_month, faq.all_time) == (0, 0, 0)


# M9 (AC8)


def test_empty_report_page_has_the_empty_line_and_no_faq_text(owner_client: Client) -> None:
    html = report_html(owner_client)
    assert EMPTY_LINE in html
    assert "FAQ chapter" not in html


# M10 (AC9)


def test_report_makes_two_queries_with_one_row_and_with_forty_rows(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    view(date(2026, 11, 1), 1)
    with django_assert_num_queries(2):
        build_report()
    DailyCount.objects.bulk_create(
        DailyCount(
            day=date.fromordinal(date(2026, 10, 1).toordinal() + n),
            kind="click",
            channel="call",
            place=PLACES[n % 4],
            count=1,
        )
        for n in range(40)
    )
    assert DailyCount.objects.count() == 41
    with django_assert_num_queries(2):
        build_report()
