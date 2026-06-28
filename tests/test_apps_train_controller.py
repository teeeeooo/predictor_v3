"""TrainController worker orchestration tests."""

import os

import pytest
from PySide6.QtCore import QObject, QEventLoop, QTimer, Signal
from PySide6.QtWidgets import QApplication

from apps.train.controllers.train_controller import TrainController
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)
from tools.dev.mock_smoke.generators import write_mock_training_data


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _wait_until(predicate, timeout_ms: int = 1500) -> None:  # noqa: ANN001
    app = _app()
    if predicate():
        app.processEvents()
        return
    loop = QEventLoop()
    poll = QTimer()
    timeout = QTimer()
    poll.setInterval(10)
    timeout.setSingleShot(True)
    poll.timeout.connect(lambda: loop.quit() if predicate() else None)
    timeout.timeout.connect(loop.quit)
    poll.start()
    timeout.start(timeout_ms)
    loop.exec()
    poll.stop()
    timeout.stop()
    app.processEvents()
    assert predicate()


def _request(tmp_path, run_id: str = "run-controller") -> TrainingRequest:  # noqa: ANN001
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
    )


class FakeTrainingRunner(QObject):
    """Runner double that lets tests observe controller wiring."""

    log_event = Signal(object)
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal(object)

    def __init__(self, *, finish_immediately: bool = True) -> None:
        super().__init__()
        self.started = False
        self.cancel_called = False
        self.request = None
        self.finish_immediately = finish_immediately
        self.is_running = False

    def start(self, request):  # noqa: ANN001
        self.started = True
        self.is_running = True
        self.request = request
        self.log_event.emit(TrainingLogEvent(request.run_id, "fake runner started"))
        self.progress.emit(
            TrainingProgress(
                run_id=request.run_id,
                completed=0,
                total=1,
                message="running",
                indeterminate=False,
            )
        )
        if self.finish_immediately:
            QTimer.singleShot(0, self.complete)

    def cancel(self) -> bool:
        self.cancel_called = True
        self.is_running = False
        self.cancelled.emit(
            TrainingResult(
                run_id=self.request.run_id,
                status="cancelled",
                model_path=self.request.model_output_path,
                message="cancelled",
            )
        )
        return True

    def complete(self) -> None:
        self.is_running = False
        self.progress.emit(
            TrainingProgress(
                run_id=self.request.run_id,
                completed=1,
                total=1,
                message="complete",
                indeterminate=False,
            )
        )
        self.finished.emit(
            TrainingResult(
                run_id=self.request.run_id,
                status="complete",
                model_path=self.request.model_output_path,
                message="complete",
            )
        )


def test_train_controller_start_runs_worker_service(tmp_path):
    _app()
    runner = FakeTrainingRunner()
    controller = TrainController(runner=runner)
    finished = []
    progress = []

    controller.start(
        _request(tmp_path),
        progress_callback=progress.append,
        finished_callback=finished.append,
    )
    _wait_until(lambda: finished and controller._runner is None)

    assert progress[-1].completed == progress[-1].total
    assert finished[0].status == "complete"
    assert controller.last_result == finished[0]
    assert not controller.is_running


def test_train_controller_rejects_double_start(tmp_path):
    _app()
    runner = FakeTrainingRunner(finish_immediately=False)
    controller = TrainController(runner=runner)

    controller.start(_request(tmp_path))
    assert runner.started
    assert controller.is_running
    with pytest.raises(RuntimeError, match="already in progress"):
        controller.start(_request(tmp_path, "second"))

    runner.complete()
    _wait_until(lambda: controller._runner is None)


def test_train_controller_missing_data_path_returns_controlled_error(tmp_path):
    _app()
    controller = TrainController()
    failed = []
    request = TrainingRequest(
        run_id="run-missing",
        data_path=str(tmp_path / "missing.csv"),
        model_output_path=str(tmp_path / "model.pkl"),
    )

    result = controller.start(request, failed_callback=failed.append)

    assert result is not None
    assert result.status == "error"
    assert failed[0] == result
    assert controller.last_result == result
    assert controller._runner is None


def test_train_controller_cancel_calls_worker_cancel(tmp_path):
    _app()
    runner = FakeTrainingRunner(finish_immediately=False)
    controller = TrainController(runner=runner)
    cancelled = []

    controller.start(_request(tmp_path), cancelled_callback=cancelled.append)
    assert runner.started
    assert controller.cancel()
    _wait_until(lambda: cancelled and controller._runner is None)

    assert runner.cancel_called
    assert cancelled[0].status == "cancelled"
    assert controller.last_result == cancelled[0]


def test_train_controller_source_does_not_import_widgets():
    source = "apps/train/controllers/train_controller.py"
    text = open(source, encoding="utf-8").read()

    assert "QtWidgets" not in text
    assert "TrainModelPanel" not in text
    assert "QThread" not in text
