"""The "Skill and hook tests" axis runs only the test folders that exist.

Run: uv run pytest .flow/plugin/skills/build-verify-report/tests --no-cov -q
"""

from importlib import util
from pathlib import Path
from types import ModuleType

import pytest

SKILL = Path(__file__).resolve().parents[1]


def load() -> ModuleType:
    spec = util.spec_from_file_location("build_report_axis", SKILL / "build_report.py")
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load()


class Recorder:
    def __init__(self, code: int, out: str) -> None:
        self.code, self.out = code, out
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], root: Path) -> tuple[int, str]:
        self.calls.append(args)
        return self.code, self.out


def plugin(tmp_path: Path, *folders: str) -> Path:
    root = tmp_path / "plugin"
    for folder in folders:
        (root / folder).mkdir(parents=True)
    return root


def test_missing_hook_tests_folder_is_left_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(BUILD, "PLUGIN_ROOT", plugin(tmp_path, "skills"))
    project = tmp_path / "project"
    project.mkdir()
    run = Recorder(0, "3 passed in 0.1s")

    result = BUILD.skill_and_hook_axis(project, run)

    assert result == {
        "name": "Skill and hook tests",
        "status": "PASS",
        "evidence": "3 passed, 0 failed",
    }
    (args,) = run.calls
    assert str(tmp_path / "plugin" / "skills") in args
    assert not any(arg.endswith("hooks/tests") for arg in args)
    assert not any(arg.endswith(".claude/skills") for arg in args)


def test_no_test_folder_at_all_passes_with_a_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(BUILD, "PLUGIN_ROOT", plugin(tmp_path))
    project = tmp_path / "project"
    project.mkdir()
    run = Recorder(4, "ERROR: file or directory not found")

    result = BUILD.skill_and_hook_axis(project, run)

    assert result["status"] == "PASS"
    assert result["evidence"] == "no skill or hook tests found"
    assert run.calls == []


def test_folders_without_any_test_pass_with_a_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(BUILD, "PLUGIN_ROOT", plugin(tmp_path, "skills"))
    run = Recorder(5, "no tests ran in 0.01s")

    result = BUILD.skill_and_hook_axis(tmp_path, run)

    assert result["status"] == "PASS"
    assert result["evidence"] == "no skill or hook tests found"


def test_a_failing_test_still_fails_the_axis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(BUILD, "PLUGIN_ROOT", plugin(tmp_path, "hooks/tests"))
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    run = Recorder(1, "1 failed, 4 passed in 0.3s")

    result = BUILD.skill_and_hook_axis(tmp_path, run)

    assert result["status"] == "FAIL"
    assert result["evidence"] == "4 passed, 1 failed"
    (args,) = run.calls
    assert str(tmp_path / ".claude" / "skills") in args
