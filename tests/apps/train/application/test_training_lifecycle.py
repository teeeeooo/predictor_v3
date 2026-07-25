"""Shared training lifecycle orchestration tests."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import joblib
import pytest
from PySide6.QtCore import QEventLoop, QTimer

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.composition.training_results import build_candidate_publisher
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


def _service(repository, **kwargs):  # noqa: ANN001
    return TrainingLifecycleService(
        repository=repository,
        publisher=build_candidate_publisher(repository),
        **kwargs,
    )


def test_success_publishes_candidate_and_preserves_active(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    publish_candidate(repository, registry_snapshot, "candidate-active")
    repository.replace_active(
        "candidate-active",
        activated_at="2026-01-01T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    execution = ArtifactExecution(artifact_for(registry_snapshot))
    service = _service(
        repository,
        execution=execution,
        registry_provider=lambda: registry_snapshot,
    )
    finished = []

    service.start(_request(tmp_path, registry_snapshot), finished_callback=finished.append)

    assert finished[0].publication_outcome == "published"
    assert Path(finished[0].model_path).is_file()
    assert repository.read_active().candidate_id == "candidate-active"
    assert execution.disposed


def test_publication_failed_rollback_returns_structured_recovery_outcome(
    tmp_path, registry_snapshot
):
    def fail(stage):  # noqa: ANN001
        if stage in {"after_candidate_replace", "before_candidate_rollback"}:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=fail
    )
    service = _service(
        repository,
        execution=ArtifactExecution(artifact_for(registry_snapshot)),
        registry_provider=lambda: registry_snapshot,
    )
    failed = []

    service.start(
        _request(tmp_path, registry_snapshot),
        failed_callback=failed.append,
    )

    assert failed[0].status == "error"
    assert failed[0].publication_outcome == "recovery-required", failed[0]
    assert repository.list_candidates() == ()
    assert not service.is_running


def test_failure_and_cancel_preserve_active_and_publish_nothing(
    tmp_path, registry_snapshot
):
    for terminal in ("failed", "cancelled"):
        repository = ModelLifecycleRepository(tmp_path / terminal)
        publish_candidate(repository, registry_snapshot, "candidate-active")
        repository.replace_active(
            "candidate-active",
            activated_at="2026-01-01T00:00:00+00:00",
            source="test",
            expected_revision=0,
        )
        service = _service(
            repository,
            execution=ArtifactExecution(artifact_for(registry_snapshot), terminal),
            registry_provider=lambda: registry_snapshot,
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
    service = _service(
        repository,
        execution=ArtifactExecution(artifact_for(registry_snapshot)),
        registry_provider=lambda: registry_snapshot,
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
    service = _service(
        repository,
        registry_provider=lambda: registry_snapshot,
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


def test_training_result_application_uses_ports_not_concrete_file_adapters():
    publication = Path(
        "apps/train/application/candidate_publication.py"
    ).read_text(encoding="utf-8")
    lifecycle = Path(
        "apps/train/application/training_lifecycle.py"
    ).read_text(encoding="utf-8")
    evidence_port = Path(
        "apps/train/application/training_results/evidence.py"
    ).read_text(encoding="utf-8")

    combined = publication + lifecycle + evidence_port
    assert "apps.train.adapters" not in combined
    assert "artifact_sha256" not in combined
    assert "read_text(" not in evidence_port
    assert "write_text(" not in evidence_port
    assert ".unlink(" not in evidence_port


def test_qprocess_success_publishes_candidate_without_auto_activation(
    tmp_path, registry_snapshot, qprocess_app
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = _service(
        repository,
        execution=QProcessTrainingRunner(
            extra_args=("--dev-fast", "--dev-rows", "8")
        ),
        registry_provider=lambda: registry_snapshot,
    )
    finished = []
    loop = QEventLoop()
    timeout = QTimer()
    timeout.setSingleShot(True)
    timeout.timeout.connect(loop.quit)

    def record_finished(result):  # noqa: ANN001
        finished.append(result)
        loop.quit()

    service.start(
        _request(tmp_path, registry_snapshot, "candidate-qprocess"),
        finished_callback=record_finished,
    )
    if not finished:
        timeout.start(20000)
        loop.exec()
        timeout.stop()
    qprocess_app.processEvents()

    if not finished:
        service.cancel()
        cleanup = QEventLoop()
        cleanup_timeout = QTimer()
        cleanup_timeout.setSingleShot(True)
        cleanup_timeout.timeout.connect(cleanup.quit)
        cleanup_timeout.start(3000)
        while service.is_running and cleanup_timeout.isActive():
            QTimer.singleShot(25, cleanup.quit)
            cleanup.exec()
        cleanup_timeout.stop()
        qprocess_app.processEvents()
        pytest.fail("QProcess lifecycle publication did not reach terminal state")
    assert finished[0].publication_outcome == "published"
    assert not service.is_running
    assert service._execution is None
    assert repository.read_active(optional=True) is None
    assert repository.read_candidate("candidate-qprocess").model_path.is_file()
