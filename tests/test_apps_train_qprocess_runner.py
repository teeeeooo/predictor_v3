"""QProcessTrainingRunner process-boundary tests."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEventLoop, QProcess, QTimer

from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.ports.training_execution_port import (
    TrainingExecutionCallbacks,
    TrainingExecutionPort,
)
from apps.train.state.training_run_state import TrainingRequest
from tools.dev.mock_smoke.generators import write_mock_training_data


def _request(tmp_path, run_id: str) -> TrainingRequest:  # noqa: ANN001
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
    )


def _run_to_terminal(
    qprocess_app,
    runner,
    request,
    *,
    after_start=None,
    timeout_ms: int = 20000,
):  # noqa: ANN001
    terminal = []
    progress = []
    started = []
    loop = QEventLoop()
    timeout = QTimer()
    timeout.setSingleShot(True)

    def record(kind, result):  # noqa: ANN001
        terminal.append((kind, result))
        loop.quit()

    callbacks = TrainingExecutionCallbacks(
        started=started.append,
        log=lambda _event: None,
        progress=progress.append,
        finished=lambda result: record("finished", result),
        failed=lambda result: record("failed", result),
        cancelled=lambda result: record("cancelled", result),
    )
    timeout.timeout.connect(loop.quit)
    runner.start(request, callbacks)
    if after_start is not None:
        after_start(runner)
    if not terminal:
        timeout.start(timeout_ms)
        loop.exec()
        timeout.stop()
    qprocess_app.processEvents()

    if not terminal:
        runner.cancel()
        cleanup = QEventLoop()
        cleanup_timeout = QTimer()
        cleanup_timeout.setSingleShot(True)
        cleanup_timeout.timeout.connect(cleanup.quit)
        process = runner._process
        if process is not None:
            process.finished.connect(cleanup.quit)
        cleanup_timeout.start(3000)
        cleanup.exec()
        cleanup_timeout.stop()
        runner.dispose()
        qprocess_app.processEvents()
        pytest.fail("QProcess did not produce a terminal event")
    assert len(terminal) == 1
    assert runner._process is None
    assert not runner.is_running
    return terminal[0], progress, started


def test_qprocess_runner_dev_fast_success_promotes_final_artifact(
    tmp_path, qprocess_app
):
    request = _request(tmp_path, "run-process-success")
    runner = QProcessTrainingRunner(extra_args=("--dev-fast", "--dev-rows", "8"))

    (kind, result), progress, started = _run_to_terminal(
        qprocess_app, runner, request
    )

    assert (kind, result.status) == ("finished", "complete")
    assert Path(request.model_output_path).exists()
    assert not list(tmp_path.glob("*.tmp"))
    assert progress[-1].completed == progress[-1].total
    assert started == [request]
    assert isinstance(runner, TrainingExecutionPort)
    runner.dispose()


@pytest.mark.parametrize("cancel_phase", ("starting", "running"))
def test_qprocess_cancel_is_exactly_once_cancelled(
    tmp_path, qprocess_app, cancel_phase
):
    request = _request(tmp_path, f"run-process-cancel-{cancel_phase}")
    runner = QProcessTrainingRunner(
        extra_args=("--hang-before-start",),
        terminate_timeout_ms=100,
    )

    def schedule_cancel(active_runner):  # noqa: ANN001
        def cancel_twice():
            assert active_runner.cancel()
            assert active_runner.cancel()

        if cancel_phase == "starting":
            cancel_twice()
            return
        process = active_runner._process
        assert process is not None
        if process.state() == QProcess.Running:
            cancel_twice()
        else:
            process.started.connect(cancel_twice)

    (kind, result), _progress, started = _run_to_terminal(
        qprocess_app, runner, request, after_start=schedule_cancel
    )

    assert (kind, result.status) == ("cancelled", "cancelled")
    assert result.message == "Training process cancelled."
    assert started == []
    assert not Path(request.model_output_path).exists()
    assert not list(tmp_path.glob("*.tmp"))
    runner.dispose()


def test_qprocess_genuine_launch_failure_is_failed(tmp_path, qprocess_app):
    request = _request(tmp_path, "run-process-launch-failure")
    runner = QProcessTrainingRunner(
        python_executable=str(tmp_path / "does-not-exist-python")
    )

    (kind, result), _progress, started = _run_to_terminal(
        qprocess_app, runner, request
    )

    assert (kind, result.status) == ("failed", "error")
    assert result.message == "Training process failed to start."
    assert started == []
    assert not Path(request.model_output_path).exists()
    assert not list(tmp_path.glob("*.tmp"))
    runner.dispose()
