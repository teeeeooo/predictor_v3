"""Worker for background Train execution."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QObject, Signal, Slot

from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)


class TrainWorker(QObject):
    """Run a training request cooperatively without owning UI state."""

    log_event = Signal(object)
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal(object)

    def __init__(
        self,
        request: TrainingRequest,
        service: TrainingService | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._request = request
        self._service = service or TrainingService()
        self._cancel_requested = False

    @Slot()
    def run(self) -> None:
        """Execute training through the service and emit a terminal signal."""
        if self._cancel_requested:
            self.cancelled.emit(
                TrainingResult(
                    run_id=self._request.run_id,
                    status="cancelled",
                    model_path=self._request.model_output_path,
                    message="Training cancelled before start.",
                )
            )
            return

        try:
            result = self._service.train(
                self._request,
                log_callback=self._handle_log_event,
                progress_callback=self._handle_progress,
            )
        except Exception as exc:  # pragma: no cover - defensive worker boundary
            self.failed.emit(
                TrainingResult(
                    run_id=self._request.run_id,
                    status="error",
                    model_path=self._request.model_output_path,
                    message=str(exc).splitlines()[0],
                )
            )
            return

        if result.status == "cancelled":
            self.cancelled.emit(result)
            return
        if result.status == "error":
            self.failed.emit(result)
            return
        if self._cancel_requested:
            result = replace(
                result,
                message=(
                    f"{result.message} Cancellation was requested, but the "
                    "training backend completed before it could stop."
                ).strip(),
            )
        self.finished.emit(result)

    def cancel(self) -> None:
        """Request cooperative cancellation from the service/backend."""
        self._cancel_requested = True
        self._service.cancel()

    def _handle_log_event(self, event: TrainingLogEvent) -> None:
        self.log_event.emit(event)

    def _handle_progress(self, progress: TrainingProgress) -> None:
        self.progress.emit(progress)
