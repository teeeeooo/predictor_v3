"""Compatibility wrapper for AS/NZS Excel HSPF compatibility calculator.

Actual implementation lives in `core.calculators.standards.asnzs_hspf_excel`.
"""

from core.calculators.standards.asnzs_hspf_excel import (
    ASNZSExcelHSPFCompatibilityCalculator,
    get_workbook_helper_column_map,
    get_workbook_output_anchor_map,
)

__all__ = [
    "ASNZSExcelHSPFCompatibilityCalculator",
    "get_workbook_helper_column_map",
    "get_workbook_output_anchor_map",
]
