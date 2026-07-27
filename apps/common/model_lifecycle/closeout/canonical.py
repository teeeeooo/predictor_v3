"""Deterministic, finite JSON identities for Phase 5H persisted contracts."""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

_SHA256 = re.compile(r"[0-9a-f]{64}")
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def require_safe_identity(value: object, name: str) -> str:
    if type(value) is not str or _SAFE_ID.fullmatch(value) is None:
        raise ValueError(f"{name} is not a safe identity")
    return value


def require_sha256(value: object, name: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def canonical_payload(value: Any) -> Any:
    """Return a detached JSON value and reject lossy/non-finite content."""
    if value is None or type(value) in {str, bool, int}:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("persisted closeout contracts require finite numbers")
        return int(value) if value.is_integer() else value
    if isinstance(value, dict):
        if any(type(key) is not str for key in value):
            raise ValueError("persisted closeout object keys must be strings")
        return {
            key: canonical_payload(value[key])
            for key in sorted(value)
        }
    if isinstance(value, (list, tuple)):
        return [canonical_payload(item) for item in value]
    raise ValueError(
        f"unsupported persisted closeout value: {type(value).__name__}"
    )


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_payload(value),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def content_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path) -> str:  # noqa: ANN001
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
