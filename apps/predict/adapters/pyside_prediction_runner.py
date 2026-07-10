"""PySide adapter around the prediction worker."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, QTimer, Signal

from apps.predict.ports.prediction_execution_port import PredictionJob
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort
from apps.predict.workers.prediction_worker import PredictionWorker


class PySidePredictionRunner(QObject):
    """Own QThread/PredictionWorker lifecycle for PySide surfaces."""

    progress = Signal(object)
    row_result = Signal(object)
    finished = Signal(object)
    cancelled = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        service: PredictionServicePort,
        worker_cls: type[PredictionWorker] = PredictionWorker,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._worker_cls = worker_cls
        self._thread: QThread | None = None
        self._worker: PredictionWorker | None = None
        self._terminal: tuple[str, object] | None = None

    @property
    def is_running(self) -> bool:
        """Return whether a worker thread is active."""
        return self._thread is not None

    def start(self, job: PredictionJob) -> None:
        """Start the PySide worker for a prepared prediction job."""
        if self.is_running:
            raise RuntimeError("Prediction runner already in progress.")
        self._terminal = None
        self._thread = QThread()
        self._worker = self._worker_cls(job, service=self._service)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.row_result.connect(self.row_result)
        self._worker.progress.connect(self.progress)
        self._worker.finished.connect(lambda summary: self._store_terminal("finished", summary))
        self._worker.cancelled.connect(lambda summary: self._store_terminal("cancelled", summary))
        self._worker.failed.connect(lambda exc: self._store_terminal("failed", exc))
        self._worker.finished.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(lambda: QTimer.singleShot(0, self._emit_terminal_and_clear))
        self._thread.start()

    def cancel(self) -> None:
        """Request cooperative worker cancellation."""
        if self._worker is not None:
            self._worker.cancel()

    def dispose(self) -> None:
        """Schedule this adapter for deletion after terminal cleanup."""

        self.deleteLater()

    def _clear(self) -> None:
        self._thread = None
        self._worker = None

    def _store_terminal(self, kind: str, payload: object) -> None:
        self._terminal = (kind, payload)

    def _emit_terminal_and_clear(self) -> None:
        terminal = self._terminal
        self._clear()
        self._terminal = None
        if terminal is None:
            return
        kind, payload = terminal
        if kind == "finished":
            self.finished.emit(payload)
        elif kind == "cancelled":
            self.cancelled.emit(payload)
        else:
            self.failed.emit(payload)
