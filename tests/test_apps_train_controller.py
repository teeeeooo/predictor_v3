"""TrainController worker orchestration tests."""

from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from apps.train.controllers.train_controller import TrainController
from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)
from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend
from tools.dev.mock_smoke.generators import write_mock_training_data


def _app() -> QCoreApplication:
    return QCoreApplication.instance() or QCoreApplication([])


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


class BlockingTrainingBackend:
    """Backend double that lets tests observe controller running state."""

    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self.cancel_called = False

    def __call__(self, request, log_callback=None, progress_callback=None):  # noqa: ANN001
        self.started.set()
        if progress_callback is not None:
            progress_callback(
                TrainingProgress(
                    run_id=request.run_id,
                    completed=0,
                    total=1,
                    message="blocking",
                    indeterminate=False,
                )
            )
        assert self.release.wait(1)
        if self.cancel_called:
            return TrainingResult(
                run_id=request.run_id,
                status="cancelled",
                model_path=request.model_output_path,
                message="cancelled",
            )
        return TrainingResult(
            run_id=request.run_id,
            status="complete",
            model_path=request.model_output_path,
            message="complete",
        )

    def cancel(self) -> None:
        self.cancel_called = True
        self.release.set()


def test_train_controller_start_runs_worker_service(tmp_path):
    _app()
    controller = TrainController(
        service=TrainingService(backend=DevFastTrainingBackend(rows=8))
    )
    finished = []
    progress = []

    controller.start(
        _request(tmp_path),
        progress_callback=progress.append,
        finished_callback=finished.append,
    )
    _wait_until(lambda: finished and controller._thread is None)

    assert progress[-1].completed == progress[-1].total
    assert finished[0].status == "complete"
    assert controller.last_result == finished[0]
    assert not controller.is_running


def test_train_controller_rejects_double_start(tmp_path):
    _app()
    backend = BlockingTrainingBackend()
    controller = TrainController(service=TrainingService(backend=backend))

    controller.start(_request(tmp_path))
    assert backend.started.wait(1)
    assert controller.is_running
    with pytest.raises(RuntimeError, match="already in progress"):
        controller.start(_request(tmp_path, "second"))

    backend.release.set()
    _wait_until(lambda: controller._thread is None)


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
    assert controller._thread is None


def test_train_controller_cancel_calls_worker_cancel(tmp_path):
    _app()
    backend = BlockingTrainingBackend()
    controller = TrainController(service=TrainingService(backend=backend))
    cancelled = []

    controller.start(_request(tmp_path), cancelled_callback=cancelled.append)
    assert backend.started.wait(1)
    assert controller.cancel()
    _wait_until(lambda: cancelled and controller._thread is None)

    assert backend.cancel_called
    assert cancelled[0].status == "cancelled"
    assert controller.last_result == cancelled[0]


def test_train_controller_source_does_not_import_widgets():
    source = "apps/train/controllers/train_controller.py"
    text = open(source, encoding="utf-8").read()

    assert "QtWidgets" not in text
    assert "TrainModelPanel" not in text
