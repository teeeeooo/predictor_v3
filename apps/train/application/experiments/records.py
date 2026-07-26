"""Persisted run payload projection and current build identity."""

from __future__ import annotations

import platform
import hashlib
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any

from apps.train.application.experiments.contracts import (
    RUN_RECORD_VERSION,
    TRAINING_EXECUTION_ID,
    ResolvedExperiment,
)
from apps.train.state.training_run_state import TrainingRequest, TrainingResult


def run_record(
    request: TrainingRequest,
    resolved: ResolvedExperiment,
    *,
    status: str,
    attempt: int,
    revision: str,
) -> dict[str, Any]:
    return {
        "schema_version": RUN_RECORD_VERSION,
        "run_id": request.run_id,
        "candidate_id": request.candidate_id,
        "campaign_id": request.campaign_id,
        "attempt": attempt,
        "status": status,
        "started_at": utc_now(),
        "finished_at": "",
        "resolved_specification": resolved.payload,
        "contract_identity": {
            "specification_fingerprint": resolved.fingerprint,
            "definition_generation": request.generation_id,
            "registry_fingerprint": request.registry_fingerprint,
            "ordered_ml_fingerprint": request.ordered_ml_fingerprint,
            "derived_semantics_fingerprint": request.derived_semantics_fingerprint,
            "one_hot_fingerprint": request.one_hot_fingerprint,
            "training_execution": TRAINING_EXECUTION_ID,
            "preprocessing": request.preprocess_version,
            "metric_contract": resolved.payload["evaluation"]["metric_contract"],
            "data_request": resolved.payload["data"],
            "data_sha256": file_sha256(request.data_path),
            "evaluation_request": resolved.payload["evaluation"],
            "build_revision": revision,
            "python": platform.python_version(),
        },
        "result": None,
    }


def result_payload(
    result: TrainingResult, *, log_reference: str | None
) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "status": result.status,
        "candidate_id": result.candidate_id,
        "publication_outcome": result.publication_outcome,
        "candidate_reference": result.candidate_id or None,
        "evidence_reference": (
            f"run_evidence/{result.run_id}/training_result.json"
            if result.evidence_path else None
        ),
        "log_reference": log_reference,
        "message": result.message,
        "diagnostics": {
            "summary": result.summary,
            "raw_log_path": result.log_path or None,
        },
    }


def result_status(result: TrainingResult) -> str:
    if result.status == "complete" and result.publication_outcome == "published":
        return "success"
    if result.status in {"cancelled", "partial", "lock_conflict"}:
        return result.status
    return "training_failure"


def current_revision() -> str:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z"],
            check=True,
            capture_output=True,
            timeout=2,
        ).stdout
        if not status:
            return head
        digest = hashlib.sha256(status)
        digest.update(subprocess.run(
            ["git", "diff", "--binary", "HEAD"],
            check=True,
            capture_output=True,
            timeout=5,
        ).stdout)
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            check=True,
            capture_output=True,
            timeout=2,
        ).stdout.split(b"\0")
        for raw_path in sorted(item for item in untracked if item):
            digest.update(raw_path)
            path = Path(raw_path.decode("utf-8", errors="surrogateescape"))
            if path.is_file() and path.suffix in {".py", ".pyi", ".toml", ".cfg"}:
                digest.update(path.read_bytes())
        return f"{head}+dirty.{digest.hexdigest()}"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
