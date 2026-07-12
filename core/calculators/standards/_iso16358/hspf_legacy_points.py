"""Legacy/simple ISO heating point resolution."""


class HSPFLegacyPointMixin:
    def _heating_points(self, measured_inputs: dict) -> list:
        default_temps = {"H1": 7.0, "H2": 2.0, "H3": -7.0}
        configured_temps = self.config.get("heating_test_temperatures", default_temps)
        points = []

        for key, data in measured_inputs.items():
            if not isinstance(data, dict):
                continue

            if "capacity" not in data or "power" not in data:
                continue

            temp = data.get("temp")
            if temp is None:
                temp = data.get("temp_c")
            if temp is None:
                temp = configured_temps.get(key)
            if temp is None:
                continue

            points.append((float(temp), float(data["capacity"]), float(data["power"])))

        points.sort(key=lambda x: x[0])
        if len(points) < 2:
            raise ValueError("HSPF Phase 1 requires at least two heating points.")

        return points

    def interpolate_heating(self, tj: float, measured_inputs: dict) -> dict:
        points = self._heating_points(measured_inputs)

        if tj <= points[0][0]:
            lower, upper = points[0], points[1]
        elif tj >= points[-1][0]:
            lower, upper = points[-2], points[-1]
        else:
            selected_interval = None
            for i in range(len(points) - 1):
                candidate_lower = points[i]
                candidate_upper = points[i + 1]
                if candidate_lower[0] <= tj <= candidate_upper[0]:
                    selected_interval = (candidate_lower, candidate_upper)
                    break
            lower, upper = selected_interval or (points[0], points[1])

        t1, c1, p1 = lower
        t2, c2, p2 = upper

        if t2 == t1:
            raise ValueError("Heating point temperatures cannot be equal.")

        capacity = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
        power = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
        return {"capacity": capacity, "power": power}

    def calc_auxiliary_heat(
        self,
        load: float,
        available_capacity: float,
        hours: float,
        aux_cop: float = 1.0
    ) -> dict:
        # ISO 16358-2 HSPF Phase 1 assumes all capacity shortage is covered by make-up heat.
        # Auxiliary capacity limiting is intentionally not modeled here.
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        auxiliary_heat = max(0.0, load - available_capacity)
        auxiliary_energy = auxiliary_heat * hours / aux_cop
        return {
            "auxiliary_heat": auxiliary_heat,
            "auxiliary_energy": auxiliary_energy
        }

    def _heating_stage_points(self, measured_inputs: dict) -> dict:
        stage_points = {"high": [], "half": [], "min": []}
        for key, data in measured_inputs.items():
            if not isinstance(data, dict):
                continue
            if "capacity" not in data or "power" not in data:
                continue

            key_lower = key.lower()
            if "half" in key_lower:
                stage = "half"
            elif "min" in key_lower:
                stage = "min"
            elif (
                "full" in key_lower
                or "max" in key_lower
                or "defrost" in key_lower
            ):
                stage = "high"
            else:
                continue

            temp = data.get("temp")
            if temp is None:
                temp = data.get("temp_c")
            if temp is None:
                continue

            stage_points[stage].append((
                float(temp),
                float(data["capacity"]),
                float(data["power"]),
            ))

        for points in stage_points.values():
            points.sort(key=lambda x: x[0])
        return stage_points

    def _has_variable_heating_points(self, measured_inputs: dict) -> bool:
        stage_points = self._heating_stage_points(measured_inputs)
        return (
            len(stage_points["high"]) >= 3
            and len(stage_points["half"]) >= 1
            and len(stage_points["min"]) >= 1
        )

    def _point_at_temp(self, points: list, target_temp: float, label: str) -> tuple:
        for temp, capacity, power in points:
            if temp == target_temp:
                return temp, capacity, power
        raise ValueError(f"Missing heating {label} point at {target_temp}C.")

    def _linear_heating_point(
        self,
        tj: float,
        lower_point: tuple,
        upper_point: tuple
    ) -> dict:
        t1, c1, p1 = lower_point
        t2, c2, p2 = upper_point
        if t2 == t1:
            raise ValueError("Heating point temperatures cannot be equal.")

        capacity = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
        power = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
        return {"capacity": capacity, "power": power}
