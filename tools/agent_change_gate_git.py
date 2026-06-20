"""Git index access for the staged agent change gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


@dataclass(frozen=True)
class StagedChange:
    status: str
    path: str
    old_path: str | None = None


class GitCommandError(RuntimeError):
    pass


class GitIndex:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def staged_changes(self) -> tuple[StagedChange, ...]:
        output = self._run("diff", "--cached", "--name-status", "-z")
        tokens = output.split("\0")
        changes: list[StagedChange] = []
        index = 0
        while index < len(tokens) and tokens[index]:
            status = tokens[index]
            index += 1
            if status.startswith(("R", "C")):
                old_path = tokens[index]
                path = tokens[index + 1]
                index += 2
                changes.append(StagedChange(status[0], path, old_path))
            else:
                path = tokens[index]
                index += 1
                changes.append(StagedChange(status[0], path))
        return tuple(changes)

    def index_text(self, path: str) -> str:
        return self._run("show", f":{path}")

    def head_text(self, path: str) -> str | None:
        result = subprocess.run(
            ("git", "show", f"HEAD:{path}"),
            cwd=self.repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout

    def whitespace_errors(self) -> str:
        result = subprocess.run(
            ("git", "diff", "--cached", "--check"),
            cwd=self.repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return result.stdout.strip() if result.returncode else ""

    def added_line_numbers(self, path: str) -> frozenset[int]:
        """Return line numbers added to the staged/index version of ``path``."""
        output = self._run(
            "diff", "--cached", "--unified=0", "--no-color", "--", path
        )
        added: set[int] = set()
        current = 0
        for line in output.splitlines():
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if match:
                current = int(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                added.add(current)
                current += 1
            elif line.startswith("-") and not line.startswith("---"):
                continue
            elif current and not line.startswith("\\"):
                current += 1
        return frozenset(added)

    def manifest_path(self) -> Path:
        path = self._run("rev-parse", "--git-path", "agent_task_manifest.yml").strip()
        candidate = Path(path)
        return candidate if candidate.is_absolute() else self.repo_root / candidate

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            ("git", *args),
            cwd=self.repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise GitCommandError(f"git {' '.join(args)} failed: {detail}")
        return result.stdout
