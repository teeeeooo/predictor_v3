"""Phase 5C terminal evidence and immutable Candidate publication guards."""

from __future__ import annotations

import json
import hashlib
from dataclasses import replace
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
    assert len(candidate.manifest.analysis_artifacts) == 10
    assert sum(
        reference.required
        for reference in candidate.manifest.analysis_artifacts
    ) == 9
    assert (
        candidate.path / "core_training_evidence.json"
    ).is_file()
    core_reference = next(
        reference
        for reference in candidate.manifest.analysis_artifacts
        if reference.category == "core_training_evidence"
    )
    assert core_reference.required is False
    assert core_reference.path == "core_training_evidence.json"
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


class _CompleteEvidenceExecution(_ArtifactExecution):
    def start(self, request, callbacks):  # noqa: ANN001
        joblib.dump(artifact_for(self.snapshot), request.model_output_path)
        now = datetime.now(timezone.utc).isoformat()
        evidence = CoreTrainingEvidence(
            started_at=now,
            finished_at=now,
            duration_seconds=1.25,
            training_data_sha256="complete-data",
            training_data_rows=8,
            evaluation_context={"scope": "test", "fold_count": 2, "seed": 42},
            targets=tuple(
                _complete_target_evidence(target, index)
                for index, group in enumerate(self.snapshot.groups)
                for target in group.targets
            ),
            preprocessing={"status": "applied", "feature_data_quality": ()},
            status="complete",
            blocking_reasons=("original-core-reason",),
        )
        (
            Path(request.model_output_path).parent
            / "core_training_evidence.json"
        ).write_text(json.dumps(evidence.to_payload()), encoding="utf-8")
        callbacks.finished(TrainingResult(
            request.run_id,
            "complete",
            model_path=request.model_output_path,
            message="core training complete",
        ))


def _complete_target_evidence(target, index):  # noqa: ANN001
    return {
        "target_identity": target.identity,
        "target_ml_name": target.ml_name,
        "status": "complete",
        "metrics": {
            "evaluation_scope": "test",
            "sample_count": 8,
            "fold_count": 2,
            "seed": 42,
            "r2": 0.8 + index * 0.01,
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
    }


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


def _failure_service(tmp_path, *, failure_hook=None):  # noqa: ANN001
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=failure_hook
    )
    publish_candidate(repository, snapshot, "active")
    repository.replace_active(
        "active",
        activated_at="2026-07-25T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    service = _service(
        repository,
        execution=_CompleteEvidenceExecution(snapshot),
        registry_provider=lambda: snapshot,
    )
    return snapshot, repository, service


def _start_failure_run(tmp_path, service, run_id):  # noqa: ANN001
    failed = []
    service.start(
        TrainingRequest(
            run_id=run_id,
            candidate_id=f"candidate-{run_id}",
            data_path=str(
                write_mock_training_data(
                    output_dir=tmp_path / f"data-{run_id}", rows=8
                )
            ),
        ),
        failed_callback=failed.append,
    )
    return failed[0]


def _assert_preserved_original_evidence(repository, run_id, before):  # noqa: ANN001
    evidence_path = repository.run_evidence_path / run_id
    payload = json.loads(
        (evidence_path / "training_result.json").read_text(encoding="utf-8")
    )
    assert payload["run"]["training_status"] == "complete"
    assert payload["run"]["status"] == "failed"
    assert payload["run"]["publication_outcome"] != "published"
    assert payload["targets"]
    assert all(item["status"] == "complete" for item in payload["targets"])
    assert all("r2" in item["metrics"] for item in payload["targets"])
    assert any(
        item["reason"] == "original-core-reason"
        for item in payload["blocking_reasons"]
    )
    assert repository.read_active() == before
    assert [
        item.manifest.candidate_id for item in repository.list_candidates()
    ] == ["active"]
    assert [path.name for path in repository.run_evidence_path.iterdir()] == [
        run_id
    ]
    assert not list(repository.staging_path.iterdir())
    assert not {
        "model.pkl",
        "core_training_evidence.json",
        "manifest.json",
        "result.json",
    } & {path.name for path in evidence_path.iterdir()}
    return evidence_path, payload


def test_persistent_artifact_writer_failure_uses_minimal_structured_fallback(
    tmp_path,
):
    _snapshot, repository, service = _failure_service(tmp_path)
    before = repository.read_active()
    calls = {"count": 0}

    def always_fail(_staging, _result):  # noqa: ANN001
        calls["count"] += 1
        raise OSError("persistent xlsx failure")

    service._publisher._artifacts.write = always_fail
    failed = _start_failure_run(tmp_path, service, "persistent-writer")

    evidence_path, payload = _assert_preserved_original_evidence(
        repository, "persistent-writer", before
    )
    assert calls["count"] == 2
    assert failed.publication_outcome == "artifact_generation_failed"
    assert payload["run"]["failure_stage"] == "artifact_generation_or_validation"
    assert payload["run"]["failure_reason"] == "persistent xlsx failure"
    assert payload["run"]["artifact_mode"] == "minimal_structured_fallback"
    assert payload["artifacts"] == [{
        "category": "training_result",
        "path": "training_result.json",
        "required": True,
    }]
    assert {path.name for path in evidence_path.iterdir()} == {
        "training_result.json"
    }


def test_lifecycle_hash_validation_failure_preserves_original_target_evidence(
    tmp_path,
):
    _snapshot, repository, service = _failure_service(tmp_path)
    before = repository.read_active()
    original_write = service._publisher._artifacts.write
    calls = {"count": 0}

    def wrong_hash(staging, result):  # noqa: ANN001
        references = original_write(staging, result)
        calls["count"] += 1
        if calls["count"] == 1:
            return (
                replace(references[0], sha256="0" * 64),
                *references[1:],
            )
        return references

    service._publisher._artifacts.write = wrong_hash
    failed = _start_failure_run(tmp_path, service, "hash-validation")

    _evidence_path, payload = _assert_preserved_original_evidence(
        repository, "hash-validation", before
    )
    assert failed.publication_outcome == "failed"
    assert payload["run"]["failure_stage"] == "lifecycle_validation"
    assert "hash mismatch" in payload["run"]["failure_reason"]


def test_post_artifact_publication_failure_preserves_original_target_evidence(
    tmp_path,
):
    enabled = {"value": False}

    def fail(stage):  # noqa: ANN001
        if enabled["value"] and stage == "before_candidate_replace":
            raise OSError("atomic publication failed")

    _snapshot, repository, service = _failure_service(
        tmp_path, failure_hook=fail
    )
    before = repository.read_active()
    enabled["value"] = True

    failed = _start_failure_run(tmp_path, service, "publication-failure")

    evidence_path, payload = _assert_preserved_original_evidence(
        repository, "publication-failure", before
    )
    assert failed.publication_outcome == "failed"
    assert payload["run"]["failure_stage"] == "candidate_publication"
    assert payload["run"]["failure_reason"] == "atomic publication failed"
    assert not (evidence_path / "manifest.json").exists()
    assert not (evidence_path / "result.json").exists()


def test_publication_recovery_required_preserves_original_target_evidence(
    tmp_path,
):
    enabled = {"value": False}

    def fail(stage):  # noqa: ANN001
        if enabled["value"] and stage in {
            "after_candidate_replace",
            "before_candidate_rollback",
        }:
            raise OSError(stage)

    _snapshot, repository, service = _failure_service(
        tmp_path, failure_hook=fail
    )
    before = repository.read_active()
    enabled["value"] = True

    failed = _start_failure_run(tmp_path, service, "durability-failure")

    _evidence_path, payload = _assert_preserved_original_evidence(
        repository, "durability-failure", before
    )
    assert failed.publication_outcome == "recovery-required"
    assert payload["run"]["failure_stage"] == "candidate_publication_durability"
    assert "recovery required" in payload["run"]["failure_reason"]
    assert list(repository.root.glob(".candidate-recovery-*.json"))

    enabled["value"] = False
    repository.recover_candidate_publication(
        "candidate-durability-failure"
    )
    for staging in tuple(repository.staging_path.iterdir()):
        repository.discard_staging(staging)
    assert not list(repository.root.glob(".candidate-recovery-*.json"))
    assert not list(repository.staging_path.iterdir())


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


def _assert_read_and_promotion_reject_without_active_change(
    repository, snapshot
):  # noqa: ANN001
    before = repository.read_active()
    with pytest.raises(CandidateCorruptionError):
        repository.read_candidate("integrity-candidate")
    promoted = ModelPromotionService(
        repository, lambda: snapshot
    ).promote("integrity-candidate", expected_revision=before.revision)

    assert promoted.status == "blocked"
    assert repository.read_active() == before


def test_canonical_alias_coexistence_blocks_read_and_promotion(tmp_path):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)

    def add_alias(payload):  # noqa: ANN001
        reference = next(
            item for item in payload["analysis_artifacts"]
            if item["path"] == "analysis/target_metrics.csv"
        )
        payload["analysis_artifacts"].append({
            **reference,
            "path": "analysis/./target_metrics.csv",
        })

    _rewrite_manifest(candidate_path, add_alias)

    _assert_read_and_promotion_reject_without_active_change(
        repository, snapshot
    )


def test_result_manifest_equivalent_alias_mismatch_is_rejected(tmp_path):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)

    def alias_result(payload):  # noqa: ANN001
        reference = next(
            item for item in payload["artifacts"]
            if item["path"] == "analysis/target_metrics.csv"
        )
        reference["path"] = "analysis//target_metrics.csv"

    _rewrite_result_and_hash(candidate_path, alias_result)

    _assert_read_and_promotion_reject_without_active_change(
        repository, snapshot
    )


@pytest.mark.parametrize(
    "required",
    ("false", "true", 0, 1, None, [], {}),
    ids=("false-string", "true-string", "zero", "one", "null", "list", "object"),
)
@pytest.mark.parametrize("owner", ("manifest", "result"))
def test_artifact_required_rejects_non_boolean_json_types(
    tmp_path, owner, required
):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)

    def invalidate(payload):  # noqa: ANN001
        collection = (
            payload["analysis_artifacts"]
            if owner == "manifest"
            else payload["artifacts"]
        )
        collection[0]["required"] = required

    if owner == "manifest":
        _rewrite_manifest(candidate_path, invalidate)
    else:
        _rewrite_result_and_hash(candidate_path, invalidate)

    _assert_read_and_promotion_reject_without_active_change(
        repository, snapshot
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("path", None),
        ("path", 1),
        ("path", []),
        ("path", {}),
        ("path", ""),
        ("path", "/analysis/target_metrics.csv"),
        ("path", "../training_result.json"),
        ("path", "outside/artifact.csv"),
        ("path", "analysis/../training_result.json"),
        ("path", "analysis/target_metrics.csv/"),
        ("category", None),
        ("category", 1),
        ("category", []),
        ("category", {}),
        ("category", ""),
        ("sha256", None),
        ("sha256", 1),
        ("sha256", []),
        ("sha256", {}),
        ("sha256", ""),
        ("sha256", "not-a-sha256"),
        ("sha256", "A" * 64),
    ),
)
def test_manifest_artifact_reference_rejects_invalid_field_types_and_formats(
    tmp_path, field, value
):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)
    _rewrite_manifest(
        candidate_path,
        lambda payload: payload["analysis_artifacts"][0].update(
            {field: value}
        ),
    )

    _assert_read_and_promotion_reject_without_active_change(
        repository, snapshot
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("path", None),
        ("path", []),
        ("path", ""),
        ("category", None),
        ("category", 1),
        ("category", {}),
        ("category", ""),
    ),
)
def test_structured_result_artifact_rejects_invalid_field_types(
    tmp_path, field, value
):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)
    _rewrite_result_and_hash(
        candidate_path,
        lambda payload: payload["artifacts"][0].update({field: value}),
    )

    _assert_read_and_promotion_reject_without_active_change(
        repository, snapshot
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


def test_canonical_v2_candidate_remains_readable_and_promotable(tmp_path):
    repository, snapshot, candidate_path = _published_v2_with_active(tmp_path)

    def make_analysis_eligible(payload):  # noqa: ANN001
        payload["promotion_eligibility"]["eligible"] = True
        payload["blocking_reasons"] = []

    _rewrite_result_and_hash(candidate_path, make_analysis_eligible)

    def make_candidate_eligible(payload):  # noqa: ANN001
        payload["promotion_eligible"] = True
        payload["blocking_reasons"] = []

    _rewrite_manifest(candidate_path, make_candidate_eligible)
    result_path = candidate_path / "result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["promotion_eligible"] = True
    result["blocking_reasons"] = []
    result_path.write_text(json.dumps(result), encoding="utf-8")

    candidate = repository.read_candidate("integrity-candidate")
    promoted = ModelPromotionService(
        repository, lambda: snapshot
    ).promote("integrity-candidate", expected_revision=1)

    assert candidate.manifest.analysis_artifacts
    assert promoted.status == "active"
    assert repository.read_active().candidate_id == "integrity-candidate"
