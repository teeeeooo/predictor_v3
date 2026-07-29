"""Atomic durable publication for one confirmation start permit."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from apps.common.model_lifecycle.filesystem import LifecycleFilesystem


def publish_start_permit_atomic(
    filesystem: LifecycleFilesystem,
    final_path: Path,
    payload: dict,
    *,
    failure_hook=None,  # noqa: ANN001
) -> None:
    """Publish complete canonical bytes without exposing an incomplete final."""
    hook = failure_hook or (lambda _stage: None)
    encoded = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    ).encode("utf-8")
    temporary = final_path.with_name(
        f".{final_path.name}.publishing-{uuid4().hex}.tmp"
    )
    with filesystem.open_exclusive(temporary) as target:
        hook("after_temporary_create")
        midpoint = max(1, len(encoded) // 2)
        target.write(encoded[:midpoint])
        hook("during_temporary_write")
        target.write(encoded[midpoint:])
        hook("before_temporary_flush_fsync")
    with filesystem.open_regular(temporary) as source:
        if source.read() != encoded:
            raise ValueError(
                "confirmation start permit temporary bytes changed"
            )
    hook("after_temporary_fsync_before_commit")
    filesystem.publish_file_exclusive(
        temporary,
        final_path,
        after_publish=lambda: hook("after_final_commit"),
    )
    filesystem.remove_file(temporary, missing_ok=True)
