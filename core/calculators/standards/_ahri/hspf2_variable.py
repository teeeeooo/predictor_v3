"""AHRI 210/240-2026 variable-capacity HSPF2 seasonal engine."""

from .hspf2_performance import HSPF2VariablePerformance
from .hspf2_result import assemble_hspf2_result


class HSPF2VariableCapacityEngine:
    def __init__(self, context, point_resolver):
        self.context = context
        self.point_resolver = point_resolver
        self.performance = HSPF2VariablePerformance()

    def calculate(self, test_points: dict, **kwargs) -> dict:
        p = self.performance
        canonical_points = self.point_resolver.legacy_to_canonical(test_points)
        seasonal = self.context.seasonal_context(kwargs)
        resolved = self.point_resolver.resolve_variable_capacity(canonical_points, kwargs)
        full_points = resolved.full_points
        low_points = resolved.low_points
        h22_capacity, h22_power = full_points["H22"]

        f_def_seasonal = 1.0 + 0.03 * (
            1.0 - p.safe_div(seasonal.t_test - 90, seasonal.t_max - 90)
        )
        total_heating_btu = 0.0
        total_energy_wh = 0.0
        bin_details = []

        for i, temp_f in enumerate(seasonal.bin_temps):
            hours = seasonal.bin_hours[i]
            fractional_hours = seasonal.fractional_bin_hours[i]
            if hours <= 0:
                continue

            building_load = p.building_load(
                temp_f,
                resolved.q_a_full,
                seasonal.variable_capacity_slope_factor,
                seasonal.zero_load_temp_f,
                seasonal.outdoor_design_temp_f,
            )
            q_full, p_full = p.full_capacity_power_at_temp(
                temp_f, full_points, resolved.h1_nom, resolved.h4_point
            )
            q_int, p_int, int_meta = p.intermediate_capacity_power_at_temp(
                temp_f, resolved.h2_int, low_points, full_points
            )
            if seasonal.minimum_speed_limited:
                q_low, p_low = p.minimum_limited_low_capacity_power_at_temp(
                    temp_f, low_points, resolved.h2_int, (q_int, p_int)
                )
            else:
                q_low, p_low = p.low_capacity_power_at_temp(temp_f, low_points)

            cop_low = p.safe_div(q_low, p_low * 3.412) if p_low > 0 else 0.0
            cop_full = p.safe_div(q_full, p_full * 3.412) if p_full > 0 else 0.0
            cop_int = p.safe_div(q_int, p_int * 3.412) if p_int > 0 else 0.0

            if building_load <= 0:
                operating_case = "Case 0"
                delta_j, hlf, plf, cop_bin = 1.0, None, 1.0, None
                q_comp = e_comp = q_aux = e_aux = 0.0
            elif building_load <= q_low:
                operating_case = "Case I"
                hlf = p.safe_div(building_load, q_low)
                plf = max(0.01, 1.0 - seasonal.c_d_heating * (1.0 - hlf))
                delta_j = p.delta_at_bin(temp_f, cop_low, seasonal.t_off, seasonal.t_on)
                cop_bin = cop_low
                q_comp = building_load * delta_j * hours
                e_comp = p_low * hlf * delta_j * hours / plf
                q_aux = building_load * (1.0 - delta_j) * hours
                e_aux = p.safe_div(q_aux, seasonal.auxiliary_eer)
            elif q_low < building_load < q_full:
                operating_case = "Case II"
                hlf, plf = None, 1.0
                valid_case_ii_points = (
                    q_low <= q_int < q_full
                    if seasonal.minimum_speed_limited
                    else q_low < q_int < q_full
                )
                if not valid_case_ii_points:
                    raise ValueError(
                        "HSPF2 v3 AHRI Case II requires q_low < q_int < q_full at every Case II bin: "
                        f"temp_f={temp_f}, q_low={q_low}, q_int={q_int}, q_full={q_full}"
                    )
                if q_int > q_low and building_load <= q_int:
                    cop_bin = cop_low + p.safe_div(building_load - q_low, q_int - q_low) * (
                        cop_int - cop_low
                    )
                else:
                    cop_bin = cop_int + p.safe_div(building_load - q_int, q_full - q_int) * (
                        cop_full - cop_int
                    )
                delta_j = p.delta_at_bin(temp_f, cop_bin, seasonal.t_off, seasonal.t_on)
                q_comp = building_load * delta_j * hours
                e_comp = p.safe_div(building_load, cop_bin * 3.412) * delta_j * hours
                q_aux = building_load * (1.0 - delta_j) * hours
                e_aux = p.safe_div(q_aux, seasonal.auxiliary_eer)
            else:
                operating_case = "Case III"
                hlf, plf, cop_bin = 1.0, 1.0, cop_full
                delta_j = p.delta_at_bin(temp_f, cop_full, seasonal.t_off, seasonal.t_on)
                q_comp = q_full * delta_j * hours
                e_comp = p_full * delta_j * hours
                q_aux = max(0.0, building_load - q_full * delta_j) * hours
                e_aux = p.safe_div(q_aux, seasonal.auxiliary_eer)

            q_j = q_comp + q_aux
            e_j = e_comp + e_aux
            total_heating_btu += q_j
            total_energy_wh += e_j
            bin_details.append(
                {
                    "bin_no": i + 1,
                    "bin": i + 1,
                    "temp_F": temp_f,
                    "hours": hours,
                    "fractional_hours": fractional_hours,
                    "operating_case": operating_case,
                    "building_load": round(building_load, 2),
                    "delta_j": delta_j,
                    "HLF_j": round(hlf, 6) if hlf is not None else None,
                    "PLF_j": round(plf, 6),
                    "q_low": round(q_low, 2),
                    "p_low": round(p_low, 2),
                    "q_int": round(q_int, 2),
                    "p_int": round(p_int, 2),
                    "q_full": round(q_full, 2),
                    "p_full": round(p_full, 2),
                    "COP_low": round(cop_low, 6),
                    "COP_int": round(cop_int, 6),
                    "COP_full": round(cop_full, 6),
                    "COP_bin": round(cop_bin, 6) if cop_bin is not None else None,
                    "q_comp": round(q_comp, 2),
                    "e_comp": round(e_comp, 2),
                    "q_aux": round(q_aux, 2),
                    "e_aux": round(e_aux, 2),
                    "q_j": round(q_j, 2),
                    "E_j": round(e_j, 2),
                    "aux_ratio": round(p.safe_div(e_aux, e_j), 4) if e_j > 0 else 0.0,
                    "debug_info": {
                        "formula_path": "ahri_210_240_2026_variable_capacity_heating",
                        "full_capacity_method": (
                            "eq_11_209_11_210"
                            if temp_f >= 45
                            else "eq_11_213_11_214"
                            if temp_f > 17
                            else "h4full_low_temp_line"
                            if resolved.h4_point is not None
                            else "no_h4full_h1full_h3full_line"
                        ),
                        "low_capacity_method": seasonal.case_i_low_source,
                        "intermediate_capacity_method": int_meta["method"],
                        "intermediate_metadata": {
                            key: round(value, 6) if isinstance(value, float) else value
                            for key, value in int_meta.items()
                        },
                    },
                }
            )

        if total_energy_wh <= 0:
            raise ValueError("HSPF2 AHRI calculation error: total_energy_wh must be > 0.")
        if total_heating_btu <= 0:
            raise ValueError("HSPF2 AHRI calculation error: total_heating_btu must be > 0.")

        raw_hspf2_base = p.safe_div(total_heating_btu, total_energy_wh)
        raw_hspf2 = raw_hspf2_base * seasonal.fdef_override
        rounded_hspf2 = p.round_nearest_025(raw_hspf2)
        return assemble_hspf2_result(
            seasonal,
            resolved,
            h22_capacity,
            h22_power,
            f_def_seasonal,
            total_heating_btu,
            total_energy_wh,
            raw_hspf2_base,
            raw_hspf2,
            rounded_hspf2,
            bin_details,
        )
