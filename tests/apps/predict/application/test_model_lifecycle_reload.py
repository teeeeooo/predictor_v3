"""Phase 5E loaded-model observation and safe reload behavior."""

from __future__ import annotations

from dataclasses import replace

import pytest

from apps.common.model_lifecycle import ActiveModelResolver, ModelLifecycleRepository
from apps.predict.application.model_lifecycle import PredictModelLifecycleService
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from apps.predict.services.prediction_service import PredictionService
from tests.apps.common.model_lifecycle.conftest import artifact_for, publish_candidate
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


@pytest.fixture
def repository(tmp_path):
    return ModelLifecycleRepository(tmp_path / "lifecycle")


@pytest.fixture
def registry_snapshot():
    return model_registry_snapshot(bootstrap_manifest())


def _activate(repository, candidate_id: str, revision: int) -> None:
    repository.replace_active(
        candidate_id,
        activated_at=f"2026-07-{revision:02d}T00:00:00+00:00",
        source="test",
        expected_revision=revision - 1,
    )


def _service(path, runtime):  # noqa: ANN001
    return PredictionService(model_file=path, runtime_snapshot=runtime)


def test_active_change_requires_explicit_reload_and_success_swaps_whole_service(
    repository,
    registry_snapshot,
):
    artifact_a = artifact_for(registry_snapshot)
    artifact_a["bundle_marker"] = "A"
    artifact_b = artifact_for(registry_snapshot)
    artifact_b["bundle_marker"] = "B"
    first = publish_candidate(
        repository,
        registry_snapshot,
        "candidate-a",
        artifact=artifact_a,
    )
    second = publish_candidate(
        repository,
        registry_snapshot,
        "candidate-b",
        artifact=artifact_b,
    )
    _activate(repository, first.manifest.candidate_id, 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]

    _activate(repository, second.manifest.candidate_id, 2)
    observed = lifecycle.refresh()

    assert observed.status == "reload-required"
    assert observed.loaded.candidate_id == "candidate-a"
    assert observed.loaded.active_revision == 1
    assert installed[0] is original
    assert installed[0]._model_data["bundle_marker"] == "A"

    outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda service: installed.__setitem__(0, service),
    )

    assert outcome.status == "reloaded"
    assert installed[0] is not original
    assert installed[0]._model_file == str(second.model_path)
    assert installed[0]._model_data["bundle_marker"] == "B"
    assert lifecycle.loaded.candidate_id == "candidate-b"
    assert lifecycle.loaded.active_revision == 2
    assert lifecycle.status.status == "current"


def test_reload_failure_and_corrupt_active_preserve_loaded_service(
    repository,
    registry_snapshot,
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]
    _activate(repository, "candidate-b", 2)
    second.model_path.write_bytes(b"corrupt")

    outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda service: installed.__setitem__(0, service),
    )

    assert outcome.status == "failed"
    assert installed[0] is original
    assert lifecycle.loaded.candidate_id == "candidate-a"
    assert lifecycle.loaded.active_revision == 1
    assert lifecycle.status.status == "reload-failed"
    assert "기존 모델" in outcome.message
    assert lifecycle.status.diagnostic


def test_reload_is_blocked_while_prediction_runs_without_preparation(
    repository,
    registry_snapshot,
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    calls = []
    lifecycle = PredictModelLifecycleService(
        repository,
        runtime,
        lambda path, snapshot: calls.append(path) or _service(path, snapshot),
    )
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    _activate(repository, second.manifest.candidate_id, 2)

    outcome = lifecycle.reload(
        prediction_running=True,
        swap_service=lambda _service: pytest.fail("must not swap"),
    )

    assert outcome.status == "blocked"
    assert calls == []
    assert lifecycle.loaded.candidate_id == "candidate-a"


def test_active_revision_race_discards_stale_prepared_service(
    repository,
    registry_snapshot,
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    third = publish_candidate(repository, registry_snapshot, "candidate-c")
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    raced = False

    def factory(path, snapshot):  # noqa: ANN001
        service = _service(path, snapshot)
        original_prepare = service.prepare_model

        def prepare():
            nonlocal raced
            original_prepare()
            if not raced:
                raced = True
                _activate(repository, third.manifest.candidate_id, 3)

        service.prepare_model = prepare
        return service

    lifecycle = PredictModelLifecycleService(repository, runtime, factory)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]
    _activate(repository, second.manifest.candidate_id, 2)

    outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda service: installed.__setitem__(0, service),
    )

    assert outcome.status == "failed"
    assert installed[0] is original
    assert lifecycle.loaded.candidate_id == "candidate-a"
    assert ActiveModelResolver(repository).resolve().candidate_id == "candidate-c"


def test_runtime_incompatibility_fails_before_swap(
    repository,
    registry_snapshot,
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    _activate(repository, first.manifest.candidate_id, 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    lifecycle.set_runtime_snapshot(
        replace(runtime, preprocessing_version="future-version")
    )
    _activate(repository, second.manifest.candidate_id, 2)

    outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda _service: pytest.fail("must not swap"),
    )

    assert outcome.status == "failed"
    assert lifecycle.loaded.candidate_id == "candidate-a"


def test_active_read_failure_keeps_loaded_identity(
    repository,
    registry_snapshot,
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    _activate(repository, first.manifest.candidate_id, 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(first.model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    repository.active_reference_path.write_text("{invalid", encoding="utf-8")

    status = lifecycle.refresh()

    assert status.status == "active-unavailable"
    assert status.loaded.candidate_id == "candidate-a"
    assert status.loaded.active_revision == 1
    assert status.diagnostic
