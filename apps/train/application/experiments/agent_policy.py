"""Phase 5G campaign policy defaults and validation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .contracts import ExperimentContractError
from .agent_contracts import (
    AGENT_CAMPAIGN_VERSION,
    BASELINE_MODES,
    CHANGE_CATEGORIES,
    METRIC_DIRECTIONS,
)


def default_policy() -> dict[str, Any]:
    return {
        "max_iterations": 5,
        "allowed_categories": sorted(CHANGE_CATEGORIES),
        "baseline": {
            "mode": "no_active",
            "active_candidate_id": None,
            "evidence_candidate_id": None,
        },
        "ranking": {
            "primary_metric": "rmse",
            "direction": "lower",
            "tolerance": 0.0,
            "guardrail_thresholds": [],
            "instability_thresholds": [],
        },
    }


def validate_campaign_definition(payload: Any) -> dict[str, Any]:
    _object(payload, "campaign definition")
    _keys(
        payload,
        {"schema_version", "base_specification"},
        {"policy"},
        "campaign definition",
    )
    if payload["schema_version"] != AGENT_CAMPAIGN_VERSION:
        _fail("unsupported_agent_campaign_version", "Unsupported agent campaign version.")
    _object(payload["base_specification"], "base_specification")
    policy = _merge(default_policy(), payload.get("policy", {}))
    _validate_policy(policy)
    return {
        "schema_version": AGENT_CAMPAIGN_VERSION,
        "base_specification": deepcopy(payload["base_specification"]),
        "policy": policy,
    }


def _validate_policy(policy: dict[str, Any]) -> None:
    _keys(
        policy,
        {"max_iterations", "allowed_categories", "baseline", "ranking"},
        set(),
        "campaign policy",
    )
    maximum = policy["max_iterations"]
    if type(maximum) is not int or not 1 <= maximum <= 100:
        _fail("campaign_budget_invalid", "max_iterations must be between 1 and 100.")
    allowed = policy["allowed_categories"]
    if (
        not isinstance(allowed, list)
        or any(item not in CHANGE_CATEGORIES for item in allowed)
        or len(allowed) != len(set(allowed))
    ):
        _fail("campaign_policy_invalid", "allowed_categories is invalid.")
    baseline = policy["baseline"]
    _keys(
        baseline,
        {"mode", "active_candidate_id", "evidence_candidate_id"},
        set(),
        "baseline policy",
    )
    if baseline["mode"] not in BASELINE_MODES:
        _fail("baseline_mode_invalid", "Campaign baseline mode is invalid.")
    for name in ("active_candidate_id", "evidence_candidate_id"):
        if baseline[name] is not None and (
            type(baseline[name]) is not str or not baseline[name]
        ):
            _fail("baseline_reference_invalid", f"{name} is invalid.")
    ranking = policy["ranking"]
    _keys(
        ranking,
        {
            "primary_metric",
            "direction",
            "tolerance",
            "guardrail_thresholds",
            "instability_thresholds",
        },
        set(),
        "ranking policy",
    )
    if (
        type(ranking["primary_metric"]) is not str
        or not ranking["primary_metric"]
        or ranking["direction"] not in METRIC_DIRECTIONS
        or type(ranking["tolerance"]) not in {int, float}
        or ranking["tolerance"] < 0
    ):
        _fail("ranking_policy_invalid", "Primary ranking policy is invalid.")
    _thresholds(ranking["guardrail_thresholds"], guardrail=True)
    _thresholds(ranking["instability_thresholds"], guardrail=False)


def _thresholds(values: Any, *, guardrail: bool) -> None:
    if not isinstance(values, list):
        _fail("ranking_policy_invalid", "Threshold policy must be an array.")
    required = (
        {"target", "metric", "direction", "max_degradation"}
        if guardrail else {"target", "metric", "max_std"}
    )
    for item in values:
        _object(item, "threshold")
        _keys(item, required, set(), "threshold")
        numeric = item["max_degradation" if guardrail else "max_std"]
        if (
            any(type(item[name]) is not str or not item[name] for name in ("target", "metric"))
            or type(numeric) not in {int, float}
            or numeric < 0
            or (guardrail and item["direction"] not in METRIC_DIRECTIONS)
        ):
            _fail("ranking_policy_invalid", "Threshold entry is invalid.")


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    _object(override, "policy")
    unknown = set(override).difference(base)
    if unknown:
        _fail("unsupported_policy_field", f"Unsupported field: {sorted(unknown)[0]}.")
    merged = deepcopy(base)
    for key, value in override.items():
        merged[key] = (
            _merge(merged[key], value)
            if isinstance(merged[key], dict) and isinstance(value, dict)
            else deepcopy(value)
        )
    return merged


def _object(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        _fail("contract_type_invalid", f"{name} must be an object.")


def _keys(payload, required, optional, name):  # noqa: ANN001, ANN202
    missing = required.difference(payload)
    unknown = set(payload).difference(required | optional)
    if missing or unknown:
        detail = sorted(missing or unknown)[0]
        _fail("contract_fields_invalid", f"{name} field set is invalid: {detail}.")


def _fail(code: str, message: str) -> None:
    raise ExperimentContractError(code, message)
