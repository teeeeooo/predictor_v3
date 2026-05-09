"""
AS/NZS / Energy Rating SEER Excel HSPF compatibility calculator skeleton.
REFERENCE_TYPE = ASNZS_EXCEL_COMPAT
This module is not part of the ISO16358 common path.
It serves as a separate compatibility path to prevent contamination of calculator_iso16358.py.
UI integration via resolver-backed adapter is required before exposure.
"""

REFERENCE_TYPE = "ASNZS_EXCEL_COMPAT"
CALCULATOR_ID = "asnzs_excel_hspf"

class ASNZSExcelHSPFCompatibilityCalculator:
    def calculate_hspf(self, measured_inputs: dict, options: dict = None) -> dict:
        """
        AS/NZS Excel HSPF compatibility calculation is not implemented yet.
        
        This skeleton must not be used as ISO common HSPF.
        
        Input contract: Hybrid Input (canonical performance points + compatibility options).
        Boundary: Reference type must be ASNZS_EXCEL_COMPAT.
        """
        raise NotImplementedError(
            "AS/NZS Excel HSPF compatibility calculation is not implemented yet. "
            "This skeleton must not be used as ISO common HSPF. "
            "Boundary: ASNZS_EXCEL_COMPAT. NOT ISO common HSPF."
        )
