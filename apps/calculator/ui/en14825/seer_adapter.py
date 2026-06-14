"""Adapter layer translating UI inputs (W) to core calculator inputs (kW) and parsing results for SEER."""

from typing import Dict, Optional, Tuple
from core.calculator_en14825 import EN14825Calculator
from apps.calculator.ui.en14825.seer_models import (
    SeerPointInput,
    SeerPointComputed,
    SeerResultSummary,
)

class SeerAdapter:
    """Adapter to compute intermediate values and coordinate with the core calculator."""

    def __init__(self, calculator: Optional[EN14825Calculator] = None) -> None:
        self.calculator = calculator or EN14825Calculator()

    @staticmethod
    def get_part_load_info(tj: float, p_design_c_w: float, t_design_c: float) -> Tuple[float, float]:
        """Calculate part load ratio (%) and part load (W) for a given outdoor dry-bulb temperature.

        Formula matches the core cooling load line:
        part_load_ratio = max(0.0, (tj - 16.0) / (t_design_c - 16.0))
        """
        if p_design_c_w <= 0:
            return 0.0, 0.0
        if t_design_c == 16.0:
            # Prevent division by zero, matches core behavior raise
            return 0.0, 0.0

        ratio = (tj - 16.0) / (t_design_c - 16.0)
        ratio = max(0.0, ratio)
        return ratio * 100.0, p_design_c_w * ratio

    def get_seer_defaults(self) -> dict:
        """Return UI defaults owned by the unified EN14825 config."""
        try:
            seer_config = self.calculator.seer_config
            defaults = seer_config["defaults"]
            return {
                "t_design_c": float(seer_config["design"]["t_design_c"]),
                "degradation_coefficient": float(defaults["degradation_coefficient"]),
                "appliance_type": str(defaults["appliance_type"]),
            }
        except AttributeError as exc:
            raise ValueError("SEER calculator does not expose seer_config defaults.") from exc
        except KeyError as exc:
            raise ValueError(f"Missing SEER UI default config key: {exc.args[0]}") from exc

    def compute_points(self, inputs: Dict[str, SeerPointInput]) -> Dict[str, SeerPointComputed]:
        """Compute intermediate fields (EER, derived power, comparison percentages, and cell states)."""
        computed = {}
        for key in ("A", "B", "C", "D"):
            inp = inputs.get(key) or SeerPointInput()
            comp = SeerPointComputed()

            # 1. Declared point computations
            # Capacity state
            if inp.declared_capacity is not None:
                if inp.declared_capacity > 0:
                    comp.declared_capacity_state = "neutral"
                else:
                    comp.declared_capacity_state = "invalid"
            else:
                comp.declared_capacity_state = "unavailable"

            # EER state
            if inp.declared_eer is not None:
                if inp.declared_eer > 0:
                    comp.declared_eer_state = "neutral"
                else:
                    comp.declared_eer_state = "invalid"
            else:
                comp.declared_eer_state = "unavailable"

            # Derived Power
            if (inp.declared_capacity is not None and inp.declared_capacity > 0 and
                    inp.declared_eer is not None and inp.declared_eer > 0):
                comp.declared_power_w_for_core = inp.declared_capacity / inp.declared_eer

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

            # Tested EER
            if (inp.tested_capacity is not None and inp.tested_capacity > 0 and
                    inp.tested_power is not None and inp.tested_power > 0):
                comp.tested_eer = inp.tested_capacity / inp.tested_power
                comp.tested_eer_state = "neutral"
            else:
                comp.tested_eer_state = "unavailable"

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

            # EER % = tested_eer / declared_eer * 100
            if (comp.tested_eer is not None and comp.tested_eer > 0 and
                    inp.declared_eer is not None and inp.declared_eer > 0):
                eer_pct = (comp.tested_eer / inp.declared_eer) * 100.0
                comp.eer_percent = eer_pct
                if eer_pct < 90.0:
                    comp.eer_percent_state = "invalid"
                else:
                    comp.eer_percent_state = "pass"
            else:
                comp.eer_percent_state = "unavailable"

            computed[key] = comp
        return computed

    def calculate(
        self,
        inputs: Dict[str, SeerPointInput],
        p_design_c_w: float,
        p_to_w: float = 0.0,
        p_sb_w: float = 0.0,
        p_ck_w: float = 0.0,
        p_off_w: float = 0.0,
        t_design_c: float = None,
        cd: float = None,
        appliance_type: str = None,
    ) -> SeerResultSummary:
        """Call the core SEER calculator and build the final summary.

        Performs W -> kW conversion on boundary.
        """
        summary = SeerResultSummary()
        if t_design_c is None or cd is None or appliance_type is None:
            config_defaults = self.get_seer_defaults()
            if t_design_c is None:
                t_design_c = config_defaults["t_design_c"]
            if cd is None:
                cd = config_defaults["degradation_coefficient"]
            if appliance_type is None:
                appliance_type = config_defaults["appliance_type"]

        if p_design_c_w <= 0:
            summary.status_code = "invalid_design_load"
            summary.message = "Design cooling load must be > 0"
            return summary
        if t_design_c == 16.0:
            summary.status_code = "invalid_t_design"
            summary.message = "t_design_c cannot be 16°C"
            return summary

        # 1. Check completeness of declared and tested source sets
        computed_points = self.compute_points(inputs)

        declared_complete = True
        tested_complete = True
        for key in ("A", "B", "C", "D"):
            comp = computed_points[key]
            inp = inputs.get(key)

            # Declared completeness check
            if (inp is None or inp.declared_capacity is None or inp.declared_eer is None or
                    comp.declared_power_w_for_core is None or inp.declared_capacity <= 0 or inp.declared_eer <= 0):
                declared_complete = False

            # Tested completeness check
            if (inp is None or inp.tested_capacity is None or inp.tested_power is None or
                    comp.tested_eer is None or inp.tested_capacity <= 0 or inp.tested_power <= 0):
                tested_complete = False

        if not declared_complete and not tested_complete:
            summary.status_code = "input_incomplete"
            summary.message = "Both Declared and Tested datasets are incomplete"
            return summary

        # Convert auxiliary inputs to kW
        p_design_c_kw = p_design_c_w / 1000.0
        p_to_kw = p_to_w / 1000.0
        p_sb_kw = p_sb_w / 1000.0
        p_ck_kw = p_ck_w / 1000.0
        p_off_kw = p_off_w / 1000.0

        # 2. Run core calculations
        # Declared-only calculation
        if declared_complete:
            core_declared_points = {}
            for key in ("A", "B", "C", "D"):
                inp = inputs[key]
                comp = computed_points[key]
                # core expects (capacity_kW, power_kW)
                core_declared_points[key] = (inp.declared_capacity / 1000.0, comp.declared_power_w_for_core / 1000.0)

            try:
                dec_res = self.calculator.calculate_seer(
                    test_points=core_declared_points,
                    p_to=p_to_kw,
                    p_sb=p_sb_kw,
                    p_ck=p_ck_kw,
                    p_off=p_off_kw,
                    p_design_c=p_design_c_kw,
                    t_design_c=t_design_c,
                    cd=cd,
                    appliance_type=appliance_type,
                )
                summary.declared_seer = dec_res["seer"]
                summary.declared_qc_kwh = dec_res["qc_kwh"]
                summary.declared_seer_state = "neutral"
                summary.declared_qc_state = "neutral"
            except Exception as exc:
                summary.status_code = "declared_error"
                summary.message = f"Declared calculation error: {str(exc)}"
                return summary

        # Tested-only calculation
        if tested_complete:
            core_tested_points = {}
            for key in ("A", "B", "C", "D"):
                inp = inputs[key]
                # core expects (capacity_kW, power_kW)
                core_tested_points[key] = (inp.tested_capacity / 1000.0, inp.tested_power / 1000.0)

            try:
                test_res = self.calculator.calculate_seer(
                    test_points=core_tested_points,
                    p_to=p_to_kw,
                    p_sb=p_sb_kw,
                    p_ck=p_ck_kw,
                    p_off=p_off_kw,
                    p_design_c=p_design_c_kw,
                    t_design_c=t_design_c,
                    cd=cd,
                    appliance_type=appliance_type,
                )
                summary.tested_seer = test_res["seer"]
                summary.tested_qc_kwh = test_res["qc_kwh"]
                summary.tested_seer_state = "neutral"
                summary.tested_qc_state = "neutral"
            except Exception as exc:
                summary.status_code = "tested_error"
                summary.message = f"Tested calculation error: {str(exc)}"
                return summary

        # 3. Comparison results
        if declared_complete and tested_complete:
            if summary.declared_seer is not None and summary.declared_seer > 0 and summary.tested_seer is not None:
                seer_pct = (summary.tested_seer / summary.declared_seer) * 100.0
                summary.seer_percent = seer_pct
                if seer_pct < 92.0:
                    summary.seer_percent_state = "invalid"
                else:
                    summary.seer_percent_state = "pass"
            else:
                summary.seer_percent_state = "unavailable"
        else:
            summary.seer_percent_state = "unavailable"

        summary.status_code = "complete"
        summary.message = "Calculation completed successfully"
        return summary
