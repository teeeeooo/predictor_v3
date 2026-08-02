"""Runtime-neutral data contracts for the Predict workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from apps.predict.application.result_contract import PredictionExecutionContext
from apps.predict.application.result_enrichment import ExecutionInputEvidence
from apps.predict.application.target_outcome import PredictionTargetDescriptor


@dataclass(frozen=True)
class PredictionInputRequest:
    """Validated input for one core prediction call."""

    case_id: str
    row_input: dict[str, Any]
    context: PredictionExecutionContext | None = None
    capacity_inputs: tuple[ExecutionInputEvidence, ...] = ()
    requested_targets: tuple[PredictionTargetDescriptor, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "row_input", MappingProxyType(dict(self.row_input)))
        object.__setattr__(self, "requested_targets", tuple(self.requested_targets))
        object.__setattr__(self, "capacity_inputs", tuple(self.capacity_inputs))
        if self.context is not None and self.context.case_id != self.case_id:
            raise ValueError("prediction request context case_id mismatch")
        if (
            self.context is not None
            and self.context.requested_target_identities
            != tuple(item.target_identity for item in self.requested_targets)
        ):
            raise ValueError("prediction request Target contract mismatch")


@dataclass(frozen=True)
class PredictionInputOutcome:
    """Result of converting one case row into a prediction request."""

    case_id: str
    request: PredictionInputRequest | None = None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        """Return whether this row can be sent to the prediction service."""

        return self.request is not None and not self.errors


@dataclass(frozen=True)
class PredictionServiceResult:
    """Prediction outcome for one prepared request."""

    case_id: str
    status: str
    predictions: dict[str, float] = field(default_factory=dict)
    message: str = ""
    context: PredictionExecutionContext | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "predictions", MappingProxyType(dict(self.predictions)))
        if self.context is not None and self.context.case_id != self.case_id:
            raise ValueError("prediction result context case_id mismatch")


@dataclass(frozen=True)
class PredictionModelStatus:
    """Model artifact status exposed to controllers and presentation."""

    model_path: str
    status: str
    message: str = ""
