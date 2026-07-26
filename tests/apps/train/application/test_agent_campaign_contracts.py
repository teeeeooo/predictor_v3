from __future__ import annotations

from copy import deepcopy

import pytest

from apps.train.application.experiments.agent_contracts import (
    AGENT_CAMPAIGN_VERSION,
    PROPOSAL_VERSION,
    default_policy,
    validate_campaign_definition,
    validate_proposal,
)
from apps.train.application.experiments.candidate_gate import evaluate_candidate
from apps.train.application.experiments.contracts import ExperimentContractError
from apps.train.application.experiments.contracts import resolve_specification
from apps.train.application.experiments.resolution import resolve_registry
from apps.train.application.experiments.leaderboard import rebuild_leaderboard
from apps.train.application.experiments.recommendation import build_recommendation
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


def _definition(specification, *, policy=None):  # noqa: ANN001
    return {
        "schema_version": AGENT_CAMPAIGN_VERSION,
        "base_specification": specification,
        **({"policy": policy} if policy else {}),
    }


def _proposal(delta, *, baseline="bootstrap", category="parameter_search_space"):  # noqa: ANN001
    return {
        "schema_version": PROPOSAL_VERSION,
        "proposal_id": "proposal-1",
        "hypothesis": "A bounded change may improve the primary metric.",
        "primary_change_category": category,
        "baseline_reference": baseline,
        "delta": delta,
        "expected_effect": "Lower validation error.",
        "rationale": "Deterministic fixture rationale.",
    }


def _analysis(*, rmse=1.0, rmse_std=0.1, eligible=True):  # noqa: ANN001
    return {
        "run": {
            "status": "valid_completed",
            "duration_seconds": 2.0,
        },
        "training_context": {},
        "targets": [{
            "target_identity": "target-a",
            "status": "complete",
            "metrics": {"rmse": rmse, "rmse_std": rmse_std},
            "rfecv": {"feature_count_after": 3},
        }],
        "blocking_reasons": (
            [] if eligible else [{
                "code": "unpublished_experimental_features",
                "reason": "experimental",
            }]
        ),
    }


def _run_record(*, candidate_id="candidate-a", specification=None):  # noqa: ANN001
    return {
        "run_id": f"run-{candidate_id}",
        "status": "success",
        "resolved_specification": specification or {
            "targets": {
                "primary": ["target-a"],
                "guardrail": [],
                "production_required": ["target-a"],
            },
            "features": {
                "included": [],
                "excluded": [],
                "experimental_derived": [],
            },
        },
        "result": {
            "candidate_reference": candidate_id,
            "evidence_reference": f"candidates/{candidate_id}/training_result.json",
        },
    }


def _gate(candidate_id, rmse):  # noqa: ANN001
    return evaluate_candidate(
        _analysis(rmse=rmse),
        run_record=_run_record(candidate_id=candidate_id),
        policy=default_policy(),
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )


def test_agent_policy_defaults_to_total_five_and_proposal_cannot_change_budget():
    specification = {"schema_version": "predictor_v3.experiment.v1"}
    definition = validate_campaign_definition(_definition(specification))

    assert definition["policy"]["max_iterations"] == 5
    with pytest.raises(ExperimentContractError) as failure:
        validate_proposal(
            _proposal({"campaign": {"max_iterations": 50}}),
            policy=definition["policy"],
        )
    assert failure.value.code == "proposal_delta_forbidden"
    configured = validate_campaign_definition(
        _definition(specification, policy={"max_iterations": 10})
    )
    assert configured["policy"]["max_iterations"] == 10


def test_combined_proposal_is_explicit_and_marks_causal_attribution_unseparated():
    proposal = _proposal(
        {
            "optuna": {"trials": 2},
            "features": {"excluded": ["feature-a"]},
        },
        category="combined_experiment",
    )
    proposal["combined"] = True
    proposal["combined_categories"] = [
        "parameter_search_space",
        "existing_feature_policy",
    ]

    accepted = validate_proposal(proposal, policy=default_policy())

    assert accepted["combined"] is True
    assert accepted["causal_attribution_separable"] is False


def test_rfecv_proposal_uses_closed_declarative_group_override():
    proposal = _proposal(
        {"rfecv": {
            "group_overrides": [{"group": "cooling", "enabled": False}]
        }},
        category="rfecv",
    )

    accepted = validate_proposal(proposal, policy=default_policy())

    assert accepted["delta"]["rfecv"]["group_overrides"][0] == {
        "group": "cooling",
        "enabled": False,
    }
    snapshot = model_registry_snapshot(bootstrap_manifest())
    group = snapshot.groups[0]
    resolved = resolve_specification({
        "data": {"source_path": "fixture.csv"},
        "rfecv": {
            "group_overrides": [{
                "group": group.registry_key,
                "enabled": not group.use_rfe,
            }]
        },
    })
    adjusted = resolve_registry(snapshot, resolved.payload)
    assert adjusted.groups[0].use_rfe is (not group.use_rfe)


def test_gate_blocks_partial_experimental_and_threshold_violations_with_evidence():
    specification = _run_record()["resolved_specification"]
    specification = deepcopy(specification)
    specification["features"]["experimental_derived"] = [{"output": "x"}]
    policy = default_policy()
    policy["ranking"]["instability_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "max_std": 0.05,
    }]
    run = _run_record(specification=specification)

    gate = evaluate_candidate(
        _analysis(rmse_std=0.2, eligible=False),
        run_record=run,
        policy=policy,
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )

    codes = {item["code"] for item in gate["blocking_reasons"]}
    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False
    assert {
        "unpublished_experimental_feature",
        "excessive_instability",
    } <= codes
    assert all("evidence_reference" in item for item in gate["blocking_reasons"])


def test_configured_guardrail_and_instability_evidence_fail_closed_when_unresolved():
    policy = default_policy()
    policy["ranking"]["guardrail_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "direction": "lower",
        "max_degradation": 0.1,
    }]
    policy["ranking"]["instability_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "max_std": 0.1,
    }]
    analysis = _analysis()
    del analysis["targets"][0]["metrics"]["rmse_std"]

    gate = evaluate_candidate(
        analysis,
        run_record=_run_record(),
        policy=policy,
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )
    missing_metric = _analysis()
    del missing_metric["targets"][0]["metrics"]["rmse"]
    metric_gate = evaluate_candidate(
        missing_metric,
        run_record=_run_record(candidate_id="candidate-missing-metric"),
        policy=policy,
        baseline_analysis=_analysis(rmse=1.0),
        artifact_integrity={"valid": True},
    )

    codes = {item["code"] for item in gate["blocking_reasons"]}
    assert gate["guardrail_evidence"]["status"] == "unresolved"
    assert gate["stability_evidence"]["status"] == "unresolved"
    assert {
        "guardrail_evidence_unresolved",
        "instability_evidence_unresolved",
    } <= codes
    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False
    assert gate["exploratory_eligible"] is True
    assert "guardrail_evidence_unresolved" in {
        item["code"] for item in metric_gate["blocking_reasons"]
    }


def test_configured_gate_evidence_distinguishes_pass_violation_and_not_configured():
    policy = default_policy()
    policy["ranking"]["guardrail_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "direction": "lower",
        "max_degradation": 0.1,
    }]
    policy["ranking"]["instability_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "max_std": 0.1,
    }]
    baseline = _analysis(rmse=1.0)
    passed = evaluate_candidate(
        _analysis(rmse=0.95, rmse_std=0.05),
        run_record=_run_record(candidate_id="candidate-pass"),
        policy=policy,
        baseline_analysis=baseline,
        artifact_integrity={"valid": True},
    )
    violated = evaluate_candidate(
        _analysis(rmse=1.5, rmse_std=0.2),
        run_record=_run_record(candidate_id="candidate-violated"),
        policy=policy,
        baseline_analysis=baseline,
        artifact_integrity={"valid": True},
    )
    unconfigured = evaluate_candidate(
        _analysis(rmse=0.9),
        run_record=_run_record(candidate_id="candidate-unconfigured"),
        policy=default_policy(),
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )

    assert passed["gate_pass"] is True
    assert passed["guardrail_evidence"]["status"] == "passed"
    assert passed["stability_evidence"]["status"] == "passed"
    violation_codes = {
        item["code"] for item in violated["blocking_reasons"]
    }
    assert {"guardrail_violation", "excessive_instability"} <= violation_codes
    assert violated["guardrail_evidence"]["status"] == "violated"
    assert violated["stability_evidence"]["status"] == "violated"
    assert unconfigured["gate_pass"] is True
    assert unconfigured["guardrail_evidence"]["status"] == "not_configured"
    assert unconfigured["stability_evidence"]["status"] == "not_configured"


def test_unresolved_gate_evidence_is_excluded_from_incumbent_and_recommendation():
    policy = default_policy()
    policy["ranking"]["guardrail_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "direction": "lower",
        "max_degradation": 0.1,
    }]
    analysis = _analysis()
    gate = evaluate_candidate(
        analysis,
        run_record=_run_record(candidate_id="candidate-unresolved"),
        policy=policy,
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )
    baseline = {
        "mode": "no_active",
        "active_candidate_id": None,
        "comparable": False,
    }
    leaderboard = rebuild_leaderboard(
        [gate], policy=policy, baseline=baseline
    )
    campaign = {
        "campaign_id": "campaign-unresolved",
        "policy": policy,
        "baseline": baseline,
        "budget": {"remaining_iterations": 0},
        "leaderboard": leaderboard,
        "iterations": [],
    }

    artifact = build_recommendation(
        campaign,
        recommendation_id="recommendation-unresolved",
        created_at="2026-07-26T00:00:00+00:00",
    )

    assert leaderboard["incumbent_candidate_id"] is None
    assert leaderboard["entries"][0]["rank"] is None
    assert artifact["recommended_candidate"] is None
    assert artifact["runner_up"] is None
    assert artifact["rejected_candidates"][0]["reason_codes"] == [
        "guardrail_evidence_unresolved"
    ]
    assert (
        artifact["hard_gate_results"][0]["guardrail_evidence"]["status"]
        == "unresolved"
    )


def test_partial_target_scoped_evidence_is_exploratory_but_not_production_eligible():
    specification = deepcopy(_run_record()["resolved_specification"])
    specification["targets"]["primary"] = ["target-a"]
    specification["targets"]["production_required"] = ["target-a", "target-b"]
    run = _run_record(candidate_id=None, specification=specification)
    run["status"] = "partial"
    run["result"]["candidate_reference"] = None

    gate = evaluate_candidate(
        _analysis(),
        run_record=run,
        policy=default_policy(),
        baseline_analysis=None,
        artifact_integrity={
            "valid": False,
            "code": "incomplete_artifact",
            "reason": "partial evidence only",
            "evidence_reference": "run_evidence/run-partial/training_result.json",
        },
    )

    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False
    assert gate["exploratory_eligible"] is True
    assert "production_required_target_failure" in {
        item["code"] for item in gate["blocking_reasons"]
    }


@pytest.mark.parametrize(
    ("analysis_code", "gate_code"),
    [
        ("target_leakage", "target_leakage"),
        ("unreproducible_predict_feature", "predict_feature_unreproducible"),
        ("invalid_derived_feature_output", "invalid_derived_feature_output"),
        ("candidate_publication_failed", "incomplete_artifact"),
        ("unknown_compatibility_block", "lifecycle_compatibility_failure"),
    ],
)
def test_gate_maps_lifecycle_blockers_to_closed_reason_codes(
    analysis_code, gate_code
):
    analysis = _analysis()
    analysis["blocking_reasons"] = [{
        "code": analysis_code,
        "reason": "deterministic blocker",
    }]

    gate = evaluate_candidate(
        analysis,
        run_record=_run_record(),
        policy=default_policy(),
        baseline_analysis=None,
        artifact_integrity={"valid": True},
    )

    assert gate_code in {
        item["code"] for item in gate["blocking_reasons"]
    }
    assert gate["gate_pass"] is False


def test_leaderboard_and_incumbent_rebuild_deterministically_without_active_confusion():
    gates = [_gate("candidate-b", 0.8), _gate("candidate-a", 0.8)]
    baseline = {
        "mode": "no_active",
        "active_candidate_id": None,
        "comparable": False,
    }

    first = rebuild_leaderboard(gates, policy=default_policy(), baseline=baseline)
    second = rebuild_leaderboard(
        list(reversed(gates)), policy=default_policy(), baseline=baseline
    )

    assert first == second
    assert first["incumbent_candidate_id"] == "candidate-a"
    assert first["baseline"]["active_candidate_id"] is None
    assert first["entries"][0]["tie_break_basis"].startswith("candidate_id")

    failed = _gate("candidate-failed", 0.1)
    failed["gate_pass"] = False
    failed["production_eligible"] = False
    failed["blocking_reasons"] = [{
        "code": "target_leakage",
        "evidence_reference": "fixture",
        "message": "blocked",
    }]
    rebuilt = rebuild_leaderboard(
        [failed, *gates], policy=default_policy(), baseline=baseline
    )
    assert rebuilt["incumbent_candidate_id"] == "candidate-a"
    assert rebuilt["entries"][-1]["rank"] is None


def test_recommendation_supports_no_candidate_and_keeps_unbenchmarked_active():
    campaign = {
        "campaign_id": "campaign-1",
        "policy": default_policy(),
        "baseline": {
            "mode": "unbenchmarked_active",
            "active_candidate_id": "active-a",
            "comparable": False,
        },
        "budget": {"remaining_iterations": 0},
        "leaderboard": rebuild_leaderboard(
            [_gate("candidate-a", 0.8)],
            policy=default_policy(),
            baseline={"mode": "unbenchmarked_active"},
        ),
        "iterations": [],
    }

    artifact = build_recommendation(
        campaign,
        recommendation_id="recommendation-1",
        created_at="2026-07-26T00:00:00+00:00",
    )

    assert artifact["recommended_candidate"] is None
    assert artifact["conclusion"] == "keep_current_active"
    assert artifact["approval_required"] is True
    assert artifact["final_confirmation_required"] is True
    assert artifact["production_ready"] is False
    assert "unbenchmarked" in " ".join(
        artifact["uncertainty_and_limitations"]
    ).lower()
