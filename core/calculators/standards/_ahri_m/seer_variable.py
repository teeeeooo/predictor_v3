"""AHRI 210/240 Appendix M variable-speed SEER seasonal engine."""

from __future__ import annotations

from collections.abc import Mapping

from .numeric import lagrange_three, line_crossing, linear_value, round_nearest_005, safe_div

_REQUIRED_POINTS = ("A2", "B2", "EV", "B1", "F1")


class AppendixMSeerEngine:
    def __init__(self, config: Mapping[str, object]) -> None:
        self.config = config
        bin_data = config["bin_data"]
        self.bin_temps = tuple(float(value) for value in bin_data["bin_temps_f"])
        self.bin_fractions = tuple(float(value) for value in bin_data["fractional_bin_hours"])
        if len(self.bin_temps) != len(self.bin_fractions) or abs(sum(self.bin_fractions) - 1.0) > 1e-12:
            raise ValueError("Invalid Appendix M SEER bin table")
        constants = config["constants"]
        self.sf = float(constants["sizing_factor"])
        self.cd_default = float(config["defaults"]["c_d_cooling"])

    def calculate(self, test_points: Mapping[str, object], *, c_d_cooling: float | None = None) -> dict:
        points = self._normalize_points(test_points)
        cd = self.cd_default if c_d_cooling is None else float(c_d_cooling)
        if not 0.0 <= cd < 1.0:
            raise ValueError("c_d_cooling must satisfy 0 <= CDc < 1")
        a2, b2, ev, b1, f1 = (points[key] for key in _REQUIRED_POINTS)

        def building_load(t: float) -> float:
            return (t - 65.0) / 30.0 * (a2[0] / self.sf)

        def q_min(t: float) -> float:
            return linear_value(t, 67.0, f1[0], 82.0, b1[0])

        def p_min(t: float) -> float:
            return linear_value(t, 67.0, f1[1], 82.0, b1[1])

        def q_full(t: float) -> float:
            return linear_value(t, 82.0, b2[0], 95.0, a2[0])

        def p_full(t: float) -> float:
            return linear_value(t, 82.0, b2[1], 95.0, a2[1])

        q_min_87, p_min_87 = q_min(87.0), p_min(87.0)
        q_full_87, p_full_87 = q_full(87.0), p_full(87.0)
        nq = safe_div(ev[0] - q_min_87, q_full_87 - q_min_87, label="SEER NQ")
        ne = safe_div(ev[1] - p_min_87, p_full_87 - p_min_87, label="SEER NE")
        self._validate_fraction("NQ", nq)
        self._validate_fraction("NE", ne)
        min_q_slope = (b1[0] - f1[0]) / 15.0
        min_p_slope = (b1[1] - f1[1]) / 15.0
        full_q_slope = (a2[0] - b2[0]) / 13.0
        full_p_slope = (a2[1] - b2[1]) / 13.0
        mq = min_q_slope * (1.0 - nq) + full_q_slope * nq
        me = min_p_slope * (1.0 - ne) + full_p_slope * ne

        def q_int(t: float) -> float:
            return ev[0] + mq * (t - 87.0)

        def p_int(t: float) -> float:
            return ev[1] + me * (t - 87.0)

        t1 = line_crossing(q_min, building_load, label="SEER T1")
        tv = line_crossing(q_int, building_load, label="SEER Tv")
        t2 = line_crossing(q_full, building_load, label="SEER T2")
        anchors = (
            (t1, safe_div(q_min(t1), p_min(t1), label="minimum EER")),
            (tv, safe_div(q_int(tv), p_int(tv), label="intermediate EER")),
            (t2, safe_div(q_full(t2), p_full(t2), label="full EER")),
        )
        rows = []
        total_q = 0.0
        total_e = 0.0
        for index, (temp, fraction) in enumerate(zip(self.bin_temps, self.bin_fractions), start=1):
            bl = building_load(temp)
            ql, pl = q_min(temp), p_min(temp)
            qi, pi = q_int(temp), p_int(temp)
            qf, pf = q_full(temp), p_full(temp)
            if bl <= ql:
                x = safe_div(bl, ql, label="SEER load factor")
                plf = 1.0 - cd * (1.0 - x)
                q_contrib = bl * fraction
                e_contrib = safe_div(x * pl, plf, label="SEER PLF") * fraction
                eer_bin = safe_div(q_contrib, e_contrib, label="SEER Case I EER") if e_contrib else 0.0
                case = "Case I"
            elif bl < qf:
                eer_bin = lagrange_three(temp, anchors)
                if eer_bin <= 0:
                    raise ValueError("Appendix M SEER quadratic EER must be positive")
                q_contrib = bl * fraction
                e_contrib = bl / eer_bin * fraction
                case = "Case II"
            else:
                q_contrib = qf * fraction
                e_contrib = pf * fraction
                eer_bin = safe_div(qf, pf, label="SEER full EER")
                case = "Case III"
            total_q += q_contrib
            total_e += e_contrib
            rows.append({
                "bin_no": index, "tj": temp, "hours": fraction, "operating_case": case,
                "building_load": bl, "q_low": ql, "q_int": qi, "q_full": qf,
                "eer_low": safe_div(ql, pl, label="SEER low EER"),
                "eer_int": safe_div(qi, pi, label="SEER intermediate point EER"),
                "eer_full": safe_div(qf, pf, label="SEER full EER"),
                "eer_bin": eer_bin, "q_total": q_contrib, "e_total": e_contrib,
            })
        raw = safe_div(total_q, total_e, label="SEER seasonal ratio")
        published = round_nearest_005(raw)
        return {
            "SEER": published, "raw_seer": raw, "published_seer": published,
            "seasonal_cooling_numerator": total_q,
            "seasonal_energy_denominator": total_e,
            "nq": nq, "ne": ne, "mq": mq, "me": me,
            "t1": t1, "tv": tv, "t2": t2,
            "quadratic_eer_anchors": anchors,
            "bin_details": rows,
            "summary": {"metadata": {"standard_method": "appendix_m", "compressor_type": "variable_speed"}},
        }

    @staticmethod
    def _validate_fraction(label: str, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Appendix M SEER {label} must be within [0, 1]")

    @staticmethod
    def _normalize_points(test_points: Mapping[str, object]) -> dict[str, tuple[float, float]]:
        if set(test_points) != set(_REQUIRED_POINTS):
            raise ValueError(f"Appendix M SEER requires exactly {_REQUIRED_POINTS}")
        result = {}
        for key in _REQUIRED_POINTS:
            value = test_points[key]
            if not isinstance(value, (tuple, list)) or len(value) != 2:
                raise ValueError(f"{key} must be a (capacity, power) pair")
            capacity, power = float(value[0]), float(value[1])
            if capacity <= 0 or power <= 0:
                raise ValueError(f"{key} capacity and power must be > 0")
            result[key] = (capacity, power)
        return result
