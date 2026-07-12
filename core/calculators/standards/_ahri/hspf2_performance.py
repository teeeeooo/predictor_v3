"""Pure variable-capacity HSPF2 performance primitives."""

from decimal import Decimal, ROUND_HALF_UP

from .numeric import linear_interpolate, safe_div


class HSPF2VariablePerformance:
    @staticmethod
    def safe_div(num: float, den: float, fallback: float = 0.0) -> float:
        return safe_div(num, den, fallback)

    def linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        return linear_interpolate(x, x1, y1, x2, y2)

    @staticmethod
    def round_nearest_025(value: float) -> float:
        step = Decimal("0.025")
        rounded_units = (Decimal(str(value)) / step).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        return float(rounded_units * step)

    def low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_low = q_h1_low + (q_h0_low - q_h1_low) * self.safe_div(temp_f - 47, 62 - 47)
        p_low = p_h1_low + (p_h0_low - p_h1_low) * self.safe_div(temp_f - 47, 62 - 47)
        return max(0.0, q_low), max(0.0, p_low)

    def canonical_low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        point_temps = {"H11": 47, "H2V": 35, "H31": 17}
        points = []
        for key in ("H11", "H2V", "H31"):
            value = low_points.get(key)
            if value is None:
                continue
            capacity, power = value
            if capacity <= 0 or power <= 0:
                raise ValueError(
                    f"Invalid canonical low-speed test point {key}: capacity={capacity}, power={power}"
                )
            points.append((point_temps[key], capacity, power))
        if len(points) < 2:
            return None, None
        points.sort(reverse=True)
        for idx in range(len(points) - 1):
            high_temp, q_high, p_high = points[idx]
            low_temp, q_low, p_low = points[idx + 1]
            if high_temp >= temp_f >= low_temp:
                return max(0.0, self.linear(temp_f, high_temp, q_high, low_temp, q_low)), max(
                    0.0, self.linear(temp_f, high_temp, p_high, low_temp, p_low)
                )
        if temp_f > points[0][0]:
            x1, q1, p1 = points[0]
            x2, q2, p2 = points[1]
        else:
            x1, q1, p1 = points[-2]
            x2, q2, p2 = points[-1]
        return max(0.0, self.linear(temp_f, x1, q1, x2, q2)), max(
            0.0, self.linear(temp_f, x1, p1, x2, p2)
        )

    def minimum_limited_low_capacity_power_at_temp(
        self,
        temp_f: float,
        low_points: dict,
        h2int_point: tuple,
        int_point_at_temp: tuple,
    ) -> tuple:
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_h2_int, p_h2_int = h2int_point
        q_int, p_int = int_point_at_temp
        if temp_f >= 47:
            q_low = q_h1_low + (q_h0_low - q_h1_low) * self.safe_div(temp_f - 47, 62 - 47)
            p_low = p_h1_low + (p_h0_low - p_h1_low) * self.safe_div(temp_f - 47, 62 - 47)
        elif temp_f >= 35:
            q_low = q_h2_int + (q_h1_low - q_h2_int) * self.safe_div(temp_f - 35, 47 - 35)
            p_low = p_h2_int + (p_h1_low - p_h2_int) * self.safe_div(temp_f - 35, 47 - 35)
        else:
            q_low = q_int
            p_low = p_int
        return max(0.0, q_low), max(0.0, p_low)

    def full_capacity_power_at_temp(
        self,
        temp_f: float,
        full_points: dict,
        nominal_point: tuple,
        h4_point: tuple = None,
    ) -> tuple:
        q_h1_full, p_h1_full = full_points["H12"]
        q_h1_nom, p_h1_nom = nominal_point
        q_h2_full, p_h2_full = full_points["H22"]
        q_h3_full, p_h3_full = full_points["H32"]
        if temp_f >= 45:
            q_base = self.linear(temp_f, 17, q_h3_full, 47, q_h1_full)
            p_base = self.linear(temp_f, 17, p_h3_full, 47, p_h1_full)
            q_full = q_base * self.safe_div(q_h1_nom, q_h1_full, 1.0)
            p_full = p_base * self.safe_div(p_h1_nom, p_h1_full, 1.0)
        elif temp_f > 17:
            q_full = self.linear(temp_f, 17, q_h3_full, 35, q_h2_full)
            p_full = self.linear(temp_f, 17, p_h3_full, 35, p_h2_full)
        elif h4_point is not None and temp_f > 5:
            q_h4_full, p_h4_full = h4_point
            q_full = q_h4_full + (q_h3_full - q_h4_full) * self.safe_div(temp_f - 5, 17 - 5)
            p_full = p_h4_full + (p_h3_full - p_h4_full) * self.safe_div(temp_f - 5, 17 - 5)
        elif h4_point is not None and temp_f <= 5:
            q_h4_full, p_h4_full = h4_point
            q_full = q_h4_full + (q_h1_full - q_h3_full) * self.safe_div(temp_f - 5, 47 - 17)
            p_full = p_h4_full + (p_h1_full - p_h3_full) * self.safe_div(temp_f - 5, 47 - 17)
        else:
            q_full = self.linear(temp_f, 17, q_h3_full, 47, q_h1_full)
            p_full = self.linear(temp_f, 17, p_h3_full, 47, p_h1_full)
        return max(0.0, q_full), max(0.0, p_full)

    def intermediate_capacity_power_at_temp(
        self, temp_f: float, h2int_point: tuple, low_points: dict, full_points: dict
    ) -> tuple:
        q_h2_int, p_h2_int = h2int_point
        q_low_35, p_low_35 = self.low_capacity_power_at_temp(35, low_points)
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_h2_full, p_h2_full = full_points["H22"]
        q_h3_full, p_h3_full = full_points["H32"]
        n_hq = self.safe_div(q_h2_int - q_low_35, q_h2_full - q_low_35)
        n_he = self.safe_div(p_h2_int - p_low_35, p_h2_full - p_low_35)
        if not (0.0 <= n_hq <= 1.0 and 0.0 <= n_he <= 1.0):
            raise ValueError(
                "HSPF2 v3 AHRI path requires H2Int capacity/power between Low(35F) and H2Full: "
                f"N_Hq={n_hq}, N_HE={n_he}"
            )
        m_hq = self.safe_div(q_h0_low - q_h1_low, 62 - 47) * (1.0 - n_hq) + self.safe_div(
            q_h2_full - q_h3_full, 35 - 17
        ) * n_hq
        m_he = self.safe_div(p_h0_low - p_h1_low, 62 - 47) * (1.0 - n_he) + self.safe_div(
            p_h2_full - p_h3_full, 35 - 17
        ) * n_he
        return max(0.0, q_h2_int + m_hq * (temp_f - 35)), max(
            0.0, p_h2_int + m_he * (temp_f - 35)
        ), {
            "method": "ahri_210_240_2026_eq_11_199_to_11_204",
            "N_Hq": n_hq,
            "N_HE": n_he,
            "M_Hq": m_hq,
            "M_HE": m_he,
            "q_low_35": q_low_35,
            "p_low_35": p_low_35,
        }

    @staticmethod
    def delta_at_bin(temp_f: float, cop: float, t_off: float, t_on: float) -> float:
        if temp_f <= t_off or cop < 1.0:
            return 0.0
        if temp_f <= t_on:
            return 0.5
        return 1.0

    def building_load(
        self, temp_f: float, q_h1_calc: float, c_vs: float, t_zl: float, t_od: float
    ) -> float:
        load = q_h1_calc * c_vs * self.safe_div(t_zl - temp_f, t_zl - t_od)
        return max(0.0, load)
