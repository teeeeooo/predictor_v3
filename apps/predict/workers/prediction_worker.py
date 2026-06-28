"""Prediction worker for batch prediction runs."""

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest
from apps.predict.services.prediction_service import PredictionService


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


class PredictionWorker(QObject):
    """Run prediction requests cooperatively without owning UI/session state."""

    progress = Signal(object)
    row_result = Signal(object)
    finished = Signal(object)
    cancelled = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        job: PredictionJob,
        service: PredictionService | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._job = job
        self._service = service or PredictionService()
        self._cancel_requested = False

    @Slot()
    def run(self) -> None:
        """Process the job and emit row/progress/final signals."""
        complete = 0
        error = 0
        try:
            for index, request in enumerate(self._job.requests):
                if self._cancel_requested:
                    self._emit_cancelled(complete, error, processed=index)
                    return

                result = self._service.predict_one(request)
                self.row_result.emit(result)
                if result.status == "complete":
                    complete += 1
                elif result.status == "error":
                    error += 1

                processed = index + 1
                self.progress.emit(
                    PredictionProgress(
                        run_id=self._job.run_id,
                        completed=processed,
                        total=self._job.total,
                        current_case_id=request.case_id,
                        message=f"{processed} / {self._job.total}",
                    )
                )

                if self._cancel_requested:
                    self._emit_cancelled(complete, error, processed=processed)
                    return
        except Exception as exc:  # pragma: no cover - defensive infrastructure boundary
            self.failed.emit(exc)
            return

        self.finished.emit(
            PredictionWorkerSummary(
                run_id=self._job.run_id,
                total=self._job.total,
                complete=complete,
                error=error,
                cancelled=0,
            )
        )

    def cancel(self) -> None:
        """Request cooperative cancellation between rows."""
        self._cancel_requested = True

    def _emit_cancelled(self, complete: int, error: int, processed: int) -> None:
        remaining = max(self._job.total - processed, 0)
        self.cancelled.emit(
            PredictionWorkerSummary(
                run_id=self._job.run_id,
                total=self._job.total,
                complete=complete,
                error=error,
                cancelled=remaining,
            )
        )
