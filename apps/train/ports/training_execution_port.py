"""UI/runtime-neutral training execution port."""

from __future__ import annotations

from typing import Protocol

from apps.train.state.training_run_state import TrainingRequest


class TrainingExecutionPort(Protocol):
    """Port for a running training execution backend."""

    @property
    def is_running(self) -> bool:
        """Return whether a training process is active."""

    def start(self, request: TrainingRequest) -> None:
        """Start training for the immutable request."""

    def cancel(self) -> bool:
        """Hard-cancel the active training execution when possible."""
