from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate import evaluate_cached
from tools.agent_change_gate_git import GitIndex
from tools.agent_change_gate_models import (
    parse_change_gate,
    parse_manifest,
    parse_record_metadata,
)


VALID_GATE = """\
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: checked
"""

VALID_RECORD = """\
# Result

record:
  date: 2026-07-10
  topic: focused-gate-test
  tags: test, harness
  memory_review: no-change
  memory_reason: existing memory is sufficient

""" + VALID_GATE


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
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


def _stage_record(
    repo: Path,
    name: str = "2026-07-10-focused-gate-test.md",
    text: str = VALID_RECORD,
    *,
    with_index: bool = True,
) -> str:
    path = f"result_reports/records/2026-07/{name}"
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    _git(repo, "add", path)
    if with_index:
        index = repo / "result_reports/REPORT_INDEX.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(
            f"| {chr(96)}{path}{chr(96)} |\n",
            encoding="utf-8",
        )
        _git(repo, "add", "result_reports/REPORT_INDEX.md")
    return path


def _findings(repo: Path) -> list[tuple[str, str]]:
    return [
        (item.severity, item.message)
        for item in evaluate_cached(GitIndex(repo))
    ]


def _messages(repo: Path, severity: str | None = None) -> list[str]:
    return [
        item.message
        for item in evaluate_cached(GitIndex(repo))
        if severity is None or item.severity == severity
    ]


def test_record_change_gate_and_manifest_parsers_validate_closed_schemas() -> None:
    metadata = parse_record_metadata(VALID_RECORD)
    assert metadata.memory_review == "no-change"
    gate = parse_change_gate(VALID_RECORD)
    assert gate.new_source == "split"
    with pytest.raises(ValueError, match="exactly"):
        parse_change_gate(VALID_GATE + "  code_map_check: checked\n")
    with pytest.raises(ValueError, match="exactly"):
        parse_change_gate(VALID_GATE + "  report_exemption: none\n")
    with pytest.raises(ValueError, match="exactly"):
        parse_record_metadata(VALID_RECORD.replace("  tags:", "  extra: x\n  tags:"))

    manifest = parse_manifest(
        """\
allowed_paths:
  - tools/existing.py
report_path: result_reports/records/2026-07/2026-07-10-focused-gate-test.md
"""
    )
    assert manifest.allowed_paths == ("tools/existing.py",)
    assert manifest.report_path == (
        "result_reports/records/2026-07/2026-07-10-focused-gate-test.md"
    )
    with pytest.raises(ValueError, match="unknown manifest"):
        parse_manifest(
            "allowed_paths:\n"
            "  - tools/existing.py\n"
            "report_exemption:\n"
            "  reason: status-only\n"
        )


def test_ordinary_tool_change_does_not_require_report(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")

    assert not _findings(repo)


def test_structural_change_without_report_is_warning_first(repo: Path) -> None:
    target = repo / "tools/new_helper.py"
    target.write_text("def helper():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "tools/new_helper.py")

    findings = _findings(repo)
    assert not [item for item in findings if item[0] == "error"]
    assert any("reuse/commonization" in message for _, message in findings)


def test_new_record_requires_staged_index(repo: Path) -> None:
    _stage_record(repo, with_index=False)

    assert any("REPORT_INDEX.md update" in message for message in _messages(repo, "error"))


def test_valid_new_record_is_accepted(repo: Path) -> None:
    _stage_record(repo)

    assert not _messages(repo, "error")


def test_record_reads_staged_blob_not_worktree(repo: Path) -> None:
    path = _stage_record(repo)
    (repo / path).write_text("record:\n  invalid: worktree only\n", encoding="utf-8")

    assert not _messages(repo, "error")


def test_result_records_are_append_only(repo: Path) -> None:
    path = _stage_record(repo)
    _git(repo, "commit", "-qm", "add record")
    target = repo / path
    target.write_text(VALID_RECORD + "\ncorrection in place\n", encoding="utf-8")
    _git(repo, "add", path)

    assert any("append-only" in message for message in _messages(repo, "error"))


def test_memory_update_requires_staged_seed(repo: Path) -> None:
    updated = VALID_RECORD.replace(
        "memory_review: no-change",
        "memory_review: updated",
    )
    _stage_record(repo, text=updated)
    assert any("requires the staged memory seed" in message for message in _messages(repo, "error"))

    seed = repo / "result_reports/memory/project_memory_seed.md"
    seed.parent.mkdir(parents=True, exist_ok=True)
    seed.write_text("# Memory\n", encoding="utf-8")
    _git(repo, "add", "result_reports/memory/project_memory_seed.md")
    assert not any("requires the staged memory seed" in message for message in _messages(repo, "error"))


def test_record_path_and_date_must_match(repo: Path) -> None:
    _stage_record(repo, name="2026-07-11-wrong-date.md")

    assert any("date must match" in message for message in _messages(repo, "error"))


@pytest.mark.parametrize(
    ("line_count", "severity", "expected"),
    [
        (300, "warning", "split or justify"),
        (351, "error", "exceeds 350 LOC"),
    ],
)
def test_new_production_source_loc_policy(
    repo: Path,
    line_count: int,
    severity: str,
    expected: str,
) -> None:
    app = repo / "apps/new_feature.py"
    app.parent.mkdir()
    app.write_text(
        "\n".join(f"VALUE_{i} = {i}" for i in range(line_count)) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "apps/new_feature.py")

    assert any(expected in message for message in _messages(repo, severity))


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

    assert any("hotspot net +40 LOC" in message for message in _messages(repo, "warning"))
    assert not _messages(repo, "error")


def test_manifest_still_limits_staged_scope(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")
    git_dir = repo / _git(repo, "rev-parse", "--git-dir").strip()
    (git_dir / "agent_task_manifest.yml").write_text(
        "allowed_paths:\n"
        "  - docs/not-staged.md\n",
        encoding="utf-8",
    )

    assert any("staged paths not allowed" in message for message in _messages(repo, "error"))


def test_docs_only_change_has_no_findings(repo: Path) -> None:
    docs = repo / "docs/note.md"
    docs.parent.mkdir()
    docs.write_text("docs only\n", encoding="utf-8")
    _git(repo, "add", "docs/note.md")

    assert not _findings(repo)
