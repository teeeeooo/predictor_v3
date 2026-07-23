"""Shared training lifecycle orchestration tests."""

import os
from pathlib import Path

import joblib
import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.state.training_run_state import TrainingRequest, TrainingResult
from tests.apps.common.model_lifecycle.conftest import artifact_for, publish_candidate
from tools.dev.mock_smoke.generators import write_mock_training_data
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


@pytest.fixture
def registry_snapshot():
    return model_registry_snapshot(bootstrap_manifest())


class ArtifactExecution:
    def __init__(self, artifact, terminal="finished") -> None:  # noqa: ANN001
        self.artifact = artifact
        self.terminal = terminal
        self.disposed = False
        self.request = None

    @property
    def is_running(self):
        return False

    def start(self, request, callbacks):  # noqa: ANN001
        self.request = request
        if self.terminal == "finished":
            joblib.dump(self.artifact, request.model_output_path)
            callbacks.finished(TrainingResult(
                request.run_id, "complete", model_path=request.model_output_path
            ))
        elif self.terminal == "cancelled":
            callbacks.cancelled(TrainingResult(request.run_id, "cancelled"))
        else:
            callbacks.failed(TrainingResult(request.run_id, "error", message="failed"))

    def cancel(self):
        return False

    def dispose(self):
        self.disposed = True


def _request(tmp_path, snapshot, candidate_id="candidate-new"):  # noqa: ANN001
    return TrainingRequest(
        run_id=f"run-{candidate_id}",
        candidate_id=candidate_id,
        data_path=str(write_mock_training_data(output_dir=tmp_path, rows=8)),
    )


def test_success_publishes_candidate_and_preserves_active(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    publish_candidate(repository, registry_snapshot, "candidate-active")
    repository.replace_active(
        "candidate-active", activated_at="2026-01-01T00:00:00+00:00", source="test"
    )
    execution = ArtifactExecution(artifact_for(registry_snapshot))
    service = TrainingLifecycleService(
        execution=execution,
        registry_provider=lambda: registry_snapshot,
        repository=repository,
    )
    finished = []

    service.start(_request(tmp_path, registry_snapshot), finished_callback=finished.append)

    assert finished[0].publication_outcome == "published"
    assert Path(finished[0].model_path).is_file()
    assert repository.read_active().candidate_id == "candidate-active"
    assert execution.disposed


def test_failure_and_cancel_preserve_active_and_publish_nothing(
    tmp_path, registry_snapshot
):
    for terminal in ("failed", "cancelled"):
        repository = ModelLifecycleRepository(tmp_path / terminal)
        publish_candidate(repository, registry_snapshot, "candidate-active")
        repository.replace_active(
            "candidate-active", activated_at="2026-01-01T00:00:00+00:00", source="test"
        )
        service = TrainingLifecycleService(
            execution=ArtifactExecution(artifact_for(registry_snapshot), terminal),
            registry_provider=lambda: registry_snapshot,
            repository=repository,
        )
        service.start(_request(tmp_path, registry_snapshot, f"candidate-{terminal}"))

        assert repository.read_active().candidate_id == "candidate-active"
        assert len(repository.list_candidates()) == 1


def test_publication_exception_becomes_terminal_error_and_preserves_active(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("publish failure"))
            if stage == "before_candidate_replace" else None
        ),
    )
    service = TrainingLifecycleService(
        execution=ArtifactExecution(artifact_for(registry_snapshot)),
        registry_provider=lambda: registry_snapshot,
        repository=repository,
    )
    failed = []

    service.start(
        _request(tmp_path, registry_snapshot),
        failed_callback=failed.append,
    )

    assert failed[0].status == "error"
    assert failed[0].publication_outcome == "failed"
    assert repository.read_active(optional=True) is None
    assert repository.list_candidates() == ()


def test_lifecycle_resource_status_reports_controlled_bootstrap(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    service = TrainingLifecycleService(
        registry_provider=lambda: registry_snapshot,
        repository=repository,
    )

    status = service.resource_status(str(data_path))

    assert status.data_status == "exists"
    assert status.model_status == "missing-active"
    assert "No Active model" in status.message


def test_shared_application_boundary_has_no_pyside_or_train_only_imports():
    source = Path("apps/train/application/training_lifecycle.py").read_text(
        encoding="utf-8"
    )
    assert "PySide6" not in source
    assert "optuna" not in source
    assert "sklearn" not in source


def test_qprocess_success_publishes_candidate_without_auto_activation(
    tmp_path, registry_snapshot
):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = TrainingLifecycleService(
        execution=QProcessTrainingRunner(
            extra_args=("--dev-fast", "--dev-rows", "8")
        ),
        registry_provider=lambda: registry_snapshot,
        repository=repository,
    )
    finished = []
    service.start(
        _request(tmp_path, registry_snapshot, "candidate-qprocess"),
        finished_callback=finished.append,
    )
    loop = QEventLoop()
    poll = QTimer()
    timeout = QTimer()
    poll.setInterval(10)
    timeout.setSingleShot(True)
    poll.timeout.connect(lambda: loop.quit() if finished else None)
    timeout.timeout.connect(loop.quit)
    poll.start()
    timeout.start(5000)
    loop.exec()
    poll.stop()
    timeout.stop()
    app.processEvents()

    assert finished and finished[0].publication_outcome == "published"
    assert repository.read_active(optional=True) is None
    assert repository.read_candidate("candidate-qprocess").model_path.is_file()
