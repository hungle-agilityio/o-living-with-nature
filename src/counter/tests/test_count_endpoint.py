"""The count address /count/ and the daily totals it stores (issue #87, AC1 to AC9)."""

from datetime import UTC, date, datetime

import pytest
from django.apps import apps
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings
from pytest_mock import MockerFixture

from counter.forms import CountForm
from counter.models import DailyCount
from counter.services import record_count, today_in_da_nang

pytestmark = pytest.mark.django_db

COUNT = "/count/"
CHANNELS = ["call", "whatsapp", "zalo"]
PLACES = ["bar", "rent", "contact"]


def post(client: Client, data: dict[str, str], **headers: str) -> int:
    return client.post(COUNT, data, headers=headers).status_code


# AC1: the app, the model and what it stores


def test_counter_app_is_installed() -> None:
    assert apps.is_installed("counter")


def test_model_has_only_the_daily_total_fields() -> None:
    names = {field.name for field in DailyCount._meta.get_fields()}
    assert names == {"id", "day", "kind", "channel", "place", "count"}
    assert DailyCount._meta.verbose_name_plural == "Contact counts"


def test_migration_matches_the_model() -> None:
    call_command("makemigrations", "counter", check=True, dry_run=True, verbosity=0)


def test_one_row_per_day_kind_channel_and_place() -> None:
    DailyCount.objects.create(day=date(2026, 11, 13), kind="view", channel="", place="", count=1)
    with pytest.raises(IntegrityError), transaction.atomic():
        DailyCount.objects.create(
            day=date(2026, 11, 13), kind="view", channel="", place="", count=1
        )


# AC2: a valid count adds 1 and answers 204


def test_view_is_counted() -> None:
    client = Client()
    response = client.post(COUNT, {"kind": "view"})
    assert response.status_code == 204
    assert response.content == b""
    row = DailyCount.objects.get()
    assert (row.kind, row.channel, row.place, row.count) == ("view", "", "", 1)
    assert row.day == today_in_da_nang()


def test_two_views_give_a_count_of_two() -> None:
    client = Client()
    assert post(client, {"kind": "view"}) == 204
    assert post(client, {"kind": "view"}) == 204
    assert DailyCount.objects.get().count == 2


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("place", PLACES)
def test_click_is_counted_per_channel_and_place(channel: str, place: str) -> None:
    client = Client()
    data = {"kind": "click", "channel": channel, "place": place}
    assert post(client, data) == 204
    assert post(client, data) == 204
    row = DailyCount.objects.get()
    assert (row.kind, row.channel, row.place, row.count) == ("click", channel, place, 2)


def test_different_clicks_go_to_different_rows() -> None:
    client = Client()
    post(client, {"kind": "click", "channel": "call", "place": "bar"})
    post(client, {"kind": "click", "channel": "zalo", "place": "rent"})
    post(client, {"kind": "view"})
    assert DailyCount.objects.count() == 3


def test_fields_are_checked_by_a_django_form() -> None:
    assert CountForm({"kind": "view"}).is_valid()
    assert not CountForm({"kind": "nope"}).is_valid()


# AC3: everything else stores nothing


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"kind": "nope"},
        {"kind": "click"},
        {"kind": "click", "channel": "call"},
        {"kind": "click", "place": "bar"},
        {"kind": "click", "channel": "email", "place": "bar"},
        {"kind": "click", "channel": "call", "place": "footer"},
        {"kind": "view", "channel": "call"},
        {"kind": "view", "place": "bar"},
        {"kind": "view", "channel": "call", "place": "bar"},
    ],
)
def test_invalid_count_answers_400_and_stores_nothing(data: dict[str, str]) -> None:
    assert post(Client(), data) == 400
    assert DailyCount.objects.count() == 0


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete", "head", "options"])
def test_other_methods_answer_405(method: str) -> None:
    response = getattr(Client(), method)(COUNT)
    assert response.status_code == 405
    assert DailyCount.objects.count() == 0


# AC4: the origin check and no CSRF token


def test_foreign_origin_answers_403_and_stores_nothing() -> None:
    assert post(Client(), {"kind": "view"}, Origin="https://evil.example") == 403
    assert DailyCount.objects.count() == 0


def test_same_origin_is_accepted() -> None:
    assert post(Client(), {"kind": "view"}, Origin="http://testserver") == 204
    assert DailyCount.objects.get().count == 1


def test_same_host_other_scheme_is_refused() -> None:
    assert post(Client(), {"kind": "view"}, Origin="https://testserver") == 403
    assert DailyCount.objects.count() == 0


def test_https_origin_behind_the_proxy_is_accepted(settings: Settings) -> None:
    settings.SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # As a browser behind Render's proxy sends it: the host, the origin and the proxy's scheme.
    headers = {"Host": "testserver", "Origin": "https://testserver", "X-Forwarded-Proto": "https"}
    status = post(Client(), {"kind": "view"}, **headers)
    assert status == 204
    assert DailyCount.objects.get().count == 1


def test_no_csrf_token_is_needed() -> None:
    client = Client(enforce_csrf_checks=True)
    assert post(client, {"kind": "view"}) == 204


# AC5: no cookie for a visitor


@pytest.mark.parametrize(
    "data", [{"kind": "view"}, {"kind": "nope"}, {"kind": "click", "channel": "call"}]
)
def test_no_cookie_is_set(data: dict[str, str]) -> None:
    client = Client(enforce_csrf_checks=True)
    response = client.post(COUNT, data)
    assert "Set-Cookie" not in response.headers
    assert not response.cookies
    assert not client.cookies
    response = client.get(COUNT)
    assert "Set-Cookie" not in response.headers
    assert not client.cookies


# AC6: the owner's own visits are not counted


def test_staff_user_is_not_counted() -> None:
    owner = User.objects.create_user("owner", password="pw-for-tests", is_staff=True)
    client = Client()
    client.force_login(owner)
    assert post(client, {"kind": "view"}) == 204
    assert post(client, {"kind": "click", "channel": "call", "place": "bar"}) == 204
    assert DailyCount.objects.count() == 0


# AC7: the day is the date in Đà Nẵng


def test_day_follows_da_nang_time(mocker: MockerFixture) -> None:
    clock = mocker.patch("counter.services.timezone.now")
    clock.return_value = datetime(2026, 11, 13, 16, 59, tzinfo=UTC)  # 23:59 in Đà Nẵng
    assert post(Client(), {"kind": "view"}) == 204
    clock.return_value = datetime(2026, 11, 13, 17, 1, tzinfo=UTC)  # 00:01 next day
    assert post(Client(), {"kind": "view"}) == 204
    days = sorted(DailyCount.objects.values_list("day", "count"))
    assert days == [(date(2026, 11, 13), 1), (date(2026, 11, 14), 1)]


def test_row_created_by_another_request_is_counted_without_error() -> None:
    day = date(2026, 1, 1)
    DailyCount.objects.create(day=day, kind="view", channel="", place="", count=1)
    with transaction.atomic():  # an enclosing transaction stays usable
        record_count(kind="view", channel="", place="", day=day)
        assert DailyCount.objects.get(day=day).count == 2


def test_record_count_uses_the_given_day() -> None:
    record_count(kind="view", channel="", place="", day=date(2026, 1, 1))
    record_count(kind="view", channel="", place="", day=date(2026, 1, 1))
    assert DailyCount.objects.get(day=date(2026, 1, 1)).count == 2


# AC8: at most 2 queries per count; / keeps its one query


def test_first_count_makes_at_most_two_queries(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    with django_assert_max_num_queries(2):
        assert post(client, {"kind": "view"}) == 204


def test_next_count_makes_at_most_two_queries(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    post(client, {"kind": "click", "channel": "call", "place": "bar"})
    with django_assert_max_num_queries(2):
        assert post(client, {"kind": "click", "channel": "call", "place": "bar"}) == 204
    assert DailyCount.objects.get().count == 2


def test_home_page_still_makes_one_query(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    with django_assert_num_queries(1):
        assert client.get("/").status_code == 200
