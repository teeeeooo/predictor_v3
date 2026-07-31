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
