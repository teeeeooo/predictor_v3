"""ISO 16358-1 CSPF interpolation and boundary performance."""


class CSPFPerformanceMixin:
    def interpolate(self, tj: float, resolved_points: dict) -> dict:
        grouped = {}
        for point_key, data in resolved_points.items():
            parts = point_key.split("_")
            if len(parts) != 2:
                continue
            try:
                temp = float(parts[0])
                load_type = parts[1]
            except ValueError:
                continue
            grouped.setdefault(load_type, []).append(
                (temp, data["capacity"], data["power"])
            )

        interpolated = {}
        for load_type, points in grouped.items():
            points.sort(key=lambda item: item[0])
            if len(points) == 1:
                interpolated[load_type] = {
                    "capacity": points[0][1],
                    "power": points[0][2],
                }
                continue

            if tj <= points[0][0]:
                t1, c1, p1 = points[0]
                t2, c2, p2 = points[1]
            elif tj >= points[-1][0]:
                t1, c1, p1 = points[-2]
                t2, c2, p2 = points[-1]
            else:
                for i in range(len(points) - 1):
                    t1, c1, p1 = points[i]
                    t2, c2, p2 = points[i + 1]
                    if t1 <= tj <= t2:
                        break
                else:
                    continue

            c_tj = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
            p_tj = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
            interpolated[load_type] = {"capacity": c_tj, "power": p_tj}

        return interpolated

    def _iso_boundary_temperature(
        self,
        ref_capacity: float,
        capacity_35: float,
        capacity_29: float,
    ) -> float:
        dt = self.t_100_load - self.t_0_load
        denominator = 6 * ref_capacity + (capacity_29 - capacity_35) * dt
        if denominator == 0:
            raise ValueError("Cannot calculate ISO boundary EER temperature.")
        boundary_temp = (
            6 * ref_capacity * self.t_0_load
            + 6 * capacity_35 * dt
            + 35 * (capacity_29 - capacity_35) * dt
        ) / denominator
        return self._round_iso_boundary_temperature(boundary_temp)

    def _iso_linear_29_35(self, value_35: float, value_29: float, tj: float) -> float:
        return value_35 + (value_29 - value_35) / (35 - 29) * (35 - tj)

    def _iso_boundary_eer(self, resolved_points: dict, load_type: str) -> tuple:
        point_35 = resolved_points.get(f"35_{load_type}")
        point_29 = resolved_points.get(f"29_{load_type}")
        if point_35 is None or point_29 is None:
            raise ValueError(
                f"ISO boundary EER requires 35_{load_type} and 29_{load_type}."
            )

        ref_point = resolved_points.get(self.reference_point)
        if ref_point is None:
            raise ValueError(
                f"Reference point '{self.reference_point}' not found for ISO boundary EER."
            )

        boundary_temp = self._iso_boundary_temperature(
            ref_point["capacity"],
            point_35["capacity"],
            point_29["capacity"],
        )
        capacity = self._iso_linear_29_35(
            point_35["capacity"], point_29["capacity"], boundary_temp
        )
        power = self._iso_linear_29_35(
            point_35["power"], point_29["power"], boundary_temp
        )
        if power <= 0:
            raise ValueError("ISO boundary EER power must be positive.")
        return boundary_temp, capacity / power

    def _iso_boundary_eer_t3_piecewise(
        self,
        resolved_points: dict,
        load_type: str,
        tj: float,
    ) -> tuple:
        if tj > 35.0:
            high_temp = 46.0
            low_temp = 35.0
        else:
            high_temp = 35.0
            low_temp = 29.0

        point_high = resolved_points.get(f"{int(high_temp)}_{load_type}")
        point_low = resolved_points.get(f"{int(low_temp)}_{load_type}")
        if point_high is None or point_low is None:
            raise ValueError(
                "T3 ISO boundary EER requires "
                f"{int(high_temp)}_{load_type} and {int(low_temp)}_{load_type}."
            )

        ref_point = resolved_points.get(self.reference_point)
        if ref_point is None:
            raise ValueError(
                f"Reference point '{self.reference_point}' not found for T3 ISO boundary EER."
            )

        load_dt = self.t_100_load - self.t_0_load
        segment_dt = high_temp - low_temp
        if load_dt == 0 or segment_dt == 0:
            raise ValueError("Cannot calculate T3 ISO boundary EER temperature.")

        load_slope = ref_point["capacity"] / load_dt
        load_intercept = -load_slope * self.t_0_load
        capacity_slope = (
            point_high["capacity"] - point_low["capacity"]
        ) / segment_dt
        capacity_intercept = point_high["capacity"] - capacity_slope * high_temp
        denominator = load_slope - capacity_slope
        if denominator == 0:
            return None

        boundary_temp = (capacity_intercept - load_intercept) / denominator
        boundary_temp = self._round_iso_boundary_temperature(boundary_temp)
        capacity = capacity_slope * boundary_temp + capacity_intercept
        power_slope = (point_high["power"] - point_low["power"]) / segment_dt
        power_intercept = point_high["power"] - power_slope * high_temp
        power = power_slope * boundary_temp + power_intercept
        if power <= 0:
            raise ValueError("T3 ISO boundary EER power must be positive.")
        return boundary_temp, capacity / power

    def _iso_boundary_eer_power(
        self,
        tj: float,
        load: float,
        resolved_points: dict,
        lower_type: str,
        upper_type: str,
    ) -> float:
        profile_cfg = self.config.get("cspf_test_profile", {})
        if profile_cfg.get("climate_profile") == "T3":
            if {lower_type, upper_type} not in ({"min", "half"}, {"half", "full"}):
                return None
            upper_boundary = self._iso_boundary_eer_t3_piecewise(
                resolved_points, upper_type, tj
            )
            lower_boundary = self._iso_boundary_eer_t3_piecewise(
                resolved_points, lower_type, tj
            )
            if upper_boundary is None or lower_boundary is None:
                return None
            t_upper, upper_eer = upper_boundary
            t_lower, lower_eer = lower_boundary
        else:
            if {lower_type, upper_type} != {"half", "full"}:
                return None
            t_upper, upper_eer = self._iso_boundary_eer(resolved_points, upper_type)
            t_lower, lower_eer = self._iso_boundary_eer(resolved_points, lower_type)

        if t_upper == t_lower:
            return None
        eer_tj = lower_eer + (upper_eer - lower_eer) / (t_upper - t_lower) * (
            tj - t_lower
        )
        if eer_tj <= 0:
            return None
        return load / eer_tj
