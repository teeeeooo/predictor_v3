"""Closeout, migration, seal, pin, and hold retention inventory."""

from __future__ import annotations

from datetime import datetime
import json

from apps.common.model_lifecycle.closeout.canonical import file_sha256
from apps.common.model_lifecycle.closeout.retention import (
    ArtifactNode,
    ArtifactReference,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore

from .retention_nodes import age_days, record_node, raw_node


def closeout_inventory(
    store: LifecycleCloseoutStore, now: datetime
) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
    nodes: list[ArtifactNode] = []
    references: list[ArtifactReference] = []
    try:
        records = _records(store)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return nodes, references, False
    complete = _snapshot_nodes(
        store, records["snapshots"], nodes, references, now
    )
    complete = _confirmation_nodes(
        store, records["confirmations"], nodes, references, now
    ) and complete
    complete = _decision_nodes(
        store, records["decisions"], nodes, references, now
    ) and complete
    complete = _migration_nodes(
        store, records["migration_previews"], nodes, references, now
    ) and complete
    _locked_test_nodes(store, records, nodes, references, now)
    hold_nodes, hold_references, hold_complete = hold_inventory(store, now)
    nodes.extend(hold_nodes)
    references.extend(hold_references)
    return nodes, references, complete and hold_complete


def _records(store: LifecycleCloseoutStore) -> dict[str, tuple[dict, ...]]:
    return {
        "snapshots": store.list_records(store.snapshots, "snapshot.json"),
        "confirmations": store.list_records(
            store.confirmations, "confirmation.json"
        ),
        "decisions": store.list_records(store.decisions, "decision.json"),
        "migration_previews": store.list_records(
            store.migration_previews, "preview.json"
        ),
        "seals": store.list_records(store.locked_tests, "seal.json"),
        "locked_results": store.list_records(
            store.locked_test_results, "result.json"
        ),
    }


def _snapshot_nodes(store, records, nodes, references, now) -> bool:  # noqa: ANN001
    complete = True
    for raw in records:
        try:
            value = store.read_snapshot(raw["snapshot_id"])
            identity = value["snapshot_id"]
            nodes.append(record_node(
                identity, "confirmation_snapshot", value,
                store.snapshots / identity, now, "snapshot",
            ))
            references.append(ArtifactReference(
                identity,
                value["meaning"]["selected_candidate"]["candidate_id"],
                "confirmation_snapshot",
            ))
            data = value["meaning"]["training_data"]
            blob_id = f"materialized-{data['content_sha256']}"
            blob_path = store.owned_materialization_path(
                data["materialized_identity"]
            )
            if not any(item.artifact_id == blob_id for item in nodes):
                nodes.append(ArtifactNode(
                    blob_id, "materialized_blob", value["created_at"],
                    blob_path.stat().st_size,
                    age_days(value["created_at"], now),
                    source_artifact_identity=str(blob_path),
                ))
            references.append(ArtifactReference(
                identity, blob_id, "snapshot_materialized_data"
            ))
        except (KeyError, OSError, TypeError, ValueError):
            complete = False
    return complete


def _confirmation_nodes(store, records, nodes, references, now) -> bool:  # noqa: ANN001
    complete = True
    for initial in records:
        try:
            value = store.read_confirmation(initial["confirmation_id"])
            identity = value["confirmation_id"]
            nodes.append(record_node(
                identity, "confirmation", value,
                store.confirmations / identity, now, "confirmation",
            ))
            references.append(ArtifactReference(
                identity, value["snapshot_id"], "confirmation_snapshot"
            ))
            if value.get("confirmation_candidate_id"):
                references.append(ArtifactReference(
                    identity,
                    value["confirmation_candidate_id"],
                    "confirmation_candidate",
                ))
            if value["status"] in {"promoted", "promotion-blocked"}:
                linkage = f"promotion-{identity}"
                nodes.append(ArtifactNode(
                    linkage, "promotion_linkage", value["updated_at"], 0,
                    source_artifact_identity=(
                        f"{store.confirmations / identity}/history"
                    ),
                ))
                references.append(ArtifactReference(
                    linkage, identity, "final_decision_evidence"
                ))
        except (KeyError, OSError, TypeError, ValueError):
            complete = False
    return complete


def _decision_nodes(store, records, nodes, references, now) -> bool:  # noqa: ANN001
    complete = True
    for value in records:
        try:
            identity = value["decision_id"]
            nodes.append(record_node(
                identity, "final_decision", value,
                store.decisions / identity, now, "final_decision",
            ))
            references.extend((
                ArtifactReference(
                    identity, value["confirmation_id"],
                    "final_decision_evidence",
                ),
                ArtifactReference(
                    identity, value["candidate_id"], "final_decision_evidence"
                ),
            ))
        except (KeyError, OSError, TypeError, ValueError):
            complete = False
    return complete


def _migration_nodes(store, records, nodes, references, now) -> bool:  # noqa: ANN001
    complete = True
    for value in records:
        try:
            identity = value["preview_id"]
            nodes.append(raw_node(
                identity, "migration_preview", value,
                store.migration_previews / identity, now,
            ))
            digest = value["source_identity"]["sha256"]
            source_id = f"migration-source-{digest}"
            if not any(item.artifact_id == source_id for item in nodes):
                nodes.append(ArtifactNode(
                    source_id, "migration_source",
                    str(value.get("created_at", now.isoformat())), 0,
                    version_disposition=value["source_disposition"],
                    source_artifact_identity=f"sha256:{digest}",
                ))
            references.append(ArtifactReference(
                identity, source_id, "unresolved_migration"
            ))
        except (KeyError, OSError, TypeError, ValueError):
            complete = False
    return complete


def _locked_test_nodes(store, records, nodes, references, now) -> None:  # noqa: ANN001
    for value in records["seals"]:
        identity = value["seal_id"]
        nodes.append(raw_node(
            identity, "locked_final_test_seal", value,
            store.locked_tests / identity, now,
        ))
    for value in records["locked_results"]:
        identity = value["result_id"]
        nodes.append(raw_node(
            identity, "locked_final_test_result", value,
            store.locked_test_results / identity, now,
        ))
        references.extend((
            ArtifactReference(
                identity, value["seal_id"], "locked_final_test_evidence"
            ),
            ArtifactReference(
                identity, value["confirmation_id"], "confirmation_final_test"
            ),
        ))


def hold_inventory(
    store: LifecycleCloseoutStore, now: datetime
) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
    nodes: list[ArtifactNode] = []
    references: list[ArtifactReference] = []
    complete = True
    for root, artifact_class, default_reason in (
        (store.pins, "pin", "user_pin"),
        (store.holds, "hold", "manual_hold"),
    ):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.json")):
            try:
                if path.is_symlink() or not path.is_file():
                    raise ValueError("unsafe hold record")
                payload = json.loads(path.read_text(encoding="utf-8"))
                reason = payload.get("reason_code", default_reason)
                if reason not in {
                    "user_pin", "audit_hold", "legal_hold", "manual_hold"
                }:
                    reason = default_reason
                identity = f"{artifact_class}-{file_sha256(path)[:24]}"
                nodes.append(ArtifactNode(
                    identity, artifact_class,
                    str(payload.get("created_at", now.isoformat())),
                    path.stat().st_size,
                    pinned=reason == "user_pin",
                    hold=reason if reason != "user_pin" else "",
                    source_artifact_identity=str(path),
                ))
                references.append(ArtifactReference(
                    identity, payload["artifact_id"], reason
                ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
    return nodes, references, complete
