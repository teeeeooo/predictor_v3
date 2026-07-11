"""UI-neutral Brazil CSPF application result models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from core.calculators.capability.results import BrazilCspfComplianceResult


ResultRow = tuple[str, str, str, str]
MeasuredPoints = Mapping[str, Mapping[str, float]]


@dataclass(frozen=True)
class BrazilRuleDisplay:
    label: str
    comparison: str
    left_value_text: str
    right_value_text: str
    status_text: str
    passed: bool


@dataclass(frozen=True)
class BrazilCspfUseCaseResult:
    status: str
    status_text: str
    rows: tuple[ResultRow, ...] = ()
    rules: tuple[BrazilRuleDisplay, ...] = ()
    final_status: str | None = None
    final_status_text: str | None = None
    operation_result: BrazilCspfComplianceResult | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
