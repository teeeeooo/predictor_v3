"""Outbound gateway for SASO T3 core calculator execution."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)
from core.calculators.capability import Iso16358CspfRequest, execute_standard_calculation


CalculatorFactory = Callable[..., object]


def calculate_saso_t3_cspf(
    measured: Mapping[str, Mapping[str, float]],
    *,
    profile_id: str,
    test_selection: str,
    calculator_factory: CalculatorFactory = create_calculator_for_profile,
) -> Mapping[str, object]:
    """Apply the SASO test selection override and run the core CSPF calculator."""
    if calculator_factory is not create_calculator_for_profile:
        calculator = calculator_factory(profile_id=profile_id)
        calculator.config["cspf_test_profile"]["test_selection"] = test_selection
        return calculator.calculate_cspf(measured)
    return execute_standard_calculation(
        "iso16358.cspf",
        Iso16358CspfRequest(profile_id, measured, test_selection=test_selection),
    )
