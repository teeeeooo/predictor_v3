"""Focused staged-index tests for the UI magic-literal gate."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate import evaluate_cached
from tools.agent_change_gate_git import GitIndex

VALID_GATE = """\
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
"""


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "ui-gate@example.invalid")
    _git(tmp_path, "config", "user.name", "UI Gate Test")
    baseline = tmp_path / "README.md"
    baseline.write_text("baseline\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    return tmp_path


def _stage(repo: Path, path: str, source: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    _git(repo, "add", path)


def _stage_report(repo: Path, gate: str = VALID_GATE) -> None:
    _stage(repo, "result_reports/active/500_ui_gate.md", gate)


def _errors(repo: Path) -> list[str]:
    return [
        f"{item.path}: {item.message}"
        for item in evaluate_cached(GitIndex(repo))
        if item.severity == "error"
    ]


def test_row_header_literal_in_production_ui_is_rejected(repo: Path) -> None:
    _stage(
        repo,
        "apps/calculator/ui/new_surface.py",
        "def build(table):\n    return table(row_header_chars=18)\n",
    )
    _stage_report(repo)

    assert any("row_header_chars" in error for error in _errors(repo))


def test_layout_token_owner_accepts_literal_definitions(repo: Path) -> None:
    _stage(
        repo,
        "apps/calculator/ui/layout_constants.py",
        'TABLE_ROW_HEADER_CHARS = 18\nTABLE_BG = "#A1B2C3"\n',
    )
    _stage_report(repo)

    assert not _errors(repo)


def test_color_literal_in_production_ui_is_rejected(repo: Path) -> None:
    _stage(repo, "apps/calculator/ui/view.py", 'BACKGROUND = "#A1B2C3"\n')
    _stage_report(repo)

    assert any("color" in error for error in _errors(repo))


@pytest.mark.parametrize(
    ("path", "source"),
    (
        ("core/domain_constants.py", "DEFROST_TEST_MINUTES = 90\n"),
        ("tests/test_calculation.py", "EXPECTED_CAPACITY = 18000\n"),
    ),
)
def test_domain_constant_and_calculation_test_are_not_blocked(
    repo: Path, path: str, source: str
) -> None:
    _stage(repo, path, source)
    _stage_report(repo)

    assert not _errors(repo)


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("min_size = (1180, 420)\n", "window min_size"),
        ("Dialog(parent, min_size=(1180, 420))\n", "window min_size"),
        (
            "class Dialog:\n"
            "    @property\n"
            "    def min_size(self):\n"
            "        return (1180, 420)\n",
            "window min_size",
        ),
        ('root.geometry("800x600")\n', "window geometry"),
        ("table(data_column_chars=14)\n", "data_column_chars"),
    ),
)
def test_other_phase_one_ui_literals_are_rejected(
    repo: Path, source: str, expected: str
) -> None:
    _stage(repo, "apps/calculator/ui/view.py", source)
    _stage_report(repo)

    assert any(expected in error for error in _errors(repo))


def test_checker_reads_staged_blob_not_worktree(repo: Path) -> None:
    path = "apps/calculator/ui/view.py"
    _stage(repo, path, "TOKEN = TABLE_ROW_HEADER_CHARS\n")
    (repo / path).write_text("table(row_header_chars=18)\n", encoding="utf-8")
    _stage_report(repo)

    assert not _errors(repo)


def test_structured_report_exemption_allows_reviewed_literal(repo: Path) -> None:
    _stage(repo, "apps/calculator/ui/view.py", 'BACKGROUND = "#A1B2C3"\n')
    _stage_report(
        repo,
        VALID_GATE.replace(
            "ui_literal_exemption: none",
            "ui_literal_exemption: approved-for-slice",
        ),
    )

    assert not _errors(repo)
