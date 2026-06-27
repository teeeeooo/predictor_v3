"""Prediction result row state for the Predict workspace."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultRow:
    """Result state linked to an input case by case_id."""

    case_id: str
    status: str = "pending"
    result_values: dict[str, Any] = field(default_factory=dict)
    message: str = ""
