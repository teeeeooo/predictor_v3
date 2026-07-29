"""Application helpers for confirmation-only child start handshakes."""

from __future__ import annotations

import json
from dataclasses import asdict, replace

from apps.common.model_lifecycle.closeout.canonical import content_sha256
from apps.common.model_lifecycle.closeout.start_handshake import (
    validate_confirmation_start_handshake,
)
from apps.train.state.training_run_state import TrainingRequest


def with_confirmation_start_handshake(
    request: TrainingRequest,
    *,
    handshake: dict,
) -> tuple[TrainingRequest, dict]:
    """Bind one frozen training meaning to one process launch attempt."""
    if request.confirmation_start_handshake_json:
        raise ValueError("confirmation start handshake is already configured")
    handshake = validate_confirmation_start_handshake(handshake)
    if (
        handshake["training_meaning_sha256"]
        != training_meaning_sha256(request)
    ):
        raise ValueError(
            "confirmation start handshake training meaning mismatch"
        )
    return (
        replace(
            request,
            confirmation_start_handshake_json=json.dumps(
                handshake,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        ),
        handshake,
    )


def training_meaning_sha256(request: TrainingRequest) -> str:
    """Hash execution semantics while excluding launch/runtime coordinates."""
    meaning = asdict(request)
    for field in (
        "run_id",
        "model_output_path",
        "confirmation_start_handshake_json",
    ):
        meaning.pop(field)
    return content_sha256(meaning)
