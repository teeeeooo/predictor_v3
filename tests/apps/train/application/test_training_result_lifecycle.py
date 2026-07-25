"""Phase 5C terminal evidence and immutable Candidate publication guards."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository, ModelPromotionService
from apps.common.model_lifecycle.errors import CandidateCorruptionError
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.composition.training_results import build_candidate_publisher
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


def _service(repository, **kwargs):  # noqa: ANN001
    return TrainingLifecycleService(
        repository=repository,
        publisher=build_candidate_publisher(repository),
        **kwargs,
    )


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
    service = _service(
        repository,
        execution=_ArtifactExecution(snapshot, status="cancelled"),
        registry_provider=lambda: snapshot,
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
    service = _service(
        repository,
        execution=_ArtifactExecution(snapshot),
        registry_provider=lambda: snapshot,
    )
    calls = {"count": 0}
    original = service._publisher._artifacts.write

    def fail_once(staging, result):  # noqa: ANN001
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("xlsx generation failed")
        original(staging, result)

    service._publisher._artifacts.write = fail_once
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
    service = _service(
        repository,
        execution=_ArtifactExecution(snapshot),
        registry_provider=lambda: snapshot,
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
    service = _service(
        repository,
        execution=_PartialExecution(snapshot),
        registry_provider=lambda: snapshot,
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


def _published_v2_with_active(tmp_path):  # noqa: ANN001
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    publish_candidate(repository, snapshot, "active")
    repository.replace_active(
        "active",
        activated_at="2026-07-25T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    service = _service(
        repository,
        execution=_ArtifactExecution(snapshot),
        registry_provider=lambda: snapshot,
    )
    service.start(TrainingRequest(
        run_id="integrity-run",
        candidate_id="integrity-candidate",
        data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
    ))
    return repository, snapshot, (
        repository.candidates_path / "integrity-candidate"
    )


def _rewrite_manifest(candidate_path, mutate):  # noqa: ANN001
    path = candidate_path / "manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _rewrite_result_and_hash(candidate_path, mutate):  # noqa: ANN001
    result_path = candidate_path / "training_result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    mutate(payload)
    result_path.write_text(json.dumps(payload), encoding="utf-8")
    sha256 = hashlib.sha256(result_path.read_bytes()).hexdigest()
    _rewrite_manifest(
        candidate_path,
        lambda manifest: next(
            item for item in manifest["analysis_artifacts"]
            if item["path"] == "training_result.json"
        ).update({"sha256": sha256}),
    )


@pytest.mark.parametrize(
    "corruption",
    (
        "missing-reference",
        "missing-file",
        "missing-reference-and-file",
        "hash-mismatch",
        "duplicate-path",
        "duplicate-identity",
        "wrong-category",
        "wrong-required",
        "future-version",
        "version-mismatch",
        "malformed-result",
    ),
)
def test_v2_analysis_corruption_blocks_read_and_promotion_without_active_change(
    tmp_path, corruption
):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)
    target_path = "analysis/target_metrics.csv"
    if corruption in {"missing-reference", "missing-reference-and-file"}:
        _rewrite_manifest(
            candidate_path,
            lambda payload: payload.update({
                "analysis_artifacts": [
                    item for item in payload["analysis_artifacts"]
                    if item["path"] != target_path
                ]
            }),
        )
    if corruption in {"missing-file", "missing-reference-and-file"}:
        (candidate_path / target_path).unlink()
    elif corruption == "hash-mismatch":
        (candidate_path / target_path).write_text("tampered", encoding="utf-8")
    elif corruption in {"duplicate-path", "duplicate-identity"}:
        def duplicate(payload):  # noqa: ANN001
            copied = dict(payload["analysis_artifacts"][0])
            if corruption == "duplicate-identity":
                copied["path"] = "analysis/duplicate.json"
                (candidate_path / copied["path"]).write_bytes(
                    (candidate_path / payload["analysis_artifacts"][0]["path"]).read_bytes()
                )
            payload["analysis_artifacts"].append(copied)
        _rewrite_manifest(candidate_path, duplicate)
    elif corruption in {"wrong-category", "wrong-required"}:
        def invalidate(payload):  # noqa: ANN001
            item = next(
                item for item in payload["analysis_artifacts"]
                if item["path"] == target_path
            )
            item[
                "category" if corruption == "wrong-category" else "required"
            ] = "wrong" if corruption == "wrong-category" else False
        _rewrite_manifest(candidate_path, invalidate)
    elif corruption == "future-version":
        _rewrite_result_and_hash(
            candidate_path,
            lambda payload: payload.update(
                {"schema_version": "training_result.v999"}
            ),
        )
        _rewrite_manifest(
            candidate_path,
            lambda payload: payload.update(
                {"analysis_contract_version": "training_result.v999"}
            ),
        )
    elif corruption == "version-mismatch":
        _rewrite_result_and_hash(
            candidate_path,
            lambda payload: payload.update(
                {"schema_version": "training_result.v999"}
            ),
        )
    elif corruption == "malformed-result":
        _rewrite_result_and_hash(
            candidate_path,
            lambda payload: payload.update({"targets": {}}),
        )

    before = repository.read_active()
    with pytest.raises(CandidateCorruptionError):
        repository.read_candidate("integrity-candidate")
    promoted = ModelPromotionService(
        repository, lambda: snapshot
    ).promote("integrity-candidate", expected_revision=before.revision)
    after = repository.read_active()

    assert promoted.status == "blocked"
    assert after == before


def test_v2_normal_read_and_v1_legacy_read_remain_supported(tmp_path):
    repository, _snapshot, _candidate_path = _published_v2_with_active(tmp_path)

    assert repository.read_candidate(
        "integrity-candidate"
    ).manifest.analysis_contract_version == "training_result.v1"
    assert repository.read_candidate("active").manifest.schema_version == (
        "model_candidate_manifest.v1"
    )
    assert not (
        repository.candidates_path / "active" / "training_result.json"
    ).exists()
