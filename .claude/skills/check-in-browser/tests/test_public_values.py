"""Tests of the allow list of public contact numbers (public_values.txt), without a browser.

Run: uv run pytest .claude/skills/check-in-browser/tests --no-cov -q
"""

from importlib import util
from pathlib import Path
from types import ModuleType

import pytest

SKILL = Path(__file__).resolve().parents[1]


def load() -> ModuleType:
    spec = util.spec_from_file_location("browser_check", SKILL / "browser_check.py")
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load()
OTHER_PHONE = "+84 912 345 678"


def test_public_values_file_lists_the_owner_number_and_allows_comments() -> None:
    lines = (SKILL / "public_values.txt").read_text(encoding="utf-8").splitlines()
    values = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    assert values == ["0945 384 500"]
    assert any(line.startswith("#") for line in lines)


def test_loader_skips_comments_and_blank_lines(tmp_path: Path) -> None:
    listed = tmp_path / "public_values.txt"
    listed.write_text("# public numbers\n\n0945 384 500\n  # indented comment\n", encoding="utf-8")
    assert CHECK.load_public_numbers(listed) == frozenset({"0945384500"})


def test_loader_returns_nothing_when_the_file_is_missing(tmp_path: Path) -> None:
    assert CHECK.load_public_numbers(tmp_path / "absent.txt") == frozenset()


@pytest.mark.parametrize(
    "written",
    [
        "0945 384 500",
        "+84 945 384 500",
        "84945384500",
        "tel:+84945384500",
        "0945.384.500",
        "0945-384-500",
    ],
)
def test_listed_number_in_any_spelling_is_not_a_finding(written: str) -> None:
    text = f"Call me on {written} any time"
    assert CHECK.phone_numbers(text) == []
    assert "phone number" not in CHECK.scan_text(text)


def test_other_numbers_are_still_reported() -> None:
    text = f"Call 0945 384 500 or {OTHER_PHONE}"
    assert CHECK.phone_numbers(text) == [OTHER_PHONE]
    assert "phone number" in CHECK.scan_text(text)


def test_landline_is_still_reported() -> None:
    assert CHECK.scan_text("Call (028) 3822 1234") == ["phone number"]


def test_redact_keeps_the_listed_number_and_hides_others() -> None:
    cleaned = CHECK.redact(f"Call +84 945 384 500 or {OTHER_PHONE}")
    assert cleaned == "Call +84 945 384 500 or [redacted]"


def test_stored_logs_keep_the_listed_number() -> None:
    stored = CHECK.redact("tel:+84945384500 failed")
    assert stored == "tel:+84945384500 failed"
    assert CHECK.scan_text(stored) == []
    step = {"name": "contact", "masking_findings": CHECK.scan_text("Zalo 0945 384 500")}
    assert CHECK.masking_of([step]) == {"status": "clean", "findings": []}


def test_explicit_allow_list_overrides_the_file() -> None:
    assert CHECK.phone_numbers("Call 0945 384 500", public=frozenset()) == ["0945 384 500"]
    assert CHECK.phone_numbers(f"Call {OTHER_PHONE}", public=frozenset({"0912345678"})) == []
