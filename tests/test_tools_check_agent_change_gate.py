from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate import evaluate_cached
from tools.agent_change_gate_git import GitIndex
from tools.agent_change_gate_models import parse_manifest


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "gate-test@example.invalid")
    _git(tmp_path, "config", "user.name", "Gate Test")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "existing.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    return tmp_path


def _messages(repo: Path, severity: str | None = None) -> list[str]:
    return [
        item.message
        for item in evaluate_cached(GitIndex(repo))
        if severity is None or item.severity == severity
    ]


def test_manifest_parser_keeps_only_local_scope_and_ui_exemption() -> None:
    manifest = parse_manifest(
        "allowed_paths:\n"
        "  - tools/existing.py\n"
        "ui_literal_exemption: approved-for-slice\n"
    )
    assert manifest.allowed_paths == ("tools/existing.py",)
    assert manifest.ui_literal_exemption == "approved-for-slice"

    with pytest.raises(ValueError, match="unknown manifest"):
        parse_manifest(
            "allowed_paths:\n"
            "  - tools/existing.py\n"
            "report_path: result_reports/records/example.md\n"
        )
    with pytest.raises(ValueError, match="literal paths"):
        parse_manifest("allowed_paths:\n  - tools/*.py\n")


def test_ordinary_tool_change_does_not_require_history_record(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")

    assert not _messages(repo, "error")


def test_result_record_paths_are_not_active_checker_contract(repo: Path) -> None:
    record = repo / "result_reports/records/2026-09/2026-09-07-example.md"
    record.parent.mkdir(parents=True)
    record.write_text("historical-style evidence\n", encoding="utf-8")
    _git(repo, "add", str(record.relative_to(repo)))

    assert not _messages(repo)


def test_structural_change_is_warning_first(repo: Path) -> None:
    target = repo / "tools/new_helper.py"
    target.write_text("def helper():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "tools/new_helper.py")

    assert not _messages(repo, "error")
    assert any("reuse/commonization" in message for message in _messages(repo, "warning"))


@pytest.mark.parametrize("line_count", [300, 351])
def test_new_production_source_size_is_warning_only(repo: Path, line_count: int) -> None:
    app = repo / "apps/new_feature.py"
    app.parent.mkdir()
    app.write_text(
        "\n".join(f"VALUE_{i} = {i}" for i in range(line_count)) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "apps/new_feature.py")

    assert not _messages(repo, "error")
    assert any("new production source is" in message for message in _messages(repo, "warning"))


def test_hotspot_growth_is_warning_first(repo: Path) -> None:
    hotspot = repo / "apps/hotspot.py"
    hotspot.parent.mkdir()
    hotspot.write_text(
        "\n".join(f"BASE_{i} = {i}" for i in range(401)) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "apps/hotspot.py")
    _git(repo, "commit", "-qm", "add hotspot")
    with hotspot.open("a", encoding="utf-8") as stream:
        stream.write("\n".join(f"ADDED_{i} = {i}" for i in range(40)) + "\n")
    _git(repo, "add", "apps/hotspot.py")

    assert not _messages(repo, "error")
    assert any("hotspot net +40 LOC" in message for message in _messages(repo, "warning"))


def test_manifest_still_limits_staged_scope(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")
    git_dir = repo / _git(repo, "rev-parse", "--git-dir").strip()
    (git_dir / "agent_task_manifest.yml").write_text(
        "allowed_paths:\n  - docs/not-staged.md\n",
        encoding="utf-8",
    )

    assert any("staged paths not allowed" in message for message in _messages(repo, "error"))


def test_python_syntax_error_remains_hard_failure(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("def broken(:\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")

    assert any("syntax error" in message for message in _messages(repo, "error"))


def test_docs_only_change_has_no_findings(repo: Path) -> None:
    docs = repo / "docs/note.md"
    docs.parent.mkdir()
    docs.write_text("docs only\n", encoding="utf-8")
    _git(repo, "add", "docs/note.md")

    assert not _messages(repo)
