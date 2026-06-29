"""Outbound gateway for SASO T3 core calculator execution."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)


CalculatorFactory = Callable[..., object]


def calculate_saso_t3_cspf(
    measured: Mapping[str, Mapping[str, float]],
    *,
    profile_id: str,
    test_selection: str,
    calculator_factory: CalculatorFactory = create_calculator_for_profile,
) -> Mapping[str, object]:
    """Apply the SASO test selection override and run the core CSPF calculator."""
    calculator = calculator_factory(profile_id=profile_id)
    calculator.config["cspf_test_profile"]["test_selection"] = test_selection
    return calculator.calculate_cspf(measured)
