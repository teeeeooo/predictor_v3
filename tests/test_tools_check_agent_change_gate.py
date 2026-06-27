from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate import evaluate_cached
from tools.agent_change_gate_git import GitIndex
from tools.agent_change_gate_models import parse_change_gate, parse_manifest


VALID_GATE = """\
# Result

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
"""


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


def _stage_report(repo: Path, name: str = "500_gate.md", text: str = VALID_GATE) -> str:
    path = f"result_reports/active/{name}"
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    _git(repo, "add", path)
    return path


def _messages(repo: Path) -> list[str]:
    return [item.message for item in evaluate_cached(GitIndex(repo))]


def _findings(repo: Path) -> list[tuple[str, str]]:
    return [
        (item.severity, item.message)
        for item in evaluate_cached(GitIndex(repo))
    ]


def test_change_gate_and_manifest_parsers_validate_closed_schemas() -> None:
    gate = parse_change_gate(VALID_GATE)
    assert gate.new_source == "split"
    with pytest.raises(ValueError, match="exactly"):
        parse_change_gate(VALID_GATE + "  extra: value\n")

    manifest = parse_manifest(
        """\
allowed_paths:
  - tools/existing.py
report_exemption:
  reason: user-approved-formatting-only
  scope: formatting-only
  approved_by_user: true
"""
    )
    assert manifest.allowed_paths == ("tools/existing.py",)
    with pytest.raises(ValueError, match="literal"):
        parse_manifest(
            "allowed_paths:\n  - tools/*.py\nreport_exemption:\n"
            "  reason: status-only\n  scope: status\n  approved_by_user: true\n"
        )


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "allowed_paths:\n  - tools/existing.py\nunknown: value\n",
            "unknown manifest top-level field",
        ),
        (
            "allowed_paths:\n  - tools/existing.py\nreport_exemption:\n  typo: value\n",
            "unknown report_exemption field",
        ),
        (
            "allowed_paths:\n  - tools/existing.py\n  report_path: report.md\n",
            "invalid manifest field placement",
        ),
        (
            "allowed_paths:\n  - tools/existing.py\nreport_exemption:\n"
            "  reason: status-only\n  scope: status\n  approved_by_user: TRUE\n",
            "approved_by_user: true",
        ),
    ],
)
def test_manifest_rejects_unknown_or_ambiguously_placed_fields(source: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_manifest(source)


def test_relevant_change_requires_staged_active_report(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", str(target.relative_to(repo)))

    assert any("requires one active report" in message for message in _messages(repo))

    report = repo / "result_reports/active/unstaged.md"
    report.parent.mkdir(parents=True)
    report.write_text(VALID_GATE, encoding="utf-8")
    assert any("requires one active report" in message for message in _messages(repo))


def test_gate_reads_staged_report_blob_not_worktree(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")
    report_path = _stage_report(repo)
    (repo / report_path).write_text("change_gate:\n  invalid: worktree-only\n", encoding="utf-8")

    assert not [item for item in evaluate_cached(GitIndex(repo)) if item.severity == "error"]


def test_source_policy_reads_staged_blob_not_larger_worktree_file(repo: Path) -> None:
    target = repo / "apps/new_feature.py"
    target.parent.mkdir()
    staged = "\n".join(f"VALUE_{i} = {i}" for i in range(240)) + "\n"
    target.write_text(staged, encoding="utf-8")
    _git(repo, "add", "apps/new_feature.py")
    working = "\n".join(f"VALUE_{i} = {i}" for i in range(360)) + "\n"
    target.write_text(working, encoding="utf-8")
    _stage_report(repo, text=VALID_GATE.replace("new_source: split", "new_source: small"))

    assert not [item for item in evaluate_cached(GitIndex(repo)) if item.severity == "error"]


def test_multiple_reports_require_manifest_selection(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")
    selected = _stage_report(repo, "500_first.md")
    second = _stage_report(repo, "501_second.md")
    assert any("multiple staged reports" in message for message in _messages(repo))

    git_dir = Path(_git(repo, "rev-parse", "--git-dir").strip())
    if not git_dir.is_absolute():
        git_dir = repo / git_dir
    (git_dir / "agent_task_manifest.yml").write_text(
        "allowed_paths:\n"
        "  - tools/existing.py\n"
        f"  - {selected}\n"
        f"  - {second}\n"
        f"report_path: {selected}\n"
        "report_exemption:\n"
        "  reason: status-only\n"
        "  scope: report-selection\n"
        "  approved_by_user: true\n",
        encoding="utf-8",
    )
    assert not [item for item in evaluate_cached(GitIndex(repo)) if item.severity == "error"]


def test_manifest_rejects_staged_paths_outside_literal_allowlist(repo: Path) -> None:
    target = repo / "tools/existing.py"
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "tools/existing.py")
    report_path = _stage_report(repo)
    git_dir = repo / _git(repo, "rev-parse", "--git-dir").strip()
    (git_dir / "agent_task_manifest.yml").write_text(
        f"allowed_paths:\n  - {report_path}\n"
        f"report_path: {report_path}\n"
        "report_exemption:\n  reason: status-only\n"
        "  scope: report-selection\n  approved_by_user: true\n",
        encoding="utf-8",
    )

    assert any("staged paths not allowed" in message for message in _messages(repo))


@pytest.mark.parametrize(
    ("line_count", "expected"),
    [(300, "requires split/justified"), (351, "exceeds 350 LOC")],
)
def test_new_production_source_loc_policy(repo: Path, line_count: int, expected: str) -> None:
    app = repo / "apps/new_feature.py"
    app.parent.mkdir()
    app.write_text("\n".join(f"VALUE_{i} = {i}" for i in range(line_count)) + "\n", encoding="utf-8")
    _git(repo, "add", "apps/new_feature.py")
    _stage_report(repo, text=VALID_GATE.replace("new_source: split", "new_source: small"))

    assert any(expected in message for message in _messages(repo))


def test_hotspot_growth_requires_explicit_decision(repo: Path) -> None:
    hotspot = repo / "apps/hotspot.py"
    hotspot.parent.mkdir()
    hotspot.write_text("\n".join(f"BASE_{i} = {i}" for i in range(401)) + "\n", encoding="utf-8")
    _git(repo, "add", "apps/hotspot.py")
    _git(repo, "commit", "-qm", "add hotspot")
    with hotspot.open("a", encoding="utf-8") as stream:
        stream.write("\n".join(f"ADDED_{i} = {i}" for i in range(40)) + "\n")
    _git(repo, "add", "apps/hotspot.py")
    _stage_report(repo, text=VALID_GATE.replace("accepted-for-slice", "none"))

    assert any("hotspot net +40 LOC" in message for message in _messages(repo))


def test_structural_source_requires_reuse_commonization_decision(repo: Path) -> None:
    target = repo / "tools" / "new_helper.py"
    target.write_text("def helper():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "tools/new_helper.py")
    _stage_report(
        repo,
        text=VALID_GATE.replace(
            "reuse_commonization: checked",
            "reuse_commonization: not_required",
        ),
    )

    assert any(
        "requires reuse_commonization decision" in message for message in _messages(repo)
    )


def test_docs_only_change_does_not_require_reuse_commonization_decision(repo: Path) -> None:
    docs = repo / "docs" / "note.md"
    docs.parent.mkdir()
    docs.write_text("docs only\n", encoding="utf-8")
    _git(repo, "add", "docs/note.md")

    assert not _findings(repo)
