"""Phase 5F strict Experiment Specification and resolver contracts."""

from __future__ import annotations

import json
import subprocess

import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.common.runtime_generation.paths import default_generation_root
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.experiments.contracts import (
    EXPERIMENT_SPEC_VERSION,
    ExperimentContractError,
    resolve_specification,
)
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.experiments.records import (
    APPLICATION_REPOSITORY_ROOT,
    current_revision,
)
from apps.train.composition.experiments import (
    PROJECT_ROOT,
    build_headless_experiment_service,
)
from apps.train.application.training_lifecycle import TrainingLifecycleService
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tools.dev.mock_smoke.generators import write_mock_training_data
from apps.train.interfaces.headless.cli import main
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


def test_production_revision_is_repository_owned_outside_caller_cwd(
    tmp_path, monkeypatch
):
    from_repository_cwd = current_revision()
    monkeypatch.chdir(tmp_path)

    from_external_cwd = current_revision()

    assert from_external_cwd == from_repository_cwd
    assert from_external_cwd["status"] == "identified"
    assert from_external_cwd["revision"]
    assert PROJECT_ROOT == APPLICATION_REPOSITORY_ROOT


def test_revision_detects_different_build_from_external_cwd(tmp_path, monkeypatch):
    repository = tmp_path / "revision-repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "revision@test.invalid"],
        cwd=repository,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Revision Test"],
        cwd=repository,
        check=True,
    )
    source = repository / "source.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "source.py"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"],
        cwd=repository,
        check=True,
    )
    monkeypatch.chdir(tmp_path)
    clean = current_revision(repository)

    source.write_text("VALUE = 2\n", encoding="utf-8")
    dirty = current_revision(repository)

    assert clean["status"] == dirty["status"] == "identified"
    assert clean["revision"] != dirty["revision"]
    assert dirty["dirty"] is True


@pytest.mark.parametrize("valid", (False, True))
def test_headless_validate_is_read_only_in_empty_workspace(
    tmp_path, monkeypatch, capsys, valid
):
    state = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(data)
    if not valid:
        specification["unsupported"] = True
    path = tmp_path / f"{'valid' if valid else 'invalid'}.json"
    path.write_text(json.dumps(specification), encoding="utf-8")

    status = main(["validate", str(path)])
    output = json.loads(capsys.readouterr().out)

    assert status == (EXIT_SUCCESS if valid else 2)
    assert output["outcome"] == (
        "success" if valid else "validation_failure"
    )
    assert not state.exists()


def test_headless_resolve_empty_workspace_blocks_without_bootstrap_publication(
    tmp_path, monkeypatch, capsys
):
    state = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    path = tmp_path / "valid.json"
    path.write_text(json.dumps(_spec(data)), encoding="utf-8")

    status = main(["resolve", str(path)])
    output = json.loads(capsys.readouterr().out)

    assert status == 2
    assert output["outcome"] == "validation_failure"
    assert output["diagnostics"]["code"] == "definition_generation_unavailable"
    assert not state.exists()


def test_headless_service_construction_and_validation_do_not_initialize_workspace(
    tmp_path,
):
    generation_root = tmp_path / "generations"
    lifecycle_root = tmp_path / "lifecycle"
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)

    service = build_headless_experiment_service(
        generation_root=generation_root,
        lifecycle_root=lifecycle_root,
    )
    resolved = service.validate(_spec(data))

    assert resolved.payload["experiment"]["name"] == "contract-test"
    assert not generation_root.exists()
    assert not lifecycle_root.exists()


def test_headless_resolve_reads_existing_generation_without_mutation(
    tmp_path, monkeypatch, capsys
):
    state = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    generations = DataDefinitionGenerationRepository(default_generation_root())
    generations.publish(bootstrap_manifest())
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    path = tmp_path / "valid.json"
    path.write_text(json.dumps(_spec(data)), encoding="utf-8")
    before = {
        item.relative_to(state): item.read_bytes()
        for item in state.rglob("*")
        if item.is_file()
    }

    status = main(["resolve", str(path)])
    output = json.loads(capsys.readouterr().out)
    after = {
        item.relative_to(state): item.read_bytes()
        for item in state.rglob("*")
        if item.is_file()
    }

    assert status == EXIT_SUCCESS
    assert output["outcome"] == "success"
    assert output["data"]["resolved_specification"]["experiment"]["name"] == (
        "contract-test"
    )
    assert after == before
