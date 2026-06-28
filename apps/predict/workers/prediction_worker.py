"""Prediction worker contract payloads.

The QObject worker is implemented in a later Arc 10 slice. This module starts
with Qt-free payload contracts so services, controllers, and tests can share a
stable boundary before QThread lifecycle wiring is added.
"""

from dataclasses import dataclass

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest


@dataclass(frozen=True)
class PredictionJob:
    """Immutable batch of validated prediction requests for one run."""

    run_id: str
    requests: tuple[PredictionInputRequest, ...]
    total: int


@dataclass(frozen=True)
class PredictionProgress:
    """Progress payload emitted after a worker processes a row."""

    run_id: str
    completed: int
    total: int
    current_case_id: str = ""
    message: str = ""


@dataclass(frozen=True)
class PredictionWorkerSummary:
    """Final worker counts for a prediction run."""

    run_id: str
    total: int
    complete: int = 0
    error: int = 0
    cancelled: int = 0
