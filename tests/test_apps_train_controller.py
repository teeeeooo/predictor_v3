"""Qt-free TrainController execution-port orchestration tests."""

from pathlib import Path

import pytest

from apps.train.controllers.train_controller import TrainController
from apps.train.ports.training_execution_port import (
    TrainingExecutionCallbacks,
    TrainingExecutionPort,
)
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)
from tools.dev.mock_smoke.generators import write_mock_training_data


def _request(tmp_path, run_id: str = "run-controller") -> TrainingRequest:  # noqa: ANN001
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
    )


class FakeTrainingExecution:
    """Runtime-neutral port double for controller tests."""

    def __init__(self, *, finish_immediately: bool = True) -> None:
        self.started = False
        self.cancel_called = False
        self.dispose_called = False
        self.request: TrainingRequest | None = None
        self.callbacks: TrainingExecutionCallbacks | None = None
        self.finish_immediately = finish_immediately
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(
        self,
        request: TrainingRequest,
        callbacks: TrainingExecutionCallbacks | None = None,
    ) -> None:
        assert callbacks is not None
        self.started = True
        self._is_running = True
        self.request = request
        self.callbacks = callbacks
        callbacks.log(TrainingLogEvent(request.run_id, "fake execution started"))
        callbacks.progress(
            TrainingProgress(
                run_id=request.run_id,
                completed=0,
                total=1,
                message="running",
                indeterminate=False,
            )
        )
        if self.finish_immediately:
            self.complete()

    def cancel(self) -> bool:
        assert self.request is not None
        assert self.callbacks is not None
        self.cancel_called = True
        self._is_running = False
        self.callbacks.cancelled(
            TrainingResult(
                run_id=self.request.run_id,
                status="cancelled",
                model_path=self.request.model_output_path,
                message="cancelled",
            )
        )
        return True

    def complete(self) -> None:
        assert self.request is not None
        assert self.callbacks is not None
        self._is_running = False
        self.callbacks.progress(
            TrainingProgress(
                run_id=self.request.run_id,
                completed=1,
                total=1,
                message="complete",
                indeterminate=False,
            )
        )
        self.callbacks.finished(
            TrainingResult(
                run_id=self.request.run_id,
                status="complete",
                model_path=self.request.model_output_path,
                message="complete",
            )
        )

    def dispose(self) -> None:
        self.dispose_called = True


def test_training_execution_double_satisfies_port_contract():
    assert isinstance(FakeTrainingExecution(), TrainingExecutionPort)


def test_train_controller_start_runs_execution_port(tmp_path):
    execution = FakeTrainingExecution()
    controller = TrainController(execution=execution)
    finished = []
    progress = []

    controller.start(
        _request(tmp_path),
        progress_callback=progress.append,
        finished_callback=finished.append,
    )

    assert progress[-1].completed == progress[-1].total
    assert finished[0].status == "complete"
    assert controller.last_result == finished[0]
    assert not controller.is_running
    assert execution.dispose_called
    assert controller._execution is None


def test_train_controller_rejects_double_start(tmp_path):
    execution = FakeTrainingExecution(finish_immediately=False)
    controller = TrainController(execution=execution)

    controller.start(_request(tmp_path))
    assert execution.started
    assert controller.is_running
    with pytest.raises(RuntimeError, match="already in progress"):
        controller.start(_request(tmp_path, "second"))

    execution.complete()
    assert controller._execution is None


def test_train_controller_missing_data_path_returns_controlled_error(tmp_path):
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
    assert controller._execution is None


def test_train_controller_valid_request_without_adapter_is_controlled_error(tmp_path):
    controller = TrainController()
    failed = []

    result = controller.start(_request(tmp_path), failed_callback=failed.append)

    assert result is not None
    assert result.status == "error"
    assert "adapter is not configured" in result.message
    assert failed == [result]


def test_train_controller_uses_execution_factory_for_each_run(tmp_path):
    executions: list[FakeTrainingExecution] = []

    def factory() -> FakeTrainingExecution:
        execution = FakeTrainingExecution()
        executions.append(execution)
        return execution

    controller = TrainController(execution_factory=factory)

    controller.start(_request(tmp_path, "first"))
    controller.start(_request(tmp_path, "second"))

    assert len(executions) == 2
    assert all(execution.dispose_called for execution in executions)


def test_train_controller_cancel_calls_execution_port(tmp_path):
    execution = FakeTrainingExecution(finish_immediately=False)
    controller = TrainController(execution=execution)
    cancelled = []

    controller.start(_request(tmp_path), cancelled_callback=cancelled.append)
    assert controller.cancel()

    assert execution.cancel_called
    assert cancelled[0].status == "cancelled"
    assert controller.last_result == cancelled[0]
    assert controller._execution is None


def test_train_controller_source_is_runtime_neutral():
    source = Path("apps/train/controllers/train_controller.py").read_text(encoding="utf-8")

    for forbidden in (
        "PySide6",
        "QProcess",
        "QObject",
        "QThread",
        ".connect(",
        "deleteLater",
    ):
        assert forbidden not in source
