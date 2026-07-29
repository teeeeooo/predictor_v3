"""Lifecycle protection graph and read-only retention preview policy."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .canonical import canonical_payload, content_sha256, require_safe_identity
from .contracts import RETENTION_PREVIEW_VERSION


@dataclass(frozen=True)
class ArtifactNode:
    artifact_id: str
    artifact_class: str
    created_at: str
    size_bytes: int
    age_days: int = 0
    pinned: bool = False
    hold: str = ""
    version_disposition: str = "current_and_executable"
    source_artifact_identity: str = ""


@dataclass(frozen=True)
class ArtifactReference:
    source_id: str
    target_id: str
    reason_code: str
    active: bool = True
    completeness: str = "complete"


@dataclass(frozen=True)
class RetentionPolicy:
    minimum_age_days: int = 30
    keep_latest_count: int = 5
    maximum_reclaim_bytes: int = 0


PROTECTION_REASONS = {
    "current_active",
    "loaded_predict_model",
    "active_history",
    "deployment_export",
    "campaign_in_progress",
    "campaign_resumable",
    "campaign_incumbent",
    "selected_recommendation",
    "confirmation_snapshot",
    "confirmation_candidate",
    "final_decision_evidence",
    "unresolved_migration",
    "user_pin",
    "audit_hold",
    "legal_hold",
    "manual_hold",
    "unknown_version",
    "unsupported_version",
    "loaded_model_lease_missing",
    "loaded_model_lease_expired",
    "loaded_model_lease_unknown",
    "reference_graph_incomplete",
    "run_candidate",
    "campaign_proposal",
    "campaign_attempt",
    "attempt_run",
    "campaign_gate",
    "gate_candidate",
    "campaign_leaderboard",
    "campaign_recommendation",
    "snapshot_materialized_data",
    "locked_final_test_evidence",
    "confirmation_final_test",
}


def build_retention_preview(
    *,
    nodes: list[ArtifactNode],
    references: list[ArtifactReference],
    policy: RetentionPolicy,
    reference_complete: bool,
    loaded_model_lease_status: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    _validate_policy(policy)
    by_id = {_node_identity(item): item for item in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("retention inventory contains duplicate artifact identities")
    incoming: dict[str, list[ArtifactReference]] = {
        identity: [] for identity in by_id
    }
    outgoing: dict[str, list[ArtifactReference]] = {
        identity: [] for identity in by_id
    }
    graph_incomplete = not reference_complete
    for reference in references:
        require_safe_identity(reference.source_id, "retention reference source")
        require_safe_identity(reference.target_id, "retention reference target")
        if (
            reference.target_id not in by_id
            or reference.completeness != "complete"
        ):
            graph_incomplete = True
        elif reference.active:
            incoming[reference.target_id].append(reference)
            if reference.source_id in outgoing:
                outgoing[reference.source_id].append(reference)
    lease_reason = {
        "current": "",
        "missing": "loaded_model_lease_missing",
        "expired": "loaded_model_lease_expired",
        "unknown": "loaded_model_lease_unknown",
    }.get(loaded_model_lease_status)
    if lease_reason is None:
        raise ValueError("loaded model lease disposition is invalid")
    entries = []
    ordered = sorted(
        nodes,
        key=lambda item: (item.artifact_class, item.created_at, item.artifact_id),
        reverse=True,
    )
    class_rank: dict[str, int] = {}
    reclaim_total = 0
    for node in ordered:
        class_rank[node.artifact_class] = class_rank.get(node.artifact_class, 0) + 1
        reasons = {
            reference.reason_code
            for reference in incoming[node.artifact_id]
        }
        if node.pinned:
            reasons.add("user_pin")
        if node.hold:
            reasons.add(
                node.hold
                if node.hold in {"audit_hold", "legal_hold", "manual_hold"}
                else "manual_hold"
            )
        if node.version_disposition in {
            "unsupported_future_version",
            "corrupt_or_incomplete",
        }:
            reasons.add(
                "unsupported_version"
                if node.version_disposition == "unsupported_future_version"
                else "unknown_version"
            )
        if graph_incomplete:
            reasons.add("reference_graph_incomplete")
        if lease_reason:
            reasons.add(lease_reason)
        policy_eligible = (
            node.age_days >= policy.minimum_age_days
            and class_rank[node.artifact_class] > policy.keep_latest_count
        )
        eligible = policy_eligible and not reasons
        if (
            eligible
            and policy.maximum_reclaim_bytes
            and reclaim_total + node.size_bytes > policy.maximum_reclaim_bytes
        ):
            eligible = False
            reasons.add("preview_reclaim_bound_exceeded")
        if eligible:
            reclaim_total += node.size_bytes
        entries.append({
            "artifact_id": node.artifact_id,
            "artifact_class": node.artifact_class,
            "size_bytes": node.size_bytes,
            "referenced": bool(incoming[node.artifact_id]),
            "protected": bool(reasons),
            "preservation_reason_codes": sorted(reasons),
            "policy_eligible": policy_eligible,
            "disposition": "eligible" if eligible else "blocked",
            "reference_completeness": (
                "complete" if not graph_incomplete else "incomplete"
            ),
            "incoming_references": sorted(
                [asdict(item) for item in incoming[node.artifact_id]],
                key=lambda item: (
                    item["source_id"], item["target_id"], item["reason_code"]
                ),
            ),
            "outgoing_references": sorted(
                [asdict(item) for item in outgoing[node.artifact_id]],
                key=lambda item: (
                    item["source_id"], item["target_id"], item["reason_code"]
                ),
            ),
        })
    ordered_nodes = sorted(
        (asdict(item) for item in nodes),
        key=lambda item: (item["artifact_class"], item["artifact_id"]),
    )
    ordered_references = sorted(
        (asdict(item) for item in references),
        key=lambda item: (
            item["source_id"], item["target_id"], item["reason_code"]
        ),
    )
    identity_input = {
        "nodes": ordered_nodes,
        "references": ordered_references,
        "policy": asdict(policy),
        "reference_complete": reference_complete,
        "loaded_model_lease_status": loaded_model_lease_status,
    }
    preview_id = f"retention-preview-{content_sha256(identity_input)}"
    return canonical_payload({
        "schema_version": RETENTION_PREVIEW_VERSION,
        "preview_id": preview_id,
        "created_at": f"content-addressed:{preview_id}",
        "policy": asdict(policy),
        "reference_complete": not graph_incomplete,
        "loaded_model_lease_status": loaded_model_lease_status,
        "entries": entries,
        "nodes": ordered_nodes,
        "references": ordered_references,
        "eligible_reclaim_bytes": reclaim_total,
        "delete_authority": False,
        "apply_implemented": False,
    })


def _node_identity(node: ArtifactNode) -> str:
    require_safe_identity(node.artifact_id, "retention artifact identity")
    if (
        type(node.size_bytes) is not int
        or node.size_bytes < 0
        or type(node.age_days) is not int
        or node.age_days < 0
        or not node.artifact_class
        or not node.created_at
    ):
        raise ValueError("retention artifact metadata is invalid")
    return node.artifact_id


def _validate_policy(policy: RetentionPolicy) -> None:
    if (
        type(policy.minimum_age_days) is not int
        or policy.minimum_age_days < 0
        or type(policy.keep_latest_count) is not int
        or policy.keep_latest_count < 0
        or type(policy.maximum_reclaim_bytes) is not int
        or policy.maximum_reclaim_bytes < 0
    ):
        raise ValueError("retention policy values must be bounded non-negative integers")
