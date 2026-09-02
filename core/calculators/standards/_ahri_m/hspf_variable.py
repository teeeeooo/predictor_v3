"""AHRI 210/240-2017 Appendix M variable-speed Region IV HSPF engine."""

from __future__ import annotations

from collections.abc import Mapping

from .numeric import linear_value, round_nearest_005, safe_div

_REQUIRED = ("H01", "H11", "H1N", "H2V", "H32")
_OPTIONAL = ("H12", "H22")
_BTU_PER_WH = 3.413


class AppendixMHspfEngine:
    def __init__(self, config: Mapping[str, object]) -> None:
        self.config = config
        region = config["region_iv"]
        self.bin_temps = tuple(float(value) for value in region["bin_temps_f"])
        self.bin_fractions = tuple(float(value) for value in region["fractional_bin_hours"])
        if len(self.bin_temps) != len(self.bin_fractions):
            raise ValueError("Invalid Appendix M HSPF bin table")
        self.tod = float(region["outdoor_design_temp_f"])
        self.c = float(region["building_load_factor"])
        self.hlh = float(region["heating_load_hours"])
        constants = config["constants"]
        self.csf = float(constants["split_capacity_slope_factor"])
        self.psf = float(constants["power_slope_factor"])
        self.dhr_values = tuple(float(value) for value in constants["standardized_dhr_btu_per_h"])
        self.cd_default = float(config["defaults"]["c_d_heating"])

    def calculate(
        self,
        test_points: Mapping[str, object],
        *,
        h1n_same_speed_as_h32: bool = False,
        c_d_heating: float | None = None,
        t_off: float | None = None,
        t_on: float | None = None,
        demand_defrost: bool = False,
        defrost_test_minutes: float | None = None,
        defrost_max_minutes: float | None = None,
    ) -> dict:
        points = self._normalize_points(test_points)
        cd = self.cd_default if c_d_heating is None else float(c_d_heating)
        if not 0.0 <= cd < 1.0:
            raise ValueError("c_d_heating must satisfy 0 <= CDh < 1")
        f_def = self._demand_defrost_factor(
            demand_defrost=demand_defrost,
            test_minutes=defrost_test_minutes,
            max_minutes=defrost_max_minutes,
        )
        if (t_off is None) != (t_on is None):
            raise ValueError("t_off and t_on must both be supplied or both be omitted")
        if t_off is not None and float(t_on) < float(t_off):
            raise ValueError("t_on must be >= t_off")

        h01, h11, h1n, h2v, h32 = (points[key] for key in _REQUIRED)
        dhr_min_raw = h1n[0] * (65.0 - self.tod) / 60.0
        dhr_max_raw = 2.0 * dhr_min_raw
        dhr_min = self._nearest_dhr(dhr_min_raw)
        dhr_max = self._nearest_dhr(dhr_max_raw)
        h47_full, h12_source = self._full_47(points, h1n_same_speed_as_h32)
        h35_full, h22_source = self._full_35(points, h47_full)

        def q_min(t: float) -> float:
            return linear_value(t, 47.0, h11[0], 62.0, h01[0])

        def p_min(t: float) -> float:
            return linear_value(t, 47.0, h11[1], 62.0, h01[1])

        def q_full(t: float) -> float:
            if t >= 45.0 or t <= 17.0:
                return linear_value(t, 17.0, h32[0], 47.0, h47_full[0])
            return linear_value(t, 17.0, h32[0], 35.0, h35_full[0])

        def p_full(t: float) -> float:
            if t >= 45.0 or t <= 17.0:
                return linear_value(t, 17.0, h32[1], 47.0, h47_full[1])
            return linear_value(t, 17.0, h32[1], 35.0, h35_full[1])

        q_min_35, p_min_35 = q_min(35.0), p_min(35.0)
        nq = safe_div(h2v[0] - q_min_35, h35_full[0] - q_min_35, label="HSPF NQ")
        ne = safe_div(h2v[1] - p_min_35, h35_full[1] - p_min_35, label="HSPF NE")
        self._validate_fraction("NQ", nq)
        self._validate_fraction("NE", ne)
        mq = ((h01[0] - h11[0]) / 15.0) * (1.0 - nq) + nq * ((h35_full[0] - h32[0]) / 18.0)
        me = ((h01[1] - h11[1]) / 15.0) * (1.0 - ne) + ne * ((h35_full[1] - h32[1]) / 18.0)

        def q_int(t: float) -> float:
            return h2v[0] + mq * (t - 35.0)

        def p_int(t: float) -> float:
            return h2v[1] + me * (t - 35.0)

        def building_load(t: float) -> float:
            return (65.0 - t) / (65.0 - self.tod) * self.c * dhr_min

        rows = []
        total_load = total_comp = total_resistance = 0.0
        for temp, fraction in zip(self.bin_temps, self.bin_fractions):
            bl = building_load(temp)
            qm, pm = q_min(temp), p_min(temp)
            qi, pi = q_int(temp), p_int(temp)
            qf, pf = q_full(temp), p_full(temp)
            delta = self._cutout_delta(temp, t_off=t_off, t_on=t_on)
            if bl <= qm:
                x = safe_div(bl, qm, label="HSPF load factor")
                plf = 1.0 - cd * (1.0 - x)
                comp = safe_div(x * pm * delta, plf, label="HSPF PLF") * fraction
                resistance = bl * (1.0 - delta) / _BTU_PER_WH * fraction
                cop_bin = safe_div(qm, _BTU_PER_WH * pm, label="HSPF minimum COP")
                case = "Case I"
            elif bl < qf:
                cop_min = safe_div(qm, _BTU_PER_WH * pm, label="HSPF minimum COP")
                cop_int = safe_div(qi, _BTU_PER_WH * pi, label="HSPF intermediate COP")
                cop_full = safe_div(qf, _BTU_PER_WH * pf, label="HSPF full COP")
                if bl < qi:
                    cop_bin = cop_min + safe_div(cop_int - cop_min, qi - qm, label="HSPF low-int COP slope") * (bl - qm)
                else:
                    cop_bin = cop_int + safe_div(cop_full - cop_int, qf - qi, label="HSPF int-full COP slope") * (bl - qi)
                if cop_bin <= 0:
                    raise ValueError("Appendix M HSPF interpolated COP must be positive")
                comp = bl / (_BTU_PER_WH * cop_bin) * delta * fraction
                resistance = bl * (1.0 - delta) / _BTU_PER_WH * fraction
                case = "Case II"
            else:
                cop_bin = safe_div(qf, _BTU_PER_WH * pf, label="HSPF full COP")
                comp = pf * delta * fraction
                resistance = (bl - qf * delta) / _BTU_PER_WH * fraction
                case = "Case III"
            load_contrib = bl * fraction
            total_load += load_contrib
            total_comp += comp
            total_resistance += resistance
            rows.append({
                "tj": temp, "hours": fraction, "operating_case": case,
                "building_load": bl, "q_low": qm, "q_int": qi, "q_full": qf,
                "cop_bin": cop_bin, "cutout_delta": delta,
                "q_comp": max(load_contrib - resistance * _BTU_PER_WH, 0.0),
                "e_comp": comp, "q_aux": resistance * _BTU_PER_WH,
                "e_aux": resistance, "q_total": load_contrib,
                "e_total": comp + resistance,
            })
        raw_base = safe_div(total_load, total_comp + total_resistance, label="HSPF seasonal ratio")
        raw = raw_base * f_def
        published = round_nearest_005(raw)
        return {
            "HSPF": published, "raw_hspf": raw, "published_hspf": published,
            "region": "IV", "dhr_min_raw": dhr_min_raw, "dhr_min_standardized": dhr_min,
            "dhr_max_raw": dhr_max_raw, "dhr_max_standardized": dhr_max,
            "f_def": f_def, "seasonal_heating_load_numerator": total_load,
            "seasonal_compressor_energy_denominator": total_comp,
            "seasonal_resistance_energy_denominator": total_resistance,
            "nq": nq, "ne": ne, "mq": mq, "me": me,
            "bin_details": rows,
            "summary": {"metadata": {"standard_method": "appendix_m_2017", "compressor_type": "variable_speed", "rating_dhr": "minimum", "h12_source": h12_source, "h22_source": h22_source}},
        }

    def _full_47(self, points, same_speed: bool):
        if "H12" in points:
            return points["H12"], "tested"
        if same_speed:
            return points["H1N"], "h1n_same_speed_as_h32"
        h32 = points["H32"]
        return (h32[0] * (1.0 + 30.0 * self.csf), h32[1] * (1.0 + 30.0 * self.psf)), "calculated_from_h32"

    def _full_35(self, points, h47_full):
        if "H22" in points:
            return points["H22"], "tested"
        h32 = points["H32"]
        return (0.90 * (h32[0] + 0.6 * (h47_full[0] - h32[0])), 0.985 * (h32[1] + 0.6 * (h47_full[1] - h32[1]))), "appendix_m_fallback"

    @staticmethod
    def _demand_defrost_factor(
        *,
        demand_defrost: bool,
        test_minutes: float | None,
        max_minutes: float | None,
    ) -> float:
        """AHRI 210/240-2017 Eq. 11.129 through 11.132."""
        if not demand_defrost:
            if test_minutes is not None or max_minutes is not None:
                raise ValueError(
                    "defrost interval inputs require demand_defrost=True"
                )
            return 1.0
        if test_minutes is None or max_minutes is None:
            raise ValueError(
                "demand defrost requires defrost_test_minutes and defrost_max_minutes"
            )
        test = max(float(test_minutes), 90.0)
        maximum = min(float(max_minutes), 720.0)
        if maximum <= 90.0:
            raise ValueError("defrost_max_minutes must resolve above 90 minutes")
        if test > maximum:
            raise ValueError("defrost_test_minutes must not exceed defrost_max_minutes")
        return 1.0 + 0.03 * (1.0 - (test - 90.0) / (maximum - 90.0))

    @staticmethod
    def _cutout_delta(temp: float, *, t_off: float | None, t_on: float | None) -> float:
        if t_off is None:
            return 1.0
        if temp <= float(t_off):
            return 0.0
        if temp <= float(t_on):
            return 0.5
        return 1.0

    def _nearest_dhr(self, value: float) -> float:
        return min(self.dhr_values, key=lambda candidate: (abs(candidate - value), -candidate))

    @staticmethod
    def _validate_fraction(label: str, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Appendix M HSPF {label} must be within [0, 1]")

    @staticmethod
    def _normalize_points(test_points: Mapping[str, object]) -> dict[str, tuple[float, float]]:
        keys = set(test_points)
        if not set(_REQUIRED) <= keys or not keys <= set(_REQUIRED + _OPTIONAL):
            raise ValueError(f"Appendix M HSPF requires {_REQUIRED} with optional {_OPTIONAL}")
        result = {}
        for key, value in test_points.items():
            if not isinstance(value, (tuple, list)) or len(value) != 2:
                raise ValueError(f"{key} must be a (capacity, power) pair")
            capacity, power = float(value[0]), float(value[1])
            if capacity <= 0 or power <= 0:
                raise ValueError(f"{key} capacity and power must be > 0")
            result[key] = (capacity, power)
        return result
