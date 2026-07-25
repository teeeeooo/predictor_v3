"""Load core evidence and supported Active baselines without mutation."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.state.training_run_state import TrainingResult
from core.ml.training_results import CoreTrainingEvidence

from .contracts import TrainingAnalysisResult


def load_active_baseline(
    repository: ModelLifecycleRepository,
) -> tuple[TrainingAnalysisResult | None, str, str]:
    active = repository.read_active(optional=True)
    if active is None:
        return None, "", ""
    candidate = repository.read_candidate(active.candidate_id)
    path = candidate.path / "training_result.json"
    if not path.is_file():
        return (
            None,
            active.candidate_id,
            "Active Candidate has no supported training analysis.",
        )
    return (
        TrainingAnalysisResult.from_payload(
            json.loads(path.read_text(encoding="utf-8"))
        ),
        active.candidate_id,
        "",
    )


def load_candidate_evidence(
    staging: Path,
    targets,
) -> CoreTrainingEvidence:
    path = staging / "core_training_evidence.json"
    if path.is_file():
        return CoreTrainingEvidence.from_payload(
            json.loads(path.read_text(encoding="utf-8"))
        )
    now = datetime.now(timezone.utc).isoformat()
    return CoreTrainingEvidence(
        started_at=now,
        finished_at=now,
        duration_seconds=0.0,
        training_data_sha256="unavailable-dev-smoke",
        training_data_rows=0,
        evaluation_context={
            "scope": "dev_mock_unverified",
            "reason": "DEV smoke does not establish model quality.",
        },
        targets=tuple(_dev_target(target) for target in targets),
        preprocessing={
            "status": "unavailable",
            "reason": "DEV smoke bypasses production preprocessing.",
            "feature_data_quality": (),
        },
        blocking_reasons=("dev_mock_quality_unverified",),
    )


def load_terminal_evidence(
    staging: Path,
    result: TrainingResult,
) -> CoreTrainingEvidence:
    path = staging / "core_training_evidence.json"
    if path.is_file():
        evidence = CoreTrainingEvidence.from_payload(
            json.loads(path.read_text(encoding="utf-8"))
        )
        return (
            replace(evidence, status=result.status)
            if result.status and evidence.status != result.status
            else evidence
        )
    now = datetime.now(timezone.utc).isoformat()
    reason = result.message or f"Training ended with status {result.status}."
    return CoreTrainingEvidence(
        started_at=now,
        finished_at=now,
        duration_seconds=0.0,
        training_data_sha256="unavailable",
        training_data_rows=0,
        evaluation_context={
            "status": "unavailable",
            "reason": "Training did not produce evaluation evidence.",
        },
        targets=(),
        preprocessing={
            "status": "unavailable",
            "reason": "Training did not produce preprocessing evidence.",
            "feature_data_quality": (),
        },
        status="cancelled" if result.status == "cancelled" else "failed",
        blocking_reasons=(reason,),
    )


def _dev_target(target) -> dict:  # noqa: ANN001
    return {
        "target_identity": target.identity,
        "target_ml_name": target.ml_name,
        "status": "complete",
        "metrics": {
            "evaluation_scope": "dev_mock_unverified",
            "sample_count": 0,
            "fold_count": 0,
            "seed": None,
            "r2": None,
            "mae": None,
            "rmse": None,
        },
        "rfecv": {
            "status": "unavailable",
            "feature_count_before": 0,
            "feature_count_after": 0,
            "features": [],
        },
        "feature_importance": [],
        "optuna": {
            "status": "not_used",
            "selected_parameters": {},
            "trials": [],
        },
    }
