"""Structured stdout event parsing for training process runners."""

from __future__ import annotations

import json

from apps.common.model_lifecycle.closeout.start_handshake import (
    validate_confirmation_start_handshake,
    validate_confirmation_start_grant,
    validate_confirmation_start_permit,
)
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
    TrainingStartRequest,
)


def parse_training_event(
    line: str,
    request: TrainingRequest,
) -> tuple[
    str,
    TrainingLogEvent
    | TrainingProgress
    | TrainingResult
    | TrainingRequest
    | TrainingStartRequest,
]:
    """Parse one child-process stdout line into a runner payload."""
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return "log", TrainingLogEvent(request.run_id, line)

    event_type = event.get("type")
    if event_type == "training_start_requested":
        handshake = _exact_start_handshake(event, request)
        return "training_start_requested", TrainingStartRequest(
            run_id=request.run_id,
            handshake=handshake,
        )
    if event_type == "training_started":
        if request.confirmation_start_handshake_json:
            _exact_start_handshake(event, request)
        return "training_started", request
    if event_type == "progress":
        return "progress", TrainingProgress(
            run_id=event.get("run_id", request.run_id),
            completed=int(event.get("completed", 0)),
            total=int(event.get("total", 0)),
            message=str(event.get("message", "")),
            indeterminate=bool(event.get("indeterminate", True)),
        )
    if event_type == "result":
        return "result", TrainingResult(
            run_id=event.get("run_id", request.run_id),
            status=str(event.get("status", "error")),
            summary=str(event.get("summary", "")),
            model_path=str(event.get("model_path", request.model_output_path)),
            log_path=str(event.get("log_path", "")),
            message=str(event.get("message", "")),
            generation_id=str(event.get("generation_id", request.generation_id)),
            registry_fingerprint=str(event.get("registry_fingerprint", request.registry_fingerprint)),
            evidence_path=str(event.get("evidence_path", "")),
        )
    return "log", TrainingLogEvent(
        run_id=event.get("run_id", request.run_id),
        message=str(event.get("message", line)),
        level=str(event.get("level", "info")),
    )


def _exact_start_handshake(
    event: dict,
    request: TrainingRequest,
) -> dict:
    if event.get("run_id") != request.run_id:
        raise ValueError("training start event run identity mismatch")
    if not request.confirmation_start_handshake_json:
        raise ValueError("unexpected confirmation training start handshake")
    expected = validate_confirmation_start_handshake(
        json.loads(request.confirmation_start_handshake_json)
    )
    actual = validate_confirmation_start_handshake(event.get("handshake"))
    if actual != expected:
        raise ValueError("training start event handshake mismatch")
    return actual


def serialize_training_start_grant(
    request: TrainingRequest,
    grant: dict,
) -> str:
    """Serialize one exact parent-to-child post-durability grant."""
    if not request.confirmation_start_handshake_json:
        raise ValueError("unexpected confirmation training start grant")
    handshake = validate_confirmation_start_handshake(
        json.loads(request.confirmation_start_handshake_json)
    )
    with open(handshake["permit_path"], "r", encoding="utf-8") as source:
        permit = json.load(source)
    validate_confirmation_start_permit(permit, handshake)
    exact = validate_confirmation_start_grant(grant, handshake, permit)
    return json.dumps(
        {
            "type": "training_start_granted",
            "run_id": request.run_id,
            "grant": exact,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
