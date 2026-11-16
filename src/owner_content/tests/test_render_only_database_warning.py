"""The missing-DATABASE_URL warning fires only on Render (the variable RENDER is set)."""

import pytest
from pytest_django import Settings

from owner_content.checks import W001_MESSAGE, database_url_is_set


def _no_database_value(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    settings.DEBUG = False
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DJANGO_DB_NAME", raising=False)


def test_debug_off_without_database_value_on_render_warns(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    _no_database_value(settings, monkeypatch)
    monkeypatch.setenv("RENDER", "true")

    (warning,) = database_url_is_set(None)

    assert warning.id == "config.W001"
    assert warning.msg == W001_MESSAGE


@pytest.mark.parametrize("render", [None, "", "  "])
def test_debug_off_without_database_value_off_render_does_not_warn(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, render: str | None
) -> None:
    _no_database_value(settings, monkeypatch)
    if render is None:
        monkeypatch.delenv("RENDER", raising=False)
    else:
        monkeypatch.setenv("RENDER", render)

    assert database_url_is_set(None) == []
