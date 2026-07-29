"""Actual child-process regressions for confirmation start permits."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from apps.common.model_lifecycle.closeout.start_handshake import (
    CONFIRMATION_START_HANDSHAKE_VERSION,
    build_confirmation_start_handshake,
    build_confirmation_start_permit,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.application.confirmation.execution_contracts import (
    FrozenConfirmationRequest,
)
from apps.train.application.confirmation.lifecycle_executor import (
    TrainingLifecycleConfirmationExecutor,
)
from apps.train.application.training_start_handshake import (
    training_meaning_sha256,
)
from apps.train.adapters.subprocess_training_runner import (
    SubprocessTrainingRunner,
)
from apps.train.composition.experiments import (
    build_headless_experiment_service,
)
from apps.train.ports.training_execution_port import TrainingExecutionCallbacks
from apps.train.state.training_run_state import TrainingRequest
from tools.dev.mock_smoke.generators import write_mock_training_data
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


HASH = "a" * 64


def test_training_meaning_is_stable_across_launch_attempt_coordinates() -> None:
    first = TrainingRequest(
        run_id="confirmation-run-attempt-one",
        model_output_path="/tmp/attempt-one/model.pkl",
        candidate_id="candidate-confirmation",
        publication_source="confirmation",
    )
    second = replace(
        first,
        run_id="confirmation-run-attempt-two",
        model_output_path="/tmp/attempt-two/model.pkl",
    )

    assert training_meaning_sha256(first) == training_meaning_sha256(second)


def _request(
    tmp_path: Path,
    *,
    run_id: str,
    attempt_id: str,
    permit_path: Path,
) -> tuple[TrainingRequest, dict]:
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    handshake = build_confirmation_start_handshake(
        confirmation_id="confirmation-process-boundary",
        execution_key=HASH,
        attempt_id=attempt_id,
        training_meaning_sha256=HASH,
        permit_path=permit_path,
    )
    request = TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
        publication_source="confirmation",
        confirmation_fixed_parameters_json='{"target": {"depth": 1}}',
        confirmation_fixed_features_json='{"target": ["feature"]}',
        confirmation_start_handshake_json=json.dumps(
            handshake, sort_keys=True, separators=(",", ":")
        ),
    )
    return request, handshake


def _run(
    request: TrainingRequest,
    *,
    work_marker: Path,
    start_requested,
    timeout: str = "0.25",
) -> tuple[list, list, list]:
    started: list = []
    finished: list = []
    failed: list = []
    runner = SubprocessTrainingRunner(
        extra_args=(
            "--dev-fast",
            "--dev-rows",
            "8",
            "--start-permit-timeout-seconds",
            timeout,
            "--actual-work-marker-path",
            str(work_marker),
        )
    )
    runner.start(
        request,
        TrainingExecutionCallbacks(
            started=started.append,
            log=lambda _event: None,
            progress=lambda _event: None,
            finished=finished.append,
            failed=failed.append,
            cancelled=lambda result: failed.append(result),
            start_requested=start_requested,
        ),
    )
    return started, finished, failed


def test_child_does_no_work_when_parent_fails_before_permit(
    tmp_path: Path,
) -> None:
    permit_path = tmp_path / "execution_started.json"
    work_marker = tmp_path / "actual-work"
    request, _handshake = _request(
        tmp_path,
        run_id="permit-before-parent-failure",
        attempt_id="attempt-first",
        permit_path=permit_path,
    )
    requested = []

    started, finished, failed = _run(
        request,
        work_marker=work_marker,
        start_requested=requested.append,
    )

    assert len(requested) == 1
    assert started == []
    assert finished == []
    assert len(failed) == 1
    assert not permit_path.exists()
    assert not work_marker.exists()
    assert not Path(request.model_output_path).exists()


def test_child_starts_only_after_exact_durable_permit(
    tmp_path: Path,
) -> None:
    permit_path = tmp_path / "execution_started.json"
    work_marker = tmp_path / "actual-work"
    request, handshake = _request(
        tmp_path,
        run_id="permit-success",
        attempt_id="attempt-success",
        permit_path=permit_path,
    )

    def permit(_start_request) -> None:  # noqa: ANN001
        permit_path.write_text(
            json.dumps(build_confirmation_start_permit(handshake)),
            encoding="utf-8",
        )

    started, finished, failed = _run(
        request,
        work_marker=work_marker,
        start_requested=permit,
    )

    assert started == [request]
    assert len(finished) == 1
    assert failed == []
    assert work_marker.read_text(encoding="utf-8").strip() == request.run_id
    assert Path(request.model_output_path).exists()


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("execution_key", "b" * 64),
        ("attempt_id", "attempt-stale"),
        (
            "protocol_version",
            CONFIRMATION_START_HANDSHAKE_VERSION + ".corrupt",
        ),
    ),
)
def test_corrupt_or_stale_permit_never_crosses_work_boundary(
    tmp_path: Path,
    field: str,
    replacement: str,
) -> None:
    permit_path = tmp_path / "execution_started.json"
    work_marker = tmp_path / "actual-work"
    request, handshake = _request(
        tmp_path,
        run_id=f"permit-corrupt-{field}",
        attempt_id="attempt-current",
        permit_path=permit_path,
    )

    def corrupt(_start_request) -> None:  # noqa: ANN001
        permit = build_confirmation_start_permit(handshake)
        permit[field] = replacement
        permit_path.write_text(json.dumps(permit), encoding="utf-8")

    started, finished, failed = _run(
        request,
        work_marker=work_marker,
        start_requested=corrupt,
    )

    assert started == []
    assert finished == []
    assert len(failed) == 1
    assert not work_marker.exists()
    assert not Path(request.model_output_path).exists()


def test_stale_waiting_child_cannot_consume_replacement_attempt_permit(
    tmp_path: Path,
) -> None:
    permit_path = tmp_path / "execution_started.json"
    first_marker = tmp_path / "first-work"
    second_marker = tmp_path / "second-work"
    first, _first_handshake = _request(
        tmp_path,
        run_id="stale-first-child",
        attempt_id="attempt-first",
        permit_path=permit_path,
    )
    second, second_handshake = _request(
        tmp_path,
        run_id="replacement-child",
        attempt_id="attempt-second",
        permit_path=permit_path,
    )

    def publish_replacement(_start_request) -> None:  # noqa: ANN001
        permit_path.write_text(
            json.dumps(build_confirmation_start_permit(second_handshake)),
            encoding="utf-8",
        )

    first_started, _first_finished, first_failed = _run(
        first,
        work_marker=first_marker,
        start_requested=publish_replacement,
    )
    second_started, second_finished, second_failed = _run(
        second,
        work_marker=second_marker,
        start_requested=lambda _request: None,
    )

    assert first_started == []
    assert len(first_failed) == 1
    assert not first_marker.exists()
    assert second_started == [second]
    assert len(second_finished) == 1
    assert second_failed == []
    assert second_marker.exists()


def test_non_confirmation_child_keeps_existing_start_behavior(
    tmp_path: Path,
) -> None:
    work_marker = tmp_path / "ordinary-work"
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    request = TrainingRequest(
        run_id="ordinary-training",
        data_path=str(data_path),
        model_output_path=str(tmp_path / "ordinary.pkl"),
    )
    requested = []

    started, finished, failed = _run(
        request,
        work_marker=work_marker,
        start_requested=requested.append,
    )

    assert requested == []
    assert started == [request]
    assert len(finished) == 1
    assert failed == []
    assert work_marker.exists()


def test_normal_confirmation_completes_real_subprocess_and_candidate_publication(
    tmp_path: Path,
) -> None:
    lifecycle_root = tmp_path / "lifecycle"
    generation_root = tmp_path / "generations"
    repository = ModelLifecycleRepository(lifecycle_root)
    store = LifecycleCloseoutStore(lifecycle_root)
    data_path = write_mock_training_data(
        output_dir=tmp_path / "data",
        rows=8,
    )
    materialized = store.materialize_local_source(
        data_path,
        filtering_meaning={"kind": "process-handshake-test"},
    )
    experiments = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        generation_root=generation_root,
        extra_training_args=("--dev-fast", "--dev-rows", "8"),
    )
    specification = experiments.validate({
        "schema_version": "predictor_v3.experiment.v1",
        "experiment": {"name": "confirmation-handshake", "purpose": "test"},
        "data": {"source_path": str(data_path)},
    })
    snapshot = model_registry_snapshot(bootstrap_manifest())
    target_ids = tuple(
        target.identity
        for group in snapshot.groups
        for target in group.targets
    )
    execution_key = "c" * 64
    permit_path = store.confirmation_execution_start_permit_path(
        execution_key
    )

    def prepare(training_meaning_sha256: str) -> dict:
        return build_confirmation_start_handshake(
            confirmation_id="confirmation-real-process",
            execution_key=execution_key,
            attempt_id="attempt-real-process",
            training_meaning_sha256=training_meaning_sha256,
            permit_path=permit_path,
        )

    def permit(handshake: dict) -> None:
        permit_path.parent.mkdir(parents=True, exist_ok=True)
        permit_path.write_text(
            json.dumps(build_confirmation_start_permit(handshake)),
            encoding="utf-8",
        )

    executor = TrainingLifecycleConfirmationExecutor(
        experiments,
        repository,
        object(),
        closeout_store=store,
    )
    result = executor.execute(FrozenConfirmationRequest(
        confirmation_id="confirmation-real-process",
        snapshot_id="snapshot-process",
        selected_candidate_id="selected-process",
        resolved_specification=specification.payload,
        production_required_targets=target_ids,
        selected_parameters={
            identity: {"depth": 1} for identity in target_ids
        },
        training_data={
            "materialized_identity": materialized["materialized_identity"]
        },
        definition_runtime={
            "confirmation_targets": [
                {
                    "identity": identity,
                    "ordered_features": ["mock-feature"],
                }
                for identity in target_ids
            ]
        },
        evaluation_contract={},
        execution_key=execution_key,
        start_attempt_id="attempt-real-process",
        start_permit_path=str(permit_path),
        execution_start_prepare=prepare,
        execution_start_permit=permit,
    ))

    assert result.status == "succeeded"
    assert (
        result.confirmation_candidate_id
        == "candidate-confirmation-real-process"
    )
    assert permit_path.exists()
    candidates = repository.list_candidates()
    assert len(candidates) == 1
