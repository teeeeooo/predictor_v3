"""Shared node projection helpers for the lifecycle retention inventory."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.closeout.compatibility import (
    inspect_persisted_contract,
)
from apps.common.model_lifecycle.closeout.retention import ArtifactNode


def directory_size(path: Path) -> int:
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink()
    )


def age_days(created_at: str, now: datetime) -> int:
    try:
        created = datetime.fromisoformat(created_at).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return 0
    return max((now - created).days, 0)


def record_node(
    identity: str,
    artifact_class: str,
    payload: dict[str, Any],
    path: Path,
    now: datetime,
    contract_kind: str,
) -> ArtifactNode:
    disposition = inspect_persisted_contract(contract_kind, payload)
    return raw_node(
        identity,
        artifact_class,
        payload,
        path,
        now,
        version_disposition=disposition.status,
    )


def raw_node(
    identity: str,
    artifact_class: str,
    payload: dict[str, Any],
    path: Path,
    now: datetime,
    *,
    version_disposition: str = "current_and_executable",
) -> ArtifactNode:
    created_at = str(payload.get("created_at", now.isoformat()))
    return ArtifactNode(
        identity,
        artifact_class,
        created_at,
        directory_size(path),
        age_days(created_at, now),
        version_disposition=version_disposition,
        source_artifact_identity=str(path),
    )
