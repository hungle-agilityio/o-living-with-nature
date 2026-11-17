"""The enquiry address /enquiry/ and the enquiries it stores (issue #116, AC1 to AC10)."""

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.apps import apps
from django.core.management import call_command
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from enquiries.forms import EnquiryForm
from enquiries.models import Enquiry
from enquiries.months import month_label, move_in_months, short_month_label

pytestmark = pytest.mark.django_db

EN = "/enquiry/"
VI = "/vi/enquiry/"
TODAY = date(2026, 11, 16)
# 12:00 on 16 Nov 2026 in Đà Nẵng (UTC+7).
NOON = datetime(2026, 11, 16, 5, 0, tzinfo=UTC)
# 00:00 on 16 Nov 2026 in Đà Nẵng.
MIDNIGHT = datetime(2026, 11, 15, 17, 0, tzinfo=UTC)

VALID = {
    "name": "Anna K.",
    "reply_to": "anna.k@example.com",
    "move_in": "2027-01",
    "stay": "6-12",
    "message": "Hello Bún, we work remotely.",
}


@pytest.fixture(autouse=True)
def clock(mocker: MockerFixture) -> MagicMock:
    """Freeze "now" at noon on 16 Nov 2026 in Đà Nẵng."""
    mock: MagicMock = mocker.patch("django.utils.timezone.now")
    mock.return_value = NOON
    return mock


def make_enquiries(count: int, *, created_at: datetime | None = None) -> None:
    Enquiry.objects.bulk_create(
        [
            Enquiry(name=f"N{i}", reply_to="old@example.com", message="Hi", language="en")
            for i in range(count)
        ]
    )
    if created_at is not None:
        Enquiry.objects.update(created_at=created_at)


def form(data: dict[str, str], language: str = "en") -> EnquiryForm:
    return EnquiryForm(data, language=language, today=TODAY)


def codes(bound: EnquiryForm) -> dict[str, list[str]]:
    return {
        field: [error.code or "" for error in errors]
        for field, errors in bound.errors.as_data().items()
    }


def template_names(response: Any) -> list[str]:
    return [t.name for t in getattr(response, "templates", [])]


# M1 (AC1): fields, lengths, defaults; the migration matches the model


def test_enquiries_app_is_installed() -> None:
    assert apps.is_installed("enquiries")


def test_enquiry_has_exactly_the_agreed_fields() -> None:
    names = {field.name for field in Enquiry._meta.get_fields()}
    assert names == {
        "id",
        "created_at",
        "name",
        "reply_to",
        "move_in",
        "stay",
        "message",
        "language",
        "status",
    }


def test_enquiry_field_lengths_and_defaults() -> None:
    meta = Enquiry._meta
    assert meta.get_field("name").max_length == 80
    assert meta.get_field("reply_to").max_length == 120
    assert meta.get_field("move_in").max_length == 7
    assert meta.get_field("move_in").blank is True
    assert meta.get_field("stay").max_length == 4
    assert meta.get_field("stay").blank is True
    assert meta.get_field("message").max_length == 1000
    assert meta.get_field("language").max_length == 2
    assert meta.get_field("status").max_length == 7
    assert meta.get_field("status").default == "new"
    created_at: Any = meta.get_field("created_at")
    assert created_at.db_index is True
    assert created_at.auto_now_add is True


def test_enquiry_choices_labels_and_names() -> None:
    meta = Enquiry._meta
    assert list(meta.get_field("stay").choices or []) == [
        ("1-3", "1–3 months"),
        ("3-6", "3–6 months"),
        ("6-12", "6–12 months"),
        ("12+", "A year or more"),
    ]
    assert list(meta.get_field("language").choices or []) == [
        ("en", "English"),
        ("vi", "Vietnamese"),
    ]
    assert list(meta.get_field("status").choices or []) == [
        ("new", "New"),
        ("replied", "Replied"),
    ]
    assert meta.verbose_name == "Enquiry"
    assert meta.verbose_name_plural == "Enquiries"
    assert meta.ordering == ["-created_at"]


def test_new_enquiry_is_new_and_str_has_no_personal_data() -> None:
    row = Enquiry.objects.create(
        name="Anna K.", reply_to="anna.k@example.com", message="Hello", language="en"
    )
    assert row.status == "new"
    assert str(row) == f"Enquiry {row.pk}"


def test_enquiry_migration_matches_the_model() -> None:
    call_command("makemigrations", "enquiries", check=True, dry_run=True, verbosity=0)


# M2 (AC1): nothing that identifies the visitor


def test_enquiry_has_no_field_for_ip_agent_referrer_cookie_or_visitor() -> None:
    forbidden = ("ip", "agent", "referrer", "referer", "cookie", "visitor", "session", "user")
    for field in Enquiry._meta.get_fields():
        assert not any(word in field.name for word in forbidden), field.name


# M3 (AC2): the accepted values


@pytest.mark.parametrize("reply_to", ["anna.k@example.com", "+84 905 000 111", "0905-000-111"])
def test_reply_to_accepts_an_email_or_a_phone_number(reply_to: str) -> None:
    bound = form({**VALID, "reply_to": reply_to})
    assert bound.is_valid(), bound.errors


@pytest.mark.parametrize("move_in", ["2027-01", ""])
@pytest.mark.parametrize("stay", ["6-12", ""])
def test_move_in_and_stay_may_be_chosen_or_left_empty(move_in: str, stay: str) -> None:
    bound = form({**VALID, "move_in": move_in, "stay": stay})
    assert bound.is_valid(), bound.errors


def test_move_in_and_stay_may_be_left_out_of_the_post() -> None:
    data = {k: v for k, v in VALID.items() if k not in {"move_in", "stay"}}
    assert form(data).is_valid()


def test_move_in_months_start_with_this_month_and_run_twelve() -> None:
    assert move_in_months(TODAY) == [
        "2026-11",
        "2026-12",
        "2027-01",
        "2027-02",
        "2027-03",
        "2027-04",
        "2027-05",
        "2027-06",
        "2027-07",
        "2027-08",
        "2027-09",
        "2027-10",
    ]


def test_month_labels() -> None:
    assert month_label("2027-01", "en") == "January 2027"
    assert month_label("2027-01", "vi") == "Tháng 1/2027"
    assert short_month_label("2027-01") == "Jan 2027"


# M4 (AC2): the refused values and their error codes


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("name", "", "required"),
        ("name", "   ", "required"),
        ("message", "", "required"),
        ("message", "    ", "required"),
        ("reply_to", "0905 12", "invalid_reply"),
        ("reply_to", "1234567890123456", "invalid_reply"),
        ("reply_to", "anna@", "invalid_reply"),
        ("reply_to", "0905\t000\n111", "invalid_reply"),
        ("move_in", "2026-10", "invalid_choice"),
        ("move_in", "2027-11", "invalid_choice"),
        ("stay", "2-4", "invalid_choice"),
        ("name", "n" * 81, "max_length"),
        ("message", "m" * 1001, "max_length"),
    ],
)
def test_refused_values_carry_their_error_code(field: str, value: str, code: str) -> None:
    bound = form({**VALID, field: value})
    assert not bound.is_valid()
    assert codes(bound) == {field: [code]}


def test_limits_themselves_are_accepted() -> None:
    assert form({**VALID, "name": "n" * 80, "message": "m" * 1000}).is_valid()


def test_a_browser_line_break_counts_as_one_character() -> None:
    # A browser sends each line break of a textarea as CRLF; the visitor saw one character.
    message = ("m" * 99 + "\r\n") * 10  # 1000 characters as typed, 1010 as sent
    bound = form({**VALID, "message": message})
    assert bound.is_valid(), bound.errors
    assert "\r" not in bound.cleaned_data["message"]
    assert len(bound.cleaned_data["message"]) == 999  # the last line break is stripped


# M5 (AC3): an English post is stored and answered with 303


def test_english_post_is_stored_and_redirects_to_the_sent_address() -> None:
    response = Client().post(EN, VALID)
    assert response.status_code == 303
    assert response["Location"] == "/?enquiry=sent#enquiry"
    row = Enquiry.objects.get()
    assert (row.name, row.reply_to, row.move_in, row.stay) == (
        "Anna K.",
        "anna.k@example.com",
        "2027-01",
        "6-12",
    )
    assert row.message == "Hello Bún, we work remotely."
    assert (row.language, row.status) == ("en", "new")


# M6 (AC3): a Vietnamese post is stored with language vi


def test_vietnamese_post_is_stored_and_redirects_to_the_vietnamese_sent_address() -> None:
    response = Client().post(VI, VALID)
    assert response.status_code == 303
    assert response["Location"] == "/vi/?enquiry=sent#enquiry"
    row = Enquiry.objects.get()
    assert (row.language, row.status) == ("vi", "new")


# M7 (AC4): the trap


@pytest.mark.parametrize(
    "data",
    [
        {**VALID, "website": "http://spam.example"},
        {"name": "", "reply_to": "0905 12", "website": "http://spam.example"},
    ],
)
@pytest.mark.parametrize(
    ("path", "location"),
    [(EN, "/?enquiry=sent#enquiry"), (VI, "/vi/?enquiry=sent#enquiry")],
)
def test_filled_trap_stores_nothing_and_looks_sent(
    data: dict[str, str], path: str, location: str
) -> None:
    response = Client().post(path, data)
    assert response.status_code == 303
    assert response["Location"] == location
    assert Enquiry.objects.count() == 0


# M8 (AC5): a wrong post


def test_wrong_post_answers_400_with_the_home_page_and_the_bound_form() -> None:
    response = Client().post(EN, {**VALID, "name": "", "reply_to": "0905 12"})
    assert response.status_code == 400
    assert "pages/home.html" in template_names(response)
    assert Enquiry.objects.count() == 0
    assert response.context["enquiry_state"] == "errors"
    bound = response.context["enquiry_form"]
    assert bound.is_bound
    assert codes(bound) == {"name": ["required"], "reply_to": ["invalid_reply"]}


def test_empty_post_is_the_errors_page() -> None:
    response = Client().post(EN, {})
    assert response.status_code == 400
    assert response.context["enquiry_state"] == "errors"
    assert Enquiry.objects.count() == 0


# M9 (AC6): the daily limit follows the day in Đà Nẵng


def test_twenty_first_post_today_is_paused() -> None:
    make_enquiries(20, created_at=MIDNIGHT + timedelta(minutes=1))
    response = Client().post(EN, VALID)
    assert response.status_code == 429
    assert Enquiry.objects.count() == 20
    assert response.context["enquiry_state"] == "paused"
    assert not response.context["enquiry_form"].is_bound


def test_nineteen_posts_today_still_allow_the_twentieth() -> None:
    make_enquiries(19, created_at=MIDNIGHT + timedelta(minutes=1))
    assert Client().post(EN, VALID).status_code == 303
    assert Enquiry.objects.count() == 20


def test_enquiries_at_midnight_sharp_count_for_today() -> None:
    make_enquiries(20, created_at=MIDNIGHT)
    assert Client().post(EN, VALID).status_code == 429


def test_yesterday_evening_does_not_count_after_midnight(clock: MagicMock) -> None:
    make_enquiries(20, created_at=MIDNIGHT - timedelta(minutes=1))  # 23:59 yesterday
    clock.return_value = MIDNIGHT + timedelta(minutes=1)  # 00:01 today
    response = Client().post(EN, VALID)
    assert response.status_code == 303
    assert Enquiry.objects.count() == 21


# M10 (AC7): origin, cookies and methods


def test_foreign_origin_answers_403_and_stores_nothing() -> None:
    response = Client().post(EN, VALID, headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    assert Enquiry.objects.count() == 0


def test_post_without_origin_is_accepted() -> None:
    assert Client().post(EN, VALID).status_code == 303
    assert Enquiry.objects.count() == 1


def test_post_with_the_sites_own_origin_is_accepted() -> None:
    response = Client().post(EN, VALID, headers={"Origin": "http://testserver"})
    assert response.status_code == 303
    assert Enquiry.objects.count() == 1


def test_no_csrf_token_is_needed() -> None:
    assert Client(enforce_csrf_checks=True).post(EN, VALID).status_code == 303


@pytest.mark.parametrize(
    "data", [VALID, {"name": ""}, {**VALID, "website": "x"}], ids=["stored", "errors", "trap"]
)
def test_no_cookie_is_set(data: dict[str, str]) -> None:
    client = Client()
    response = client.post(EN, data)
    assert "Set-Cookie" not in response.headers
    assert not response.cookies
    assert not client.cookies


def test_no_cookie_on_a_paused_or_forbidden_post() -> None:
    client = Client()
    forbidden = client.post(EN, VALID, headers={"Origin": "https://evil.example"})
    assert "Set-Cookie" not in forbidden.headers
    make_enquiries(20, created_at=MIDNIGHT + timedelta(minutes=1))
    paused = client.post(EN, VALID)
    assert paused.status_code == 429
    assert "Set-Cookie" not in paused.headers
    assert not client.cookies


@pytest.mark.parametrize("path", [EN, VI])
def test_get_answers_405(path: str) -> None:
    response = Client().get(path)
    assert response.status_code == 405
    assert "Set-Cookie" not in response.headers


# M11 (AC8): enquiries older than 365 days are deleted when one is stored


def test_old_enquiry_is_deleted_and_recent_one_kept() -> None:
    make_enquiries(2)
    old, recent = Enquiry.objects.order_by("pk")
    Enquiry.objects.filter(pk=old.pk).update(created_at=NOON - timedelta(days=366))
    Enquiry.objects.filter(pk=recent.pk).update(created_at=NOON - timedelta(days=364))
    assert Client().post(EN, VALID).status_code == 303
    remaining = set(Enquiry.objects.values_list("pk", flat=True))
    assert old.pk not in remaining
    assert recent.pk in remaining
    assert len(remaining) == 2


def test_nothing_is_deleted_when_the_post_is_refused() -> None:
    make_enquiries(1)
    Enquiry.objects.update(created_at=NOON - timedelta(days=400))
    assert Client().post(EN, {**VALID, "name": ""}).status_code == 400
    assert Enquiry.objects.count() == 1


# M12 (AC9): query budget and the sent state of the home page


def test_stored_post_makes_at_most_three_queries(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    with django_assert_max_num_queries(3):
        assert client.post(EN, VALID).status_code == 303
    assert Enquiry.objects.count() == 1


def test_refused_post_makes_at_most_one_query(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    client = Client()
    with django_assert_max_num_queries(1):
        assert client.post(EN, {**VALID, "name": ""}).status_code == 400


def test_foreign_origin_post_makes_at_most_one_query(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    with django_assert_max_num_queries(1):
        response = Client().post(EN, VALID, headers={"Origin": "https://evil.example"})
        assert response.status_code == 403


def test_paused_post_makes_at_most_two_queries(
    django_assert_max_num_queries: DjangoAssertNumQueries,
) -> None:
    make_enquiries(20, created_at=MIDNIGHT + timedelta(minutes=1))
    client = Client()
    with django_assert_max_num_queries(2):
        assert client.post(EN, VALID).status_code == 429


@pytest.mark.parametrize("path", ["/", "/?enquiry=sent", "/?enquiry=nope", "/vi/"])
def test_home_page_still_makes_one_query(
    django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    client = Client()
    with django_assert_num_queries(1):
        assert client.get(path).status_code == 200


@pytest.mark.parametrize(
    ("path", "state"),
    [
        ("/", "form"),
        ("/?enquiry=sent", "sent"),
        ("/?enquiry=nope", "form"),
        ("/?enquiry=", "form"),
        ("/vi/?enquiry=sent", "sent"),
    ],
)
def test_home_page_state_follows_the_enquiry_query(path: str, state: str) -> None:
    response = Client().get(path)
    assert response.context["enquiry_state"] == state
    assert not response.context["enquiry_form"].is_bound


# M13 (AC10): no personal data in any log record. Kept apart from the query-count tests.

NAME = "Zebulon Quuxington"
REPLY = "zq.private@example.com"
MESSAGE = "Confidential-message-7731"


def assert_no_personal_data(caplog: pytest.LogCaptureFixture) -> None:
    for record in caplog.records:
        text = f"{record.getMessage()} {record.args!r} {record.exc_text}"
        for secret in (NAME, REPLY, MESSAGE, "Zebulon", "Confidential"):
            assert secret not in text, record.name


def test_stored_post_logs_no_personal_data(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    data = {**VALID, "name": NAME, "reply_to": REPLY, "message": MESSAGE}
    assert Client().post(EN, data).status_code == 303
    assert Enquiry.objects.count() == 1
    assert_no_personal_data(caplog)


def test_refused_post_logs_no_personal_data(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    data = {"name": NAME, "reply_to": REPLY + " bad@", "message": MESSAGE, "stay": "2-4"}
    assert Client().post(EN, data).status_code == 400
    assert Enquiry.objects.count() == 0
    assert_no_personal_data(caplog)


def test_paused_post_logs_no_personal_data(caplog: pytest.LogCaptureFixture) -> None:
    make_enquiries(20, created_at=MIDNIGHT + timedelta(minutes=1))
    caplog.set_level(logging.DEBUG)
    data = {**VALID, "name": NAME, "reply_to": REPLY, "message": MESSAGE}
    assert Client().post(EN, data).status_code == 429
    assert_no_personal_data(caplog)
