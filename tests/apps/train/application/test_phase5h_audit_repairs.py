from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import joblib
import pytest

from apps.common.model_lifecycle.closeout.canonical import (
    content_sha256,
    file_sha256,
)
from apps.common.model_lifecycle.closeout.contracts import (
    build_locked_final_test,
)
from apps.common.model_lifecycle.closeout.migration import preview_migration
from apps.common.model_lifecycle.closeout.retention import (
    ArtifactNode,
    ArtifactReference,
    RetentionPolicy,
    build_retention_preview,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.train.application.confirmation.locked_test_evaluator import (
    LockedFinalTestEvaluator,
)
from apps.train.application.confirmation.promotion_policy import (
    RecommendationPromotionAuthorization,
)
from apps.train.application.confirmation.snapshot_evidence import (
    candidate_artifacts,
    directory_artifacts,
    specification_fingerprint,
)
from apps.train.application.confirmation.snapshot_integrity import (
    SnapshotIntegrityValidator,
)
from apps.train.application.confirmation.retention import (
    LifecycleRetentionApplicationService,
)

NOW = "2026-07-28T00:00:00+00:00"
HASH = "a" * 64


def _membership(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        next(reader)
        for row in reader:
            digest.update(
                json.dumps(row, separators=(",", ":")).encode("utf-8")
            )
            digest.update(b"\n")
    return digest.hexdigest()


def test_captured_candidate_and_definition_bytes_are_revalidated(
    tmp_path: Path,
) -> None:
    root = tmp_path / "lifecycle"
    candidate_path = root / "candidates" / "selected-1"
    candidate_path.mkdir(parents=True)
    for name, content in (
        ("manifest.json", "{}\n"),
        ("result.json", "{}\n"),
        ("model.pkl", "model"),
    ):
        (candidate_path / name).write_text(content, encoding="utf-8")
    manifest = SimpleNamespace(
        analysis_artifacts=(),
        model_sha256=file_sha256(candidate_path / "model.pkl"),
    )
    candidate = SimpleNamespace(path=candidate_path, manifest=manifest)
    generation_path = tmp_path / "generation-1"
    generation_path.mkdir()
    (generation_path / "manifest.json").write_text("{}\n", encoding="utf-8")
    generation = SimpleNamespace(path=generation_path)
    source = tmp_path / "training.csv"
    source.write_text("x,target\n1,2\n", encoding="utf-8")
    store = LifecycleCloseoutStore(root)
    data_request = {"source_path": str(source)}
    training_data = store.materialize_local_source(
        source,
        filtering_meaning={
            "selection": data_request,
            "preprocessing": {},
            "row_filter_owner": "core.ml.training.load_and_preprocess",
        },
        expected_content_sha256=file_sha256(source),
    )
    specification = {"data": data_request}
    run = {
        "run_id": "run-1",
        "contract_identity": {
            "data_sha256": file_sha256(source),
            "data_request": data_request,
        },
    }
    campaign = {"campaign_id": "campaign-1"}
    recommendation = {"recommendation_id": "recommendation-1"}
    experiments = SimpleNamespace(
        read_run=lambda _identity: run,
        read_campaign=lambda _identity: campaign,
        read_campaign_evidence=lambda *_args: recommendation,
    )
    repository = SimpleNamespace(
        root=root,
        read_candidate=lambda _identity: candidate,
    )
    generations = SimpleNamespace(
        active_generation_id=lambda: "generation-1",
        read_generation=lambda _identity: generation,
    )
    validator = SnapshotIntegrityValidator(
        repository, generations, store
    )
    validator._experiments = experiments  # noqa: SLF001
    meaning = {
        "selected_candidate": {
            "candidate_id": "selected-1",
            "manifest_sha256": file_sha256(candidate_path / "manifest.json"),
            "model_sha256": manifest.model_sha256,
        },
        "candidate_artifacts": candidate_artifacts(
            candidate_path, manifest
        ),
        "definition_runtime": {
            "generation_id": "generation-1",
            "bundle_files": directory_artifacts(generation_path),
        },
        "source_run": {
            "run_id": "run-1",
            "sha256": content_sha256(run),
        },
        "resolved_specification": specification,
        "specification_fingerprint": specification_fingerprint(specification),
        "campaign": {
            "campaign_id": "campaign-1",
            "sha256": content_sha256(campaign),
        },
        "recommendation": {
            "recommendation_id": "recommendation-1",
            "sha256": content_sha256(recommendation),
        },
        "training_data": training_data,
    }
    validator.validate(meaning)
    (candidate_path / "result.json").write_text('{"changed":true}\n')
    with pytest.raises(ValueError, match="Candidate artifacts"):
        validator.validate(meaning)


def test_locked_final_test_actual_evaluation_and_immutable_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "lifecycle"
    candidate_path = root / "candidates" / "confirmed-1"
    candidate_path.mkdir(parents=True)
    joblib.dump({}, candidate_path / "model.pkl")
    (candidate_path / "manifest.json").write_text("{}\n")
    targets = (
        SimpleNamespace(identity="target-a", ml_name="ml-a"),
        SimpleNamespace(identity="target-b", ml_name="ml-b"),
    )
    candidate = SimpleNamespace(
        path=candidate_path,
        manifest=SimpleNamespace(
            definition_generation_id="generation-1",
            targets=targets,
        ),
    )
    repository = SimpleNamespace(
        read_candidate=lambda _identity: candidate
    )
    generations = SimpleNamespace(
        read_generation=lambda _identity: object()
    )
    runtime = SimpleNamespace(
        target_result_keys=(("ml-a", "truth-a"), ("ml-b", "truth-b")),
        derived=None,
        zero_fill_policy_by_ml_name={},
        ordered_input_ml_names=("x",),
    )
    monkeypatch.setattr(
        "apps.train.application.confirmation.locked_test_evaluator."
        "build_predict_runtime_snapshot",
        lambda _generation: runtime,
    )
    monkeypatch.setattr(
        "apps.train.application.confirmation.locked_test_evaluator.predict_row",
        lambda _model, row, **_kwargs: {
            "ml-a": float(row["truth-a"]),
            "ml-b": float(row["truth-b"]),
        },
    )
    dataset = tmp_path / "locked.csv"
    dataset.write_text(
        "x,truth-a,truth-b\n1,2,4\n2,4,8\n3,6,12\n",
        encoding="utf-8",
    )
    seal = build_locked_final_test(
        data_sha256=file_sha256(dataset),
        ordered_membership_sha256=_membership(dataset),
        target_identities=["target-a", "target-b"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection",
        evaluation_contract={
            "metric_contract": HASH,
            "schema_contract": HASH,
            "pass_thresholds": {
                "target-a": {
                    "r2": {"direction": "minimum", "value": 0.9}
                }
            },
        },
        required_source_hashes={"snapshot": HASH},
        dataset_reference={
            "path": str(dataset),
            "sha256": file_sha256(dataset),
        },
        created_before_selection=True,
    )
    store = LifecycleCloseoutStore(root)
    store.write_locked_final_test(seal)
    store.consume_locked_final_test(
        seal["seal_id"],
        confirmation_id="confirmation-1",
        consumed_at=NOW,
    )
    evaluator = LockedFinalTestEvaluator(
        repository,
        generations,
        store,
        clock=lambda: SimpleNamespace(isoformat=lambda: NOW),
    )
    result = evaluator.evaluate(
        seal,
        confirmation_id="confirmation-1",
        candidate_id="confirmed-1",
    )
    assert result["passed"] is True
    assert result["target_results"][0]["metrics"]["rmse"] == 0.0
    result_path = (
        store.locked_test_results / result["result_id"] / "result.json"
    )
    before = result_path.read_bytes()
    assert evaluator.evaluate(
        seal,
        confirmation_id="confirmation-1",
        candidate_id="confirmed-1",
    ) == result
    assert result_path.read_bytes() == before
    assert store.read_locked_final_test(seal["seal_id"])["status"] == "consumed"

    monkeypatch.setattr(
        "apps.train.application.confirmation.locked_test_evaluator.predict_row",
        lambda _model, _row, **_kwargs: {"ml-a": 0.0, "ml-b": 0.0},
    )
    failed_seal = build_locked_final_test(
        data_sha256=file_sha256(dataset),
        ordered_membership_sha256=_membership(dataset),
        target_identities=["target-a", "target-b"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection-retry",
        evaluation_contract={
            "metric_contract": "b" * 64,
            "schema_contract": HASH,
            "pass_thresholds": {
                "target-a": {
                    "r2": {"direction": "minimum", "value": 0.9}
                }
            },
        },
        required_source_hashes={"snapshot": HASH},
        dataset_reference={
            "path": str(dataset),
            "sha256": file_sha256(dataset),
        },
        created_before_selection=True,
    )
    store.write_locked_final_test(failed_seal)
    store.consume_locked_final_test(
        failed_seal["seal_id"],
        confirmation_id="confirmation-2",
        consumed_at=NOW,
    )
    failed = evaluator.evaluate(
        failed_seal,
        confirmation_id="confirmation-2",
        candidate_id="confirmed-1",
    )
    assert failed["passed"] is False


def test_incompatible_seal_blocks_before_consumption(tmp_path: Path) -> None:
    dataset = tmp_path / "locked.csv"
    dataset.write_text("x,target\n1,2\n", encoding="utf-8")
    meaning = {
        "target_roles": {"production_required": ["target-a"]},
        "training_data": {"content_sha256": HASH},
        "definition_runtime": {"bundle_files": {"manifest.json": {"sha256": HASH}}},
        "evaluation_contract": {"metric": "r2"},
        "feature_contract": {"ordered": ["x"]},
    }
    snapshot = {"snapshot_id": "snapshot-1", "meaning": meaning}
    seal = build_locked_final_test(
        data_sha256=file_sha256(dataset),
        ordered_membership_sha256=_membership(dataset),
        target_identities=["target-b"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection",
        evaluation_contract={
            "metric_contract": content_sha256(meaning["evaluation_contract"]),
            "schema_contract": content_sha256({
                "targets": meaning["target_roles"],
                "features": meaning["feature_contract"],
            }),
        },
        required_source_hashes={
            "snapshot": content_sha256(snapshot),
            "training_data": HASH,
            "definition_bundle": content_sha256(
                meaning["definition_runtime"]["bundle_files"]
            ),
            "evaluation_contract": content_sha256(
                meaning["evaluation_contract"]
            ),
        },
        dataset_reference={
            "path": str(dataset),
            "sha256": file_sha256(dataset),
        },
        created_before_selection=True,
    )
    store = LifecycleCloseoutStore(tmp_path / "lifecycle")
    store.write_locked_final_test(seal)
    evaluator = LockedFinalTestEvaluator(
        SimpleNamespace(),
        SimpleNamespace(),
        store,
        clock=lambda: SimpleNamespace(isoformat=lambda: NOW),
    )
    with pytest.raises(ValueError, match="Target order"):
        evaluator.preflight(seal, snapshot)
    assert store.read_locked_final_test(seal["seal_id"])["status"] == "sealed"
    compatible = build_locked_final_test(
        data_sha256=file_sha256(dataset),
        ordered_membership_sha256=_membership(dataset),
        target_identities=["target-a"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection-compatible",
        evaluation_contract=seal["evaluation_contract"],
        required_source_hashes=seal["required_source_hashes"],
        dataset_reference=seal["dataset_reference"],
        created_before_selection=True,
    )
    evaluator.preflight(compatible, snapshot)


def test_orphan_confirmation_candidate_is_never_generic_promotable(
    tmp_path: Path,
) -> None:
    policy = RecommendationPromotionAuthorization(tmp_path)
    policy._experiments = SimpleNamespace(list_campaigns=lambda: ())  # noqa: SLF001
    policy._repository = SimpleNamespace(  # noqa: SLF001
        read_candidate=lambda _identity: SimpleNamespace(
            manifest=SimpleNamespace(source="confirmation")
        )
    )
    assert policy.review("orphan-1", "user-promotion", 0) == (
        False,
        "confirmation_linkage_incomplete",
    )


def test_retention_graph_exposes_required_nodes_and_true_references() -> None:
    classes = (
        "candidate", "active", "active_history", "deployment_export",
        "loaded_model_lease", "run", "campaign", "proposal", "attempt",
        "gate", "leaderboard", "recommendation", "confirmation_snapshot",
        "materialized_blob", "confirmation", "locked_final_test_seal",
        "locked_final_test_result", "final_decision", "promotion_linkage",
        "migration_source", "migration_preview", "pin", "audit_hold",
    )
    nodes = [
        ArtifactNode(
            f"node-{index}", kind, NOW, 1,
            source_artifact_identity=f"source:{kind}:{index}",
        )
        for index, kind in enumerate(classes)
    ]
    references = [
        ArtifactReference("node-20", "node-19", "unresolved_migration"),
        ArtifactReference("node-16", "node-15", "locked_final_test_evidence"),
    ]
    preview = build_retention_preview(
        nodes=nodes,
        references=references,
        policy=RetentionPolicy(),
        reference_complete=False,
        loaded_model_lease_status="missing",
    )
    assert {item["artifact_class"] for item in preview["nodes"]} == set(classes)
    assert all(item["source_artifact_identity"] for item in preview["nodes"])
    assert all(
        item["source_id"] != item["target_id"]
        for item in preview["references"]
    )
    migration_entry = next(
        item for item in preview["entries"]
        if item["artifact_class"] == "migration_source"
    )
    assert migration_entry["incoming_references"][0]["source_id"] == "node-20"


def test_preview_reconstruction_reuses_exact_persisted_bytes(
    tmp_path: Path,
) -> None:
    payload = preview_migration(
        artifact_kind="run",
        payload={"schema_version": "legacy.v1"},
        source_sha256=HASH,
        proposed_contract_version="current.v1",
    )
    first = LifecycleCloseoutStore(tmp_path)
    first_path = first.write_migration_preview(payload)
    before = first_path.read_bytes()
    second = LifecycleCloseoutStore(tmp_path)
    second_path = second.write_migration_preview(
        preview_migration(
            artifact_kind="run",
            payload={"schema_version": "legacy.v1"},
            source_sha256=HASH,
            proposed_contract_version="current.v1",
        )
    )
    assert second_path == first_path
    assert second_path.read_bytes() == before
    with ThreadPoolExecutor(max_workers=2) as pool:
        paths = list(pool.map(
            lambda _index: LifecycleCloseoutStore(
                tmp_path
            ).write_migration_preview(payload),
            range(2),
        ))
    assert paths == [first_path, first_path]
    assert first_path.read_bytes() == before


def test_retention_service_keeps_missing_deployment_index_visible_and_stable(
    tmp_path: Path,
) -> None:
    repository = SimpleNamespace(
        root=tmp_path,
        active_reference_path=tmp_path / "active_model.json",
        list_candidates=lambda: (),
        read_active=lambda optional=False: None,
    )
    first = LifecycleRetentionApplicationService(
        repository,
        clock=lambda: SimpleNamespace(
            isoformat=lambda: NOW,
        ),
    ).preview(RetentionPolicy())
    second = LifecycleRetentionApplicationService(
        repository,
        clock=lambda: SimpleNamespace(
            isoformat=lambda: "2036-12-31T23:59:59+00:00",
        ),
    ).preview(RetentionPolicy())
    assert first == second
    deployment = next(
        item for item in first["nodes"]
        if item["artifact_class"] == "deployment_export"
    )
    assert deployment["source_artifact_identity"] == (
        "missing:deployment-export-index"
    )
    assert first["reference_complete"] is False
    assert all(item["disposition"] == "blocked" for item in first["entries"])


def test_retention_populated_synthetic_inventory_is_clock_independent(
    tmp_path: Path,
) -> None:
    repository = SimpleNamespace(
        root=tmp_path,
        active_reference_path=tmp_path / "active_model.json",
        list_candidates=lambda: (),
        read_active=lambda optional=False: None,
    )
    campaign = {
        "schema_version": "predictor_v3.agent_campaign.v1",
        "campaign_id": "campaign-stable",
        "status": "completed",
        "created_at": NOW,
        "proposals": [{"proposal_id": "proposal-stable"}],
        "attempt_history": [{"iteration": 1, "run_id": "run-stable"}],
        "gates": [{"candidate_id": "candidate-stable"}],
        "leaderboard": [],
        "incumbent_candidate_id": "candidate-stable",
        "recommendations": [{
            "recommendation_id": "recommendation-stable",
            "recommended_candidate": {"candidate_id": "candidate-stable"},
        }],
    }

    def build(clock_value: str) -> LifecycleRetentionApplicationService:
        service = LifecycleRetentionApplicationService(
            repository,
            clock=lambda: SimpleNamespace(
                isoformat=lambda: clock_value,
            ),
        )
        service._experiments = SimpleNamespace(  # noqa: SLF001
            runs=tmp_path / "runs",
            campaigns=tmp_path / "campaigns",
            list_campaigns=lambda: (campaign,),
        )
        return service

    first = build(NOW).preview(RetentionPolicy())
    path = (
        tmp_path / "closeout" / "retention_previews"
        / first["preview_id"] / "preview.json"
    )
    before = path.read_bytes()
    second = build("2046-01-01T00:00:00+00:00").preview(
        RetentionPolicy()
    )
    assert second == first
    assert path.read_bytes() == before
    assert {
        node["artifact_class"] for node in first["nodes"]
    }.issuperset({"proposal", "attempt", "gate", "leaderboard"})
    assert all(
        node["created_at"] != "2046-01-01T00:00:00+00:00"
        for node in first["nodes"]
    )

    campaign["gates"].append({"candidate_id": "candidate-changed"})
    changed = build("2056-01-01T00:00:00+00:00").preview(
        RetentionPolicy()
    )
    assert changed["preview_id"] != first["preview_id"]
