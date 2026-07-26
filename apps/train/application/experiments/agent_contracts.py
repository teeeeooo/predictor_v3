"""Closed Phase 5G campaign, proposal, and policy contracts."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .contracts import ExperimentContractError

AGENT_CAMPAIGN_VERSION = "predictor_v3.agent_campaign.v1"
PROPOSAL_VERSION = "predictor_v3.experiment_proposal.v1"
GATE_VERSION = "predictor_v3.candidate_gate.v1"
LEADERBOARD_VERSION = "predictor_v3.campaign_leaderboard.v1"
RECOMMENDATION_VERSION = "predictor_v3.campaign_recommendation.v1"
BUDGET_EXTENSION_VERSION = "predictor_v3.campaign_budget_extension.v1"

CHANGE_CATEGORIES = {
    "parameter_search_space",
    "rfecv",
    "preprocessing",
    "existing_feature_policy",
    "experimental_derived_feature",
    "target_scoped_exploration",
}
_CATEGORY_PATHS = {
    "parameter_search_space": {"optuna"},
    "rfecv": {"rfecv"},
    "preprocessing": {"preprocessing"},
    "existing_feature_policy": {"features.included", "features.excluded"},
    "experimental_derived_feature": {"features.experimental_derived"},
    "target_scoped_exploration": {
        "targets.primary",
        "targets.guardrail",
    },
}
BASELINE_MODES = {"comparable_active", "unbenchmarked_active", "no_active"}
METRIC_DIRECTIONS = {"higher", "lower"}
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def validate_proposal(payload: Any, *, policy: dict[str, Any]) -> dict[str, Any]:
    _require_object(payload, "proposal")
    required = {
        "schema_version",
        "proposal_id",
        "hypothesis",
        "primary_change_category",
        "baseline_reference",
        "delta",
        "expected_effect",
        "rationale",
    }
    _require_exact_keys(
        payload,
        required,
        {"combined", "combined_categories"},
        "proposal",
    )
    if payload["schema_version"] != PROPOSAL_VERSION:
        _fail("unsupported_proposal_version", "Unsupported proposal version.")
    for name in (
        "proposal_id",
        "hypothesis",
        "baseline_reference",
        "expected_effect",
        "rationale",
    ):
        if type(payload[name]) is not str or not payload[name].strip():
            _fail("proposal_field_invalid", f"{name} must be a non-empty string.")
    if _SAFE_ID.fullmatch(payload["proposal_id"]) is None:
        _fail("proposal_identity_invalid", "proposal_id is not a safe identity.")
    category = payload["primary_change_category"]
    combined = payload.get("combined", False)
    categories = payload.get("combined_categories", [])
    if type(combined) is not bool or not isinstance(categories, list):
        _fail("proposal_combination_invalid", "Combined proposal fields are invalid.")
    if combined:
        if category != "combined_experiment":
            _fail("proposal_combination_invalid", "Combined proposals must be explicit.")
        if (
            len(categories) < 2
            or any(item not in CHANGE_CATEGORIES for item in categories)
            or len(categories) != len(set(categories))
        ):
            _fail(
                "proposal_combination_invalid",
                "Combined proposals require at least two distinct known categories.",
            )
    elif category not in CHANGE_CATEGORIES or categories:
        _fail(
            "proposal_category_invalid",
            "A non-combined proposal requires one known primary category.",
        )
    effective = set(categories if combined else [category])
    allowed = set(policy["allowed_categories"])
    if not effective <= allowed:
        _fail("proposal_category_forbidden", "Campaign policy forbids this category.")
    _require_object(payload["delta"], "proposal delta")
    changed_paths = set(_leaf_paths(payload["delta"]))
    permitted = set().union(*(_CATEGORY_PATHS[item] for item in effective))
    if not changed_paths or any(
        not any(path == root or path.startswith(f"{root}.") for root in permitted)
        for path in changed_paths
    ):
        _fail(
            "proposal_delta_forbidden",
            "Proposal delta contains no change or crosses its declared category boundary.",
        )
    return {
        **deepcopy(payload),
        "combined": combined,
        "combined_categories": list(categories),
        "causal_attribution_separable": not combined,
    }


def apply_delta(before: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    return _merge(before, delta)


def changed_leaf_paths(delta: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(_leaf_paths(delta)))


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    _require_object(override, "policy or delta")
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


def _leaf_paths(payload: dict[str, Any], prefix: str = "") -> tuple[str, ...]:
    paths = []
    for key, value in payload.items():
        path = f"{prefix}.{key}".strip(".")
        if isinstance(value, dict) and value:
            paths.extend(_leaf_paths(value, path))
        else:
            paths.append(path)
    return tuple(paths)


def _require_object(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        _fail("contract_type_invalid", f"{name} must be an object.")


def _require_exact_keys(
    payload: dict[str, Any],
    required: set[str],
    optional: set[str],
    name: str,
) -> None:
    missing = required.difference(payload)
    unknown = set(payload).difference(required | optional)
    if missing or unknown:
        detail = sorted(missing or unknown)[0]
        _fail("contract_fields_invalid", f"{name} field set is invalid: {detail}.")


def _fail(code: str, message: str) -> None:
    raise ExperimentContractError(code, message)


from .agent_policy import default_policy, validate_campaign_definition  # noqa: E402
