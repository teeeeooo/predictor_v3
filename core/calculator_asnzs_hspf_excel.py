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
        AS/NZS Excel HSPF compatibility calculation - Partial Implementation (Component Accumulation Only).
        """
        if not isinstance(measured_inputs, dict):
            raise ValueError("measured_inputs must be a dict.")
        
        if measured_inputs.get("reference_type") != REFERENCE_TYPE:
            raise ValueError(f"reference_type must be {REFERENCE_TYPE}.")
            
        required_fields = ["component_details", "hstl_wh", "hspf"]
        for field in required_fields:
            if field not in measured_inputs:
                raise ValueError(f"Missing required field: {field}")
        
        options = options or {}
        matched_reference = options.get("matched_reference")
        
        return self._build_component_accumulation_result(
            hstl_wh=measured_inputs["hstl_wh"],
            component_details=measured_inputs["component_details"],
            hspf=measured_inputs["hspf"],
            matched_reference=matched_reference
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

    def _component_power_from_load_and_cop(self, load_w: float, helper_cop: float) -> float:
        if load_w < 0:
            raise ValueError("Load cannot be negative.")
        if helper_cop <= 0:
            raise ValueError("Helper COP must be positive.")
        return load_w / helper_cop

    def _component_energy_from_power(self, power_w: float, hours: float) -> float:
        if power_w < 0:
            raise ValueError("Power cannot be negative.")
        if hours < 0:
            raise ValueError("Hours cannot be negative.")
        return power_w * hours

    def _sum_component_energies(self, components: list[dict]) -> float:
        total = 0.0
        for comp in components:
            if "energy_wh" not in comp:
                raise KeyError("Component missing energy_wh.")
            energy = comp["energy_wh"]
            if energy < 0:
                raise ValueError("Energy cannot be negative.")
            total += energy
        return total

    def _build_component_energy_detail(self, name: str, load_w: float, helper_cop: float, hours: float, anchor: str = None) -> dict:
        power_w = self._component_power_from_load_and_cop(load_w, helper_cop)
        energy_wh = self._component_energy_from_power(power_w, hours)
        return {
            "name": name,
            "anchor": anchor,
            "load_w": load_w,
            "helper_cop": helper_cop,
            "power_w": power_w,
            "hours": hours,
            "energy_wh": energy_wh,
        }

    def _build_compatibility_result_envelope(
        self,
        *,
        hstl_wh: float,
        hsec_wh: float,
        hspf: float,
        workbook_diagnostics: dict = None,
        matched_reference: dict = None,
    ) -> dict:
        if hstl_wh < 0:
            raise ValueError("hstl_wh cannot be negative.")
        if hsec_wh <= 0:
            raise ValueError("hsec_wh must be positive.")
        if hspf < 0:
            raise ValueError("hspf cannot be negative.")
            
        import copy
        envelope = {
            "reference_type": REFERENCE_TYPE,
            "calculator_id": CALCULATOR_ID,
            "hstl_wh": hstl_wh,
            "hsec_wh": hsec_wh,
            "hspf": hspf,
            "workbook_diagnostics": copy.deepcopy(workbook_diagnostics) if workbook_diagnostics else {},
            "matched_reference": copy.deepcopy(matched_reference) if matched_reference else {},
        }
        return envelope

    def _build_component_accumulation_result(
        self,
        *,
        hstl_wh: float,
        component_details: list,
        hspf: float,
        matched_reference: dict = None,
    ) -> dict:
        hsec_wh = self._sum_component_energies(component_details)
        workbook_diagnostics = {
            "component_details": list(component_details),
            "output_anchors": get_workbook_output_anchor_map(),
        }
        return self._build_compatibility_result_envelope(
            hstl_wh=hstl_wh,
            hsec_wh=hsec_wh,
            hspf=hspf,
            workbook_diagnostics=workbook_diagnostics,
            matched_reference=matched_reference,
        )

    def _reconstruct_helper_cops_from_row(self, row: dict, helper_columns: list[str] = None) -> dict:
        if helper_columns is None:
            helper_columns = list(WORKBOOK_HELPER_COLUMNS.keys())
            
        helper_cops = {}
        for col in helper_columns:
            if col not in row:
                raise KeyError(f"Missing helper column: {col}")
            try:
                val = float(row[col])
            except (ValueError, TypeError):
                raise ValueError(f"Helper column {col} must be numeric.")
            
            if val <= 0:
                raise ValueError(f"Helper COP {col} must be positive.")
            helper_cops[col] = val
            
        return {
            "temperature_c": row.get("temperature_c"),
            "helper_cops": helper_cops
        }

    def _select_helper_cop(self, helper_cops: dict, anchor: str) -> float:
        if anchor not in helper_cops:
            raise KeyError(f"Missing anchor: {anchor}")
        val = helper_cops[anchor]
        if val <= 0:
            raise ValueError(f"Helper COP {anchor} must be positive.")
        return val

    def _build_component_detail_from_workbook_row(
        self,
        row: dict,
        *,
        component_anchor: str,
        load_key: str,
        helper_anchor: str,
        hours_key: str,
    ) -> dict:
        if not component_anchor:
            raise ValueError("component_anchor cannot be empty.")
        
        required_keys = [load_key, helper_anchor, hours_key]
        for key in required_keys:
            if key not in row:
                raise KeyError(f"Missing row key: {key}")
        
        try:
            load_w = float(row[load_key])
            hours = float(row[hours_key])
            helper_cops = self._reconstruct_helper_cops_from_row(row, helper_columns=[helper_anchor])
            helper_cop = self._select_helper_cop(helper_cops["helper_cops"], helper_anchor)
        except (ValueError, TypeError):
            raise ValueError("Invalid numeric value in workbook row.")
            
        detail = self._build_component_energy_detail(component_anchor, load_w, helper_cop, hours, anchor=component_anchor)
        detail["helper_anchor"] = helper_anchor
        return detail

# Workbook helper column anchor map
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

# Workbook output anchor map
WORKBOOK_OUTPUT_ANCHORS = {
    "CG": {
        "semantic_name": "component_energy_sum_candidate",
        "status": "implementation_check_required",
        "description": "AS/NZS workbook compatibility output anchor for CG; not ISO common formula.",
    },
    "CH": {
        "semantic_name": "heating_energy_component_or_total_candidate",
        "status": "implementation_check_required",
        "description": "AS/NZS workbook compatibility output anchor for CH; not ISO common formula.",
    },
    "CH48": {
        "semantic_name": "case_total_hsec_wh_reference",
        "status": "candidate",
        "description": "AS/NZS workbook compatibility reference anchor for CH48 Wh; not ISO common expected.",
    },
}

def get_workbook_output_anchor_map() -> dict:
    import copy
    return copy.deepcopy(WORKBOOK_OUTPUT_ANCHORS)
