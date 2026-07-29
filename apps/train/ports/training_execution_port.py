"""UI/runtime-neutral training execution port."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
    TrainingStartRequest,
)


@dataclass(frozen=True)
class TrainingExecutionCallbacks:
    """Callbacks used by an outbound training execution adapter."""

    started: Callable[[TrainingRequest], None]
    log: Callable[[TrainingLogEvent], None]
    progress: Callable[[TrainingProgress], None]
    finished: Callable[[TrainingResult], None]
    failed: Callable[[TrainingResult], None]
    cancelled: Callable[[TrainingResult], None]
    start_requested: (
        Callable[[TrainingStartRequest], dict] | None
    ) = None


@runtime_checkable
class TrainingExecutionPort(Protocol):
    """Port for a running training execution backend."""

    @property
    def is_running(self) -> bool:
        """Return whether a training process is active."""

    def start(
        self,
        request: TrainingRequest,
        callbacks: TrainingExecutionCallbacks | None = None,
    ) -> None:
        """Start training for the immutable request."""

    def cancel(self) -> bool:
        """Hard-cancel the active training execution when possible."""

    def dispose(self) -> None:
        """Release adapter-owned runtime resources after a terminal event."""


TrainingExecutionFactory = Callable[[], TrainingExecutionPort]
