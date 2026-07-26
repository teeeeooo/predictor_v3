"""Phase 5F workspace writer serialization and lock diagnostics."""

from __future__ import annotations

import json

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.train.application.experiments.execution_lock import (
    ExecutionLockConflict,
    WorkspaceExecutionLock,
    execution_lock_is_held,
    read_lock_metadata,
)
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.experiments.campaign import CampaignApplicationService
from apps.train.application.training_lifecycle import TrainingLifecycleService
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tools.dev.mock_smoke.generators import write_mock_training_data


def test_lock_conflict_has_diagnostics_and_no_training_or_run_mutation(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    lifecycle = TrainingLifecycleService(
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    service = ExperimentApplicationService(
        lifecycle, lifecycle_root=repository.root
    )
    data = write_mock_training_data(output_dir=tmp_path, rows=8)
    specification = service.gui_specification(str(data))
    lock = WorkspaceExecutionLock(
        repository.root, owner="gui", run_id="existing-run"
    )
    lock.acquire()
    try:
        assert execution_lock_is_held(repository.root / ".training-execution.lock")
        result = service.run(specification, run_id="conflicting-run")
        metadata = read_lock_metadata(
            repository.root / ".training-execution.lock"
        )
    finally:
        lock.release()

    assert result is not None and result.status == "lock_conflict"
    assert json.loads(result.summary)["run_id"] == "existing-run"
    assert metadata["execution_owner"] == "gui"
    assert metadata["process_id"]
    assert metadata["started_at"]
    assert metadata["heartbeat_at"]
    assert metadata["current_stage"]
    assert not (repository.root / "experiments" / "runs" / "conflicting-run").exists()
    assert repository.list_candidates() == ()
    assert not repository.staging_path.exists()


def test_lock_never_force_steals_another_owner(tmp_path):
    first = WorkspaceExecutionLock(tmp_path, owner="gui", run_id="one")
    second = WorkspaceExecutionLock(tmp_path, owner="campaign", run_id="two")
    first.acquire()
    try:
        try:
            second.acquire()
        except ExecutionLockConflict as conflict:
            assert conflict.metadata["run_id"] == "one"
        else:
            raise AssertionError("second writer unexpectedly acquired the lock")
    finally:
        first.release()


def test_campaign_lock_conflict_consumes_no_iteration_or_attempt(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    service = ExperimentApplicationService(
        TrainingLifecycleService(
            registry_provider=lambda: snapshot,
            repository=repository,
        ),
        lifecycle_root=repository.root,
        revision_provider=lambda: "head",
    )
    data = write_mock_training_data(output_dir=tmp_path, rows=8)
    specification = service.gui_specification(str(data))
    specification["campaign"] = {
        "max_iterations": 1,
        "experiments": [{"experiment": {"name": "blocked"}}],
    }
    lock = WorkspaceExecutionLock(
        repository.root, owner="gui", run_id="existing-run"
    )
    lock.acquire()
    try:
        record = CampaignApplicationService(service).start(
            specification, campaign_id="lock-conflict-campaign"
        )
    finally:
        lock.release()

    assert record["status"] == "lock_conflict"
    assert record["budget"]["consumed_iterations"] == 0
    assert record["attempt_history"] == []
    assert repository.list_candidates() == ()
    assert not repository.staging_path.exists()
