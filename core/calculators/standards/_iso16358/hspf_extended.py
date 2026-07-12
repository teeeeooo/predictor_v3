"""ISO 16358-2 extended-point fallback and formula owners."""


class HSPFExtendedPerformanceMixin:
    def _iso_hspf_minus7_fallback_factors(self, hspf_cfg: dict) -> tuple:
        minus7_fallback = hspf_cfg.get("external_calculator_minus7_fallback_override", {})
        capacity_factor = minus7_fallback.get("minus7_capacity_factor", 0.64)
        power_factor = minus7_fallback.get("minus7_power_factor", 0.82)
        return float(capacity_factor), float(power_factor)

    def _iso_hspf_has_extended_candidate(self, resolved: dict) -> bool:
        candidate = resolved.get("2_ext")
        return (
            isinstance(candidate, dict)
            and "capacity" in candidate
            and "power" in candidate
        )

    def _iso_hspf_extended_minus7_default(self, resolved: dict) -> dict:
        if "-7_ext" in resolved:
            return {
                "capacity": float(resolved["-7_ext"]["capacity"]),
                "power": float(resolved["-7_ext"]["power"]),
            }

        # ISO 16358-2 default for -7_ext when not measured.
        # 2_ext input is a 2°C frost-condition measurement, but the standard
        # factors 0.734 (capacity) / 0.877 (power) derive 2°C non-frost →
        # -7°C values (Table 1).  Convert 2°C frost → 2°C non-frost first,
        # then apply the -7°C factor.
        #   * 1.12 / * 1.06: 2°C frost → 2°C non-frost equivalent
        #   * 0.734 / * 0.877: 2°C non-frost → -7°C (ISO Table 1 derived)
        ext_2_frost = resolved["2_ext"]
        ext_2_nonfrost_capacity = float(ext_2_frost["capacity"]) * 1.12
        ext_2_nonfrost_power = float(ext_2_frost["power"]) * 1.06
        return {
            "capacity": ext_2_nonfrost_capacity * 0.734,
            "power": ext_2_nonfrost_power * 0.877,
        }

    def _iso_hspf_extended_frost_curve(self, tj: float, resolved: dict) -> dict:
        ext_m7 = self._iso_hspf_extended_minus7_default(resolved)
        ext_2_f = resolved["2_ext"]
        return {
            "capacity": ext_m7["capacity"]
            + (float(ext_2_f["capacity"]) - ext_m7["capacity"]) * (tj + 7.0) / 9.0,
            "power": ext_m7["power"]
            + (float(ext_2_f["power"]) - ext_m7["power"]) * (tj + 7.0) / 9.0,
        }

    def _iso_hspf_extended_frost_line(self, resolved: dict) -> tuple:
        ext_m7 = self._iso_hspf_extended_minus7_default(resolved)
        ext_2_f = resolved["2_ext"]
        slope = (float(ext_2_f["capacity"]) - ext_m7["capacity"]) / 9.0
        intercept = ext_m7["capacity"] - slope * -7.0
        return slope, intercept

    def _iso_hspf_extended_frost_intersection_temp(
        self,
        resolved: dict,
        load_line: tuple
    ) -> float:
        load_slope, load_intercept = load_line
        capacity_slope, capacity_intercept = self._iso_hspf_extended_frost_line(
            resolved
        )
        denominator = load_slope - capacity_slope
        if denominator == 0:
            raise ValueError(
                "ISO 16358-2 HSPF load line and extended capacity line are parallel."
            )
        return (capacity_intercept - load_intercept) / denominator

    def _iso_hspf_formula50_full_extended_frost_power(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        load_line: tuple
    ) -> dict:
        # ISO 16358-2 Formula 50 (frost full→extended):
        #   COP_fe,f(tj) = COP_ext,f(tf)
        #                + (COP_ful,f(tg) - COP_ext,f(tf)) * (tj - tf) / (tg - tf)
        #   P_fe,f(tj)   = L_h(tj) / COP_fe,f(tj)
        # tg = intersection of load line with full-stage frost capacity curve.
        # tf = intersection of load line with extended frost capacity curve.
        # COP_ful,f(tg) uses the full-stage frost curves at tg.
        # COP_ext,f(tf) uses the extended frost curve (interpolated between
        # the -7°C and 2°C extended points) at tf.
        # The implementation below uses the algebraically equivalent
        #   cop_full + (cop_ext - cop_full) * (tj - tg) / (tf - tg)
        # so the numeric output is identical to the spec form.
        tg = self._iso_hspf_intersection_temp("full", resolved, True, load_line)
        tf = self._iso_hspf_extended_frost_intersection_temp(resolved, load_line)
        denominator = tf - tg
        if denominator == 0:
            raise ValueError(
                "ISO 16358-2 HSPF full and extended boundary temperatures are equal."
            )

        cop_ful_f_tg = self._iso_hspf_boundary_cop(tg, "full", resolved, True)
        ext_tf = self._iso_hspf_extended_frost_curve(tf, resolved)
        if ext_tf["power"] <= 0:
            raise ValueError("ISO 16358-2 HSPF extended boundary power must be positive.")
        cop_ext_f_tf = ext_tf["capacity"] / ext_tf["power"]
        cop_fe_f = cop_ful_f_tg + (
            (cop_ext_f_tf - cop_ful_f_tg) * (tj - tg) / denominator
        )
        if cop_fe_f <= 0:
            raise ValueError("ISO 16358-2 HSPF Formula 50 branch COP must be positive.")

        return {
            "P_fe": bl_h / cop_fe_f,
            "tg": tg,
            "tf": tf,
            "cop_ful_f_tg": cop_ful_f_tg,
            "cop_ext_f_tf": cop_ext_f_tf,
            "cop_fe_f": cop_fe_f,
        }

    def _iso_hspf_formula47_full_extended_non_frost_power(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        load_line: tuple
    ) -> dict:
        # ISO 16358-2 Formula 47 (non-frost full→extended):
        #   COP_fe(tj) = COP_ext(th)
        #              + (COP_ful(ta) - COP_ext(th)) * (tj - th) / (ta - th)
        #   P_fe(tj)   = L_h(tj) / COP_fe(tj)
        # ta = load/full-capacity intersection, th = load/extended-capacity
        # intersection.  Both endpoints use the non-frost stage curves.
        full_temp = self._iso_hspf_intersection_temp("full", resolved, False, load_line)
        # Extended non-frost endpoint: capacity/power read from the "ext"
        # stage non-frost curve at the load-line intersection temperature.
        ext_temp = self._iso_hspf_intersection_temp("ext", resolved, False, load_line)

        denominator = full_temp - ext_temp
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF full and extended boundary temperatures are equal.")

        cop_full = self._iso_hspf_boundary_cop(full_temp, "full", resolved, False)
        cop_ext = self._iso_hspf_boundary_cop(ext_temp, "ext", resolved, False)

        # COP is linear with temperature between ext_temp and full_temp
        cop_fe = cop_ext + (cop_full - cop_ext) * (tj - ext_temp) / denominator
        if cop_fe <= 0:
            raise ValueError("ISO 16358-2 HSPF Formula 47 branch COP must be positive.")

        pi_full = self._iso_hspf_capacity_curve(tj, "full", resolved, False)
        pi_ext = self._iso_hspf_capacity_curve(tj, "ext", resolved, False)
        if bl_h < pi_full - 1e-5 or bl_h > pi_ext + 1e-5:
            raise ValueError(f"Load {bl_h} is outside the full ({pi_full}) to extended ({pi_ext}) capacity range.")

        return {
            "P_fe": bl_h / cop_fe,
            "branch": "formula47_full_extended",
            "cop_full": cop_full,
            "cop_ext": cop_ext,
            "cop_fe": cop_fe,
            "full_temp": full_temp,
            "ext_temp": ext_temp,
        }

    def _iso_hspf_pair_power_by_boundary_cop(
        self,
        tj: float,
        bl_h: float,
        low_stage: str,
        high_stage: str,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
        low_temp = self._iso_hspf_intersection_temp(
            low_stage, resolved, frost, load_line
        )
        high_temp = self._iso_hspf_intersection_temp(
            high_stage, resolved, frost, load_line
        )
        denominator = low_temp - high_temp
        if denominator == 0:
            raise ValueError(
                "ISO 16358-2 HSPF branch boundary temperatures are equal."
            )

        cop_low = self._iso_hspf_boundary_cop(low_temp, low_stage, resolved, frost)
        cop_high = self._iso_hspf_boundary_cop(high_temp, high_stage, resolved, frost)
        cop_pair = cop_high + (cop_low - cop_high) * (tj - high_temp) / denominator
        if cop_pair <= 0:
            raise ValueError("ISO 16358-2 HSPF branch COP must be positive.")
        return bl_h / cop_pair
