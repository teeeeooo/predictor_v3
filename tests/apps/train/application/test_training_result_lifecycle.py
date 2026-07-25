"""Phase 5C terminal evidence and immutable Candidate publication guards."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.common.model_lifecycle.errors import CandidateCorruptionError
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.state.training_run_state import TrainingRequest, TrainingResult
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from core.ml.training_results import CoreTrainingEvidence
from tests.apps.common.model_lifecycle.conftest import (
    artifact_for,
    publish_candidate,
)
from tools.dev.mock_smoke.generators import write_mock_training_data


class _ArtifactExecution:
    def __init__(self, snapshot, *, status: str = "complete") -> None:
        self.snapshot = snapshot
        self.status = status

    @property
    def is_running(self):
        return False

    def start(self, request, callbacks):  # noqa: ANN001
        joblib.dump(artifact_for(self.snapshot), request.model_output_path)
        terminal = TrainingResult(
            request.run_id,
            self.status,
            model_path=request.model_output_path,
            message="terminal evidence",
        )
        if self.status == "complete":
            callbacks.finished(terminal)
        elif self.status == "cancelled":
            callbacks.cancelled(terminal)
        else:
            callbacks.failed(terminal)

    def cancel(self):
        return False

    def dispose(self):
        return None


def test_cancel_preserves_active_and_structured_evidence_not_candidate(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    publish_candidate(repository, snapshot, "active")
    repository.replace_active(
        "active",
        activated_at=datetime.now(timezone.utc).isoformat(),
        source="test",
        expected_revision=0,
    )
    service = TrainingLifecycleService(
        execution=_ArtifactExecution(snapshot, status="cancelled"),
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    request = TrainingRequest(
        run_id="cancelled-run",
        candidate_id="cancelled-candidate",
        data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
    )

    service.start(request)

    assert repository.read_active().candidate_id == "active"
    assert [
        item.manifest.candidate_id for item in repository.list_candidates()
    ] == ["active"]
    evidence = json.loads(
        (
            repository.run_evidence_path
            / "cancelled-run"
            / "training_result.json"
        ).read_text()
    )
    assert evidence["run"]["status"] == "cancelled"
    assert evidence["promotion_eligibility"]["eligible"] is False


def test_artifact_failure_never_publishes_incomplete_candidate(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = TrainingLifecycleService(
        execution=_ArtifactExecution(snapshot),
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    calls = {"count": 0}
    original = service._publisher._artifact_writer.write

    def fail_once(staging, result):  # noqa: ANN001
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("xlsx generation failed")
        original(staging, result)

    service._publisher._artifact_writer.write = fail_once
    failed = []
    service.start(
        TrainingRequest(
            run_id="artifact-failure",
            candidate_id="candidate-bad",
            data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
        ),
        failed_callback=failed.append,
    )

    assert repository.list_candidates() == ()
    assert failed[0].publication_outcome == "artifact_generation_failed"
    assert (
        repository.run_evidence_path
        / "artifact-failure"
        / "training_result.json"
    ).is_file()


def test_complete_candidate_owns_hashed_analysis_artifacts(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = TrainingLifecycleService(
        execution=_ArtifactExecution(snapshot),
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    service.start(TrainingRequest(
        run_id="complete-run",
        candidate_id="complete-candidate",
        data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
    ))

    candidate = repository.read_candidate("complete-candidate")

    assert candidate.manifest.schema_version == "model_candidate_manifest.v2"
    assert len(candidate.manifest.analysis_artifacts) == 9
    assert (candidate.path / "training_report.xlsx").is_file()
    target_metrics = candidate.path / "analysis" / "target_metrics.csv"
    target_metrics.write_text("tampered", encoding="utf-8")
    with pytest.raises(CandidateCorruptionError, match="artifact hash mismatch"):
        repository.read_candidate("complete-candidate")


class _PartialExecution(_ArtifactExecution):
    def start(self, request, callbacks):  # noqa: ANN001
        joblib.dump(artifact_for(self.snapshot), request.model_output_path)
        target = next(
            target
            for group in self.snapshot.groups
            for target in group.targets
        )
        now = datetime.now(timezone.utc).isoformat()
        evidence = CoreTrainingEvidence(
            started_at=now,
            finished_at=now,
            duration_seconds=1.0,
            training_data_sha256="partial-data",
            training_data_rows=8,
            evaluation_context={"scope": "test", "fold_count": 1, "seed": 42},
            targets=({
                "target_identity": target.identity,
                "target_ml_name": target.ml_name,
                "status": "complete",
                "metrics": {
                    "evaluation_scope": "test",
                    "sample_count": 8,
                    "fold_count": 1,
                    "seed": 42,
                    "r2": 0.5,
                    "mae": 1.0,
                    "rmse": 1.2,
                },
                "rfecv": {
                    "status": "not_used",
                    "feature_count_before": 1,
                    "feature_count_after": 1,
                    "features": [],
                },
                "feature_importance": [],
                "optuna": {
                    "status": "not_used",
                    "selected_parameters": {},
                    "trials": [],
                },
            },),
            preprocessing={"status": "applied", "feature_data_quality": ()},
            status="partial",
            blocking_reasons=("another target failed",),
        )
        (Path(request.model_output_path).parent / "core_training_evidence.json").write_text(
            json.dumps(evidence.to_payload()), encoding="utf-8"
        )
        callbacks.failed(TrainingResult(
            request.run_id,
            "partial",
            model_path=request.model_output_path,
            message="one target failed",
        ))


def test_partial_preserves_successful_target_without_candidate(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = TrainingLifecycleService(
        execution=_PartialExecution(snapshot),
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    service.start(TrainingRequest(
        run_id="partial-run",
        candidate_id="partial-candidate",
        data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
    ))

    assert repository.list_candidates() == ()
    payload = json.loads(
        (
            repository.run_evidence_path
            / "partial-run"
            / "training_result.json"
        ).read_text()
    )
    assert payload["run"]["status"] == "partial"
    assert payload["targets"][0]["status"] == "complete"
    assert payload["promotion_eligibility"]["eligible"] is False
