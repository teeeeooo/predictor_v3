"""CLI for staged agent change-gate validation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.agent_change_gate import evaluate_cached, format_findings
from tools.agent_change_gate_git import GitCommandError, GitIndex


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate staged agent changes.")
    parser.add_argument("--cached", action="store_true", help="inspect the Git index")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    if not args.cached:
        parser.error("only --cached is implemented")
    try:
        findings = evaluate_cached(GitIndex(args.repo_root.resolve()))
    except GitCommandError as exc:
        sys.stderr.write(f"agent change gate: {exc}\n")
        return 2
    sys.stdout.write(format_findings(findings))
    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
