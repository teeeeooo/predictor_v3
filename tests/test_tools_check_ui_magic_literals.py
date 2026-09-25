"""Focused staged-index tests for the UI magic-literal gate."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate import evaluate_cached
from tools.agent_change_gate_git import GitIndex

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


def _errors(repo: Path) -> list[str]:
    return [
        f"{item.path}: {item.message}"
        for item in evaluate_cached(GitIndex(repo))
        if item.severity == "error"
    ]


def _warnings(repo: Path) -> list[str]:
    return [
        f"{item.path}: {item.message}"
        for item in evaluate_cached(GitIndex(repo))
        if item.severity == "warning" and item.path != "structure"
    ]


def test_row_header_literal_in_production_ui_is_rejected(repo: Path) -> None:
    _stage(
        repo,
        "apps/calculator/ui/new_surface.py",
        "def build(table):\n    return table(row_header_chars=18)\n",
    )

    assert any("row_header_chars" in error for error in _errors(repo))


def test_layout_token_owner_accepts_literal_definitions(repo: Path) -> None:
    _stage(
        repo,
        "apps/calculator/ui/layout_constants.py",
        'TABLE_ROW_HEADER_CHARS = 18\nTABLE_BG = "#A1B2C3"\n',
    )

    assert not _errors(repo)


def test_color_literal_in_production_ui_is_rejected(repo: Path) -> None:
    _stage(repo, "apps/calculator/ui/view.py", 'BACKGROUND = "#A1B2C3"\n')

    assert any("color" in error for error in _errors(repo))


def test_phase_two_ui_literal_is_warning_only(repo: Path) -> None:
    _stage(repo, "apps/calculator/ui/view.py", "button.configure(width=20, padx=4)\n")

    assert not _errors(repo)
    warnings = _warnings(repo)
    assert any("width" in warning for warning in warnings)
    assert any("padx" in warning for warning in warnings)


def test_phase_two_runtime_sentinel_values_do_not_warn(repo: Path) -> None:
    _stage(
        repo,
        "apps/calculator/ui/view.py",
        "button.configure(width=0, height=1, padx=0, pady=1)\n",
    )

    assert not _errors(repo)
    assert not _warnings(repo)


def test_phase_two_named_color_is_warning_only(repo: Path) -> None:
    _stage(repo, "apps/calculator/ui/view.py", 'label.configure(background="white")\n')

    assert not _errors(repo)
    assert any("named color" in warning for warning in _warnings(repo))


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

    assert any(expected in error for error in _errors(repo))


def test_checker_reads_staged_blob_not_worktree(repo: Path) -> None:
    path = "apps/calculator/ui/view.py"
    _stage(repo, path, "TOKEN = TABLE_ROW_HEADER_CHARS\n")
    (repo / path).write_text("table(row_header_chars=18)\n", encoding="utf-8")

    assert not _errors(repo)


def test_local_manifest_ui_literal_exemption_allows_reviewed_literal(repo: Path) -> None:
    path = "apps/calculator/ui/view.py"
    _stage(repo, path, 'BACKGROUND = "#A1B2C3"\n')
    git_dir = repo / subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (git_dir / "agent_task_manifest.yml").write_text(
        "allowed_paths:\n"
        f"  - {path}\n"
        "ui_literal_exemption: approved-for-slice\n",
        encoding="utf-8",
    )

    assert not _errors(repo)


@pytest.mark.parametrize("root", ("apps/train/ui", "apps/predict/ui"))
def test_pyside_roots_reject_new_inline_stylesheet_colors(repo: Path, root: str) -> None:
    _stage(repo, f"{root}/view.py", 'view.setStyleSheet("color: #A1B2C3;")\n')
    assert any("color" in error for error in _errors(repo))


@pytest.mark.parametrize(
    "call",
    (
        "view.resize(800, 600)",
        "view.setMinimumSize(560, 440)",
        "view.setMaximumSize(1200, 900)",
        "view.setFixedSize(320, 200)",
        "view.setMinimumWidth(520)",
        "view.setMinimumHeight(150)",
        "view.setMaximumWidth(520)",
        "view.setMaximumHeight(150)",
        "view.setFixedWidth(200)",
        "view.setFixedHeight(40)",
        "layout.setContentsMargins(8, 12, 8, 12)",
        "layout.setSpacing(12)",
        "layout.setHorizontalSpacing(8)",
        "layout.setVerticalSpacing(8)",
    ),
)
def test_qt_dimensions_and_spacing_warn_without_blocking(repo: Path, call: str) -> None:
    _stage(repo, "apps/train/ui/view.py", call + "\n")
    assert not _errors(repo)
    assert _warnings(repo)


@pytest.mark.parametrize(
    "source",
    (
        "view.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)\n",
        'layout.setSpacing(style.spacing("space.sm"))\n',
        'view.setStyleSheet(style.panel_stylesheet())\n',
        "view.resize(width, height)\n",
        "layout.setContentsMargins(0, 1, 0, 1)\n",
        "view.setFixedWidth(True)\n",
        "resize(800, 600)\n",  # Free functions are not Qt method candidates.
    ),
)
def test_owned_values_and_non_candidates_do_not_warn(repo: Path, source: str) -> None:
    _stage(repo, "apps/predict/ui/view.py", source)
    assert not _errors(repo)
    assert not _warnings(repo)


@pytest.mark.parametrize(
    "path",
    (
        "ui_common/visual_tokens.py",
        "apps/common/ui/style.py",
        "apps/common/ui/window_policy.py",
        "apps/train/application/service.py",
    ),
)
def test_shared_owners_and_application_logic_remain_outside_surface_scan(
    repo: Path, path: str
) -> None:
    _stage(repo, path, 'COLOR = "#A1B2C3"\nview.resize(800, 600)\n')
    assert not _errors(repo)
    assert not _warnings(repo)


def test_only_added_multiline_qt_argument_is_reported(repo: Path) -> None:
    path = "apps/predict/ui/view.py"
    _stage(repo, path, "view.setMinimumSize(\n    560,\n    440,\n)\n")
    _git(repo, "commit", "-qm", "existing geometry")
    _stage(repo, path, "view.setMinimumSize(\n    600,\n    440,\n)\n")
    assert not _errors(repo)
    warnings = _warnings(repo)
    assert len(warnings) == 1
    assert f"{path}:2:" in warnings[0]


def test_existing_pyside_literals_are_not_retroactively_reported(repo: Path) -> None:
    path = "apps/train/ui/view.py"
    old = 'COLOR = "#A1B2C3"\nview.resize(800, 600)\n'
    _stage(repo, path, old)
    _git(repo, "commit", "-qm", "existing presentation")
    _stage(repo, path, old + "label = title\n")
    assert not _errors(repo)
    assert not _warnings(repo)


def test_cli_allows_qt_warning_and_rejects_pyside_color(repo: Path) -> None:
    import sys

    script = Path(__file__).resolve().parents[1] / "tools/check_agent_change_gate.py"
    command = [sys.executable, str(script), "--cached", "--repo-root", str(repo)]
    _stage(repo, "apps/predict/ui/view.py", "view.setMinimumSize(560, 440)\n")
    result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0
    assert "setMinimumSize" in result.stdout
    _stage(repo, "apps/predict/ui/view.py", 'COLOR = "#A1B2C3"\n')
    result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
    assert result.returncode == 1
    assert "color" in result.stdout
