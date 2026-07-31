"""Inbound-facing protocols for Predict workflow collaborators."""

from __future__ import annotations

from typing import Protocol

from apps.predict.application.models import (
    PredictionInputOutcome,
    PredictionInputRequest,
    PredictionModelStatus,
    PredictionServiceResult,
)
from apps.predict.application.result_contract import PredictionExecutionContext
from apps.predict.application.target_outcome import PredictionTargetDescriptor
from apps.predict.state.case_row import CaseRow
from apps.predict.state.result_row import ResultRow


class PredictionInputMapper(Protocol):
    """Convert application case state into a validated model request."""

    def build_request(self, case: CaseRow) -> PredictionInputOutcome:
        """Build one request outcome."""


class PredictionResultMapper(Protocol):
    """Convert workflow outcomes into application result-row state."""

    @property
    def target_descriptors(self) -> tuple[PredictionTargetDescriptor, ...]:
        """Return the immutable runtime target projection used for mapping."""

    def from_service_result(self, result: PredictionServiceResult) -> ResultRow:
        """Convert one service result."""

    def invalid_result(self, case_id: str, message: str) -> ResultRow:
        """Build an invalid-input row."""

    def running_result(self, case_id: str) -> ResultRow:
        """Build a running row."""

    def cancelled_result(
        self,
        case_id: str,
        message: str = "Prediction cancelled.",
        *,
        context: PredictionExecutionContext,
    ) -> ResultRow:
        """Build a cancelled row."""

    def infrastructure_failure_result(
        self,
        case_id: str,
        message: str,
        *,
        context: PredictionExecutionContext,
    ) -> ResultRow:
        """Build an error row for a runner/infrastructure failure."""


class PredictionServicePort(Protocol):
    """Execute prepared prediction requests and expose model status."""

    def model_status(self) -> PredictionModelStatus:
        """Return model artifact status without mutating session state."""

    def prepare_model(self) -> None:
        """Fully load and validate the immutable runtime bundle or raise."""

    def predict_many(
        self,
        requests: list[PredictionInputRequest],
    ) -> list[PredictionServiceResult]:
        """Predict several prepared rows."""

    def predict_one(self, request: PredictionInputRequest) -> PredictionServiceResult:
        """Predict one prepared row."""
