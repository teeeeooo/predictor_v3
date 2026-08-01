"""Prediction result row state for the Predict workspace."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
)
from apps.predict.application.result_enrichment import DerivedMetricOutcome
from apps.predict.application.target_outcome import TargetOutcome


@dataclass(frozen=True, init=False)
class ResultRow:
    """Typed result state linked to one stable case identity.

    ``result_values`` remains a derived presentation compatibility facade. New
    production results store raw values only in ``target_outcomes``.
    """

    case_id: str
    status: str
    target_outcomes: tuple[TargetOutcome, ...]
    derived_metrics: tuple[DerivedMetricOutcome, ...]
    message: str
    execution_context: PredictionExecutionContext | None
    freshness: str
    stale_reason: str
    _legacy_result_values: tuple[tuple[str, Any], ...]

    def __init__(
        self,
        case_id: str,
        status: str = "pending",
        result_values: Mapping[str, Any] | None = None,
        message: str = "",
        *,
        target_outcomes: tuple[TargetOutcome, ...] = (),
        derived_metrics: tuple[DerivedMetricOutcome, ...] = (),
        execution_context: PredictionExecutionContext | None = None,
        freshness: str = "current",
        stale_reason: str = "",
    ) -> None:
        if freshness not in {"current", "stale"}:
            raise ValueError(f"unsupported result freshness: {freshness}")
        if freshness == "stale" and not stale_reason:
            raise ValueError("stale result requires a reason")
        if status in {"invalid", "cancelled"} and (target_outcomes or derived_metrics):
            raise ValueError(f"{status} result cannot contain execution outcomes")
        object.__setattr__(self, "case_id", case_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "target_outcomes", tuple(target_outcomes))
        object.__setattr__(self, "derived_metrics", tuple(derived_metrics))
        object.__setattr__(self, "message", _bounded(message))
        object.__setattr__(self, "execution_context", execution_context)
        object.__setattr__(self, "freshness", freshness)
        object.__setattr__(self, "stale_reason", _bounded(stale_reason))
        object.__setattr__(
            self, "_legacy_result_values", tuple((result_values or {}).items())
        )

    @property
    def result_values(self) -> dict[str, Any]:
        """Project raw outcomes into the existing table string facade."""
        if self.target_outcomes:
            return {
                outcome.result_key: _format_number(outcome.raw_value)
                for outcome in self.target_outcomes
                if outcome.status == "available"
            }
        return dict(self._legacy_result_values)

    def marked_stale(self, reason: str) -> "ResultRow":
        if not self.target_outcomes and self.execution_context is None:
            return self
        return ResultRow(
            self.case_id,
            self.status,
            dict(self._legacy_result_values),
            self.message,
            target_outcomes=self.target_outcomes,
            derived_metrics=self.derived_metrics,
            execution_context=self.execution_context,
            freshness="stale",
            stale_reason=_bounded(reason),
        )


def _format_number(value: float | None) -> str:
    if value is None or not isfinite(float(value)):
        return ""
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text if text != "-0" else "0"


def _bounded(message: str) -> str:
    return str(message).strip().splitlines()[0][:160] if message else ""
