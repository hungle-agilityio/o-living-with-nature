"""The push to the owner's phone when an enquiry is stored (issue #118, AC1 to AC5)."""

import json
import logging
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import Settings
from pytest_mock import MockerFixture

from enquiries.models import Enquiry
from enquiries.notify import push_new_enquiry

pytestmark = pytest.mark.django_db

SRC = Path(settings.SRC_DIR)
RENDER_YAML = SRC.parent / "render.yaml"
EN = "/enquiry/"
TOPIC = "https://ntfy.sh/o-living-test"
BASE = "https://o-living-web.onrender.com"
URLOPEN = "urllib.request.urlopen"
# 12:00 on 16 Nov 2026 in Đà Nẵng (UTC+7).
NOON = datetime(2026, 11, 16, 5, 0, tzinfo=UTC)

NAME = "Zebulon Quuxington"
REPLY = "zq.private@example.com"
MOVE_IN = "2027-01"
STAY = "6-12"
MESSAGE = "Confidential-message-7731"
VALID = {
    "name": NAME,
    "reply_to": REPLY,
    "move_in": MOVE_IN,
    "stay": STAY,
    "message": MESSAGE,
}

PROBE = "import json; from django.conf import settings; print(json.dumps(settings.NTFY_TOPIC_URL))"


def _setting_in_fresh_process(**extra: str) -> str:
    """The settings are read once per process, so each case loads them in a fresh one."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_") and key not in {"PYTHONPATH", "NTFY_TOPIC_URL"}
    }
    env.update({"DJANGO_SETTINGS_MODULE": "config.settings", "PYTHONPATH": str(SRC), **extra})
    done = subprocess.run(
        [sys.executable, "-c", PROBE], env=env, capture_output=True, text=True, check=True
    )
    value = json.loads(done.stdout.strip().splitlines()[-1])
    assert isinstance(value, str)
    return value


def _mock_urlopen(mocker: MockerFixture, status: int = 200) -> MagicMock:
    """Patch urlopen with a context manager whose response has an integer status."""
    response = MagicMock()
    response.status = status
    manager = MagicMock()
    manager.__enter__.return_value = response
    manager.__exit__.return_value = False
    mock: MagicMock = mocker.patch(URLOPEN, return_value=manager)
    return mock


def _request(mock: MagicMock) -> urllib.request.Request:
    request = mock.call_args.args[0]
    assert isinstance(request, urllib.request.Request)
    return request


def _ntfy_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [record for record in caplog.records if record.name == "enquiries"]


@pytest.fixture(autouse=True)
def clock(mocker: MockerFixture) -> MagicMock:
    """Freeze "now" at noon on 16 Nov 2026 in Đà Nẵng."""
    mock: MagicMock = mocker.patch("django.utils.timezone.now")
    mock.return_value = NOON
    return mock


@pytest.fixture
def topic(settings: Settings) -> None:
    settings.NTFY_TOPIC_URL = TOPIC
    settings.SITE_BASE_URL = BASE


def _make_enquiries(count: int) -> None:
    Enquiry.objects.bulk_create(
        [
            Enquiry(name=f"N{i}", reply_to="old@example.com", message="Hi", language="en")
            for i in range(count)
        ]
    )
    Enquiry.objects.update(created_at=NOON)


# M27 (AC1): one mocked POST with the body, the three headers and the timeout


def test_push_sends_one_post_with_body_three_headers_and_timeout(
    mocker: MockerFixture, topic: None
) -> None:
    mock = _mock_urlopen(mocker)

    push_new_enquiry()

    mock.assert_called_once()
    request = _request(mock)
    assert request.full_url == TOPIC
    assert request.get_method() == "POST"
    assert request.data == "New enquiry on Ở".encode()
    assert {key.title(): value for key, value in request.header_items()} == {
        "Title": "New enquiry",
        "Click": f"{BASE}/owner/enquiries/enquiry/",
        "Tags": "house",
    }
    assert mock.call_args.kwargs == {"timeout": 3}


def test_stored_enquiry_sends_the_push_once(mocker: MockerFixture, topic: None) -> None:
    mock = _mock_urlopen(mocker)

    response = Client().post(EN, VALID)

    assert response.status_code == 303
    assert Enquiry.objects.count() == 1
    mock.assert_called_once()
    assert _request(mock).full_url == TOPIC


# M28 (AC2): no personal data; trap, refused and over-limit posts send nothing


def test_push_request_holds_none_of_the_posted_data(mocker: MockerFixture, topic: None) -> None:
    mock = _mock_urlopen(mocker)

    assert Client().post(EN, VALID).status_code == 303

    request = _request(mock)
    text = f"{request.full_url} {request.data!r} {request.header_items()!r}"
    for secret in (NAME, "Zebulon", REPLY, MOVE_IN, STAY, MESSAGE, "Confidential"):
        assert secret not in text
    assert isinstance(request.data, bytes)
    assert request.data.decode("utf-8") == "New enquiry on Ở"


def test_trap_post_sends_nothing(mocker: MockerFixture, topic: None) -> None:
    mock = _mock_urlopen(mocker)

    response = Client().post(EN, {**VALID, "website": "http://spam.example"})

    assert response.status_code == 303
    assert Enquiry.objects.count() == 0
    mock.assert_not_called()


def test_refused_post_sends_nothing(mocker: MockerFixture, topic: None) -> None:
    mock = _mock_urlopen(mocker)

    response = Client().post(EN, {**VALID, "name": "", "reply_to": "0905 12"})

    assert response.status_code == 400
    assert Enquiry.objects.count() == 0
    mock.assert_not_called()


def test_post_over_the_daily_limit_sends_nothing(mocker: MockerFixture, topic: None) -> None:
    _make_enquiries(20)
    mock = _mock_urlopen(mocker)

    response = Client().post(EN, VALID)

    assert response.status_code == 429
    assert Enquiry.objects.count() == 20
    mock.assert_not_called()


# M29 (AC3): no address, nothing sent, the enquiry is stored


def test_push_with_no_address_calls_nothing(mocker: MockerFixture, settings: Settings) -> None:
    settings.NTFY_TOPIC_URL = ""
    mock = _mock_urlopen(mocker)

    push_new_enquiry()

    mock.assert_not_called()


def test_enquiry_is_stored_when_no_address_is_set(
    mocker: MockerFixture, settings: Settings
) -> None:
    settings.NTFY_TOPIC_URL = ""
    mock = _mock_urlopen(mocker)

    response = Client().post(EN, VALID)

    assert response.status_code == 303
    assert response["Location"] == "/?enquiry=sent#enquiry"
    assert Enquiry.objects.count() == 1
    mock.assert_not_called()


# M30 (AC4): a failing push still stores, answers 303 and logs one class name


@pytest.mark.parametrize(
    ("failure", "name"),
    [
        (TimeoutError(), "TimeoutError"),
        (urllib.error.URLError("down"), "URLError"),
    ],
    ids=["timeout", "urlerror"],
)
def test_failing_urlopen_still_stores_answers_303_and_logs_one_line(
    mocker: MockerFixture,
    topic: None,
    caplog: pytest.LogCaptureFixture,
    failure: Exception,
    name: str,
) -> None:
    caplog.set_level(logging.DEBUG)
    mocker.patch(URLOPEN, side_effect=failure)

    response = Client().post(EN, VALID)

    assert response.status_code == 303
    assert response["Location"] == "/?enquiry=sent#enquiry"
    assert Enquiry.objects.count() == 1
    records = _ntfy_records(caplog)
    assert len(records) == 1
    assert records[0].getMessage() == f"ntfy push failed: {name}"
    assert records[0].levelno == logging.WARNING


def test_status_500_still_stores_answers_303_and_logs_httperror(
    mocker: MockerFixture, topic: None, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    _mock_urlopen(mocker, status=500)

    response = Client().post(EN, VALID)

    assert response.status_code == 303
    assert response["Location"] == "/?enquiry=sent#enquiry"
    assert Enquiry.objects.count() == 1
    records = _ntfy_records(caplog)
    assert len(records) == 1
    assert records[0].getMessage() == "ntfy push failed: HTTPError"


def test_failure_log_holds_no_personal_data(
    mocker: MockerFixture, topic: None, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    mocker.patch(URLOPEN, side_effect=urllib.error.URLError(f"down {NAME} {REPLY} {MESSAGE}"))

    assert Client().post(EN, VALID).status_code == 303

    for record in caplog.records:
        text = f"{record.getMessage()} {record.args!r} {record.exc_text}"
        for secret in (NAME, "Zebulon", REPLY, MESSAGE, "Confidential"):
            assert secret not in text


def test_a_bad_address_is_caught_and_logged_as_valueerror(
    mocker: MockerFixture, settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    settings.NTFY_TOPIC_URL = "not a url"
    mock = _mock_urlopen(mocker)

    push_new_enquiry()

    mock.assert_not_called()
    records = _ntfy_records(caplog)
    assert len(records) == 1
    assert records[0].getMessage() == "ntfy push failed: ValueError"


def test_successful_push_logs_nothing(
    mocker: MockerFixture, topic: None, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    _mock_urlopen(mocker)

    push_new_enquiry()

    assert _ntfy_records(caplog) == []


# M31 (AC5): render.yaml key and the empty default


def test_render_yaml_lists_the_key_with_sync_false() -> None:
    text = RENDER_YAML.read_text()
    assert re.search(r"- key: NTFY_TOPIC_URL\n\s+sync: false", text)
    assert text.index("GOOGLE_SITE_VERIFICATION") < text.index("NTFY_TOPIC_URL")
    assert "# Set by hand on Render: the owner's private ntfy topic address" in text


def test_setting_is_empty_when_the_variable_is_unset_or_blank() -> None:
    assert _setting_in_fresh_process() == ""
    assert _setting_in_fresh_process(NTFY_TOPIC_URL="") == ""
    assert _setting_in_fresh_process(NTFY_TOPIC_URL="   ") == ""


def test_setting_is_read_without_surrounding_spaces() -> None:
    assert _setting_in_fresh_process(NTFY_TOPIC_URL=" https://ntfy.sh/x ") == "https://ntfy.sh/x"


def test_mock_helper_returns_an_integer_status(mocker: MockerFixture) -> None:
    mock = _mock_urlopen(mocker, status=200)
    manager: Any = mock.return_value
    with manager as response:
        assert response.status == 200
        assert response.headers is not None
