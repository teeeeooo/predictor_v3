"""AHRI 210/240-2026 dual-stage HSPF2 seasonal engine."""

from __future__ import annotations

from collections.abc import Mapping

from .hspf2_multicapacity import (
    RESISTANCE_BTU_PER_WH,
    assemble_result,
    availability,
    building_load,
    effective_cd,
    full_curve,
    low_curve,
    positive_point,
    seasonal_context,
)
from .numeric import safe_div
from .product import DUAL_STAGE


class HSPF2DualStageEngine:
    """Evaluate the four Section 11.2.2.2 operating cases."""

    def __init__(self, config_context) -> None:
        self.config_context = config_context

    def calculate(self, test_points: Mapping[str, object], **options: object) -> dict:
        context = seasonal_context(self.config_context, options)
        points, point_sources = self._resolve_points(test_points, options)
        q_a_full, _ = positive_point(test_points, "AFull", "A2", "A_Full")
        low_cd = effective_cd(options.get("cd_low", options.get("c_d_low")))
        full_cd = effective_cd(options.get("cd_full", options.get("c_d_full")))
        lockout_enabled = bool(options.get("low_stage_lockout_enabled", False))
        lockout_temp_f = options.get("low_stage_lockout_temp_f")
        if lockout_enabled and lockout_temp_f is None:
            raise ValueError("Dual-stage HSPF2 low-stage lockout temperature is required")
        lockout_temp_f = float(lockout_temp_f) if lockout_temp_f is not None else None

        total_heating = 0.0
        compressor_energy = 0.0
        resistance_energy = 0.0
        details: list[dict] = []
        for index, (temp_f, fraction) in enumerate(
            zip(context.bin_temps, context.fractional_hours), 1
        ):
            if fraction <= 0:
                continue
            load = building_load(temp_f, q_a_full, context)
            q_low, p_low = low_curve(temp_f, points)
            q_full, p_full = full_curve(temp_f, points, points.get("H4Full"))
            delta_low = availability(temp_f, q_low, p_low, context)
            delta_full = availability(temp_f, q_full, p_full, context)
            low_permitted = not (
                lockout_enabled and temp_f < float(lockout_temp_f)
            )

            hlf_low = hlf_full = plf = None
            if low_permitted and load <= q_low:
                case = 1
                hlf_low = safe_div(load, q_low)
                plf = max(0.01, 1.0 - low_cd * (1.0 - hlf_low))
                e_comp = safe_div(p_low * hlf_low * delta_low * fraction, plf)
                e_resistance = safe_div(load * (1.0 - delta_low) * fraction, RESISTANCE_BTU_PER_WH)
            elif low_permitted and load < q_full:
                case = 2
                hlf_low = safe_div(q_full - load, q_full - q_low)
                hlf_full = 1.0 - hlf_low
                e_comp = (p_low * hlf_low + p_full * hlf_full) * delta_low * fraction
                e_resistance = safe_div(load * (1.0 - delta_low) * fraction, RESISTANCE_BTU_PER_WH)
            elif load < q_full:
                case = 3
                hlf_full = safe_div(load, q_full)
                plf = max(0.01, 1.0 - full_cd * (1.0 - hlf_full))
                e_comp = safe_div(p_full * hlf_full * delta_full * fraction, plf)
                e_resistance = safe_div(load * (1.0 - delta_full) * fraction, RESISTANCE_BTU_PER_WH)
            else:
                case = 4
                hlf_full = 1.0
                e_comp = p_full * delta_full * fraction
                e_resistance = safe_div(
                    max(0.0, load - q_full * delta_full) * fraction,
                    RESISTANCE_BTU_PER_WH,
                )

            bin_heating = load * fraction
            total_heating += bin_heating
            compressor_energy += max(0.0, e_comp)
            resistance_energy += max(0.0, e_resistance)
            details.append(
                {
                    "bin": index,
                    "bin_no": index,
                    "temp_F": temp_f,
                    "fractional_hours": fraction,
                    "building_load": load,
                    "q_low": q_low,
                    "p_low": p_low,
                    "q_full": q_full,
                    "p_full": p_full,
                    "low_permitted": low_permitted,
                    "full_permitted": True,
                    "delta_low": delta_low,
                    "delta_full": delta_full,
                    "compressor_availability": self._availability_label(max(delta_low, delta_full)),
                    "operating_case": f"Case {case}",
                    "case": case,
                    "HLF_low": hlf_low,
                    "HLF_full": hlf_full,
                    "PLF": plf,
                    "q_comp": max(0.0, bin_heating - e_resistance * RESISTANCE_BTU_PER_WH),
                    "q_aux": e_resistance * RESISTANCE_BTU_PER_WH,
                    "e_comp": e_comp,
                    "e_aux": e_resistance,
                    "q_j": bin_heating,
                    "E_j": e_comp + e_resistance,
                }
            )

        return assemble_result(
            product=DUAL_STAGE,
            formula_path="ahri_210_240_2026_dual_stage_heating",
            context=context,
            total_heating=total_heating,
            compressor_energy=compressor_energy,
            resistance_energy=resistance_energy,
            bin_details=details,
            metadata={
                "point_sources": point_sources,
                "cd_low_used": low_cd,
                "cd_full_used": full_cd,
                "low_stage_lockout_enabled": lockout_enabled,
                "low_stage_lockout_temp_f": lockout_temp_f,
                "resistance_btu_per_wh": RESISTANCE_BTU_PER_WH,
            },
        )

    @staticmethod
    def _resolve_points(
        test_points: Mapping[str, object], options: Mapping[str, object]
    ) -> tuple[dict[str, tuple[float, float]], dict[str, str]]:
        points = {
            "H0Low": positive_point(test_points, "H0Low", "H01"),
            "H1Low": positive_point(test_points, "H1Low", "H11"),
            "H1Full": positive_point(test_points, "H1Full", "H12"),
            "H2Full": positive_point(test_points, "H2Full", "H22"),
            "H3Low": positive_point(test_points, "H3Low", "H31"),
            "H3Full": positive_point(test_points, "H3Full", "H32"),
        }
        sources = {key: "tested" for key in points}
        h2_low = positive_point(test_points, "H2Low", "H21", "H2V", required=False)
        if h2_low is None or not bool(options.get("h2_low_tested", True)):
            q_h3, p_h3 = points["H3Low"]
            q_h1, p_h1 = points["H1Low"]
            q_h2_full, p_h2_full = points["H2Full"]
            q_h3_full, p_h3_full = points["H3Full"]
            q_h1_full, p_h1_full = points["H1Full"]
            q_ratio = safe_div(q_h2_full, q_h3_full + 0.6 * (q_h1_full - q_h3_full), 1.0)
            p_ratio = safe_div(p_h2_full, p_h3_full + 0.6 * (p_h1_full - p_h3_full), 1.0)
            h2_low = (
                q_ratio * (q_h3 + 0.6 * (q_h1 - q_h3)),
                p_ratio * (p_h3 + 0.6 * (p_h1 - p_h3)),
            )
            sources["H2Low"] = "eq_11_144_11_147"
        else:
            sources["H2Low"] = "tested"
        points["H2Low"] = h2_low
        h4 = positive_point(test_points, "H4Full", "H42", required=False)
        if h4 is not None and bool(options.get("h4_full_tested", True)):
            points["H4Full"] = h4
            sources["H4Full"] = "tested"
        else:
            sources["H4Full"] = "not_provided"
        return points, sources

    @staticmethod
    def _availability_label(value: float) -> str:
        if value <= 0:
            return "unavailable"
        if value < 1:
            return "fractional"
        return "available"
