"""Confirmation-only child start authorization and process-liveness fence."""

from __future__ import annotations

import atexit
import json
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Callable

from apps.common.model_lifecycle.closeout.start_handshake import (
    validate_confirmation_start_grant,
    validate_confirmation_start_handshake,
    validate_confirmation_start_permit,
)
from apps.common.model_lifecycle.filesystem import LifecycleFilesystem
from apps.common.model_lifecycle.locking import lifecycle_lock
from apps.train.state.training_run_state import TrainingRequest

_ATTEMPT_LIVENESS = None


class TrainingStartCancelled(RuntimeError):
    """A waiting confirmation child was cancelled before actual work."""


def authorize_confirmation_training_start(
    request: TrainingRequest,
    *,
    emit_event: Callable[[dict], None],
    cancellation_requested: Callable[[], bool],
    timeout_seconds: float,
) -> dict | None:
    """Return the exact authorized attempt, or None for ordinary training."""
    if not request.confirmation_start_handshake_json:
        return None
    if timeout_seconds <= 0:
        raise ValueError("training start permit timeout must be positive")
    handshake = validate_confirmation_start_handshake(
        json.loads(request.confirmation_start_handshake_json)
    )
    _acquire_attempt_liveness(handshake)
    try:
        emit_event({
            "type": "training_start_requested",
            "run_id": request.run_id,
            "handshake": handshake,
        })
        message = _read_start_grant(
            timeout_seconds,
            cancellation_requested=cancellation_requested,
        )
        if (
            not isinstance(message, dict)
            or message.get("type") != "training_start_granted"
            or message.get("run_id") != request.run_id
        ):
            raise ValueError("confirmation start grant transport is invalid")
        permit = json.loads(
            Path(handshake["permit_path"]).read_text(encoding="utf-8")
        )
        validate_confirmation_start_permit(permit, handshake)
        validate_confirmation_start_grant(
            message.get("grant"), handshake, permit
        )
        return handshake
    except BaseException:
        _release_attempt_liveness()
        raise


def _acquire_attempt_liveness(handshake: dict) -> None:
    global _ATTEMPT_LIVENESS
    if _ATTEMPT_LIVENESS is not None:
        raise RuntimeError("confirmation attempt liveness is already held")
    lock_path = Path(handshake["liveness_lock_path"])
    filesystem = LifecycleFilesystem(lock_path.parent)
    context = lifecycle_lock(lock_path, filesystem=filesystem)
    context.__enter__()
    _ATTEMPT_LIVENESS = context
    atexit.register(_release_attempt_liveness)


def _release_attempt_liveness() -> None:
    global _ATTEMPT_LIVENESS
    context = _ATTEMPT_LIVENESS
    _ATTEMPT_LIVENESS = None
    if context is not None:
        context.__exit__(None, None, None)


def _read_start_grant(
    timeout_seconds: float,
    *,
    cancellation_requested: Callable[[], bool],
) -> dict:
    messages: queue.Queue[str] = queue.Queue(maxsize=1)

    def read_line() -> None:
        messages.put(sys.stdin.readline())

    threading.Thread(target=read_line, daemon=True).start()
    deadline = time.monotonic() + timeout_seconds
    while True:
        if cancellation_requested():
            raise TrainingStartCancelled()
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(
                "post-durability confirmation start grant was not received"
            )
        try:
            line = messages.get(timeout=min(0.05, remaining))
        except queue.Empty:
            continue
        if not line:
            raise RuntimeError(
                "confirmation start grant channel closed before authorization"
            )
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError("confirmation start grant must be an object")
        return value
