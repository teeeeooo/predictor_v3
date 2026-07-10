"""Runtime-neutral data contracts for the Predict workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PredictionInputRequest:
    """Validated input for one core prediction call."""

    case_id: str
    row_input: dict[str, Any]


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


@dataclass(frozen=True)
class PredictionModelStatus:
    """Model artifact status exposed to controllers and presentation."""

    model_path: str
    status: str
    message: str = ""
