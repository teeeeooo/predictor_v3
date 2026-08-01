"""Typed per-target prediction outcomes and their runtime descriptor."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PredictionTargetDescriptor:
    target_identity: str
    result_feature_identity: str
    ml_name: str
    result_key: str
    canonical_unit: str
    value_source: str = "model_prediction"


@dataclass(frozen=True)
class TargetOutcome:
    """One expected target's raw result before presentation formatting."""

    target_identity: str
    result_feature_identity: str
    result_key: str
    canonical_unit: str
    status: str
    value_source: str = "model_prediction"
    raw_value: float | None = None
    reason_code: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"available", "unavailable", "failed"}:
            raise ValueError(f"unsupported target outcome: {self.status}")
        if not self.target_identity or not self.result_feature_identity:
            raise ValueError("target outcome identity is required")
        if self.status == "available":
            if self.raw_value is None or not isfinite(float(self.raw_value)):
                raise ValueError("available target outcome requires a finite value")
            if self.reason_code or self.message:
                raise ValueError("available target outcome cannot carry failure detail")
        elif self.raw_value is not None:
            raise ValueError("non-available target outcome cannot carry a raw value")
        elif not self.reason_code:
            raise ValueError("non-available target outcome requires a reason code")
        object.__setattr__(self, "message", _bounded(self.message))


def _bounded(message: str) -> str:
    return str(message).strip().splitlines()[0][:160] if message else ""


def validate_runtime_target_contract(runtime) -> None:  # noqa: ANN001
    """Fail closed when one runtime carries an incoherent Target projection."""
    descriptors = tuple(runtime.target_descriptors)
    if not descriptors:
        raise ValueError("Predict runtime Target contract is empty")
    required_fields = tuple(
        (
            item.target_identity,
            item.result_feature_identity,
            item.ml_name,
            item.result_key,
            item.canonical_unit,
            item.value_source,
        )
        for item in descriptors
    )
    if any(not all(fields) for fields in required_fields):
        raise ValueError("Predict runtime Target descriptor is incomplete")
    for index, label in (
        (0, "Target identity"),
        (1, "result Feature identity"),
        (2, "Target ML name"),
        (3, "result key"),
    ):
        values = tuple(fields[index] for fields in required_fields)
        if len(values) != len(set(values)):
            raise ValueError(f"Predict runtime {label} is duplicated")
    expected_targets = tuple(item.ml_name for item in descriptors)
    expected_keys = tuple((item.ml_name, item.result_key) for item in descriptors)
    if tuple(runtime.active_targets) != expected_targets:
        raise ValueError("Predict active Target projection is incomplete")
    if tuple(runtime.target_result_keys) != expected_keys:
        raise ValueError("Predict Target/result-key projection is inconsistent")
    columns = {item.feature_identity: item for item in runtime.column_descriptors}
    for descriptor in descriptors:
        column = columns.get(descriptor.result_feature_identity)
        if (
            column is None
            or column.key != descriptor.result_key
            or column.role != "result"
            or not column.active
        ):
            raise ValueError(
                "Predict Target/result Feature projection is inconsistent"
            )
