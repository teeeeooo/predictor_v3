"""Phase 5F strict Experiment Specification and resolver contracts."""

from __future__ import annotations

import json

import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.train.application.experiments.contracts import (
    EXPERIMENT_SPEC_VERSION,
    ExperimentContractError,
    resolve_specification,
)
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.training_lifecycle import TrainingLifecycleService
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tools.dev.mock_smoke.generators import write_mock_training_data
from apps.train.interfaces.headless.command_contract import (
    EXIT_CANCELLED,
    EXIT_INTERNAL,
    EXIT_LOCK_CONFLICT,
    EXIT_PARTIAL,
    EXIT_SUCCESS,
    EXIT_TRAINING_FAILURE,
    campaign_exit,
    run_exit,
)


def _spec(data_path, **changes):  # noqa: ANN001
    payload = {
        "schema_version": EXPERIMENT_SPEC_VERSION,
        "experiment": {"name": "contract-test", "purpose": "parity"},
        "data": {"source_path": str(data_path)},
    }
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key] = {**payload[key], **value}
        else:
            payload[key] = value
    return payload


def _service(tmp_path):
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    lifecycle = TrainingLifecycleService(
        registry_provider=lambda: snapshot,
        repository=repository,
    )
    return ExperimentApplicationService(
        lifecycle,
        lifecycle_root=repository.root,
        revision_provider=lambda: "exact-test-head",
    ), snapshot, repository


def test_default_precedence_and_all_defaults_are_explicit(tmp_path):
    data = write_mock_training_data(output_dir=tmp_path, rows=8)
    campaign = _spec(data, optuna={"trials": 7, "cv_folds": 3})
    explicit = _spec(data, optuna={"trials": 2})

    resolved = resolve_specification(explicit, campaign=campaign)

    assert resolved.payload["optuna"] == {
        "cv_folds": 3,
        "trials": 2,
        "n_estimators_min": 100,
        "n_estimators_max": 500,
        "n_jobs": -1,
        "sampler_seed": None,
    }
    assert resolved.payload["campaign"]["max_iterations"] == 1
    assert resolved.payload["retry"]["max_attempts"] == 1


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"python": "print('unsafe')"}, "unsupported_specification_field"),
        ({"schema_version": "predictor_v3.experiment.v999"}, "unsupported_specification_version"),
        ({"data": {"snapshot_request": "../escape"}}, "snapshot_request_unsupported"),
        ({"campaign": {"max_iterations": 101}}, "campaign_budget_unbounded"),
        ({"retry": {"max_attempts": 6}}, "retry_policy_unbounded"),
    ],
)
def test_unsafe_unknown_and_future_contracts_fail_closed(tmp_path, change, code):
    data = write_mock_training_data(output_dir=tmp_path, rows=8)
    with pytest.raises(ExperimentContractError) as failure:
        resolve_specification(_spec(data, **change))
    assert failure.value.code == code


def test_validate_only_and_gui_headless_resolution_are_mutation_free_and_equal(
    tmp_path,
):
    service, snapshot, repository = _service(tmp_path)
    data = write_mock_training_data(output_dir=tmp_path, rows=8)
    gui_spec = service.gui_specification(str(data))
    before = set(tmp_path.rglob("*"))

    headless = service.validate(gui_spec)
    gui, gui_request = service.resolve_gui_request(
        str(data), run_id="gui-run", candidate_id="gui-candidate"
    )
    headless_request = service.training_request(
        headless, run_id="headless-run", candidate_id="headless-candidate"
    )

    assert gui.payload == headless.payload
    assert gui.fingerprint == headless.fingerprint
    assert json.loads(gui_request.registry_payload_json) == json.loads(
        headless_request.registry_payload_json
    )
    assert gui_request.optimization_config_json == headless_request.optimization_config_json
    assert tuple(snapshot.target_presentation_order) == tuple(
        json.loads(gui_request.production_required_target_ids_json)
    )
    assert set(tmp_path.rglob("*")) == before
    assert repository.list_candidates() == ()


def test_machine_exit_contract_distinguishes_terminal_outcomes():
    assert run_exit("success") == EXIT_SUCCESS
    assert run_exit("cancelled") == EXIT_CANCELLED
    assert run_exit("partial") == EXIT_PARTIAL
    assert run_exit("training_failure") == EXIT_TRAINING_FAILURE
    assert run_exit("future") == EXIT_INTERNAL
    assert campaign_exit("lock_conflict") == EXIT_LOCK_CONFLICT
    assert campaign_exit("cancelled_resumable") == EXIT_CANCELLED
    assert campaign_exit("blocked") == EXIT_TRAINING_FAILURE
