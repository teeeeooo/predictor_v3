"""Structured stdout event parsing for training process runners."""

from __future__ import annotations

import json

from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)


def parse_training_event(
    line: str,
    request: TrainingRequest,
) -> tuple[str, TrainingLogEvent | TrainingProgress | TrainingResult]:
    """Parse one child-process stdout line into a runner payload."""
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return "log", TrainingLogEvent(request.run_id, line)

    event_type = event.get("type")
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
        )
    return "log", TrainingLogEvent(
        run_id=event.get("run_id", request.run_id),
        message=str(event.get("message", line)),
        level=str(event.get("level", "info")),
    )
