"""Compatibility wrapper for calculator profile registry.

Actual implementation lives in `core.calculators.profiles`.
"""

from core.calculators.profiles import (
    CalculatorProfile,
    list_calculator_profiles,
    resolve_calculator_profile,
)

__all__ = [
    "CalculatorProfile",
    "list_calculator_profiles",
    "resolve_calculator_profile",
]
