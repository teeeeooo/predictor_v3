"""Compatibility wrapper for AHRI SEER2 calculator.

Actual implementation lives in `core.calculators.standards.ahri_seer2`.
"""

from core.calculators.standards.ahri_seer2 import AHRICalculator, get_default_ahri_seer2_config

__all__ = ["AHRICalculator", "get_default_ahri_seer2_config"]
