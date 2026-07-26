from __future__ import annotations

import json
import math

import pytest

from apps.train.application.experiments.agent_contracts import (
    AGENT_CAMPAIGN_VERSION,
    default_policy,
    validate_campaign_definition,
)
from apps.train.application.experiments.candidate_gate import evaluate_candidate
from apps.train.application.experiments.contracts import ExperimentContractError
from apps.train.application.experiments.leaderboard import rebuild_leaderboard
from apps.train.application.experiments.recommendation import build_recommendation
from apps.train.interfaces.headless.command_contract import emit

NON_FINITE = (float("nan"), float("inf"), float("-inf"))


def _analysis(*, rmse=1.0, rmse_std=0.1, target="target-a"):  # noqa: ANN001
    return {
        "run": {"status": "valid_completed", "duration_seconds": 2.0},
        "training_context": {},
        "targets": [{
            "target_identity": target,
            "status": "complete",
            "metrics": {"rmse": rmse, "rmse_std": rmse_std},
            "rfecv": {"feature_count_after": 3},
        }],
        "blocking_reasons": [],
    }


def _run_record(candidate_id="candidate-a", *, targets=None):  # noqa: ANN001
    identities = targets or ["target-a"]
    return {
        "run_id": f"run-{candidate_id}",
        "status": "success",
        "resolved_specification": {
            "targets": {
                "primary": identities,
                "guardrail": [],
                "production_required": identities,
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


def _gate(
    analysis,
    *,
    candidate_id="candidate-a",
    policy=None,
    baseline=None,
    targets=None,
):  # noqa: ANN001
    return evaluate_candidate(
        analysis,
        run_record=_run_record(candidate_id, targets=targets),
        policy=policy or default_policy(),
        baseline_analysis=baseline,
        artifact_integrity={"valid": True},
    )


def _guardrail_policy():
    policy = default_policy()
    policy["ranking"]["guardrail_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "direction": "lower",
        "max_degradation": 0.1,
    }]
    return policy


def _instability_policy():
    policy = default_policy()
    policy["ranking"]["instability_thresholds"] = [{
        "target": "target-a",
        "metric": "rmse",
        "max_std": 0.1,
    }]
    return policy


def _combined_policy():
    policy = _guardrail_policy()
    policy["ranking"]["instability_thresholds"] = (
        _instability_policy()["ranking"]["instability_thresholds"]
    )
    return policy


def _assert_strict_json(value):  # noqa: ANN001
    encoded = json.dumps(value, allow_nan=False, sort_keys=True)
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


@pytest.mark.parametrize("value", NON_FINITE)
def test_non_finite_current_primary_is_unavailable_and_excluded(value):
    gate = _gate(_analysis(rmse=value), candidate_id="candidate-invalid")
    codes = {item["code"] for item in gate["blocking_reasons"]}

    assert gate["primary_target_evidence"]["status"] == "unavailable"
    assert gate["primary_target_evidence"]["value"] is None
    assert gate["primary_target_evidence"]["current_evidence"][0]["status"] == (
        "non_finite"
    )
    assert gate["target_metrics"]["target-a"]["rmse"] is None
    assert "primary_metric_unavailable" in codes
    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False

    baseline = {
        "mode": "unbenchmarked_active",
        "active_candidate_id": "active-a",
        "comparable": False,
    }
    leaderboard = rebuild_leaderboard(
        [gate], policy=default_policy(), baseline=baseline
    )
    campaign = {
        "campaign_id": "campaign-non-finite",
        "policy": default_policy(),
        "baseline": baseline,
        "budget": {"remaining_iterations": 0},
        "leaderboard": leaderboard,
        "iterations": [],
    }
    recommendation = build_recommendation(
        campaign,
        recommendation_id="recommendation-non-finite",
        created_at="2026-07-26T00:00:00+00:00",
    )

    assert len(leaderboard["entries"]) == 1
    assert leaderboard["incumbent_candidate_id"] is None
    assert recommendation["recommended_candidate"] is None
    assert recommendation["runner_up"] is None
    assert recommendation["current_active_or_campaign_baseline"][
        "active_candidate_id"
    ] == "active-a"
    assert recommendation["rejected_candidates"][0]["candidate_id"] == (
        "candidate-invalid"
    )
    assert any(
        "unavailable selection metric evidence" in item
        for item in recommendation["uncertainty_and_limitations"]
    )
    for projected in (gate, leaderboard, recommendation):
        _assert_strict_json(projected)


@pytest.mark.parametrize("value", NON_FINITE)
def test_non_finite_baseline_primary_preserves_current_without_improvement(value):
    gate = _gate(
        _analysis(rmse=0.8),
        baseline=_analysis(rmse=value),
    )
    primary = gate["primary_target_evidence"]

    assert primary["status"] == "available"
    assert primary["value"] == 0.8
    assert primary["baseline_value"] is None
    assert primary["delta"] is None
    assert primary["comparable"] is False
    assert primary["baseline_evidence"][0]["status"] == "non_finite"
    assert gate["gate_pass"] is True
    baseline = {
        "mode": "comparable_active",
        "active_candidate_id": "active-a",
        "comparable": True,
    }
    leaderboard = rebuild_leaderboard(
        [gate], policy=default_policy(), baseline=baseline
    )
    recommendation = build_recommendation(
        {
            "campaign_id": "campaign-baseline-non-finite",
            "policy": default_policy(),
            "baseline": baseline,
            "budget": {"remaining_iterations": 0},
            "leaderboard": leaderboard,
            "iterations": [],
        },
        recommendation_id="recommendation-baseline-non-finite",
        created_at="2026-07-26T00:00:00+00:00",
    )
    assert recommendation["recommended_candidate"] is None
    assert recommendation["conclusion"] == "keep_current_active"
    _assert_strict_json(gate)
    _assert_strict_json(recommendation)


@pytest.mark.parametrize("source", ("candidate", "baseline"))
@pytest.mark.parametrize("value", NON_FINITE)
def test_non_finite_configured_guardrail_is_unresolved_with_context(source, value):
    current = _analysis(rmse=value if source == "candidate" else 0.9)
    baseline = _analysis(rmse=value if source == "baseline" else 1.0)
    gate = _gate(current, policy=_guardrail_policy(), baseline=baseline)
    entry = gate["guardrail_evidence"]["entries"][0]
    blocker = next(
        item for item in gate["blocking_reasons"]
        if item["code"] == "guardrail_evidence_unresolved"
    )

    assert entry["status"] == "unresolved"
    assert entry["value" if source == "candidate" else "baseline_value"] is None
    assert {
        "source": source,
        "target": "target-a",
        "metric": "rmse",
        "reason": "non_finite",
    } in blocker["context"]
    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False
    _assert_strict_json(gate)


@pytest.mark.parametrize("value", NON_FINITE)
def test_non_finite_configured_instability_is_unresolved_with_context(value):
    gate = _gate(
        _analysis(rmse_std=value),
        policy=_instability_policy(),
    )
    entry = gate["stability_evidence"]["entries"][0]
    blocker = next(
        item for item in gate["blocking_reasons"]
        if item["code"] == "instability_evidence_unresolved"
    )

    assert entry["status"] == "unresolved"
    assert entry["value"] is None
    assert entry["value_status"] == "non_finite"
    assert blocker["context"] == [{
        "source": "candidate",
        "target": "target-a",
        "metric": "rmse_std",
        "reason": "non_finite",
    }]
    assert gate["stability_evidence"]["aggregate_std"] is None
    assert gate["gate_pass"] is False
    assert gate["production_eligible"] is False
    _assert_strict_json(gate)


def test_mixed_non_finite_primary_and_stability_aggregates_do_not_hide_evidence():
    analysis = _analysis(rmse=0.8, rmse_std=0.05)
    analysis["targets"].append(
        _analysis(
            target="target-b", rmse=float("nan"), rmse_std=float("inf")
        )["targets"][0]
    )
    policy = default_policy()
    policy["ranking"]["instability_thresholds"] = [
        {"target": "target-a", "metric": "rmse", "max_std": 0.1},
        {"target": "target-b", "metric": "rmse", "max_std": 0.1},
    ]
    gate = _gate(
        analysis,
        policy=policy,
        targets=["target-a", "target-b"],
    )

    assert gate["primary_target_evidence"]["value"] is None
    assert gate["stability_evidence"]["status"] == "unresolved"
    assert gate["stability_evidence"]["aggregate_std"] == 0.05
    assert {
        item["code"] for item in gate["blocking_reasons"]
    } >= {
        "primary_metric_unavailable",
        "instability_evidence_unresolved",
    }
    assert gate["gate_pass"] is False
    _assert_strict_json(gate)


def test_unconfigured_non_finite_stability_does_not_invent_blocker():
    gate = _gate(_analysis(rmse=0.8, rmse_std=float("nan")))

    assert gate["stability_evidence"]["status"] == "not_configured"
    assert "instability_evidence_unresolved" not in {
        item["code"] for item in gate["blocking_reasons"]
    }
    assert gate["gate_pass"] is True
    _assert_strict_json(gate)


def test_headless_selection_projection_emits_standard_json(capsys):
    gate = _gate(
        _analysis(rmse=float("nan"), rmse_std=float("inf")),
        policy=_instability_policy(),
    )
    leaderboard = rebuild_leaderboard(
        [gate],
        policy=_instability_policy(),
        baseline={
            "mode": "no_active",
            "active_candidate_id": None,
            "comparable": False,
        },
    )

    emit(
        "campaign-leaderboard",
        "no_valid_candidate",
        "Campaign leaderboard loaded.",
        data=leaderboard,
    )

    output = capsys.readouterr().out
    assert "NaN" not in output
    assert "Infinity" not in output
    parsed = json.loads(output)
    _assert_strict_json(parsed)


def test_non_finite_gate_candidates_do_not_replace_valid_incumbent_or_runner_up():
    policy = _combined_policy()
    baseline_analysis = _analysis(rmse=1.0)
    valid = _gate(
        _analysis(rmse=0.9, rmse_std=0.05),
        candidate_id="candidate-valid",
        policy=policy,
        baseline=baseline_analysis,
    )
    invalid_guardrail = _gate(
        _analysis(rmse=float("nan"), rmse_std=0.05),
        candidate_id="candidate-invalid-guardrail",
        policy=policy,
        baseline=baseline_analysis,
    )
    invalid_stability = _gate(
        _analysis(rmse=0.8, rmse_std=float("inf")),
        candidate_id="candidate-invalid-stability",
        policy=policy,
        baseline=baseline_analysis,
    )
    baseline = {
        "mode": "no_active",
        "active_candidate_id": None,
        "comparable": False,
    }
    leaderboard = rebuild_leaderboard(
        [invalid_guardrail, valid, invalid_stability],
        policy=policy,
        baseline=baseline,
    )
    recommendation = build_recommendation(
        {
            "campaign_id": "campaign-valid-incumbent",
            "policy": policy,
            "baseline": baseline,
            "budget": {"remaining_iterations": 0},
            "leaderboard": leaderboard,
            "iterations": [],
        },
        recommendation_id="recommendation-valid-incumbent",
        created_at="2026-07-26T00:00:00+00:00",
    )

    assert leaderboard["incumbent_candidate_id"] == "candidate-valid"
    assert recommendation["recommended_candidate"]["candidate_id"] == (
        "candidate-valid"
    )
    assert recommendation["runner_up"] is None
    assert {
        item["candidate_id"] for item in recommendation["rejected_candidates"]
    } == {"candidate-invalid-guardrail", "candidate-invalid-stability"}
    _assert_strict_json(leaderboard)
    _assert_strict_json(recommendation)


@pytest.mark.parametrize("value", NON_FINITE)
@pytest.mark.parametrize(
    "policy_path",
    ("tolerance", "guardrail", "instability"),
)
def test_non_finite_policy_numeric_inputs_are_rejected(value, policy_path):
    policy = default_policy()
    if policy_path == "tolerance":
        policy["ranking"]["tolerance"] = value
    elif policy_path == "guardrail":
        policy["ranking"]["guardrail_thresholds"] = [{
            "target": "target-a",
            "metric": "rmse",
            "direction": "lower",
            "max_degradation": value,
        }]
    else:
        policy["ranking"]["instability_thresholds"] = [{
            "target": "target-a",
            "metric": "rmse",
            "max_std": value,
        }]

    with pytest.raises(ExperimentContractError) as failure:
        validate_campaign_definition({
            "schema_version": AGENT_CAMPAIGN_VERSION,
            "base_specification": {
                "schema_version": "predictor_v3.experiment.v1"
            },
            "policy": policy,
        })

    assert failure.value.code == "ranking_policy_invalid"


def test_finite_gate_still_passes_and_violation_still_blocks():
    passed = _gate(
        _analysis(rmse=0.9, rmse_std=0.05),
        policy=_combined_policy(),
        baseline=_analysis(rmse=1.0),
    )
    violated = _gate(
        _analysis(rmse=1.5, rmse_std=0.2),
        policy=_combined_policy(),
        baseline=_analysis(rmse=1.0),
    )

    assert passed["gate_pass"] is True
    assert {
        item["code"] for item in violated["blocking_reasons"]
    } >= {"guardrail_violation", "excessive_instability"}
    assert violated["gate_pass"] is False
    assert math.isfinite(passed["primary_target_evidence"]["value"])
