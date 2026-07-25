"""Filesystem evidence adapter for the application training-result ports."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.application.training_results import TrainingAnalysisResult
from apps.train.state.training_run_state import TrainingResult
from core.ml.training_results import CoreTrainingEvidence


class FilesystemTrainingEvidenceAdapter:
    def __init__(self, repository: ModelLifecycleRepository) -> None:
        self._repository = repository

    def load_active_baseline(
        self,
    ) -> tuple[TrainingAnalysisResult | None, str, str]:
        active = self._repository.read_active(optional=True)
        if active is None:
            return None, "", ""
        candidate = self._repository.read_candidate(active.candidate_id)
        path = candidate.path / "training_result.json"
        if not path.is_file():
            return None, active.candidate_id, (
                "Active Candidate has no supported training analysis."
            )
        return (
            TrainingAnalysisResult.from_payload(
                json.loads(path.read_text(encoding="utf-8"))
            ),
            active.candidate_id,
            "",
        )

    def load_candidate(
        self, staging: Path, targets: tuple[object, ...]
    ) -> CoreTrainingEvidence:
        path = staging / "core_training_evidence.json"
        if path.is_file():
            evidence = CoreTrainingEvidence.from_payload(
                json.loads(path.read_text(encoding="utf-8"))
            )
            return evidence
        now = datetime.now(timezone.utc).isoformat()
        evidence = CoreTrainingEvidence(
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
        path.write_text(
            json.dumps(
                evidence.to_payload(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return evidence

    def load_terminal(
        self, staging: Path, result: TrainingResult
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

    def prepare_terminal(self, staging: Path, candidate_id: str) -> Path:
        if not staging.is_dir():
            staging = self._repository.create_staging(candidate_id)
        (staging / "model.pkl").unlink(missing_ok=True)
        (staging / "core_training_evidence.json").unlink(missing_ok=True)
        (staging / "training_result.json").unlink(missing_ok=True)
        (staging / "training_report.xlsx").unlink(missing_ok=True)
        (staging / "manifest.json").unlink(missing_ok=True)
        (staging / "result.json").unlink(missing_ok=True)
        analysis = staging / "analysis"
        if analysis.is_dir():
            shutil.rmtree(analysis)
        return staging


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
