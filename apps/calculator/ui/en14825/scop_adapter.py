"""Adapter layer translating UI inputs (W, °C) to core calculator inputs (kW, °C) and parsing results for SCOP."""

from typing import Dict, Optional, Tuple
from core.calculator_en14825 import EN14825Calculator
from apps.calculator.ui.en14825.scop_models import (
    ScopPointInput,
    ScopPointComputed,
    ScopResultSummary,
)


class ScopAdapter:
    """Adapter to compute intermediate heating values and coordinate with the core calculator."""

    POINT_KEYS = ("A", "B", "C", "D", "TOL", "Tbiv")

    CLIMATE_DEFAULTS = {
        "average": {"tbiv": -10.0, "tol": -11.0},
        "warmer": {"tbiv": 2.0, "tol": -11.0},
        "colder": {"tbiv": -15.0, "tol": -22.0},
    }

    def __init__(self, calculator: Optional[EN14825Calculator] = None) -> None:
        self.calculator = calculator or EN14825Calculator()

    def get_climate_data(self, climate: str) -> dict:
        """Fetch climate-specific configuration data from the core calculator config."""
        if not climate:
            raise ValueError("Climate must be specified.")
        climate_key = climate.strip().lower()
        climates = self.calculator.scop_config.get("climates", {})
        if climate_key not in climates:
            raise ValueError(f"Unknown SCOP climate: {climate}")
        return climates[climate_key]

    def resolve_temperature_overrides(
        self,
        climate: str,
        tbiv_temp_c: Optional[float] = None,
        tol_temp_c: Optional[float] = None,
    ) -> Tuple[float, float]:
        """Resolve effective bivalent and TOL temperatures using climate defaults when overrides are omitted."""
        if not climate:
            raise ValueError("Climate must be specified.")
        climate_key = climate.strip().lower()

        defaults = self.CLIMATE_DEFAULTS.get(climate_key, {})
        default_tbiv = defaults.get("tbiv")
        default_tol = defaults.get("tol")

        if default_tbiv is None or default_tol is None:
            climate_data = self.get_climate_data(climate_key)
            if default_tbiv is None:
                default_tbiv = float(climate_data.get("tbiv_max_c", 2.0))
            if default_tol is None:
                default_tol = float(climate_data.get("tol_max_c", -7.0))

        eff_tbiv = tbiv_temp_c if tbiv_temp_c is not None else default_tbiv
        eff_tol = tol_temp_c if tol_temp_c is not None else default_tol

        return eff_tbiv, eff_tol

    def resolve_point_availability(
        self,
        climate: str,
        tbiv_temp_c: Optional[float] = None,
        tol_temp_c: Optional[float] = None,
    ) -> dict:
        """Resolve UI point availability from the core/config SCOP point contract."""
        climate_key = climate.strip().lower()
        climate_data = self.get_climate_data(climate_key)
        eff_tbiv, eff_tol = self.resolve_temperature_overrides(climate_key, tbiv_temp_c, tol_temp_c)
        resolver = getattr(self.calculator, "_resolve_scop_point_contract", None)
        if not callable(resolver):
            raise ValueError("SCOP calculator does not expose point contract resolver.")

        contract = resolver(climate_key, climate_data, eff_tbiv, eff_tol)
        required = tuple(contract["required_independent_points"])
        mapped = dict(contract["mapped_points"])
        inactive = tuple(contract["inactive_points"])
        temperatures = dict(contract["resolved_temperatures"])
        required_set = set(required)
        inactive_set = set(inactive)

        point_states = {}
        for key in self.POINT_KEYS:
            if key in required_set:
                state = "required"
            elif key in mapped:
                state = "mapped"
            elif key in inactive_set and key in ("TOL", "Tbiv"):
                state = "threshold_only"
            elif key in inactive_set:
                state = "inactive"
            else:
                state = "inactive"
            point_states[key] = {
                "state": state,
                "required": state == "required",
                "mapped_from": mapped.get(key),
                "temp_c": temperatures.get(key),
            }

        return {
            "required_independent_points": required,
            "mapped_points": mapped,
            "inactive_points": inactive,
            "resolved_temperatures": temperatures,
            "points": point_states,
        }

    @staticmethod
    def get_part_load_info(tj: float, p_design_h_w: float, t_design_h: float) -> Tuple[float, float]:
        """Calculate part load ratio (%) and part load (W) for a given outdoor dry-bulb temperature.

        Formula matches the core heating load line:
        part_load_ratio = max(0.0, (tj - 16.0) / (t_design_h - 16.0))
        """
        if p_design_h_w <= 0:
            return 0.0, 0.0
        if t_design_h == 16.0:
            # Prevent division by zero, matches core behavior
            return 0.0, 0.0

        ratio = (tj - 16.0) / (t_design_h - 16.0)
        ratio = max(0.0, ratio)
        return ratio * 100.0, p_design_h_w * ratio

    def compute_points(self, inputs: Dict[str, ScopPointInput]) -> Dict[str, ScopPointComputed]:
        """Compute intermediate fields (COP, derived power, comparison percentages, and cell states)."""
        computed = {}
        for key in self.POINT_KEYS:
            inp = inputs.get(key) or ScopPointInput()
            comp = ScopPointComputed()

            # 1. Declared point computations
            # Capacity state
            if inp.declared_capacity is not None:
                if inp.declared_capacity > 0:
                    comp.declared_capacity_state = "neutral"
                else:
                    comp.declared_capacity_state = "invalid"
            else:
                comp.declared_capacity_state = "unavailable"

            # COP state
            if inp.declared_cop is not None:
                if inp.declared_cop > 0:
                    comp.declared_cop_state = "neutral"
                else:
                    comp.declared_cop_state = "invalid"
            else:
                comp.declared_cop_state = "unavailable"

            # Derived Power
            if (inp.declared_capacity is not None and inp.declared_capacity > 0 and
                    inp.declared_cop is not None and inp.declared_cop > 0):
                comp.declared_power_w_for_core = inp.declared_capacity / inp.declared_cop

            # 2. Tested point computations
            # Capacity state
            if inp.tested_capacity is not None:
                if inp.tested_capacity > 0:
                    comp.tested_capacity_state = "neutral"
                else:
                    comp.tested_capacity_state = "invalid"
            else:
                comp.tested_capacity_state = "unavailable"

            # Power state
            if inp.tested_power is not None:
                if inp.tested_power > 0:
                    comp.tested_power_state = "neutral"
                else:
                    comp.tested_power_state = "invalid"
            else:
                comp.tested_power_state = "unavailable"

            # Tested COP
            if (inp.tested_capacity is not None and inp.tested_capacity > 0 and
                    inp.tested_power is not None and inp.tested_power > 0):
                comp.tested_cop = inp.tested_capacity / inp.tested_power
                comp.tested_cop_state = "neutral"
            else:
                comp.tested_cop_state = "unavailable"

            # 3. Point-level comparison % & cell states
            # Capacity % = tested_capacity / declared_capacity * 100
            if (inp.tested_capacity is not None and inp.tested_capacity > 0 and
                    inp.declared_capacity is not None and inp.declared_capacity > 0):
                cap_pct = (inp.tested_capacity / inp.declared_capacity) * 100.0
                comp.capacity_percent = cap_pct
                if cap_pct < 90.0 or cap_pct >= 110.0:
                    comp.capacity_percent_state = "invalid"
                else:
                    comp.capacity_percent_state = "pass"
            else:
                comp.capacity_percent_state = "unavailable"

            # COP % = tested_cop / declared_cop * 100
            if (comp.tested_cop is not None and comp.tested_cop > 0 and
                    inp.declared_cop is not None and inp.declared_cop > 0):
                cop_pct = (comp.tested_cop / inp.declared_cop) * 100.0
                comp.cop_percent = cop_pct
                if cop_pct < 90.0:
                    comp.cop_percent_state = "invalid"
                else:
                    comp.cop_percent_state = "pass"
            else:
                comp.cop_percent_state = "unavailable"

            computed[key] = comp
        return computed

    def calculate(
        self,
        inputs: Dict[str, ScopPointInput],
        p_design_h_w: float,
        climate: str,
        p_to_w: float = 0.0,
        p_sb_w: float = 0.0,
        p_ck_w: float = 0.0,
        p_off_w: float = 0.0,
        cd: Optional[float] = None,
        appliance_type: Optional[str] = None,
        tbiv_temp_c: Optional[float] = None,
        tol_temp_c: Optional[float] = None,
    ) -> ScopResultSummary:
        """Call the core SCOP calculator and build the final summary.

        Performs W -> kW conversion on boundary.
        """
        summary = ScopResultSummary(climate=climate)

        if p_design_h_w <= 0:
            summary.status_code = "invalid_design_load"
            summary.message = "Design heating load must be > 0"
            return summary

        try:
            climate_data = self.get_climate_data(climate)
            t_design_h = float(climate_data["t_design_h_c"])
        except Exception as exc:
            summary.status_code = "invalid_climate"
            summary.message = f"Invalid climate: {str(exc)}"
            return summary

        if t_design_h == 16.0:
            summary.status_code = "invalid_t_design"
            summary.message = "t_design_h cannot be 16°C"
            return summary

        # Check bivalent / TOL overrides relation using resolved defaults
        try:
            eff_tbiv, eff_tol = self.resolve_temperature_overrides(climate, tbiv_temp_c, tol_temp_c)
        except Exception as exc:
            summary.status_code = "invalid_climate"
            summary.message = f"Invalid climate: {str(exc)}"
            return summary

        if eff_tol > eff_tbiv:
            summary.status_code = "invalid_temp_override"
            summary.message = f"TOL ({eff_tol}) must be <= Tbiv ({eff_tbiv})"
            return summary

        computed_points = self.compute_points(inputs)
        try:
            availability = self.resolve_point_availability(climate, eff_tbiv, eff_tol)
            required_points = availability["required_independent_points"]
        except Exception as exc:
            summary.status_code = "invalid_point_contract"
            summary.message = f"Invalid point availability: {str(exc)}"
            return summary

        # 1. Check completeness of declared and tested source sets
        declared_complete = True
        tested_complete = True
        for key in required_points:
            comp = computed_points[key]
            inp = inputs.get(key)

            # Declared completeness check
            if (inp is None or inp.declared_capacity is None or inp.declared_cop is None or
                    comp.declared_power_w_for_core is None or inp.declared_capacity <= 0 or inp.declared_cop <= 0):
                declared_complete = False

            # Tested completeness check
            if (inp is None or inp.tested_capacity is None or inp.tested_power is None or
                    comp.tested_cop is None or inp.tested_capacity <= 0 or inp.tested_power <= 0):
                tested_complete = False

        if not declared_complete and not tested_complete:
            summary.status_code = "input_incomplete"
            summary.message = "Both Declared and Tested datasets are incomplete"
            return summary

        # Convert auxiliary inputs to kW
        p_design_h_kw = p_design_h_w / 1000.0
        p_to_kw = p_to_w / 1000.0
        p_sb_kw = p_sb_w / 1000.0
        p_ck_kw = p_ck_w / 1000.0
        p_off_kw = p_off_w / 1000.0

        # 2. Run core calculations
        # Declared-only calculation
        if declared_complete:
            core_declared_points = {}
            for key in required_points:
                inp = inputs[key]
                comp = computed_points[key]
                core_declared_points[key] = {
                    "capacity": inp.declared_capacity / 1000.0,
                    "power": comp.declared_power_w_for_core / 1000.0,
                }

            try:
                dec_res = self.calculator.calculate_scop(
                    test_points=core_declared_points,
                    p_to=p_to_kw,
                    p_sb=p_sb_kw,
                    p_ck=p_ck_kw,
                    p_off=p_off_kw,
                    p_design_h=p_design_h_kw,
                    climate=climate,
                    cd=cd,
                    appliance_type=appliance_type,
                    tbiv_temp_c=eff_tbiv,
                    tol_temp_c=eff_tol,
                )
                summary.declared_scop = dec_res["scop"]
                summary.declared_qh_kwh = dec_res["qh_kwh"]
                summary.declared_total_kwh = dec_res["total_kwh"]
                summary.declared_scop_state = "neutral"
                summary.declared_qh_state = "neutral"
            except Exception as exc:
                summary.status_code = "declared_error"
                summary.message = f"Declared calculation error: {str(exc)}"
                return summary

        # Tested-only calculation
        if tested_complete:
            core_tested_points = {}
            for key in required_points:
                inp = inputs[key]
                core_tested_points[key] = {
                    "capacity": inp.tested_capacity / 1000.0,
                    "power": inp.tested_power / 1000.0,
                }

            try:
                test_res = self.calculator.calculate_scop(
                    test_points=core_tested_points,
                    p_to=p_to_kw,
                    p_sb=p_sb_kw,
                    p_ck=p_ck_kw,
                    p_off=p_off_kw,
                    p_design_h=p_design_h_kw,
                    climate=climate,
                    cd=cd,
                    appliance_type=appliance_type,
                    tbiv_temp_c=eff_tbiv,
                    tol_temp_c=eff_tol,
                )
                summary.tested_scop = test_res["scop"]
                summary.tested_qh_kwh = test_res["qh_kwh"]
                summary.tested_total_kwh = test_res["total_kwh"]
                summary.tested_scop_state = "neutral"
                summary.tested_qh_state = "neutral"
            except Exception as exc:
                summary.status_code = "tested_error"
                summary.message = f"Tested calculation error: {str(exc)}"
                return summary

        # 3. Comparison results
        if declared_complete and tested_complete:
            if summary.declared_scop is not None and summary.declared_scop > 0 and summary.tested_scop is not None:
                scop_pct = (summary.tested_scop / summary.declared_scop) * 100.0
                summary.scop_percent = scop_pct
                if scop_pct < 92.0:
                    summary.scop_percent_state = "invalid"
                else:
                    summary.scop_percent_state = "pass"
            else:
                summary.scop_percent_state = "unavailable"
        else:
            summary.scop_percent_state = "unavailable"

        summary.status_code = "complete"
        summary.message = "Calculation completed successfully"
        return summary
