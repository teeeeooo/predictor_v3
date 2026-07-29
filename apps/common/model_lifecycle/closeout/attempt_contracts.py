"""Immutable confirmation attempt abandonment evidence."""

from __future__ import annotations

from typing import Any

from .canonical import (
    canonical_payload,
    content_sha256,
    require_safe_identity,
    require_sha256,
)
from .contract_validation import required_text


CONFIRMATION_ATTEMPT_ABANDONED_VERSION = (
    "predictor_v3.confirmation_attempt_abandoned.v1"
)


def build_attempt_abandoned(
    *,
    execution_key: str,
    confirmation_id: str,
    attempt_id: str,
    handshake_sha256: str,
    abandoned_at: str,
    reason_code: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": CONFIRMATION_ATTEMPT_ABANDONED_VERSION,
        "status": "abandoned",
        "execution_key": require_sha256(
            execution_key, "confirmation execution_key"
        ),
        "confirmation_id": require_safe_identity(
            confirmation_id, "confirmation_id"
        ),
        "attempt_id": require_safe_identity(
            attempt_id, "confirmation attempt_id"
        ),
        "handshake_sha256": require_sha256(
            handshake_sha256, "confirmation handshake_sha256"
        ),
        "abandoned_at": required_text(
            abandoned_at, "confirmation attempt abandoned_at"
        ),
        "reason_code": required_text(
            reason_code, "confirmation attempt abandon reason"
        ),
    }
    return {**payload, "evidence_sha256": content_sha256(payload)}


def validate_attempt_abandoned(value: Any) -> dict[str, Any]:
    payload = canonical_payload(value)
    expected = build_attempt_abandoned(
        execution_key=payload.get("execution_key"),
        confirmation_id=payload.get("confirmation_id"),
        attempt_id=payload.get("attempt_id"),
        handshake_sha256=payload.get("handshake_sha256"),
        abandoned_at=payload.get("abandoned_at"),
        reason_code=payload.get("reason_code"),
    )
    if payload != expected:
        raise ValueError("confirmation attempt abandonment is corrupt")
    return expected
