"""Shared strict validators for persisted Phase 5H contracts."""

from __future__ import annotations

from typing import Any

from .canonical import require_safe_identity, require_sha256


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def required_text(value: Any, name: str) -> str:
    if type(value) is not str or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def identity_array(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty identity array")
    identities = [require_safe_identity(item, name) for item in value]
    if len(identities) != len(set(identities)):
        raise ValueError(f"{name} contains duplicate identities")
    return identities


def invalid_hash_descriptor(value: Any) -> bool:
    if not isinstance(value, dict):
        return True
    try:
        require_sha256(value.get("sha256"), "artifact sha256")
    except ValueError:
        return True
    return type(value.get("size_bytes")) is not int or value["size_bytes"] < 0
