"""Phase 5E loaded-model observation and safe reload behavior."""

from __future__ import annotations

from dataclasses import replace
from threading import Event, Thread

import pytest

from apps.common.model_lifecycle import ActiveModelResolver, ModelLifecycleRepository
from apps.common.model_lifecycle.durability_errors import (
    LifecycleRecoveryRequiredError,
)
from apps.predict.application.model_lifecycle import (
    LoadedModelIdentity,
    PredictModelLifecycleService,
)
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
    assert "로드된 모델" in outcome.message
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


def test_older_b_failure_cannot_regress_newer_c_reload_state(
    repository,
    registry_snapshot,
):
    artifacts = {}
    candidates = {}
    for name in ("a", "b", "c", "d"):
        artifact = artifact_for(registry_snapshot)
        artifact["bundle_marker"] = name.upper()
        artifacts[name] = artifact
        candidates[name] = publish_candidate(
            repository,
            registry_snapshot,
            f"candidate-{name}",
            artifact=artifact,
        )
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(candidates["a"].model_path), runtime)
    b_prepared = Event()
    resume_b = Event()

    def factory(path, snapshot):  # noqa: ANN001
        service = _service(path, snapshot)
        if path == str(candidates["b"].model_path):
            prepare = service.prepare_model

            def wait_after_prepare():
                prepare()
                b_prepared.set()
                assert resume_b.wait(timeout=5)

            service.prepare_model = wait_after_prepare
        return service

    lifecycle = PredictModelLifecycleService(repository, runtime, factory)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]
    _activate(repository, "candidate-b", 2)
    b_outcomes = []
    b_thread = Thread(
        target=lambda: b_outcomes.append(
            lifecycle.reload(
                prediction_running=False,
                swap_service=lambda service: installed.__setitem__(0, service),
            )
        )
    )
    b_thread.start()
    assert b_prepared.wait(timeout=5)

    _activate(repository, "candidate-c", 3)
    c_outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda service: installed.__setitem__(0, service),
    )
    active_after_c = repository.read_active()
    resume_b.set()
    b_thread.join(timeout=5)

    assert not b_thread.is_alive()
    assert c_outcome.status == "reloaded"
    assert c_outcome.applied_to_shared_state
    assert installed[0]._model_data["bundle_marker"] == "C"
    assert lifecycle.loaded == LoadedModelIdentity(
        "candidate-c",
        3,
        runtime.generation_id,
    )
    assert lifecycle.status.status == "current"
    assert not lifecycle.status.reload_required
    assert repository.read_active() == active_after_c
    assert b_outcomes[0].status == "failed"
    assert b_outcomes[0].reason_code == "stale_active_revision"
    assert not b_outcomes[0].applied_to_shared_state
    assert b_outcomes[0].model_status.status == "current"

    before_late_refresh = lifecycle.status
    assert lifecycle.status == before_late_refresh
    assert installed[0]._load_model_data()["bundle_marker"] == "C"

    _activate(repository, "candidate-d", 4)
    changed = lifecycle.refresh()
    assert changed.status == "reload-required"
    assert changed.reload_required


def test_older_refresh_cannot_regress_newer_c_reload_success(
    repository,
    registry_snapshot,
    monkeypatch,
):
    candidates = {}
    for name in ("a", "b", "c"):
        artifact = artifact_for(registry_snapshot)
        artifact["bundle_marker"] = name.upper()
        candidates[name] = publish_candidate(
            repository,
            registry_snapshot,
            f"candidate-{name}",
            artifact=artifact,
        )
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(candidates["a"].model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]
    _activate(repository, "candidate-b", 2)
    refresh_observed = Event()
    resume_refresh = Event()
    original_observe = lifecycle._observe_status

    def observe_then_wait(*, operation_id):
        observed = original_observe(operation_id=operation_id)
        if not refresh_observed.is_set():
            refresh_observed.set()
            assert resume_refresh.wait(timeout=5)
        return observed

    monkeypatch.setattr(lifecycle, "_observe_status", observe_then_wait)
    refresh_results = []
    refresh_thread = Thread(target=lambda: refresh_results.append(lifecycle.refresh()))
    refresh_thread.start()
    assert refresh_observed.wait(timeout=5)

    _activate(repository, "candidate-c", 3)
    c_outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda service: installed.__setitem__(0, service),
    )
    active_after_c = repository.read_active()
    resume_refresh.set()
    refresh_thread.join(timeout=5)

    assert not refresh_thread.is_alive()
    assert refresh_results[0].status == "reload-required"
    assert refresh_results[0].active_candidate_id == "candidate-b"
    assert not lifecycle.is_operation_current(refresh_results[0].operation_id)
    assert c_outcome.status == "reloaded"
    assert installed[0]._model_data["bundle_marker"] == "C"
    assert lifecycle.loaded.candidate_id == "candidate-c"
    assert lifecycle.status.status == "current"
    assert not lifecycle.status.reload_required
    assert repository.read_active() == active_after_c
    assert installed[0]._load_model_data()["bundle_marker"] == "C"


def test_older_refresh_cannot_regress_newer_c_reload_failure(
    repository,
    registry_snapshot,
    monkeypatch,
):
    candidates = {
        name: publish_candidate(
            repository,
            registry_snapshot,
            f"candidate-{name}",
        )
        for name in ("a", "b", "c")
    }
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(candidates["a"].model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    _activate(repository, "candidate-b", 2)
    refresh_observed = Event()
    resume_refresh = Event()
    original_observe = lifecycle._observe_status

    def observe_then_wait(*, operation_id):
        observed = original_observe(operation_id=operation_id)
        if not refresh_observed.is_set():
            refresh_observed.set()
            assert resume_refresh.wait(timeout=5)
        return observed

    monkeypatch.setattr(lifecycle, "_observe_status", observe_then_wait)
    refresh_results = []
    refresh_thread = Thread(target=lambda: refresh_results.append(lifecycle.refresh()))
    refresh_thread.start()
    assert refresh_observed.wait(timeout=5)

    _activate(repository, "candidate-c", 3)
    lifecycle.set_runtime_snapshot(
        replace(runtime, preprocessing_version="future-version")
    )
    c_outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda _service: pytest.fail("must not swap"),
    )
    status_after_c = lifecycle.status
    resume_refresh.set()
    refresh_thread.join(timeout=5)

    assert not refresh_thread.is_alive()
    assert refresh_results[0].status == "reload-required"
    assert c_outcome.reason_code == "incompatible_active"
    assert status_after_c.status == "reload-failed"
    assert lifecycle.status == status_after_c
    assert lifecycle.status.reason_code == "incompatible_active"
    assert lifecycle.loaded.candidate_id == "candidate-a"
    assert ActiveModelResolver(repository).resolve().candidate_id == "candidate-c"


def test_older_b_reload_and_callback_state_preserve_newer_c_failure(
    repository,
    registry_snapshot,
):
    candidates = {
        name: publish_candidate(
            repository,
            registry_snapshot,
            f"candidate-{name}",
        )
        for name in ("a", "b", "c")
    }
    _activate(repository, "candidate-a", 1)
    runtime = compatibility_predict_runtime_snapshot()
    original = _service(str(candidates["a"].model_path), runtime)
    b_prepared = Event()
    resume_b = Event()

    def factory(path, snapshot):  # noqa: ANN001
        service = _service(path, snapshot)
        if path == str(candidates["b"].model_path):
            prepare = service.prepare_model

            def wait_after_prepare():
                prepare()
                b_prepared.set()
                assert resume_b.wait(timeout=5)

            service.prepare_model = wait_after_prepare
        return service

    lifecycle = PredictModelLifecycleService(repository, runtime, factory)
    lifecycle.initialize_loaded(
        original,
        candidate_id="candidate-a",
        active_revision=1,
    )
    installed = [original]
    _activate(repository, "candidate-b", 2)
    b_outcomes = []
    b_thread = Thread(
        target=lambda: b_outcomes.append(
            lifecycle.reload(
                prediction_running=False,
                swap_service=lambda service: installed.__setitem__(0, service),
            )
        )
    )
    b_thread.start()
    assert b_prepared.wait(timeout=5)

    _activate(repository, "candidate-c", 3)
    lifecycle.set_runtime_snapshot(
        replace(runtime, preprocessing_version="future-version")
    )
    c_outcome = lifecycle.reload(
        prediction_running=False,
        swap_service=lambda _service: pytest.fail("must not swap"),
    )
    c_failure = lifecycle.status
    active_after_c = repository.read_active()
    resume_b.set()
    b_thread.join(timeout=5)

    assert not b_thread.is_alive()
    assert c_outcome.reason_code == "incompatible_active"
    assert c_outcome.applied_to_shared_state
    assert c_failure.status == "reload-failed"
    assert b_outcomes[0].reason_code == "stale_active_revision"
    assert not b_outcomes[0].applied_to_shared_state
    assert b_outcomes[0].model_status == c_failure
    assert lifecycle.status == c_failure
    assert lifecycle.status.reason_code == "incompatible_active"
    assert installed[0] is original
    assert lifecycle.loaded.candidate_id == "candidate-a"
    assert repository.read_active() == active_after_c


@pytest.mark.parametrize(
    ("setup", "reason_code"),
    (
        ("running", "prediction_running"),
        ("missing", "missing_active"),
        ("recovery", "recovery_required"),
        ("corrupt", "corrupt_active"),
        ("incompatible", "incompatible_active"),
        ("preparation", "replacement_preparation_failed"),
        ("internal", "internal_failure"),
    ),
)
def test_reload_failures_are_structured_and_keep_internal_details_out_of_message(
    repository,
    registry_snapshot,
    monkeypatch,
    setup,
    reason_code,
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    runtime = compatibility_predict_runtime_snapshot()
    if setup != "missing":
        _activate(repository, "candidate-a", 1)
    original = _service(str(candidate.model_path), runtime)
    lifecycle = PredictModelLifecycleService(repository, runtime, _service)
    if setup != "missing":
        lifecycle.initialize_loaded(
            original,
            candidate_id="candidate-a",
            active_revision=1,
        )
    if setup == "corrupt":
        candidate.model_path.write_bytes(b"secret-corrupt-path")
    if setup == "incompatible":
        lifecycle.set_runtime_snapshot(
            replace(runtime, preprocessing_version="secret-fingerprint-version")
        )
    if setup == "preparation":
        lifecycle._service_factory = lambda *_args: (_ for _ in ()).throw(
            RuntimeError("secret replacement path")
        )
    if setup == "recovery":
        monkeypatch.setattr(
            repository,
            "read_active",
            lambda *args, **kwargs: (_ for _ in ()).throw(
                LifecycleRecoveryRequiredError("secret recovery marker")
            ),
        )
    swap_service = (
        (lambda _service: (_ for _ in ()).throw(
            RuntimeError("secret swap callback")
        ))
        if setup == "internal"
        else (lambda _service: pytest.fail("must not swap"))
    )

    outcome = lifecycle.reload(
        prediction_running=setup == "running",
        swap_service=swap_service,
    )

    assert outcome.reason_code == reason_code
    assert outcome.recommended_action
    assert outcome.preserved_loaded_model == (setup != "missing")
    assert outcome.applied_to_shared_state
    assert lifecycle.status == outcome.model_status
    assert lifecycle.status.reason_code == reason_code
    assert "secret" not in outcome.message
    assert "RuntimeError" not in outcome.message
    if setup not in {"running", "missing"}:
        assert outcome.diagnostic
        assert outcome.diagnostic_traceback
