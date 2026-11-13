"""A step with a close-up shows only the close-up; a step without one shows its full page.

Run: uv run pytest .flow/plugin/skills/build-verify-report/tests --no-cov -q
"""

import base64
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any

SKILL = Path(__file__).resolve().parents[1]


def load() -> ModuleType:
    spec = util.spec_from_file_location("build_report_close_ups", SKILL / "build_report.py")
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load()


def image(folder: Path, name: str, content: bytes) -> tuple[str, str]:
    path = folder / name
    path.write_bytes(content)
    return str(path), base64.b64encode(content).decode()


def report(shots: list[str], close_ups: dict[str, str]) -> dict[str, Any]:
    return {
        "title": "t",
        "verdict": "PASS",
        "branch": "b",
        "commit": "c",
        "date": "d",
        "axes": [],
        "screenshots": shots,
        "close_ups": close_ups,
    }


def test_captured_step_shows_only_its_close_up(tmp_path: Path) -> None:
    full, full_data = image(tmp_path, "01-home.png", b"full-page-bytes")
    close, close_data = image(tmp_path, "01-home-element.png", b"close-up-bytes")

    body = BUILD.render_body(report([full], {full: close}))

    assert close_data in body
    assert full_data not in body
    assert body.count("<img") == 2  # the close-up and the empty lightbox image
    assert "<figcaption>01-home</figcaption>" in body


def test_step_without_capture_shows_its_full_page(tmp_path: Path) -> None:
    full, full_data = image(tmp_path, "02-faq.png", b"only-full-page")

    body = BUILD.render_body(report([full], {}))

    assert full_data in body
    assert "<figcaption>02-faq</figcaption>" in body
