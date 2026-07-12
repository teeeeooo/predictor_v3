"""EN 14825 load lines, declared-point performance, and interpolation."""

from __future__ import annotations


class EN14825PerformanceCurve:
    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(
        self, x: float, x1: float, y1: float, x2: float, y2: float
    ) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def _interpolate_from_points(
        self,
        tj: float,
        points: list,
        value_key: str = "value",
        extrapolate_upper: bool = False,
    ) -> tuple:
        if not points:
            raise ValueError("Interpolation requires at least one point.")

        ordered = sorted(points, key=lambda point: point["temp_c"])
        if tj <= ordered[0]["temp_c"]:
            point = ordered[0]
            return point[value_key], f"clamped_to_{point.get('key', point['temp_c'])}"
        if tj >= ordered[-1]["temp_c"]:
            if extrapolate_upper and len(ordered) >= 2:
                low = ordered[-2]
                high = ordered[-1]
                value = self._linear(
                    tj,
                    low["temp_c"],
                    low[value_key],
                    high["temp_c"],
                    high[value_key],
                )
                return value, (
                    f"extrapolated_{low.get('key', low['temp_c'])}_"
                    f"{high.get('key', high['temp_c'])}"
                )
            point = ordered[-1]
            return point[value_key], f"clamped_to_{point.get('key', point['temp_c'])}"

        for index in range(len(ordered) - 1):
            low = ordered[index]
            high = ordered[index + 1]
            if low["temp_c"] <= tj <= high["temp_c"]:
                if tj == low["temp_c"]:
                    return low[value_key], f"direct_{low.get('key', low['temp_c'])}"
                if tj == high["temp_c"]:
                    return high[value_key], f"direct_{high.get('key', high['temp_c'])}"
                value = self._linear(
                    tj,
                    low["temp_c"],
                    low[value_key],
                    high["temp_c"],
                    high[value_key],
                )
                return value, (
                    f"linear_{low.get('key', low['temp_c'])}_"
                    f"{high.get('key', high['temp_c'])}"
                )
        raise ValueError(f"Interpolation failed at Tj={tj}")

    def _cooling_load_at_temp(
        self, tj: float, p_design_c: float, t_design_c: float
    ) -> float:
        if p_design_c <= 0:
            raise ValueError(
                f"p_design_c must be > 0 for SEER calculation: {p_design_c}"
            )
        if t_design_c == 16:
            raise ValueError(
                "t_design_c cannot be 16°C for SEER cooling load line."
            )
        return max(0.0, p_design_c * (tj - 16.0) / (t_design_c - 16.0))

    def _cooling_condition_load(
        self, condition_temp: float, p_design_c: float, t_design_c: float
    ) -> float:
        return self._cooling_load_at_temp(
            condition_temp, p_design_c, t_design_c
        )

    def _part_load_performance(
        self,
        capacity: float,
        power: float,
        load: float,
        cd: float,
        apply_degradation: bool = True,
    ) -> dict:
        if capacity <= 0 or power <= 0:
            raise ValueError(
                f"Invalid declared point: capacity={capacity}, power={power}"
            )
        if load < 0:
            raise ValueError(f"Declared point load must not be negative: {load}")

        full_load_efficiency = capacity / power
        if apply_degradation and capacity > load:
            cr = self._safe_div(load, capacity)
            degradation_factor = max(0.0, 1.0 - cd * (1.0 - cr))
            part_load_efficiency = full_load_efficiency * degradation_factor
        else:
            cr = 1.0
            part_load_efficiency = full_load_efficiency
            degradation_factor = 1.0
        return {
            "full_load_efficiency": full_load_efficiency,
            "part_load_efficiency": part_load_efficiency,
            "cr": cr,
            "degradation_factor": degradation_factor,
        }

    def _eer_pl_at_declared_point(
        self,
        capacity: float,
        power: float,
        load: float,
        cd: float,
        apply_degradation: bool = True,
    ) -> dict:
        data = self._part_load_performance(
            capacity, power, load, cd, apply_degradation
        )
        return {
            "eer_dc": data["full_load_efficiency"],
            "eer_pl": data["part_load_efficiency"],
            "cr": data["cr"],
            "degradation_factor": data["degradation_factor"],
        }

    def _heating_part_load(
        self, tj: float, p_design_h: float, t_design_h: float
    ) -> float:
        if p_design_h <= 0:
            raise ValueError(
                f"p_design_h must be > 0 for SCOP calculation: {p_design_h}"
            )
        if t_design_h == 16:
            raise ValueError(
                "t_design_h cannot be 16°C for SCOP heating load line."
            )
        ph = p_design_h * (tj - 16.0) / (t_design_h - 16.0)
        return max(0.0, ph)

    def _scop_pl_at_declared_point(
        self, point: dict, load: float, cd: float
    ) -> dict:
        capacity = point["capacity"]
        load_gap_ratio = self._safe_div(capacity - load, load) if load > 0 else 0.0
        data = self._part_load_performance(
            capacity,
            point["power"],
            load,
            cd,
            apply_degradation=(capacity > load and load_gap_ratio > 0.10),
        )
        return {
            "cop_dc": data["full_load_efficiency"],
            "cop_pl": data["part_load_efficiency"],
            "cr": data["cr"],
            "degradation_factor": data["degradation_factor"],
        }
