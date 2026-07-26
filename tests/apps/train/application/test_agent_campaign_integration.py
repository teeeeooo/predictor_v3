from __future__ import annotations

import json

from apps.train.application.experiments.agent_campaign import (
    AgentCampaignApplicationService,
)
from apps.train.application.experiments.agent_contracts import (
    AGENT_CAMPAIGN_VERSION,
    PROPOSAL_VERSION,
)
from apps.train.composition.experiments import build_headless_experiment_service
from apps.train.interfaces.headless.cli import main
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tools.dev.mock_smoke.generators import write_mock_training_data
from tests.apps.train.application.test_experiment_integration import (
    _DynamicArtifactExecution,
    _StartFailureExecution,
    _service,
)


def _definition(data_path):  # noqa: ANN001
    targets = list(
        model_registry_snapshot(bootstrap_manifest()).target_presentation_order
    )
    return {
        "schema_version": AGENT_CAMPAIGN_VERSION,
        "base_specification": {
            "schema_version": "predictor_v3.experiment.v1",
            "experiment": {"name": "phase5g-integration", "purpose": "test"},
            "data": {"source_path": str(data_path)},
            "targets": {
                "primary": [targets[0]],
                "production_required": targets,
            },
            "optuna": {
                "cv_folds": 2,
                "trials": 2,
                "n_estimators_min": 2,
                "n_estimators_max": 2,
                "n_jobs": 1,
                "sampler_seed": 42,
            },
        },
    }


def _proposal(delta):  # noqa: ANN001
    return {
        "schema_version": PROPOSAL_VERSION,
        "proposal_id": "bounded-tuning",
        "hypothesis": "One bounded search adjustment may improve evidence.",
        "primary_change_category": "parameter_search_space",
        "baseline_reference": "bootstrap",
        "delta": delta,
        "expected_effect": "Different bounded search evidence.",
        "rationale": "Integration fixture.",
    }


def test_agent_campaign_persists_budget_rejection_iteration_and_operator_extension(
    tmp_path,
):
    lifecycle_root = tmp_path / "lifecycle"
    generation_root = tmp_path / "generations"
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    service = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        generation_root=generation_root,
        campaign_id="agent-loop",
        extra_training_args=("--dev-fast", "--dev-rows", "8"),
    )
    campaigns = AgentCampaignApplicationService(service)

    created = campaigns.create(_definition(data), campaign_id="agent-loop")
    rejected = campaigns.submit_proposal(
        "agent-loop", _proposal({"campaign": {"max_iterations": 99}})
    )
    ready = campaigns.submit_proposal(
        "agent-loop", _proposal({"optuna": {"trials": 1}})
    )
    executed = campaigns.execute("agent-loop", "bounded-tuning")

    assert created["budget"] == {
        "max_iterations": 5,
        "consumed_iterations": 0,
        "remaining_iterations": 5,
    }
    assert rejected["status"] == "proposal_rejected"
    assert rejected["budget"]["consumed_iterations"] == 0
    assert rejected["proposals"][-1]["reason_code"] == "proposal_delta_forbidden"
    assert ready["status"] == "ready_to_execute"
    assert executed["budget"]["consumed_iterations"] == 1
    assert executed["budget"]["remaining_iterations"] == 4
    assert executed["attempt_history"][0]["training_started"] is True
    proposal_reference = executed["proposals"][-1]["evidence_reference"]
    assert proposal_reference.endswith("/bounded-tuning/proposal.json")
    proposal_evidence = service.store.read_campaign_evidence(
        "agent-loop", "proposals", "bounded-tuning", "proposal.json"
    )
    run = service.inspect_run(executed["completed_runs"][0]["run_id"])
    assert proposal_evidence["recorded_at"] <= run["training_started_at"]

    restarted_service = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        generation_root=generation_root,
        campaign_id="agent-loop",
        extra_training_args=("--dev-fast", "--dev-rows", "8"),
    )
    restarted = AgentCampaignApplicationService(restarted_service)
    persisted = restarted.status("agent-loop")
    extended = restarted.extend_budget_operator(
        "agent-loop",
        new_total=7,
        operator_reference="operator-approved-test",
    )

    assert persisted["budget"]["consumed_iterations"] == 1
    assert persisted["budget"]["remaining_iterations"] == 4
    assert extended["budget"]["max_iterations"] == 7
    assert extended["budget"]["remaining_iterations"] == 6
    assert extended["budget_extensions"]
    extension_id = extended["budget_extensions"][0].split("/")[-2]
    extension = restarted_service.store.read_campaign_evidence(
        "agent-loop",
        "budget_extensions",
        extension_id,
        "extension.json",
    )
    assert extension["approval_required_before"] is True
    assert extension["approval_recorded"] is True
    assert extension["old_total_maximum"] == 5
    assert extension["new_total_maximum"] == 7


def test_prestart_failure_preserves_proposal_and_resume_reuses_attempt_scope(
    tmp_path,
):
    factories = {"count": 0}

    def execution_factory():
        factories["count"] += 1
        if factories["count"] == 1:
            return _StartFailureExecution()
        return _DynamicArtifactExecution()

    service, _snapshot, repository = _service(tmp_path, execution_factory)
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    definition = _definition(data)
    definition["base_specification"]["targets"]["primary"] = list(
        definition["base_specification"]["targets"]["production_required"]
    )
    definition["base_specification"]["retry"] = {
        "max_attempts": 2,
        "retryable_statuses": ["training_failure"],
    }
    campaigns = AgentCampaignApplicationService(service)
    campaigns.create(definition, campaign_id="resumable-agent-loop")
    accepted = campaigns.submit_proposal(
        "resumable-agent-loop", _proposal({"optuna": {"trials": 1}})
    )
    execution_key = accepted["pending_execution"]["execution_key"]

    failed = campaigns.execute("resumable-agent-loop", "bounded-tuning")

    assert failed["status"] == "failed_resumable"
    assert failed["current_proposal_id"] == "bounded-tuning"
    assert failed["pending_execution"] == {
        "proposal_id": "bounded-tuning",
        "execution_key": execution_key,
        "iteration": 1,
        "evidence_reference": accepted["pending_execution"]["evidence_reference"],
        "max_attempts": 2,
        "attempts_used": 1,
        "remaining_attempts": 1,
    }
    assert failed["budget"]["consumed_iterations"] == 0
    assert failed["attempt_history"][0]["proposal_id"] == "bounded-tuning"
    assert failed["attempt_history"][0]["attempt_scope"] == execution_key
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None

    restarted_service, _snapshot, restarted_repository = _service(
        tmp_path, execution_factory
    )
    restarted = AgentCampaignApplicationService(restarted_service)
    resumed = restarted.resume("resumable-agent-loop")

    assert resumed["budget"]["consumed_iterations"] == 1
    assert [item["attempt"] for item in resumed["attempt_history"]] == [1, 2]
    assert {
        item["attempt_scope"] for item in resumed["attempt_history"]
    } == {execution_key}
    assert all(
        item["proposal_id"] == "bounded-tuning"
        for item in resumed["attempt_history"]
    )
    assert resumed["current_proposal_id"] is None
    assert resumed["pending_execution"] is None
    assert len(restarted_repository.list_candidates()) == 1
    assert restarted_repository.read_active(optional=True) is None


def test_proposal_identity_cannot_reset_exhausted_attempt_allowance(tmp_path):
    factories = {"count": 0}

    def execution_factory():
        factories["count"] += 1
        return _StartFailureExecution()

    service, _snapshot, repository = _service(tmp_path, execution_factory)
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    definition = _definition(data)
    definition["base_specification"]["retry"] = {
        "max_attempts": 1,
        "retryable_statuses": ["training_failure"],
    }
    campaigns = AgentCampaignApplicationService(service)
    campaigns.create(definition, campaign_id="exhausted-agent-proposal")
    campaigns.submit_proposal(
        "exhausted-agent-proposal", _proposal({"optuna": {"trials": 1}})
    )
    failed = campaigns.execute(
        "exhausted-agent-proposal", "bounded-tuning"
    )
    record_path = (
        service.store.campaigns / "exhausted-agent-proposal" / "record.json"
    )
    before = record_path.read_bytes()
    duplicate = _proposal({"optuna": {"trials": 1}})
    duplicate.update({
        "proposal_id": "renamed-proposal",
        "hypothesis": "Different display text for the same resolved change.",
        "expected_effect": "Different display text.",
        "rationale": "Different display metadata.",
    })

    rejected = campaigns.submit_proposal(
        "exhausted-agent-proposal", duplicate
    )
    replacement = _proposal({"optuna": {"trials": 3}})
    replacement["proposal_id"] = "materially-different"
    replacement_rejected = campaigns.submit_proposal(
        "exhausted-agent-proposal", replacement
    )

    assert failed["pending_execution"]["remaining_attempts"] == 0
    assert rejected["status"] == "proposal_rejected"
    assert rejected["failure"]["code"] == "proposal_retry_exhausted"
    assert rejected["failure"]["pending_proposal_id"] == "bounded-tuning"
    assert replacement_rejected["failure"]["code"] == "proposal_replacement_blocked"
    assert factories["count"] == 1
    assert len(failed["attempt_history"]) == 1
    assert record_path.read_bytes() == before
    assert repository.list_candidates() == ()
    assert repository.read_active(optional=True) is None


def test_materially_different_proposal_gets_new_scope_after_terminal_iteration(
    tmp_path,
):
    service, _snapshot, _repository = _service(
        tmp_path, lambda: _DynamicArtifactExecution()
    )
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    campaigns = AgentCampaignApplicationService(service)
    definition = _definition(data)
    definition["base_specification"]["targets"]["primary"] = list(
        definition["base_specification"]["targets"]["production_required"]
    )
    campaigns.create(definition, campaign_id="terminal-agent-proposal")
    first = campaigns.submit_proposal(
        "terminal-agent-proposal", _proposal({"optuna": {"trials": 1}})
    )
    first_key = first["pending_execution"]["execution_key"]
    completed = campaigns.execute(
        "terminal-agent-proposal", "bounded-tuning"
    )
    next_proposal = _proposal({"optuna": {"trials": 3}})
    next_proposal["proposal_id"] = "materially-different"

    accepted = campaigns.submit_proposal(
        "terminal-agent-proposal", next_proposal
    )

    assert completed["current_proposal_id"] is None
    assert accepted["status"] == "ready_to_execute"
    assert accepted["pending_execution"]["execution_key"] != first_key


def test_budget_exhaustion_blocks_new_proposal_and_training(tmp_path):
    lifecycle_root = tmp_path / "lifecycle"
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    definition = _definition(data)
    definition["policy"] = {"max_iterations": 1}
    service = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        generation_root=tmp_path / "generations",
        campaign_id="exhausted-loop",
        extra_training_args=("--dev-fast", "--dev-rows", "8"),
    )
    campaigns = AgentCampaignApplicationService(service)
    campaigns.create(definition, campaign_id="exhausted-loop")
    campaigns.submit_proposal(
        "exhausted-loop", _proposal({"optuna": {"trials": 1}})
    )
    exhausted = campaigns.execute("exhausted-loop", "bounded-tuning")
    before_runs = len(tuple(service.store.runs.iterdir()))

    blocked = campaigns.submit_proposal(
        "exhausted-loop",
        {
            **_proposal({"optuna": {"trials": 2}}),
            "proposal_id": "must-not-run",
        },
    )

    assert exhausted["status"] == "budget_exhausted"
    assert exhausted["recommendation_status"] == "recommendation_ready"
    assert len(exhausted["recommendations"]) == 1
    assert blocked["status"] == "budget_exhausted"
    assert blocked["failure"]["code"] == "campaign_budget_exhausted"
    assert blocked["budget"]["consumed_iterations"] == 1
    assert len(tuple(service.store.runs.iterdir())) == before_runs


def test_campaign_can_complete_without_recommendation(tmp_path):
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    service = build_headless_experiment_service(
        lifecycle_root=tmp_path / "lifecycle",
        generation_root=tmp_path / "generations",
        campaign_id="completed-loop",
    )
    campaigns = AgentCampaignApplicationService(service)
    campaigns.create(_definition(data), campaign_id="completed-loop")

    completed = campaigns.complete_without_recommendation("completed-loop")

    assert completed["status"] == "completed_without_recommendation"
    assert completed["recommendations"] == []
    assert completed["approval_required"] is True


def test_recommendation_history_is_immutable_and_has_no_production_authority(
    tmp_path,
):
    lifecycle_root = tmp_path / "lifecycle"
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    service = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        generation_root=tmp_path / "generations",
        campaign_id="recommendation-loop",
    )
    campaigns = AgentCampaignApplicationService(service)
    campaigns.create(_definition(data), campaign_id="recommendation-loop")

    first = campaigns.recommend(
        "recommendation-loop", recommendation_id="recommendation-1"
    )
    second = campaigns.recommend(
        "recommendation-loop", recommendation_id="recommendation-2"
    )

    assert first["recommended_candidate"] is None
    assert first["approval_required"] is True
    assert second["recommendation_id"] == "recommendation-2"
    assert not (lifecycle_root / "active.json").exists()
    assert not (lifecycle_root / "deployment_exports").exists()
    record = campaigns.status("recommendation-loop")
    assert len(record["recommendations"]) == 2


def test_headless_agent_commands_share_campaign_store_without_file_guessing(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    data = write_mock_training_data(output_dir=tmp_path / "data", rows=8)
    definition_path = tmp_path / "definition.json"
    proposal_path = tmp_path / "proposal.json"
    definition_path.write_text(json.dumps(_definition(data)), encoding="utf-8")
    proposal_path.write_text(
        json.dumps(_proposal({"optuna": {"trials": 1}})),
        encoding="utf-8",
    )

    assert main([
        "campaign-create",
        str(definition_path),
        "--campaign-id",
        "cli-agent-loop",
    ]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["data"]["budget"]["remaining_iterations"] == 5

    assert main([
        "campaign-proposal-submit",
        "cli-agent-loop",
        str(proposal_path),
    ]) == 0
    submitted = json.loads(capsys.readouterr().out)
    assert submitted["outcome"] == "ready_to_execute"

    assert main(["campaign-budget", "cli-agent-loop"]) == 0
    budget = json.loads(capsys.readouterr().out)
    assert budget["data"]["policy"]["max_iterations"] == 5
    assert budget["data"]["budget"]["remaining_iterations"] == 5

    assert main(["campaign-incumbent", "cli-agent-loop"]) == 0
    incumbent = json.loads(capsys.readouterr().out)
    assert incumbent["data"]["incumbent_candidate_id"] is None
    assert incumbent["data"]["active_candidate_id"] is None
