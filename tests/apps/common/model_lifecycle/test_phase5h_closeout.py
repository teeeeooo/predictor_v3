from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from apps.common.model_lifecycle.closeout.compatibility import (
    CORRUPT_INCOMPLETE,
    UNSUPPORTED_FUTURE,
    inspect_persisted_contract,
)
from apps.common.model_lifecycle.closeout.contracts import (
    build_locked_final_test,
    build_snapshot_record,
)
from apps.common.model_lifecycle.closeout.loaded_model_lease import (
    inspect_loaded_model_leases,
)
from apps.common.model_lifecycle.closeout.migration import preview_migration
from apps.common.model_lifecycle.closeout.retention import (
    ArtifactNode,
    RetentionPolicy,
    build_retention_preview,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore

HASH = "a" * 64
NOW = "2026-07-27T00:00:00+00:00"


def _meaning(training_data: dict) -> dict:
    return {
        "recommendation": {"id": "rec-1"},
        "campaign": {"id": "campaign-1"},
        "selected_candidate": {"candidate_id": "candidate-1"},
        "source_run": {"run_id": "run-1"},
        "candidate_artifacts": {
            "manifest.json": {"sha256": HASH, "size_bytes": 1},
        },
        "resolved_specification": {"fixed": True},
        "specification_fingerprint": HASH,
        "definition_runtime": {"generation_id": "generation-1"},
        "target_roles": {"production_required": ["target-1"]},
        "feature_contract": {"ordered": ["feature-1"]},
        "evaluation_contract": {"metric": "r2"},
        "training_configuration": {"selected_parameters": {}},
        "baseline": {"active_revision": 0},
        "build_identity": {"commit": "build-1"},
        "training_semantic_identity": HASH,
        "training_data": training_data,
    }


def test_snapshot_identity_is_canonical_and_owned_bytes_survive_source_change(
    tmp_path: Path,
) -> None:
    source = tmp_path / "training.csv"
    source.write_text("feature,target\n1,2\n3,4\n", encoding="utf-8")
    store = LifecycleCloseoutStore(tmp_path / "lifecycle")
    materialized = store.materialize_local_source(
        source,
        filtering_meaning={"selection": "all", "row_order": "source"},
    )
    first = build_snapshot_record(
        _meaning(materialized), created_at=NOW, actor_kind="user"
    )
    second = build_snapshot_record(
        dict(reversed(list(_meaning(materialized).items()))),
        created_at="2026-07-28T00:00:00+00:00",
        actor_kind="operator",
    )
    assert first["snapshot_id"] == second["snapshot_id"]

    source.write_text("feature,target\n9,9\n", encoding="utf-8")
    owned = store.owned_materialization_path(
        materialized["materialized_identity"]
    )
    assert hashlib.sha256(owned.read_bytes()).hexdigest() == (
        materialized["content_sha256"]
    )


def test_partial_nonfinite_and_unverified_external_snapshots_fail_closed(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="incomplete"):
        build_snapshot_record({}, created_at=NOW, actor_kind="user")
    incomplete = _meaning({
        "materialization_kind": "owned_source_bytes",
        "content_sha256": HASH,
        "ordered_row_set_sha256": HASH,
        "row_count": 1,
        "column_count": 1,
    })
    incomplete["evaluation_contract"] = {"metric": float("nan")}
    with pytest.raises(ValueError, match="finite"):
        build_snapshot_record(incomplete, created_at=NOW, actor_kind="user")
    store = LifecycleCloseoutStore(tmp_path / "lifecycle")
    with pytest.raises(ValueError, match="cannot prove preservation"):
        store.validate_external_reference({
            "object_version_id": "object-v1",
            "content_sha256": HASH,
            "size_bytes": 1,
            "schema_columns": ["x"],
            "row_count": 1,
            "column_count": 1,
            "ordered_row_set_sha256": HASH,
            "filtering_meaning": {},
            "retrievability_verified_until": NOW,
            "retrievability_verified": False,
            "independent_row_meaning_preserved": True,
        })


def test_locked_final_test_is_single_use(tmp_path: Path) -> None:
    store = LifecycleCloseoutStore(tmp_path / "lifecycle")
    seal = build_locked_final_test(
        seal_id="seal-1",
        data_sha256=HASH,
        ordered_membership_sha256=HASH,
        target_identities=["target-1"],
        split_policy="unseen external holdout",
        created_at=NOW,
        creation_identity="campaign-preselection",
        created_before_selection=True,
    )
    store.write_locked_final_test(seal)
    consumed = store.consume_locked_final_test(
        "seal-1", confirmation_id="confirmation-1", consumed_at=NOW
    )
    assert consumed["status"] == "consumed"
    assert store.read_locked_final_test("seal-1")["status"] == "consumed"
    with pytest.raises(ValueError, match="already consumed"):
        store.consume_locked_final_test(
            "seal-1", confirmation_id="confirmation-2", consumed_at=NOW
        )


def test_compatibility_and_previews_are_read_only_and_fail_closed() -> None:
    future = inspect_persisted_contract(
        "snapshot", {"schema_version": "predictor_v3.confirmation_snapshot.v2"}
    )
    assert future.status == UNSUPPORTED_FUTURE
    corrupt = inspect_persisted_contract("snapshot", {})
    assert corrupt.status == CORRUPT_INCOMPLETE

    source = {"schema_version": "legacy.v1", "meaning": {"old": True}}
    before = repr(source)
    migration = preview_migration(
        artifact_kind="run",
        payload=source,
        source_sha256=HASH,
        proposed_contract_version="predictor_v3.experiment_run.v1",
        created_at=NOW,
    )
    assert migration["apply_implemented"] is False
    assert repr(source) == before

    preview = build_retention_preview(
        nodes=[ArtifactNode("candidate-1", "candidate", NOW, 100, age_days=100)],
        references=[],
        policy=RetentionPolicy(minimum_age_days=0, keep_latest_count=0),
        reference_complete=False,
        loaded_model_lease_status="missing",
        created_at=NOW,
    )
    assert preview["entries"][0]["disposition"] == "blocked"
    assert "reference_graph_incomplete" in preview["entries"][0][
        "preservation_reason_codes"
    ]
    assert inspect_loaded_model_leases([], now=NOW)[0] == "missing"
