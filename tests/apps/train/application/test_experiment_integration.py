"""Targeted Phase 5F application integration through Candidate publication."""

from __future__ import annotations

import json

import joblib
import pandas as pd
import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository
from apps.train.application.experiments.campaign import CampaignApplicationService
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.composition.training_results import build_candidate_publisher
from apps.train.state.training_run_state import TrainingResult
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    model_registry_snapshot,
)
from core.ml.training_results import TrainingOptimizationConfig
from tests.apps.common.model_lifecycle.conftest import artifact_for, publish_candidate
from tools.dev.mock_smoke.generators import write_mock_training_data


class _DynamicArtifactExecution:
    def __init__(self, *, terminal: str = "finished", before_terminal=None) -> None:  # noqa: ANN001
        self.terminal = terminal
        self.before_terminal = before_terminal or (lambda: None)

    @property
    def is_running(self):
        return False

    def start(self, request, callbacks):  # noqa: ANN001
        snapshot = ModelRegistrySnapshot.from_payload(
            json.loads(request.registry_payload_json)
        )
        callbacks.started(request)
        if self.terminal == "finished":
            joblib.dump(artifact_for(snapshot), request.model_output_path)
        self.before_terminal()
        result = TrainingResult(
            request.run_id,
            "complete" if self.terminal == "finished" else self.terminal,
            model_path=request.model_output_path,
            message=self.terminal,
        )
        getattr(
            callbacks,
            self.terminal if self.terminal in {"finished", "cancelled"} else "failed",
        )(result)

    def cancel(self):
        return False

    def dispose(self):
        return None


class _StartFailureExecution:
    @property
    def is_running(self):
        return False

    def start(self, _request, _callbacks):  # noqa: ANN001
        raise OSError("child process creation failed")

    def cancel(self):
        return False

    def dispose(self):
        return None


class _CoreOwnerExecution:
    def __init__(self, training_module) -> None:  # noqa: ANN001
        self._training = training_module

    @property
    def is_running(self):
        return False

    def start(self, request, callbacks):  # noqa: ANN001
        snapshot = ModelRegistrySnapshot.from_payload(
            json.loads(request.registry_payload_json)
        )
        try:
            output = self._training.train_all_models_with_analysis(
                data_path=request.data_path,
                model_output_path=request.model_output_path,
                registry_snapshot=snapshot,
                training_started_callback=lambda: callbacks.started(request),
            )
        except Exception as exc:
            callbacks.failed(TrainingResult(
                request.run_id,
                "error",
                model_path=request.model_output_path,
                message=str(exc),
            ))
            return
        terminal = (
            callbacks.finished
            if output.evidence.status == "complete"
            else callbacks.failed
        )
        terminal(TrainingResult(
            request.run_id,
            (
                "complete"
                if output.evidence.status == "complete"
                else "error"
            ),
            summary=output.summary,
            model_path=request.model_output_path,
            message=output.evidence.status,
        ))

    def cancel(self):
        return False

    def dispose(self):
        return None


def _service(tmp_path, execution_factory, *, revision="test-head"):  # noqa: ANN001
    snapshot = model_registry_snapshot(bootstrap_manifest())
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    lifecycle = TrainingLifecycleService(
        execution_factory=execution_factory,
        registry_provider=lambda: snapshot,
        repository=repository,
        publisher=build_candidate_publisher(repository),
    )
    service = ExperimentApplicationService(
        lifecycle,
        lifecycle_root=repository.root,
        revision_provider=lambda: revision,
    )
    return service, snapshot, repository


def _spec(data_path, *, name="experiment", campaign=None, features=None):  # noqa: ANN001
    return {
        "schema_version": "predictor_v3.experiment.v1",
        "experiment": {"name": name, "purpose": "integration"},
        "data": {"source_path": str(data_path)},
        **({"features": features} if features else {}),
        **({"campaign": campaign} if campaign else {}),
        "optuna": {
            "cv_folds": 2,
            "trials": 1,
            "n_estimators_min": 2,
            "n_estimators_max": 2,
            "n_jobs": 1,
            "sampler_seed": 42,
        },
    }


def test_single_run_persists_resolved_contract_candidate_and_phase5c_artifacts(
    tmp_path,
):
    service, snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    publish_candidate(repository, snapshot, "active-before")
    repository.replace_active(
        "active-before",
        activated_at="2026-07-26T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)

    service.run(_spec(data), run_id="headless-complete")

    record = service.inspect_run("headless-complete")
    candidate = repository.read_candidate("candidate-headless-complete")
    assert record["status"] == "success"
    assert record["resolved_specification"]["optuna"]["trials"] == 1
    assert record["contract_identity"]["build_revision"] == {
        "status": "identified",
        "revision": "test-head",
        "dirty": False,
    }
    assert record["result"]["candidate_reference"] == candidate.manifest.candidate_id
    assert (candidate.path / "training_result.json").is_file()
    assert (candidate.path / "training_report.xlsx").is_file()
    assert repository.read_active().candidate_id == "active-before"


def test_experimental_derived_candidate_is_immutable_but_not_promotable(tmp_path):
    service, _snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    experimental = {
        "experimental_derived": [{
            "output": "Experiment Ratio",
            "operation": "safe_ratio",
            "numerator": "Cooling Capa",
            "denominator": "Evap Area",
            "zero_denominator_policy": "constant",
            "zero_value": 0.0,
        }]
    }

    service.run(
        _spec(data, features=experimental),
        run_id="experimental-derived",
    )

    candidate = repository.read_candidate("candidate-experimental-derived")
    assert candidate.manifest.contains_unpublished_features
    assert not candidate.manifest.promotion_eligible
    assert "unpublished_experimental_features" in candidate.manifest.blocking_reasons


def test_experiment_feature_policy_candidate_is_not_promotable(tmp_path):
    service, snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(data)
    specification["features"] = {"excluded": [snapshot.input_ml_names[0]]}

    service.run(specification, run_id="feature-policy")

    candidate = repository.read_candidate("candidate-feature-policy")
    assert not candidate.manifest.promotion_eligible
    assert "experiment_feature_policy" in candidate.manifest.blocking_reasons


def test_target_scoped_result_is_preserved_but_never_published_as_candidate(
    tmp_path,
):
    service, snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(data)
    specification["targets"] = {
        "primary": [snapshot.target_presentation_order[0]],
    }

    service.run(specification, run_id="target-scoped")

    record = service.inspect_run("target-scoped")
    assert record["status"] == "partial", json.dumps(record["result"])
    assert repository.list_candidates() == ()
    assert record["result"]["publication_outcome"] == "partial"
    assert record["result"]["evidence_reference"]


def test_partial_run_has_structured_record_and_evidence_but_no_candidate(tmp_path):
    service, _snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution(terminal="partial")
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)

    service.run(_spec(data), run_id="partial-run")

    record = service.inspect_run("partial-run")
    assert record["status"] == "partial"
    assert repository.list_candidates() == ()
    assert record["result"]["evidence_reference"]
    assert (
        repository.run_evidence_path
        / "partial-run"
        / "training_result.json"
    ).is_file()


def test_campaign_pause_after_current_run_resume_and_attempt_history(tmp_path):
    holder = {}
    execution_count = {"value": 0}

    def execution_factory():
        execution_count["value"] += 1
        return _DynamicArtifactExecution(
            before_terminal=(
                lambda: holder["service"].store.request_control(
                    "campaign-pause-resume", "pause"
                )
                if execution_count["value"] == 1
                else None
            )
        )

    service, _snapshot, _repository = _service(tmp_path, execution_factory)
    holder["service"] = service
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    campaign_spec = _spec(
        data,
        campaign={
            "max_iterations": 2,
            "experiments": [
                {"experiment": {"name": "first"}},
                {"experiment": {"name": "second"}},
            ],
        },
    )
    campaigns = CampaignApplicationService(service)

    paused = campaigns.start(
        campaign_spec, campaign_id="campaign-pause-resume"
    )
    resumed = campaigns.resume("campaign-pause-resume")

    assert paused["status"] == "paused"
    assert paused["budget"]["consumed_iterations"] == 1
    assert len(paused["completed_runs"]) == 1
    assert resumed["status"] == "completed"
    assert resumed["budget"]["consumed_iterations"] == 2
    assert len(resumed["completed_runs"]) == 2
    assert [item["attempt"] for item in resumed["attempt_history"]] == [1, 1]


def test_campaign_bounded_retry_preserves_attempts_without_extra_budget(tmp_path):
    terminals = iter(("failed", "finished"))
    service, _snapshot, repository = _service(
        tmp_path,
        lambda: _DynamicArtifactExecution(terminal=next(terminals)),
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "retry-once"}}],
        },
    )
    specification["retry"] = {
        "max_attempts": 2,
        "retryable_statuses": ["training_failure"],
    }

    record = CampaignApplicationService(service).start(
        specification, campaign_id="campaign-retry"
    )

    assert record["status"] == "completed"
    assert record["budget"]["consumed_iterations"] == 1
    assert [item["status"] for item in record["attempt_history"]] == [
        "training_failure",
        "success",
    ]
    assert all(item["training_started"] for item in record["attempt_history"])
    assert len(repository.list_candidates()) == 1
    assert (
        repository.run_evidence_path
        / "campaign-retry-iteration-1-attempt-1"
        / "training_result.json"
    ).is_file()


def test_campaign_cancel_is_resumable_and_does_not_publish_candidate(tmp_path):
    service, _snapshot, repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution(terminal="cancelled")
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "cancelled"}}],
        },
    )

    record = CampaignApplicationService(service).start(
        specification, campaign_id="campaign-cancelled"
    )

    assert record["status"] == "cancelled_resumable"
    assert record["budget"]["consumed_iterations"] == 1
    assert repository.list_candidates() == ()
    assert record["attempt_history"][0]["status"] == "cancelled"
    assert record["attempt_history"][0]["training_started"]


def test_core_preflight_failure_does_not_consume_iteration(
    tmp_path, monkeypatch
):
    import core.ml.training as core_training

    monkeypatch.setattr(
        core_training,
        "validate_training_input_headers",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("Core preflight failed before training.")
        ),
    )
    service, _snapshot, repository = _service(
        tmp_path, lambda: _CoreOwnerExecution(core_training)
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "core-preflight"}}],
        },
    )

    record = CampaignApplicationService(service).start(
        specification, campaign_id="campaign-core-preflight"
    )

    assert record["status"] == "failed_resumable"
    assert record["budget"]["consumed_iterations"] == 0
    assert record["completed_runs"] == []
    assert record["attempt_history"][0]["training_started"] is False
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None


def test_core_optimization_config_preflight_does_not_acknowledge_start():
    from core.ml.training_results import optimize_and_train

    acknowledgements = []
    with pytest.raises(ValueError, match="cv_folds"):
        optimize_and_train(
            pd.DataFrame({"feature": [1.0, 2.0]}),
            pd.Series([1.0, 2.0]),
            (),
            False,
            optimization_config=TrainingOptimizationConfig(cv_folds=1),
            training_started_callback=lambda: acknowledgements.append("started"),
        )

    assert acknowledgements == []


def test_core_optimization_acknowledges_before_first_training_work(
    monkeypatch,
):
    import core.ml.training_results.optimization as optimization

    sequence = []

    def fail_at_first_training_work(*_args, **_kwargs):
        sequence.append("training-work")
        raise RuntimeError("stop after boundary proof")

    monkeypatch.setattr(optimization, "_optimize", fail_at_first_training_work)
    with pytest.raises(RuntimeError, match="boundary proof"):
        optimization.optimize_and_train(
            pd.DataFrame({"feature": [1.0, 2.0]}),
            pd.Series([1.0, 2.0]),
            (),
            False,
            optimization_config=TrainingOptimizationConfig(
                cv_folds=2,
                optuna_trials=1,
                n_estimators_min=1,
                n_estimators_max=1,
                n_jobs=1,
            ),
            training_started_callback=lambda: sequence.append("acknowledged"),
        )

    assert sequence == ["acknowledged", "training-work"]


def test_core_acknowledged_failure_consumes_iteration_once(
    tmp_path, monkeypatch
):
    import core.ml.training as core_training

    def fail_after_ack(*_args, **kwargs):
        kwargs["training_started_callback"]()
        raise RuntimeError("failure after Core acknowledgement")

    monkeypatch.setattr(
        core_training,
        "optimize_and_train",
        fail_after_ack,
    )
    service, _snapshot, repository = _service(
        tmp_path, lambda: _CoreOwnerExecution(core_training)
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "core-started"}}],
        },
    )

    record = CampaignApplicationService(service).start(
        specification, campaign_id="campaign-core-started"
    )

    assert record["status"] == "failed_resumable"
    assert record["budget"]["consumed_iterations"] == 1
    assert len(record["attempt_history"]) == 1
    assert record["attempt_history"][0]["training_started"] is True
    assert record["attempt_history"][0]["consumed_iteration"] is True
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None


def test_duplicate_training_start_acknowledgement_is_idempotent(tmp_path):
    class _DuplicateStartExecution(_DynamicArtifactExecution):
        def start(self, request, callbacks):  # noqa: ANN001
            callbacks.started(request)
            callbacks.started(request)
            snapshot = ModelRegistrySnapshot.from_payload(
                json.loads(request.registry_payload_json)
            )
            joblib.dump(artifact_for(snapshot), request.model_output_path)
            callbacks.finished(TrainingResult(
                request.run_id,
                "complete",
                model_path=request.model_output_path,
                message="finished",
            ))

    service, _snapshot, repository = _service(
        tmp_path, lambda: _DuplicateStartExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "duplicate-ack"}}],
        },
    )

    record = CampaignApplicationService(service).start(
        specification, campaign_id="campaign-duplicate-ack"
    )

    assert record["status"] == "completed"
    assert record["budget"]["consumed_iterations"] == 1
    assert len(record["attempt_history"]) == 1
    assert len(repository.list_candidates()) == 1


@pytest.mark.parametrize("failure_stage", ("adapter", "process"))
def test_campaign_spawn_failure_preserves_budget_and_resume_uses_next_attempt(
    tmp_path, failure_stage
):
    factories = {"count": 0}

    def execution_factory():
        factories["count"] += 1
        if factories["count"] == 1:
            if failure_stage == "adapter":
                raise RuntimeError("execution adapter initialization failed")
            return _StartFailureExecution()
        return _DynamicArtifactExecution()

    service, _snapshot, repository = _service(tmp_path, execution_factory)
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "spawn-recovery"}}],
        },
    )
    specification["retry"] = {
        "max_attempts": 2,
        "retryable_statuses": ["training_failure"],
    }
    campaigns = CampaignApplicationService(service)

    failed = campaigns.start(
        specification, campaign_id=f"campaign-spawn-{failure_stage}"
    )

    assert failed["status"] == "failed_resumable"
    assert failed["failure"]["code"] == "training_start_failed"
    assert failed["budget"]["consumed_iterations"] == 0
    assert failed["completed_runs"] == []
    assert failed["attempt_history"] == [{
        "iteration": 1,
        "attempt": 1,
        "run_id": f"campaign-spawn-{failure_stage}-iteration-1-attempt-1",
        "status": "training_failure",
        "training_started": False,
        "consumed_iteration": False,
    }]
    assert service.inspect_run(
        f"campaign-spawn-{failure_stage}-iteration-1-attempt-1"
    )["training_started"] is False
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None

    resumed = campaigns.resume(f"campaign-spawn-{failure_stage}")

    assert resumed["status"] == "completed"
    assert resumed["budget"]["consumed_iterations"] == 1
    assert [item["attempt"] for item in resumed["attempt_history"]] == [1, 2]
    assert resumed["attempt_history"][1]["training_started"]
    assert len(repository.list_candidates()) == 1


def test_campaign_prestart_failure_exhausts_one_total_attempt_without_mutation(
    tmp_path,
):
    factories = {"count": 0}

    def execution_factory():
        factories["count"] += 1
        return _StartFailureExecution()

    service, _snapshot, repository = _service(tmp_path, execution_factory)
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "one-attempt"}}],
        },
    )
    specification["retry"] = {
        "max_attempts": 1,
        "retryable_statuses": ["training_failure"],
    }
    campaigns = CampaignApplicationService(service)
    failed = campaigns.start(specification, campaign_id="campaign-one-attempt")
    record_path = (
        service.store.campaigns / "campaign-one-attempt" / "record.json"
    )
    before = record_path.read_bytes()

    exhausted = campaigns.resume("campaign-one-attempt")

    assert failed["status"] == "failed_resumable"
    assert exhausted["status"] == "retry_exhausted"
    assert exhausted["failure"]["code"] == "campaign_retry_exhausted"
    assert exhausted["failure"]["attempts_used"] == 1
    assert factories["count"] == 1
    assert len(exhausted["attempt_history"]) == 1
    assert exhausted["budget"]["consumed_iterations"] == 0
    assert record_path.read_bytes() == before
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None


def test_campaign_three_attempt_allowance_is_total_across_resumes(tmp_path):
    factories = {"count": 0}

    def execution_factory():
        factories["count"] += 1
        return _StartFailureExecution()

    service, _snapshot, repository = _service(tmp_path, execution_factory)
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "three-attempts"}}],
        },
    )
    specification["retry"] = {
        "max_attempts": 3,
        "retryable_statuses": ["training_failure"],
    }
    campaigns = CampaignApplicationService(service)

    campaigns.start(specification, campaign_id="campaign-three-attempts")
    campaigns.resume("campaign-three-attempts")
    third = campaigns.resume("campaign-three-attempts")
    record_path = (
        service.store.campaigns / "campaign-three-attempts" / "record.json"
    )
    before = record_path.read_bytes()
    exhausted = campaigns.resume("campaign-three-attempts")

    assert third["status"] == "failed_resumable"
    assert [item["attempt"] for item in third["attempt_history"]] == [1, 2, 3]
    assert all(not item["training_started"] for item in third["attempt_history"])
    assert third["budget"]["consumed_iterations"] == 0
    assert exhausted["status"] == "retry_exhausted"
    assert factories["count"] == 3
    assert record_path.read_bytes() == before
    assert repository.list_candidates() == ()


def test_campaign_status_reconciles_durable_run_start_after_record_update_gap(
    tmp_path,
):
    service, _snapshot, _repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 1,
            "experiments": [{"experiment": {"name": "start-reconciliation"}}],
        },
    )
    campaigns = CampaignApplicationService(service)
    completed = campaigns.start(
        specification, campaign_id="campaign-start-reconciliation"
    )
    run_id = completed["completed_runs"][0]["run_id"]
    simulated_gap = campaigns.status("campaign-start-reconciliation")
    simulated_gap["status"] = "running"
    simulated_gap["budget"]["consumed_iterations"] = 0
    simulated_gap["current"] = {
        "iteration": 1,
        "attempt": 1,
        "run_id": run_id,
        "training_started": False,
        "training_started_at": "",
    }
    service.store.update_campaign(
        "campaign-start-reconciliation", simulated_gap
    )

    projected = campaigns.status("campaign-start-reconciliation")
    persisted = service.store.read_campaign("campaign-start-reconciliation")

    assert projected["current"]["training_started"] is True
    assert projected["budget"]["consumed_iterations"] == 1
    assert persisted["current"]["training_started"] is False
    assert persisted["budget"]["consumed_iterations"] == 0


def test_resume_fails_closed_when_current_build_identity_changes(tmp_path):
    revision = {"value": "head-a"}
    holder = {}
    executions = {"count": 0}

    def execution_factory():
        executions["count"] += 1
        return _DynamicArtifactExecution(
            before_terminal=lambda: holder["service"].store.request_control(
                "campaign-build-change", "pause"
            )
        )

    service, _snapshot, _repository = _service(
        tmp_path,
        execution_factory,
        revision=revision["value"],
    )
    service._revision_provider = lambda: revision["value"]
    holder["service"] = service
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 2,
            "experiments": [
                {"experiment": {"name": "one"}},
                {"experiment": {"name": "two"}},
            ],
        },
    )
    campaigns = CampaignApplicationService(service)
    assert campaigns.start(
        specification, campaign_id="campaign-build-change"
    )["status"] == "paused"
    before = _persisted_record_bytes(service)
    revision["value"] = "head-b"

    blocked = campaigns.resume("campaign-build-change")

    assert blocked["status"] == "blocked"
    assert blocked["failure"]["code"] == "resume_contract_changed"
    assert "Create a new campaign" in blocked["failure"]["next_action"]
    assert _persisted_record_bytes(service) == before
    assert executions["count"] == 1


@pytest.mark.parametrize(
    "saved_revision", ("unavailable", "head-a", "head-missing")
)
def test_resume_unavailable_build_identity_is_blocked_without_record_mutation(
    tmp_path, saved_revision
):
    holder = {}
    service, _snapshot, _repository = _service(
        tmp_path,
        lambda: _DynamicArtifactExecution(
            before_terminal=lambda: holder["service"].store.request_control(
                "campaign-unavailable-build", "pause"
            )
        ),
        revision=saved_revision,
    )
    holder["service"] = service
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 2,
            "experiments": [
                {"experiment": {"name": "one"}},
                {"experiment": {"name": "two"}},
            ],
        },
    )
    campaigns = CampaignApplicationService(service)
    assert campaigns.start(
        specification, campaign_id="campaign-unavailable-build"
    )["status"] == "paused"
    record_path = (
        service.store.campaigns
        / "campaign-unavailable-build"
        / "record.json"
    )
    if saved_revision == "head-missing":
        record = campaigns.status("campaign-unavailable-build")
        for identity in record["contract_identity"]:
            identity.pop("build_revision")
        service.store.update_campaign("campaign-unavailable-build", record)
    elif saved_revision != "unavailable":
        def unavailable_revision():
            raise RuntimeError("revision lookup failed")

        service._revision_provider = unavailable_revision
    before = record_path.read_bytes()
    all_records_before = _persisted_record_bytes(service)

    blocked = campaigns.resume("campaign-unavailable-build")

    assert blocked["status"] == "blocked"
    assert blocked["failure"]["code"] == "resume_build_identity_unavailable"
    assert "Create a new campaign" in blocked["failure"]["next_action"]
    assert record_path.read_bytes() == before
    assert _persisted_record_bytes(service) == all_records_before


def test_resume_dirty_clean_build_mismatch_is_read_only(tmp_path):
    revision = {
        "value": {
            "status": "identified",
            "revision": "head-a",
            "dirty": False,
        }
    }
    holder = {}
    executions = {"count": 0}

    def execution_factory():
        executions["count"] += 1
        return _DynamicArtifactExecution(
            before_terminal=lambda: holder["service"].store.request_control(
                "campaign-dirty-change", "pause"
            )
        )

    service, _snapshot, _repository = _service(
        tmp_path, execution_factory, revision=revision["value"]
    )
    service._revision_provider = lambda: revision["value"]
    holder["service"] = service
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    specification = _spec(
        data,
        campaign={
            "max_iterations": 2,
            "experiments": [
                {"experiment": {"name": "one"}},
                {"experiment": {"name": "two"}},
            ],
        },
    )
    campaigns = CampaignApplicationService(service)
    assert campaigns.start(
        specification, campaign_id="campaign-dirty-change"
    )["status"] == "paused"
    before = _persisted_record_bytes(service)
    revision["value"] = {
        "status": "identified",
        "revision": "head-a+dirty.changed",
        "dirty": True,
    }

    blocked = campaigns.resume("campaign-dirty-change")

    assert blocked["status"] == "blocked"
    assert blocked["failure"]["code"] == "resume_contract_changed"
    assert _persisted_record_bytes(service) == before
    assert executions["count"] == 1


def _persisted_record_bytes(service):  # noqa: ANN001, ANN202
    root = service.store.root
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("record.json"))
    }
