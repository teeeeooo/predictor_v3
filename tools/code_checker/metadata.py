"""Helper for code_checker metadata and freshness detection."""

from __future__ import annotations

import json
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .scanner import discover_python_files


SCHEMA_VERSION = "1.1.0"


def get_git_info(repo_root: Path) -> dict[str, str | bool]:
    """Retrieve Git commit and dirty status safely with fallback values."""
    info = {"commit": "unknown", "dirty": False}
    try:
        # Get short commit hash
        res_hash = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if res_hash.returncode == 0:
            info["commit"] = res_hash.stdout.strip()

        # Check dirty status
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if res_status.returncode == 0:
            info["dirty"] = len(res_status.stdout.strip()) > 0
    except Exception:
        # Fallback to defaults on any command error
        pass
    return info


def compute_source_fingerprint(
    repo_root: Path,
    input_paths: list[Path] | None = None,
) -> str:
    """Hash deterministic code map inputs, excluding generated metadata."""
    root = repo_root.resolve()
    paths = input_paths if input_paths is not None else discover_python_files(root)
    hasher = hashlib.sha256()
    for path in sorted(p.resolve() for p in paths):
        if not path.is_file():
            continue
        relpath = path.relative_to(root).as_posix()
        hasher.update(relpath.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def generate_metadata(repo_root: Path) -> dict[str, str | bool]:
    """Generate compact metadata for the reference map."""
    git_info = get_git_info(repo_root)
    return {
        "generator": "code_checker",
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "git_commit_short": git_info["commit"],
        "git_dirty": git_info["dirty"],
        "source_fingerprint": compute_source_fingerprint(repo_root),
    }


def render_metadata_comment(meta: dict[str, str | bool]) -> str:
    """Format metadata into a hidden HTML comment for easy parsing."""
    json_str = json.dumps(meta, sort_keys=True)
    return f"<!-- CODE_CHECKER_METADATA: {json_str} -->"


def parse_metadata_from_map(map_content: str) -> dict[str, str | bool] | None:
    """Extract and parse the metadata JSON comment from the map content."""
    marker = "<!-- CODE_CHECKER_METADATA: "
    if marker not in map_content:
        return None
    try:
        start_idx = map_content.find(marker) + len(marker)
        end_idx = map_content.find(" -->", start_idx)
        if end_idx == -1:
            return None
        json_str = map_content[start_idx:end_idx].strip()
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def evaluate_freshness(map_path: Path, repo_root: Path) -> dict[str, str | bool | None]:
    """Compare stored source fingerprint with current code map inputs."""
    current_git = get_git_info(repo_root)
    current_commit = current_git["commit"]
    is_current_dirty = current_git["dirty"]
    current_fingerprint = compute_source_fingerprint(repo_root)

    result = {
        "status": "unknown",
        "message": "",
        "map_commit": None,
        "map_dirty": None,
        "map_source_fingerprint": None,
        "current_source_fingerprint": current_fingerprint,
        "current_commit": current_commit,
        "current_dirty": is_current_dirty,
    }

    if not map_path.exists():
        result["status"] = "missing"
        result["message"] = f"Reference map file does not exist at {map_path}."
        return result

    try:
        content = map_path.read_text(encoding="utf-8")
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Failed to read reference map: {e}"
        return result

    meta = parse_metadata_from_map(content)
    if not meta:
        result["status"] = "metadata_missing"
        result["message"] = (
            "Reference map is missing code_checker metadata. "
            "Please regenerate the map to include freshness checks."
        )
        return result

    map_commit = meta.get("git_commit_short", "unknown")
    map_dirty = meta.get("git_dirty", False)
    map_fingerprint = meta.get("source_fingerprint")

    result["map_commit"] = map_commit
    result["map_dirty"] = map_dirty
    result["map_source_fingerprint"] = map_fingerprint

    if not isinstance(map_fingerprint, str) or not map_fingerprint:
        result["status"] = "metadata_legacy"
        result["message"] = (
            "Reference map metadata is legacy and lacks source_fingerprint. "
            "Regenerate the map with python3 -B tools/code_checker/build_reference_map.py."
        )
        return result

    if map_fingerprint != current_fingerprint:
        result["status"] = "stale"
        result["message"] = (
            f"Reference map is stale. "
            f"Map source fingerprint ({map_fingerprint}) != "
            f"Current source fingerprint ({current_fingerprint})."
        )
    else:
        result["status"] = "fresh"
        result["message"] = "Reference map matches the current source fingerprint."

    warnings = []
    if map_commit != current_commit:
        warnings.append(
            f"Map commit ({map_commit}) differs from current HEAD ({current_commit}); "
            "commit hash is informational only."
        )
    if is_current_dirty:
        warnings.append("Current working directory has uncommitted changes.")
    if map_dirty:
        warnings.append("Reference map was generated from a dirty working tree.")

    if warnings:
        result["message"] += " Warning: " + " & ".join(warnings)

    return result
