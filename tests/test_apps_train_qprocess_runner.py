"""QProcessTrainingRunner process-boundary tests."""

import os
from pathlib import Path

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.ports.training_execution_port import (
    TrainingExecutionCallbacks,
    TrainingExecutionPort,
)
from apps.train.state.training_run_state import TrainingRequest
from tools.dev.mock_smoke.generators import write_mock_training_data


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _wait_until(predicate, timeout_ms: int = 4000) -> None:  # noqa: ANN001
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


def _request(tmp_path, run_id: str) -> TrainingRequest:  # noqa: ANN001
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
    )


def test_qprocess_runner_dev_fast_success_promotes_final_artifact(tmp_path):
    _app()
    request = _request(tmp_path, "run-process-success")
    runner = QProcessTrainingRunner(extra_args=("--dev-fast", "--dev-rows", "8"))
    finished = []
    progress = []

    runner.start(
        request,
        TrainingExecutionCallbacks(
            log=lambda _event: None,
            progress=progress.append,
            finished=finished.append,
            failed=lambda _result: None,
            cancelled=lambda _result: None,
        ),
    )

    _wait_until(lambda: finished and not runner.is_running)

    assert finished[0].status == "complete"
    assert Path(request.model_output_path).exists()
    assert not list(tmp_path.glob("*.tmp"))
    assert progress[-1].completed == progress[-1].total
    assert isinstance(runner, TrainingExecutionPort)


def test_qprocess_runner_cancel_kills_hanging_process_and_removes_temp(tmp_path):
    _app()
    request = _request(tmp_path, "run-process-cancel")
    runner = QProcessTrainingRunner(
        extra_args=("--hang-before-start",),
        terminate_timeout_ms=100,
    )
    cancelled = []

    runner.cancelled.connect(cancelled.append)
    runner.start(request)
    QTimer.singleShot(100, runner.cancel)

    _wait_until(lambda: cancelled and not runner.is_running)

    assert cancelled[0].status == "cancelled"
    assert not Path(request.model_output_path).exists()
    assert not list(tmp_path.glob("*.tmp"))
