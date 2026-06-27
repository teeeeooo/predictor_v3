"""Compatibility wrapper for calculator dispatcher.

Actual implementation lives in `core.calculators.dispatcher`.
"""

from core.calculators.dispatcher import create_calculator_for_profile

__all__ = ["create_calculator_for_profile"]
