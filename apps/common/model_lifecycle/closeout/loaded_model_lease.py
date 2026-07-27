"""Read/write projection for a loaded Predict Candidate; never deletion authority."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import canonical_payload, require_safe_identity
from .contracts import LOADED_MODEL_LEASE_VERSION


def loaded_model_lease(
    *,
    lease_id: str,
    candidate_id: str,
    active_revision: int,
    process_id: int,
    observed_at: str,
    expires_at: str,
) -> dict[str, Any]:
    require_safe_identity(lease_id, "loaded model lease_id")
    require_safe_identity(candidate_id, "loaded model candidate_id")
    if (
        type(active_revision) is not int
        or active_revision < 0
        or type(process_id) is not int
        or process_id < 1
        or not observed_at
        or not expires_at
    ):
        raise ValueError("loaded model lease metadata is invalid")
    return canonical_payload({
        "schema_version": LOADED_MODEL_LEASE_VERSION,
        "lease_id": lease_id,
        "candidate_id": candidate_id,
        "active_revision": active_revision,
        "process_id": process_id,
        "observed_at": observed_at,
        "expires_at": expires_at,
    })


def inspect_loaded_model_leases(
    payloads: list[dict[str, Any]],
    *,
    now: str | None = None,
) -> tuple[str, tuple[str, ...]]:
    now_value = _parse_time(now or datetime.now(timezone.utc).isoformat())
    candidates = []
    saw_invalid = False
    for payload in payloads:
        try:
            if payload.get("schema_version") != LOADED_MODEL_LEASE_VERSION:
                raise ValueError("unsupported loaded model lease version")
            candidate_id = require_safe_identity(
                payload.get("candidate_id"), "loaded model candidate_id"
            )
            expires = _parse_time(payload.get("expires_at"))
        except (AttributeError, TypeError, ValueError):
            saw_invalid = True
            continue
        if expires >= now_value:
            candidates.append(candidate_id)
    if saw_invalid:
        return "unknown", tuple(sorted(set(candidates)))
    if candidates:
        return "current", tuple(sorted(set(candidates)))
    return ("expired" if payloads else "missing"), ()


def _parse_time(value: object) -> datetime:
    if type(value) is not str or not value:
        raise ValueError("lease time must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("lease time must include a timezone")
    return parsed.astimezone(timezone.utc)
