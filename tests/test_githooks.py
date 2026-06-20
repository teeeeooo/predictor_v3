"""Focused tests for repository Git hooks."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

from tools.agent_change_gate_models import _EXEMPTION_VALUES


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_ROOT = REPO_ROOT / ".githooks"


def _run_hook(
    name: str,
    *args: Path,
    cwd: Path = REPO_ROOT,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(HOOKS_ROOT / name), *(str(arg) for arg in args)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def test_hooks_exist_and_are_executable() -> None:
    for name in ("pre-commit", "commit-msg"):
        hook = HOOKS_ROOT / name
        assert hook.is_file()
        assert os.access(hook, os.X_OK)


def test_pre_commit_calls_cached_checker_from_repo_root(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    tools = tmp_path / "tools"
    tools.mkdir()
    checker = tools / "check_agent_change_gate.py"
    checker.write_text(
        "import sys\nprint('checker', *sys.argv[1:])\n",
        encoding="utf-8",
    )
    staged = tmp_path / "staged.txt"
    staged.write_text("clean staged content\n", encoding="utf-8")
    _git(tmp_path, "add", "staged.txt")

    result = _run_hook("pre-commit", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "checker --cached" in result.stdout


def test_commit_msg_accepts_message_without_exemption_trailer(tmp_path: Path) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("Subject\n", encoding="utf-8")

    assert _run_hook("commit-msg", message).returncode == 0


@pytest.mark.parametrize("value", sorted(_EXEMPTION_VALUES))
def test_commit_msg_accepts_allowed_exemption_trailer(tmp_path: Path, value: str) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text(
        f"Subject\n\nAgent-Report-Exemption: {value}\n",
        encoding="utf-8",
    )

    assert _run_hook("commit-msg", message).returncode == 0


@pytest.mark.parametrize(
    "trailers",
    (
        "Agent-Report-Exemption: unknown",
        "Agent-Report-Exemption:user-approved-docs-only",
        "Agent-Report-Exemption: status-only\nAgent-Report-Exemption: status-only",
    ),
)
def test_commit_msg_rejects_invalid_or_duplicate_exemption_trailer(
    tmp_path: Path,
    trailers: str,
) -> None:
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text(f"Subject\n\n{trailers}\n", encoding="utf-8")

    assert _run_hook("commit-msg", message).returncode != 0
