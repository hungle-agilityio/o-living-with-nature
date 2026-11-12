"""A lasting database and the owner's sign-in (owner-content AC1 to AC6)."""

import os
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from config.settings import BASE_DIR, database_config
from owner_content.checks import W001_MESSAGE, database_url_is_set

ROOT = Path(__file__).resolve().parents[3]
# A fake address: nothing ever connects to it.
FAKE_POSTGRES = "postgres://owner:not-a-real-secret@db.example.invalid:5432/oliving"
PASSWORD = "a-long-enough-pass"
# Address, status and query count: `/` reads the site settings (one-page AC5), the old addresses
# redirect to their chapter (one-page AC3).
PUBLIC_ADDRESSES = [
    ("/", 200, 1),
    ("/house/", 301, 0),
    ("/hoa-xuan/", 301, 0),
    ("/faq/", 301, 0),
    ("/contact/", 301, 0),
    ("/sitemap.xml", 200, 0),
    ("/robots.txt", 200, 0),
]
UNKNOWN_ADDRESS = "/this-page-does-not-exist/"


# AC1


@pytest.mark.parametrize("scheme", ["postgres", "postgresql"])
def test_database_url_gives_postgres_with_kept_connections_and_ssl(scheme: str) -> None:
    config = database_config({"DATABASE_URL": FAKE_POSTGRES.replace("postgres", scheme, 1)})

    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["NAME"] == "oliving"
    assert config["USER"] == "owner"
    assert config["HOST"] == "db.example.invalid"
    assert config["PORT"] == 5432
    assert config["CONN_MAX_AGE"] == 600
    assert config["OPTIONS"]["sslmode"] == "require"


def test_database_url_wins_over_the_sqlite_name() -> None:
    config = database_config({"DATABASE_URL": FAKE_POSTGRES, "DJANGO_DB_NAME": "/tmp/x.sqlite3"})

    assert config["ENGINE"] == "django.db.backends.postgresql"


def test_database_url_that_is_not_postgres_does_not_ask_for_ssl() -> None:
    config = database_config({"DATABASE_URL": "sqlite:////tmp/o-living-check.sqlite3"})

    assert config["ENGINE"] == "django.db.backends.sqlite3"
    assert config["CONN_MAX_AGE"] == 600
    assert "sslmode" not in config.get("OPTIONS", {})


def test_without_database_url_sqlite_uses_the_given_name() -> None:
    config = database_config({"DJANGO_DB_NAME": "/tmp/o-living-check.sqlite3"})

    assert config == {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/o-living-check.sqlite3",
    }


@pytest.mark.parametrize("environ", [{}, {"DATABASE_URL": "", "DJANGO_DB_NAME": ""}])
def test_without_database_url_or_name_sqlite_uses_db_sqlite3(environ: dict[str, str]) -> None:
    config = database_config(environ)

    assert config == {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}


def _manage(*arguments: str, **extra: str) -> subprocess.CompletedProcess[str]:
    """Run manage.py in a fresh process: the settings are read once per process."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_") and key not in {"DATABASE_URL", "PYTHONPATH"}
    }
    env.update(extra)
    return subprocess.run(
        [sys.executable, "manage.py", *arguments],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_settings_take_the_database_from_the_environment() -> None:
    probe = (
        "from django.conf import settings; d = settings.DATABASES['default']; "
        "print(d['ENGINE'], d['HOST'], d['CONN_MAX_AGE'], d['OPTIONS']['sslmode'])"
    )

    done = _manage("shell", "-c", probe, DATABASE_URL=FAKE_POSTGRES)

    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().splitlines()[-1] == (
        "django.db.backends.postgresql db.example.invalid 600 require"
    )


def test_both_dependencies_are_declared_and_locked() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")

    assert '"dj-database-url' in pyproject
    assert '"psycopg[binary]' in pyproject
    for package in ("dj-database-url", "psycopg", "psycopg-binary"):
        assert f'name = "{package}"' in lock, package


# AC2


def test_warning_text_is_the_one_of_the_spec() -> None:
    assert W001_MESSAGE == (
        "DATABASE_URL is not set: on Render the SQLite file is wiped on every deploy "
        "and the owner's settings are lost."
    )


def test_debug_off_without_any_database_value_warns(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings.DEBUG = False
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DJANGO_DB_NAME", raising=False)

    (warning,) = database_url_is_set(None)

    assert warning.id == "config.W001"
    assert warning.msg == W001_MESSAGE
    assert warning.is_serious() is False


def test_database_url_of_spaces_only_counts_as_not_set_and_warns(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings.DEBUG = False
    monkeypatch.setenv("DATABASE_URL", "  ")
    monkeypatch.delenv("DJANGO_DB_NAME", raising=False)

    assert database_config({"DATABASE_URL": "  "})["ENGINE"] == "django.db.backends.sqlite3"
    assert [warning.id for warning in database_url_is_set(None)] == ["config.W001"]


@pytest.mark.parametrize(
    ("debug", "name", "value"),
    [
        (True, None, None),
        (False, "DATABASE_URL", FAKE_POSTGRES),
        (False, "DJANGO_DB_NAME", "/tmp/o-living-check.sqlite3"),
    ],
)
def test_debug_on_or_either_value_set_does_not_warn(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    debug: bool,
    name: str | None,
    value: str | None,
) -> None:
    settings.DEBUG = debug
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DJANGO_DB_NAME", raising=False)
    if name and value:
        monkeypatch.setenv(name, value)

    assert database_url_is_set(None) == []


def test_manage_check_shows_the_warning_and_still_passes() -> None:
    done = _manage("check", DJANGO_DEBUG="0", DJANGO_SECRET_KEY="only-for-this-test")

    assert done.returncode == 0, done.stderr
    assert f"(config.W001) {W001_MESSAGE}" in done.stderr


def test_manage_check_is_quiet_with_debug_on() -> None:
    done = _manage("check")

    assert done.returncode == 0, done.stderr
    assert "config.W001" not in done.stderr + done.stdout


# AC3


@pytest.mark.django_db
def test_owner_address_sends_a_signed_out_visitor_to_the_sign_in_page(client: Client) -> None:
    response = client.get("/owner/")

    assert response.status_code == 302
    assert response["Location"] == "/owner/login/?next=/owner/"

    page = client.get("/owner/login/")

    assert page.status_code == 200
    html = page.content.decode()
    assert "Ở admin" in html
    assert re.search(r"<title>[^<]*Ở admin\s*</title>", html)
    assert 'name="password"' in html


@pytest.mark.django_db
@pytest.mark.parametrize("address", ["/admin/", "/admin/login/"])
def test_default_admin_address_is_not_found(
    client: Client, settings: Settings, address: str
) -> None:
    settings.DEBUG = False

    assert client.get(address).status_code == 404


def test_admin_titles() -> None:
    assert admin.site.site_header == "Ở admin"
    assert admin.site.site_title == "Ở admin"
    assert admin.site.index_title == "Site administration"


@pytest.mark.django_db
def test_owner_signs_in_and_sees_the_admin_index(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OWNER_USERNAME", "bun")
    monkeypatch.setenv("OWNER_PASSWORD", PASSWORD)
    call_command("ensure_owner", stdout=StringIO())

    assert client.login(username="bun", password=PASSWORD)
    response = client.get("/owner/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Ở admin" in html
    assert "Site administration" in html


# AC4


def _ensure_owner(
    monkeypatch: pytest.MonkeyPatch, username: str | None, password: str | None
) -> tuple[str, int]:
    """Run the command with these two values; give what it printed and its exit code."""
    for name, value in (("OWNER_USERNAME", username), ("OWNER_PASSWORD", password)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    out, err = StringIO(), StringIO()
    code = 0
    try:
        call_command("ensure_owner", stdout=out, stderr=err)
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else 1
    return out.getvalue() + err.getvalue(), code


@pytest.mark.django_db
def test_ensure_owner_creates_a_superuser(monkeypatch: pytest.MonkeyPatch) -> None:
    printed, code = _ensure_owner(monkeypatch, "bun", PASSWORD)

    assert (printed, code) == ("owner ready: created\n", 0)
    user = User.objects.get(username="bun")
    assert user.is_superuser and user.is_staff and user.is_active
    assert user.check_password(PASSWORD)
    assert user.password != PASSWORD  # stored hashed, never as typed


@pytest.mark.django_db
def test_ensure_owner_sets_the_password_of_an_existing_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    User.objects.create_superuser(username="bun", password="the-old-password-1")

    printed, code = _ensure_owner(monkeypatch, "bun", PASSWORD)

    assert (printed, code) == ("owner ready: password updated\n", 0)
    assert User.objects.count() == 1
    assert User.objects.get(username="bun").check_password(PASSWORD)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("username", "password"),
    [(None, None), ("bun", None), (None, PASSWORD), ("", PASSWORD), ("bun", ""), ("", "")],
)
def test_ensure_owner_skips_when_a_value_is_empty_or_missing(
    monkeypatch: pytest.MonkeyPatch, username: str | None, password: str | None
) -> None:
    printed, code = _ensure_owner(monkeypatch, username, password)

    assert printed == "owner skipped: OWNER_USERNAME and OWNER_PASSWORD are not set\n"
    assert code == 0
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_ensure_owner_refuses_a_short_password_and_creates_nobody(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    printed, code = _ensure_owner(monkeypatch, "bun", "elevenchars")

    assert printed == "owner not ready: OWNER_PASSWORD needs at least 12 characters\n"
    assert code == 1
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_ensure_owner_refuses_a_short_password_and_keeps_the_old_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    User.objects.create_superuser(username="bun", password="the-old-password-1")

    printed, code = _ensure_owner(monkeypatch, "bun", "elevenchars")

    assert code == 1
    assert "owner not ready" in printed
    assert User.objects.get(username="bun").check_password("the-old-password-1")


@pytest.mark.django_db
def test_ensure_owner_accepts_a_password_of_exactly_12_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    printed, code = _ensure_owner(monkeypatch, "bun", "twelve-chars")

    assert (printed, code) == ("owner ready: created\n", 0)


@pytest.mark.django_db
@pytest.mark.parametrize("password", [PASSWORD, "elevenchars"])
def test_ensure_owner_never_prints_the_password(
    monkeypatch: pytest.MonkeyPatch, password: str
) -> None:
    first, _code = _ensure_owner(monkeypatch, "bun", password)
    second, _code = _ensure_owner(monkeypatch, "bun", password)

    assert password not in first + second


# AC5


def _render_yaml() -> str:
    return (ROOT / "render.yaml").read_text(encoding="utf-8")


def test_render_start_command_migrates_then_ensures_the_owner_then_serves() -> None:
    (command,) = re.findall(r"^\s*startCommand:\s*(.+)$", _render_yaml(), re.MULTILINE)

    steps = [step.strip() for step in command.split("&&")]

    # `&&` stops at the first step that fails, so gunicorn starts only after both passed.
    assert len(steps) == 3
    assert steps[0].endswith("manage.py migrate --noinput")
    assert steps[1].endswith("manage.py ensure_owner")
    assert "gunicorn" in steps[2]
    assert ";" not in command and "||" not in command


@pytest.mark.parametrize("key", ["DATABASE_URL", "OWNER_USERNAME", "OWNER_PASSWORD"])
def test_render_env_vars_are_set_by_hand_on_render(key: str) -> None:
    assert re.search(rf"^\s*- key: {key}\n\s*sync: false$", _render_yaml(), re.MULTILINE)


def _environment_variables_section() -> str:
    """The section "Environment variables" of docs/architecture.md, up to the next heading."""
    text = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    (section,) = re.findall(r"^## Environment variables\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return str(section)


@pytest.mark.parametrize("key", ["DATABASE_URL", "OWNER_USERNAME", "OWNER_PASSWORD"])
def test_architecture_documents_the_variable_without_a_value(key: str) -> None:
    section = _environment_variables_section()
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section.splitlines()
        if line.startswith(f"| `{key}`")
    ]

    # One row per variable: name, purpose, where it is set. No column holds a value.
    ((name, purpose, where),) = rows
    assert name == f"`{key}`"
    assert purpose
    assert "Render" in where
    assert f"{key}=" not in section


# AC6


@pytest.mark.django_db
@pytest.mark.parametrize(("address", "status", "queries"), PUBLIC_ADDRESSES)
def test_public_address_sends_no_cookie_and_asks_the_database_nothing(
    client: Client,
    django_assert_num_queries: DjangoAssertNumQueries,
    address: str,
    status: int,
    queries: int,
) -> None:
    with django_assert_num_queries(queries):
        response = client.get(address)

    assert response.status_code == status
    assert not response.has_header("Set-Cookie")
    assert not response.cookies
    assert not client.cookies


@pytest.mark.django_db
def test_not_found_page_sends_no_cookie_and_asks_the_database_nothing(
    client: Client, settings: Settings, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    settings.DEBUG = False

    with django_assert_num_queries(0):
        response = client.get(UNKNOWN_ADDRESS)

    assert response.status_code == 404
    assert not response.has_header("Set-Cookie")
    assert not response.cookies
    assert not client.cookies
