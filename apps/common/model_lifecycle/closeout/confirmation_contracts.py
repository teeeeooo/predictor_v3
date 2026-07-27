"""Confirmation execution and explicit final-decision contracts."""

from __future__ import annotations

from typing import Any

from .canonical import canonical_payload, require_safe_identity, require_sha256
from .contract_validation import identity_array, require_object, required_text
from .contracts import (
    CONFIRMATION_STATES,
    CONFIRMATION_VERSION,
    DECISION_STATES,
    FINAL_DECISION_VERSION,
)


def build_confirmation_record(
    *,
    confirmation_id: str,
    snapshot_id: str,
    selected_candidate_id: str,
    status: str,
    created_at: str,
    updated_at: str,
    production_required_targets: list[str],
    target_results: list[dict[str, Any]] | None = None,
    confirmation_candidate_id: str | None = None,
    confirmation_candidate_manifest_sha256: str | None = None,
    locked_final_test: dict[str, Any] | None = None,
    blocking_reasons: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return validate_confirmation_record({
        "schema_version": CONFIRMATION_VERSION,
        "confirmation_id": confirmation_id,
        "snapshot_id": snapshot_id,
        "selected_candidate_id": selected_candidate_id,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
        "production_required_targets": production_required_targets,
        "target_results": target_results or [],
        "confirmation_candidate_id": confirmation_candidate_id,
        "confirmation_candidate_manifest_sha256": (
            confirmation_candidate_manifest_sha256
        ),
        "locked_final_test": locked_final_test,
        "blocking_reasons": blocking_reasons or [],
    })


def validate_confirmation_record(payload: Any) -> dict[str, Any]:
    value = require_object(payload, "confirmation record")
    if value.get("schema_version") != CONFIRMATION_VERSION:
        raise ValueError("unsupported confirmation record version")
    for name in ("confirmation_id", "snapshot_id", "selected_candidate_id"):
        require_safe_identity(value.get(name), name)
    if value.get("status") not in CONFIRMATION_STATES:
        raise ValueError("unsupported confirmation state")
    required_text(value.get("created_at"), "confirmation created_at")
    required_text(value.get("updated_at"), "confirmation updated_at")
    required = identity_array(
        value.get("production_required_targets"), "production_required_targets"
    )
    results = value.get("target_results")
    if not isinstance(results, list) or any(
        not isinstance(item, dict) for item in results
    ):
        raise ValueError("confirmation target_results must be objects")
    candidate_id = value.get("confirmation_candidate_id")
    candidate_hash = value.get("confirmation_candidate_manifest_sha256")
    if (candidate_id is None) != (candidate_hash is None):
        raise ValueError("confirmation Candidate identity/hash must be paired")
    if candidate_id is not None:
        require_safe_identity(candidate_id, "confirmation_candidate_id")
        require_sha256(candidate_hash, "confirmation Candidate manifest hash")
    if value["status"] in {"succeeded", "awaiting_user_decision"}:
        complete = {
            item.get("target_identity")
            for item in results
            if item.get("status") == "complete"
        }
        if set(required) != complete or not candidate_id:
            raise ValueError(
                "successful confirmation requires every production Target "
                "and one confirmation Candidate"
            )
    blockers = value.get("blocking_reasons")
    if not isinstance(blockers, list) or any(
        not isinstance(item, dict)
        or type(item.get("code")) is not str
        or not item["code"]
        for item in blockers
    ):
        raise ValueError("confirmation blocking_reasons are invalid")
    if value.get("locked_final_test") is not None and not isinstance(
        value["locked_final_test"], dict
    ):
        raise ValueError("locked final-test projection must be an object")
    return canonical_payload(value)


def build_final_decision(
    *,
    decision_id: str,
    status: str,
    snapshot_id: str,
    confirmation_id: str,
    candidate_id: str,
    candidate_manifest_sha256: str,
    observed_active_revision: int,
    created_at: str,
    actor_kind: str,
    authority_context: str,
    reason: str = "",
) -> dict[str, Any]:
    return validate_final_decision({
        "schema_version": FINAL_DECISION_VERSION,
        "decision_id": decision_id,
        "status": status,
        "snapshot_id": snapshot_id,
        "confirmation_id": confirmation_id,
        "candidate_id": candidate_id,
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "observed_active_revision": observed_active_revision,
        "created_at": created_at,
        "actor_kind": actor_kind,
        "authority_context": authority_context,
        "reason": reason,
    })


def validate_final_decision(payload: Any) -> dict[str, Any]:
    value = require_object(payload, "final decision")
    if value.get("schema_version") != FINAL_DECISION_VERSION:
        raise ValueError("unsupported final decision version")
    for name in ("decision_id", "snapshot_id", "confirmation_id", "candidate_id"):
        require_safe_identity(value.get(name), name)
    if value.get("status") not in DECISION_STATES:
        raise ValueError("unsupported final decision state")
    require_sha256(
        value.get("candidate_manifest_sha256"), "candidate_manifest_sha256"
    )
    revision = value.get("observed_active_revision")
    if type(revision) is not int or revision < 0:
        raise ValueError("observed Active revision must be non-negative")
    required_text(value.get("created_at"), "decision created_at")
    if value.get("actor_kind") != "user":
        raise ValueError("only a user may own a final decision")
    required_text(value.get("authority_context"), "authority_context")
    return canonical_payload(value)
