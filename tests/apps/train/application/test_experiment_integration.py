"""Targeted Phase 5F application integration through Candidate publication."""

from __future__ import annotations

import json

import joblib

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
    assert record["contract_identity"]["build_revision"] == "test-head"
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


def test_resume_fails_closed_when_current_build_identity_changes(tmp_path):
    revision = {"value": "head-a"}
    holder = {}
    service, _snapshot, _repository = _service(
        tmp_path,
        lambda: _DynamicArtifactExecution(
            before_terminal=lambda: holder["service"].store.request_control(
                "campaign-build-change", "pause"
            )
        ),
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
    revision["value"] = "head-b"

    blocked = campaigns.resume("campaign-build-change")

    assert blocked["status"] == "blocked"
    assert blocked["failure"]["code"] == "resume_contract_changed"
