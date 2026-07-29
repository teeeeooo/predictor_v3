"""Immutable confirmation snapshot identity and validation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .canonical import (
    canonical_payload,
    content_sha256,
    require_safe_identity,
    require_sha256,
)
from .contract_validation import (
    invalid_hash_descriptor,
    require_object,
    required_text,
)
from .contracts import SNAPSHOT_STATES, SNAPSHOT_VERSION


def build_snapshot_record(
    meaning: dict[str, Any],
    *,
    created_at: str,
    actor_kind: str,
    status: str = "frozen",
) -> dict[str, Any]:
    if status not in SNAPSHOT_STATES:
        raise ValueError("unsupported confirmation snapshot state")
    if actor_kind not in {"user", "system", "operator"}:
        raise ValueError("snapshot actor kind lacks lifecycle authority")
    normalized = canonical_payload(meaning)
    _require_snapshot_meaning(normalized, frozen=status == "frozen")
    identity_input = {
        "schema_version": SNAPSHOT_VERSION,
        "meaning": normalized,
    }
    record = {
        "schema_version": SNAPSHOT_VERSION,
        "snapshot_id": f"snapshot-{content_sha256(identity_input)}",
        "status": status,
        "created_at": required_text(created_at, "snapshot created_at"),
        "actor_kind": actor_kind,
        "meaning_sha256": content_sha256(normalized),
        "meaning": normalized,
    }
    return validate_snapshot_record(record)


def validate_snapshot_record(payload: Any) -> dict[str, Any]:
    value = require_object(payload, "confirmation snapshot")
    if value.get("schema_version") != SNAPSHOT_VERSION:
        raise ValueError("unsupported confirmation snapshot version")
    require_safe_identity(value.get("snapshot_id"), "snapshot_id")
    status = value.get("status")
    if status not in SNAPSHOT_STATES:
        raise ValueError("unsupported confirmation snapshot state")
    required_text(value.get("created_at"), "snapshot created_at")
    if value.get("actor_kind") not in {"user", "system", "operator"}:
        raise ValueError("snapshot actor kind is invalid")
    meaning = canonical_payload(value.get("meaning"))
    _require_snapshot_meaning(meaning, frozen=status == "frozen")
    require_sha256(value.get("meaning_sha256"), "meaning_sha256")
    if content_sha256(meaning) != value["meaning_sha256"]:
        raise ValueError("confirmation snapshot meaning hash mismatch")
    identity_input = {
        "schema_version": SNAPSHOT_VERSION,
        "meaning": meaning,
    }
    expected = f"snapshot-{content_sha256(identity_input)}"
    if value["snapshot_id"] != expected:
        raise ValueError("confirmation snapshot identity mismatch")
    return deepcopy(value)


def _require_snapshot_meaning(value: Any, *, frozen: bool) -> None:
    if not isinstance(value, dict):
        raise ValueError("confirmation snapshot meaning must be an object")
    required = {
        "recommendation",
        "campaign",
        "selected_candidate",
        "source_run",
        "candidate_artifacts",
        "resolved_specification",
        "specification_fingerprint",
        "definition_runtime",
        "target_roles",
        "feature_contract",
        "evaluation_contract",
        "training_configuration",
        "baseline",
        "build_identity",
        "training_semantic_identity",
        "training_data",
    }
    missing = required.difference(value)
    if missing and frozen:
        raise ValueError(
            "frozen confirmation snapshot meaning is incomplete: "
            + sorted(missing)[0]
        )
    if missing:
        return
    data = require_object(value["training_data"], "training_data")
    if data.get("materialization_kind") not in {
        "owned_source_bytes",
        "lossless_training_projection",
        "verified_external_reference",
    }:
        raise ValueError("snapshot training data materialization is invalid")
    require_sha256(data.get("content_sha256"), "training data content hash")
    require_sha256(data.get("ordered_row_set_sha256"), "ordered row-set hash")
    if type(data.get("row_count")) is not int or data["row_count"] < 0:
        raise ValueError("snapshot training data row count is invalid")
    if type(data.get("column_count")) is not int or data["column_count"] < 1:
        raise ValueError("snapshot training data column count is invalid")
    artifacts = require_object(value["candidate_artifacts"], "candidate_artifacts")
    if not artifacts or any(
        type(name) is not str
        or not name
        or invalid_hash_descriptor(descriptor)
        for name, descriptor in artifacts.items()
    ):
        raise ValueError("snapshot Candidate artifact hashes are invalid")
