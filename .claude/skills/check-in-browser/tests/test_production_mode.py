"""With --debug-off the app runs locally as in production: plain http and prepared style files.

Run: uv run pytest .claude/skills/check-in-browser/tests --no-cov -q
"""

from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SKILL = Path(__file__).resolve().parents[1]


def load() -> ModuleType:
    spec = util.spec_from_file_location("browser_check_production", SKILL / "browser_check.py")
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load()


class FakeProcess:
    pass


def commands(monkeypatch: pytest.MonkeyPatch, debug: bool) -> list[tuple[list[str], Any]]:
    """Every command start_app runs, in order; the server is the last one."""
    calls: list[tuple[list[str], Any]] = []
    monkeypatch.delenv("DJANGO_SECURE_SSL_REDIRECT", raising=False)
    monkeypatch.setattr(CHECK.subprocess, "run", lambda args, **kw: calls.append((args, kw)))
    monkeypatch.setattr(
        CHECK.subprocess, "Popen", lambda args, **kw: calls.append((args, kw)) or FakeProcess()
    )
    CHECK.start_app(Path("."), Path("db.sqlite3"), 8123, debug=debug)
    return calls


def manage(args: list[str]) -> str:
    return args[2]


def test_debug_off_switches_the_https_redirect_off() -> None:
    env = CHECK.app_env(Path("db.sqlite3"), debug=False)
    assert env["DJANGO_SECURE_SSL_REDIRECT"] == "0"


def test_debug_off_prepares_the_style_files_before_the_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = commands(monkeypatch, debug=False)
    names = [manage(args) for args, _ in calls]
    assert "collectstatic" in names
    assert names.index("collectstatic") < names.index("runserver")
    collect = calls[names.index("collectstatic")][0]
    assert "--noinput" in collect
    assert all(kw["env"]["DJANGO_SECURE_SSL_REDIRECT"] == "0" for _, kw in calls)


def test_debug_off_leaves_the_collected_files_to_whitenoise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = commands(monkeypatch, debug=False)[-1][0]
    assert "--nostatic" in server


def test_debug_on_changes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = commands(monkeypatch, debug=True)
    assert [manage(args) for args, _ in calls] == ["migrate", "runserver"]
    assert "--nostatic" not in calls[-1][0]
    assert all("DJANGO_SECURE_SSL_REDIRECT" not in kw["env"] for _, kw in calls)
    assert "DJANGO_SECURE_SSL_REDIRECT" not in CHECK.app_env(Path("db.sqlite3"), debug=True)
