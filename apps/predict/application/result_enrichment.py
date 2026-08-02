"""Qt-free EER/COP enrichment over execution-pinned Predict evidence."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from apps.predict.application.target_outcome import (
    MODEL_PREDICTION_VALUE_SOURCE,
    TargetOutcome,
)
from apps.predict.application.target_applicability import (
    COOLING_POWER_TARGET_ID,
    HEATING_POWER_TARGET_ID,
)


COOLING_CAPACITY_FEATURE_ID = "ufm_feature_38273f0cc29252dd8dffc5b8c6fa1c75"
HEATING_CAPACITY_FEATURE_ID = "ufm_feature_0b680f0d07ce5a5a8ec361b836545023"
COOLING_POWER_FEATURE_ID = "ufm_feature_7e37047ef3bc56ed8258efd2ebf7af2a"
HEATING_POWER_FEATURE_ID = "ufm_feature_20091175f4535f80bd8c48f807ec8f18"

CAPACITY_UNIT = "W"
POWER_UNIT = "W"
EFFICIENCY_UNIT = "W/W"


@dataclass(frozen=True)
class ExecutionInputEvidence:
    """One input value exactly as prepared for a prediction execution."""

    feature_identity: str
    source_key: str
    ml_name: str
    semantic_unit: str
    raw_value: object


@dataclass(frozen=True)
class DerivedMetricOutcome:
    """One independent Predict application metric and its source identities."""

    metric_key: str
    status: str
    capacity_feature_identity: str
    power_target_identity: str
    semantic_unit: str = EFFICIENCY_UNIT
    raw_value: float | None = None
    capacity_input: ExecutionInputEvidence | None = None
    reason_code: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        if self.metric_key not in {"eer", "cop"}:
            raise ValueError(f"unsupported Predict derived metric: {self.metric_key}")
        if self.status not in {"available", "unavailable"}:
            raise ValueError(f"unsupported derived metric status: {self.status}")
        if self.semantic_unit != EFFICIENCY_UNIT:
            raise ValueError("Predict efficiency metric unit must be W/W")
        if self.status == "available":
            if self.raw_value is None or not isfinite(float(self.raw_value)):
                raise ValueError("available derived metric requires a finite value")
            if self.capacity_input is None:
                raise ValueError("available derived metric requires capacity evidence")
            if self.reason_code or self.message:
                raise ValueError("available derived metric cannot carry unavailable detail")
        elif self.raw_value is not None or not self.reason_code:
            raise ValueError("unavailable derived metric requires a reason without value")
        object.__setattr__(self, "message", _bounded(self.message))


@dataclass(frozen=True)
class _MetricDefinition:
    metric_key: str
    capacity_feature_identity: str
    power_target_identity: str
    power_result_feature_identity: str


_METRICS = (
    _MetricDefinition(
        "eer",
        COOLING_CAPACITY_FEATURE_ID,
        COOLING_POWER_TARGET_ID,
        COOLING_POWER_FEATURE_ID,
    ),
    _MetricDefinition(
        "cop",
        HEATING_CAPACITY_FEATURE_ID,
        HEATING_POWER_TARGET_ID,
        HEATING_POWER_FEATURE_ID,
    ),
)


def build_capacity_input_evidence(column, raw_value: object) -> ExecutionInputEvidence:  # noqa: ANN001
    """Bind a prepared numeric input to the approved capacity identity."""
    if column.feature_identity not in {
        COOLING_CAPACITY_FEATURE_ID,
        HEATING_CAPACITY_FEATURE_ID,
    }:
        raise ValueError("Predict enrichment capacity identity is unsupported")
    return ExecutionInputEvidence(
        column.feature_identity,
        column.key,
        column.ml_feature,
        CAPACITY_UNIT,
        raw_value,
    )


def enrich_target_outcomes(
    capacity_inputs: tuple[ExecutionInputEvidence, ...],
    target_outcomes: tuple[TargetOutcome, ...],
) -> tuple[DerivedMetricOutcome, ...]:
    """Calculate independent raw W/W metrics or deterministic unavailability."""
    inputs = {item.feature_identity: item for item in capacity_inputs}
    targets = {item.target_identity: item for item in target_outcomes}
    return tuple(
        _metric_outcome(item, inputs, targets)
        for item in _METRICS
        if item.power_target_identity in targets
    )


def _metric_outcome(definition, inputs, targets) -> DerivedMetricOutcome:  # noqa: ANN001
    common = dict(
        metric_key=definition.metric_key,
        capacity_feature_identity=definition.capacity_feature_identity,
        power_target_identity=definition.power_target_identity,
    )
    capacity = inputs.get(definition.capacity_feature_identity)
    if capacity is None:
        return _unavailable(common, "capacity_source_missing", "Capacity input was not executed.")
    if capacity.semantic_unit != CAPACITY_UNIT:
        return _unavailable(common, "capacity_unit_mismatch", "Capacity input unit is not W.", capacity)
    capacity_value, reason = _positive_finite(capacity.raw_value, "capacity")
    if reason:
        return _unavailable(common, reason, _reason_message(reason), capacity)

    power = targets.get(definition.power_target_identity)
    if power is None:
        return _unavailable(common, "power_target_missing", "Required power Target is missing.", capacity)
    if power.result_feature_identity != definition.power_result_feature_identity:
        return _unavailable(common, "power_result_feature_mismatch", "Power Result Feature identity differs.", capacity)
    if power.canonical_unit != POWER_UNIT:
        return _unavailable(common, "power_unit_mismatch", "Power Target unit is not W.", capacity)
    if power.value_source != MODEL_PREDICTION_VALUE_SOURCE:
        return _unavailable(common, "power_value_source_mismatch", "Power Target source differs.", capacity)
    if power.status == "unavailable":
        return _unavailable(common, "power_unavailable", "Power Target is unavailable.", capacity)
    if power.status == "failed":
        return _unavailable(common, "power_failed", "Power Target failed.", capacity)
    power_value, reason = _positive_finite(power.raw_value, "power")
    if reason:
        return _unavailable(common, reason, _reason_message(reason), capacity)

    value = capacity_value / power_value
    if not isfinite(value):
        return _unavailable(common, "division_non_finite", "Efficiency division is not finite.", capacity)
    return DerivedMetricOutcome(
        **common,
        status="available",
        raw_value=value,
        capacity_input=capacity,
    )


def _positive_finite(value: object, owner: str) -> tuple[float, str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0, f"{owner}_not_numeric"
    if not isfinite(number):
        return 0.0, f"{owner}_non_finite"
    if number <= 0:
        return 0.0, f"{owner}_non_positive"
    return number, ""


def _unavailable(common, reason: str, message: str, capacity=None):  # noqa: ANN001, ANN202
    return DerivedMetricOutcome(
        **common,
        status="unavailable",
        capacity_input=capacity,
        reason_code=reason,
        message=message,
    )


def _reason_message(reason: str) -> str:
    return {
        "capacity_not_numeric": "Capacity input is not numeric.",
        "capacity_non_finite": "Capacity input is not finite.",
        "capacity_non_positive": "Capacity input must be positive.",
        "power_not_numeric": "Power Target value is not numeric.",
        "power_non_finite": "Power Target value is not finite.",
        "power_non_positive": "Power Target value must be positive.",
    }[reason]


def _bounded(message: str) -> str:
    return str(message).strip().splitlines()[0][:160] if message else ""
