"""Read-only migration disposition and preview contracts; no apply authority."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .canonical import canonical_payload, content_sha256, require_sha256
from .compatibility import (
    CORRUPT_INCOMPLETE,
    CURRENT_EXECUTABLE,
    HISTORICAL_ONLY,
    UNSUPPORTED_FUTURE,
    inspect_persisted_contract,
)
from .contracts import MIGRATION_PREVIEW_VERSION


def preview_migration(
    *,
    artifact_kind: str,
    payload: dict[str, Any],
    source_sha256: str,
    proposed_contract_version: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    require_sha256(source_sha256, "migration source hash")
    disposition = inspect_persisted_contract(artifact_kind, payload)
    eligible = disposition.status in {HISTORICAL_ONLY, CURRENT_EXECUTABLE}
    blocked_reason = ""
    if disposition.status == UNSUPPORTED_FUTURE:
        eligible = False
        blocked_reason = "unsupported_future_version"
    elif disposition.status == CORRUPT_INCOMPLETE:
        eligible = False
        blocked_reason = "source_corrupt_or_incomplete"
    elif disposition.status == CURRENT_EXECUTABLE:
        eligible = False
        blocked_reason = "migration_not_required"
    identity_input = {
        "artifact_kind": artifact_kind,
        "source_sha256": source_sha256,
        "proposed_contract_version": proposed_contract_version,
    }
    proposed_identity = f"migration-output-{content_sha256(identity_input)}"
    preview_payload = {
        **identity_input,
        "source_payload_sha256": content_sha256(payload),
    }
    preview_id = f"migration-preview-{content_sha256(preview_payload)}"
    return canonical_payload({
        "schema_version": MIGRATION_PREVIEW_VERSION,
        "preview_id": preview_id,
        "artifact_kind": artifact_kind,
        "source_identity": {
            "sha256": source_sha256,
            "payload_sha256": content_sha256(payload),
        },
        "source_disposition": disposition.status,
        "eligible": eligible,
        "blocked_reason": blocked_reason,
        "proposed_contract_version": proposed_contract_version,
        "proposed_output_identity": proposed_identity,
        "original_preservation_required": True,
        "in_place_migration_allowed": False,
        "apply_implemented": False,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
    })
