"""KS C 9306 CSPF interpolation and load-line intersection."""


class KSCSPFPerformanceMixin:
    def _interpolate_ks_cspf(self, tj: float, resolved_points: dict) -> dict:
        """KS CSPF용 부하 조건별 온도 보간.

        ``{temp}_{load_type}`` 포맷의 KS resolved point를 load_type 별로
        묶고, tj 위치에 대해 선형 보간/외삽한 capacity/power를 돌려준다.
        """
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
            points.sort(key=lambda x: x[0])
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
                t1 = c1 = p1 = t2 = c2 = p2 = None
                for i in range(len(points) - 1):
                    ta, ca, pa = points[i]
                    tb, cb, pb = points[i + 1]
                    if ta <= tj <= tb:
                        t1, c1, p1, t2, c2, p2 = ta, ca, pa, tb, cb, pb
                        break
                if t1 is None:
                    continue

            c_tj = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
            p_tj = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
            interpolated[load_type] = {"capacity": c_tj, "power": p_tj}

        return interpolated

    def _ks_cspf_performance_line(self, resolved_points: dict, load_type: str) -> tuple:
        points = []
        for point_key, data in resolved_points.items():
            parts = point_key.split("_")
            if len(parts) != 2 or parts[1] != load_type:
                continue
            points.append((float(parts[0]), data["capacity"], data["power"]))

        points.sort(key=lambda x: x[0])
        if len(points) < 2:
            return None

        t1, c1, p1 = points[0]
        t2, c2, p2 = points[-1]
        if t2 == t1:
            return None

        capacity_slope = (c2 - c1) / (t2 - t1)
        capacity_intercept = c1 - capacity_slope * t1
        power_slope = (p2 - p1) / (t2 - t1)
        power_intercept = p1 - power_slope * t1
        return capacity_slope, capacity_intercept, power_slope, power_intercept

    def _ks_cspf_intersection_power(
        self,
        tj: float,
        L_c_ref: float,
        resolved_points: dict,
        lower_type: str,
        upper_type: str,
        t_100_load: float,
        t_0_load: float,
    ) -> float:
        lower_line = self._ks_cspf_performance_line(resolved_points, lower_type)
        upper_line = self._ks_cspf_performance_line(resolved_points, upper_type)
        if lower_line is None or upper_line is None:
            return None

        load_slope = L_c_ref / (t_100_load - t_0_load)
        load_intercept = -load_slope * t_0_load

        def intersection_temperature(line):
            capacity_slope, capacity_intercept, _, _ = line
            denominator = load_slope - capacity_slope
            if denominator == 0:
                return None
            return (capacity_intercept - load_intercept) / denominator

        def power_at(line, temp):
            _, _, power_slope, power_intercept = line
            return power_slope * temp + power_intercept

        t_lower = intersection_temperature(lower_line)
        t_upper = intersection_temperature(upper_line)
        if t_lower is None or t_upper is None or t_upper == t_lower:
            return None

        p_lower = power_at(lower_line, t_lower)
        p_upper = power_at(upper_line, t_upper)
        return p_upper - ((p_upper - p_lower) / (t_upper - t_lower)) * (t_upper - tj)
