"""Deterministic bootstrap identities for legacy contract objects."""

from uuid import UUID, uuid5

_NAMESPACE = UUID("8512b4d8-9968-4df8-9a57-6f37a3adbb04")


def bootstrap_identity(kind: str, legacy_key: str) -> str:
    """Return a stable opaque identity without exposing the legacy key."""
    value = uuid5(_NAMESPACE, f"predictor-v3:{kind}:{legacy_key}").hex
    return f"ufm_{kind}_{value}"
