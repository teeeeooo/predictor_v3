"""Prediction worker for batch prediction runs."""

from PySide6.QtCore import QObject, Signal, Slot

from apps.predict.ports.prediction_execution_port import (
    PredictionJob,
    PredictionProgress,
    PredictionWorkerSummary,
)
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort


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
        service: PredictionServicePort,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._job = job
        self._service = service
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
        cancelled_requests = self._job.requests[processed:]
        remaining = max(self._job.total - processed, 0)
        self.cancelled.emit(
            PredictionWorkerSummary(
                run_id=self._job.run_id,
                total=self._job.total,
                complete=complete,
                error=error,
                cancelled=remaining,
                cancelled_case_ids=tuple(
                    request.case_id for request in cancelled_requests
                ),
            )
        )
