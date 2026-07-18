"""Pure operand eligibility policy for restricted Derived evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DerivedOperandEligibility:
    """Explain whether one stable identity can feed the Derived evaluator."""

    eligible: bool
    identity: str
    ml_name: str
    owner_kind: str
    source_kind: str
    code: str = ""
    reason: str = ""


_RUNTIME_FEATURE_ROLES = frozenset({"input", "auto", "one_hot_feature"})


def derived_operand_eligibility(
    features: Iterable[object],
    derived: Iterable[object],
    identity: str,
    *,
    target_feature_identities: Iterable[str] = (),
    consumer_identity: str = "",
    consumer_active: bool = False,
) -> DerivedOperandEligibility:
    """Resolve one operand and apply the canonical evaluator-input policy."""
    feature_matches = tuple(item for item in features if _identity(item) == identity)
    derived_matches = tuple(item for item in derived if _identity(item) == identity)
    matches = (*feature_matches, *derived_matches)
    if len(matches) != 1:
        reason = "missing" if not matches else "ambiguous"
        return _blocked(
            identity,
            "",
            "unknown",
            "unknown",
            "derived_dependency_missing" if not matches else "derived_operand_ambiguous",
            f"Derived operand identity is {reason}: {identity}",
        )
    owner = matches[0]
    if identity == consumer_identity:
        return _blocked(
            identity,
            _text(owner, "ml_name"),
            "derived",
            "derived_policy",
            "derived_self_reference",
            "A Derived definition cannot use itself as an operand.",
        )
    if derived_matches:
        ml_name = _text(owner, "ml_name")
        if not ml_name:
            return _blocked(
                identity,
                ml_name,
                "derived",
                "derived_policy",
                "derived_operand_type_invalid",
                "Derived operand has no ML name.",
            )
        if consumer_active and not bool(getattr(owner, "active", False)):
            return _blocked(
                identity,
                ml_name,
                "derived",
                "derived_policy",
                "derived_active_dependency_unavailable",
                f"Active Derived evaluation cannot use inactive Derived '{ml_name}'.",
            )
        return DerivedOperandEligibility(
            True, identity, ml_name, "derived", "derived_policy"
        )
    return _feature_eligibility(
        owner,
        target_feature_identities=frozenset(target_feature_identities),
    )


def _feature_eligibility(
    feature: object,
    *,
    target_feature_identities: frozenset[str],
) -> DerivedOperandEligibility:
    identity = _identity(feature)
    ml_name = _text(feature, "ml_name")
    role = _text(feature, "role")
    value_source = _text(feature, "value_source")
    source_kind = value_source or "feature"
    if identity in target_feature_identities or role == "result":
        return _blocked(
            identity,
            ml_name,
            "feature",
            source_kind,
            "derived_operand_target_or_result",
            "Target and prediction-result Features are not evaluator inputs.",
        )
    if not bool(getattr(feature, "active", False)):
        return _blocked(
            identity,
            ml_name,
            "feature",
            source_kind,
            "derived_active_dependency_unavailable",
            "Inactive Features are not available before Derived evaluation.",
        )
    if _text(feature, "data_type") != "number":
        return _blocked(
            identity,
            ml_name,
            "feature",
            source_kind,
            "derived_operand_type_invalid",
            "Derived operands must be numeric Features.",
        )
    if not ml_name:
        return _blocked(
            identity,
            ml_name,
            "feature",
            source_kind,
            "derived_operand_type_invalid",
            "Derived operands must have a non-empty ML name.",
        )
    if role not in _RUNTIME_FEATURE_ROLES or not bool(
        getattr(feature, "model_input_enabled", False)
    ):
        return _blocked(
            identity,
            ml_name,
            "feature",
            source_kind,
            "derived_operand_runtime_unavailable",
            "This Feature is not provided to both Train and Predict before Derived evaluation.",
        )
    return DerivedOperandEligibility(
        True, identity, ml_name, "feature", source_kind
    )


def _blocked(
    identity: str,
    ml_name: str,
    owner_kind: str,
    source_kind: str,
    code: str,
    reason: str,
) -> DerivedOperandEligibility:
    return DerivedOperandEligibility(
        False, identity, ml_name, owner_kind, source_kind, code, reason
    )


def _identity(owner: object) -> str:
    stable_identity = _text(owner, "stable_identity")
    if stable_identity:
        return stable_identity
    identity = getattr(owner, "identity", "")
    if isinstance(identity, tuple) and len(identity) == 2:
        return str(identity[1])
    return str(identity or "").strip()


def _text(owner: object, field: str) -> str:
    return str(getattr(owner, field, "") or "").strip()
