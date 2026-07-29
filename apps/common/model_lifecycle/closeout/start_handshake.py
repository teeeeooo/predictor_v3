"""Canonical confirmation-only process start handshake contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical import (
    canonical_payload,
    content_sha256,
    require_safe_identity,
    require_sha256,
)


CONFIRMATION_START_HANDSHAKE_VERSION = (
    "predictor_v3.confirmation_start_handshake.v1"
)
CONFIRMATION_START_PERMIT_VERSION = (
    "predictor_v3.confirmation_start_permit.v1"
)


def build_confirmation_start_handshake(
    *,
    confirmation_id: str,
    execution_key: str,
    attempt_id: str,
    training_meaning_sha256: str,
    permit_path: str | Path,
) -> dict[str, Any]:
    """Build one exact child launch identity and its permit location."""
    payload = {
        "protocol_version": CONFIRMATION_START_HANDSHAKE_VERSION,
        "confirmation_id": require_safe_identity(
            confirmation_id, "confirmation_id"
        ),
        "execution_key": require_sha256(
            execution_key, "confirmation execution_key"
        ),
        "attempt_id": require_safe_identity(
            attempt_id, "confirmation start attempt_id"
        ),
        "training_meaning_sha256": require_sha256(
            training_meaning_sha256, "confirmation training meaning hash"
        ),
        "permit_path": _absolute_path(permit_path),
    }
    return {
        **payload,
        "handshake_sha256": content_sha256(payload),
    }


def validate_confirmation_start_handshake(
    value: Any,
) -> dict[str, Any]:
    """Validate an exact immutable start-request payload."""
    payload = canonical_payload(value)
    if set(payload) != {
        "protocol_version",
        "confirmation_id",
        "execution_key",
        "attempt_id",
        "training_meaning_sha256",
        "permit_path",
        "handshake_sha256",
    }:
        raise ValueError("confirmation start handshake fields are invalid")
    expected = build_confirmation_start_handshake(
        confirmation_id=payload.get("confirmation_id"),
        execution_key=payload.get("execution_key"),
        attempt_id=payload.get("attempt_id"),
        training_meaning_sha256=payload.get("training_meaning_sha256"),
        permit_path=payload.get("permit_path"),
    )
    if payload != expected:
        raise ValueError("confirmation start handshake is corrupt")
    return expected


def build_confirmation_start_permit(
    handshake: dict[str, Any],
) -> dict[str, Any]:
    """Build the exact durable evidence a waiting child may consume."""
    value = validate_confirmation_start_handshake(handshake)
    return {
        "schema_version": CONFIRMATION_START_PERMIT_VERSION,
        "protocol_version": value["protocol_version"],
        "confirmation_id": value["confirmation_id"],
        "execution_key": value["execution_key"],
        "attempt_id": value["attempt_id"],
        "training_meaning_sha256": value["training_meaning_sha256"],
        "handshake_sha256": value["handshake_sha256"],
    }


def validate_confirmation_start_permit(
    value: Any,
    handshake: dict[str, Any],
) -> dict[str, Any]:
    """Require permit bytes to authorize only their exact waiting child."""
    payload = canonical_payload(value)
    expected = build_confirmation_start_permit(handshake)
    if payload != expected:
        raise ValueError("confirmation start permit is corrupt or stale")
    return expected


def _absolute_path(value: str | Path) -> str:
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("confirmation start permit path must be absolute")
    return str(path)
