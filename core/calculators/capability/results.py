"""Domain result contracts for composite calculator capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class BrazilRuleEvaluation:
    """Exact comparison values and the result of one Brazil compliance rule."""

    left_value: float
    right_value: float
    passed: bool


@dataclass(frozen=True)
class BrazilCspfComplianceResult:
    """Brazil-specific result composed from two ISO 16358 raw calculations."""

    three_point_result: Mapping[str, object]
    two_point_result: Mapping[str, object]
    three_point_exact_cspf: float
    two_point_exact_cspf: float
    rule_1_multiplier: float
    rule_1: BrazilRuleEvaluation
    rule_2: BrazilRuleEvaluation
    final_passed: bool
