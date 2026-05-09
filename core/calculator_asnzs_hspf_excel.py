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
        
        This skeleton must not be used as common HSPF.
        
        Input contract: Hybrid Input (canonical performance points + compatibility options).
        Boundary: Reference type must be ASNZS_EXCEL_COMPAT.
        """
        raise NotImplementedError(
            "AS/NZS Excel HSPF compatibility calculation is not implemented yet. "
            "This skeleton must not be used as common HSPF. "
            "Boundary: ASNZS_EXCEL_COMPAT."
        )

    def _cop_from_capacity_power(self, capacity_w: float, power_w: float) -> float:
        if capacity_w < 0:
            raise ValueError("Capacity cannot be negative.")
        if power_w <= 0:
            raise ValueError("Power must be positive.")
        return capacity_w / power_w

    def _interpolate_cop_by_temperature(
        self,
        target_temp: float,
        lower_temp: float,
        lower_cop: float,
        upper_temp: float,
        upper_cop: float,
    ) -> float:
        if lower_temp == upper_temp:
            raise ValueError("Temperatures cannot be equal.")
        if not (min(lower_temp, upper_temp) <= target_temp <= max(lower_temp, upper_temp)):
            raise ValueError("Target temperature out of range.")
            
        ratio = (target_temp - lower_temp) / (upper_temp - lower_temp)
        return lower_cop + ratio * (upper_cop - lower_cop)

    def _boundary_cop_from_point(self, point: dict) -> float:
        if "capacity_w" not in point or "power_w" not in point:
            raise ValueError("Point must contain capacity_w and power_w.")
        return self._cop_from_capacity_power(point["capacity_w"], point["power_w"])

# Workbook helper column anchor map
# Excel workbook compatibility helper columns only; not common formula.
WORKBOOK_HELPER_COLUMNS = {
    "BN": {
        "semantic_name": "helper_cop_bn",
        "status": "implementation_check_required",
        "description": "Excel workbook compatibility helper COP column BN; not common formula.",
    },
    "BP": {
        "semantic_name": "helper_cop_bp",
        "status": "implementation_check_required",
        "description": "Excel workbook compatibility helper COP column BP; not common formula.",
    },
    "BY": {
        "semantic_name": "helper_cop_by",
        "status": "implementation_check_required",
        "description": "Excel workbook compatibility helper COP column BY; not common formula.",
    },
    "CA": {
        "semantic_name": "helper_cop_ca",
        "status": "known_or_candidate",
        "description": "Excel workbook compatibility helper COP column CA; not common formula.",
    },
    "CC": {
        "semantic_name": "helper_cop_cc",
        "status": "known_or_candidate",
        "description": "Excel workbook compatibility helper COP column CC; not common formula.",
    },
}

def get_workbook_helper_column_map() -> dict:
    import copy
    return copy.deepcopy(WORKBOOK_HELPER_COLUMNS)
