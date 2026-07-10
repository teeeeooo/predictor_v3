"""Focused tests for repository Git hooks."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

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


def test_pre_commit_hook_exists_and_is_executable() -> None:
    hook = HOOKS_ROOT / "pre-commit"
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
