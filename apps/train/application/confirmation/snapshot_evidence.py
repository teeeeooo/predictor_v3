"""Hash and fixed-meaning evidence helpers for snapshot freeze."""

from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.closeout.canonical import file_sha256


def candidate_artifacts(
    path: Path, manifest  # noqa: ANN001
) -> dict[str, dict[str, Any]]:
    names = {"manifest.json", "result.json", "model.pkl"}
    names.update(
        reference.path
        for reference in manifest.analysis_artifacts
        if reference.required
    )
    artifacts = {}
    for name in sorted(names):
        artifact = path / name
        require_regular_artifact(artifact)
        artifacts[name] = {
            "sha256": file_sha256(artifact),
            "size_bytes": artifact.stat().st_size,
        }
    return artifacts


def directory_artifacts(path: Path) -> dict[str, dict[str, Any]]:
    artifacts = {}
    for artifact in sorted(path.rglob("*")):
        if artifact.is_dir():
            continue
        require_regular_artifact(artifact)
        artifacts[str(artifact.relative_to(path))] = {
            "sha256": file_sha256(artifact),
            "size_bytes": artifact.stat().st_size,
        }
    if not artifacts:
        raise ValueError("Definition generation bundle is empty")
    return artifacts


def selected_parameters(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    targets = payload.get("targets")
    if not isinstance(targets, list):
        raise ValueError("selected training parameters are unavailable")
    selected = {}
    for target in targets:
        identity = target.get("target_identity")
        parameters = target.get("optuna", {}).get("selected_parameters")
        if (
            type(identity) is not str
            or not identity
            or not isinstance(parameters, dict)
            or not parameters
        ):
            raise ValueError("selected final parameters are incomplete")
        selected[identity] = parameters
    return selected


def preflight_data(path: str, run: dict[str, Any]) -> dict[str, Any]:
    source = Path(path)
    require_regular_artifact(source)
    digest = file_sha256(source)
    if digest != run["contract_identity"]["data_sha256"]:
        raise ValueError("training data changed after the selected run")
    analysis_path = Path(run.get("result", {}).get("evidence_reference") or "")
    return {
        "materialization_kind": "owned_source_bytes",
        "materialized_identity": f"preflight-only:{digest}",
        "content_sha256": digest,
        "size_bytes": source.stat().st_size,
        "schema_columns": ["preflight"],
        "row_count": 0,
        "column_count": 1,
        "ordered_row_set_sha256": "0" * 64,
        "filtering_meaning": {
            "status": "preflight_only",
            "evidence_reference": str(analysis_path),
        },
    }


def specification_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def require_regular_artifact(path: Path) -> None:
    entry = path.lstat()
    if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
        raise ValueError(f"required immutable artifact is unsafe: {path.name}")
