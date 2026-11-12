"""Tests of how the check treats a failed request, without a browser.

Run: uv run pytest .claude/skills/check-in-browser/tests --no-cov -q
"""

from dataclasses import dataclass
from importlib import util
from pathlib import Path
from types import ModuleType

SKILL = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8815/static/media/hero/day.webm"


def load() -> ModuleType:
    spec = util.spec_from_file_location("browser_check", SKILL / "browser_check.py")
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load()


@dataclass
class Request:
    url: str
    resource_type: str
    failure: str | None


def kept(request: Request) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    CHECK.on_request_failed(request, lambda bucket, text: found.append((bucket, text)))
    return found


def test_media_request_the_browser_aborts_is_ignored() -> None:
    assert kept(Request(URL, "media", "net::ERR_ABORTED")) == []


def test_aborted_request_that_is_not_media_is_kept() -> None:
    url = "http://127.0.0.1:8815/static/js/hero.js"
    assert kept(Request(url, "script", "net::ERR_ABORTED")) == [
        ("network_failures", f"failed {url} (net::ERR_ABORTED)")
    ]


def test_media_request_that_failed_for_another_reason_is_kept() -> None:
    assert kept(Request(URL, "media", "net::ERR_CONNECTION_REFUSED")) == [
        ("network_failures", f"failed {URL} (net::ERR_CONNECTION_REFUSED)")
    ]


def test_kept_line_carries_the_reason_or_says_unknown() -> None:
    url = "http://127.0.0.1:8815/static/css/site.css"
    assert kept(Request(url, "stylesheet", None)) == [
        ("network_failures", f"failed {url} (unknown)")
    ]
