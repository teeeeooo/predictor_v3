"""UI/runtime-neutral prediction execution port payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest


@dataclass(frozen=True)
class PredictionJob:
    """Immutable batch of validated prediction requests for one run."""

    run_id: str
    requests: tuple[PredictionInputRequest, ...]
    total: int


@dataclass(frozen=True)
class PredictionProgress:
    """Progress payload emitted after a runner processes a row."""

    run_id: str
    completed: int
    total: int
    current_case_id: str = ""
    message: str = ""


@dataclass(frozen=True)
class PredictionWorkerSummary:
    """Final runner counts for a prediction run."""

    run_id: str
    total: int
    complete: int = 0
    error: int = 0
    cancelled: int = 0
    cancelled_case_ids: tuple[str, ...] = ()


class PredictionExecutionPort(Protocol):
    """Port for prediction execution runners."""

    @property
    def is_running(self) -> bool:
        """Return whether the runner is active."""

    def start(self, job: PredictionJob) -> None:
        """Start a prepared prediction job."""

    def cancel(self) -> None:
        """Request cancellation for the active prediction job."""
