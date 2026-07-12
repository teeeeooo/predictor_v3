"""ISO 16358-2 common point normalization and resolution."""


class HSPFCommonPointMixin:
    def _iso_hspf_normalize_common_points(self, measured_inputs: dict) -> dict:
        points = {}
        for key, value in measured_inputs.items():
            if not (
                isinstance(value, dict)
                and "capacity" in value
                and "power" in value
            ):
                continue
            capacity = value["capacity"]
            power = value["power"]
            if not isinstance(capacity, (int, float)) or capacity <= 0:
                raise ValueError(
                    f"Measured point '{key}' capacity must be a positive number."
                )
            if not isinstance(power, (int, float)) or power <= 0:
                raise ValueError(
                    f"Measured point '{key}' power must be a positive number."
                )
            points[key] = {
                "capacity": float(capacity),
                "power": float(power),
            }

        for required_key in ("7_full", "7_half"):
            if required_key not in points:
                raise ValueError(
                    f"ISO 16358-2 HSPF requires '{required_key}' measured inputs."
                )
        return points

    def _iso_hspf_point_on_minus7_to_7_line(
        self,
        resolved: dict,
        stage: str,
        temp: float = 2.0
    ) -> dict:
        key_7 = f"7_{stage}"
        key_m7 = f"-7_{stage}"
        return {
            "capacity": resolved[key_m7]["capacity"]
            + (resolved[key_7]["capacity"] - resolved[key_m7]["capacity"])
            * (temp + 7.0)
            / 14.0,
            "power": resolved[key_m7]["power"]
            + (resolved[key_7]["power"] - resolved[key_m7]["power"])
            * (temp + 7.0)
            / 14.0,
        }

    def _iso_hspf_resolve_common_points(
        self,
        points: dict,
        hspf_cfg: dict
    ) -> tuple:
        resolved = {key: dict(value) for key, value in points.items()}
        active_stages = ["full", "half"]
        if "7_min" in resolved:
            active_stages.append("min")

        minus7_capacity_factor, minus7_power_factor = (
            self._iso_hspf_minus7_fallback_factors(hspf_cfg)
        )
        for stage in active_stages:
            key_7 = f"7_{stage}"
            key_m7 = f"-7_{stage}"
            if key_m7 not in resolved:
                resolved[key_m7] = {
                    "capacity": resolved[key_7]["capacity"] * minus7_capacity_factor,
                    "power": resolved[key_7]["power"] * minus7_power_factor,
                }

        for stage in active_stages:
            calculated_2 = self._iso_hspf_point_on_minus7_to_7_line(
                resolved, stage
            )
            measured_2 = resolved.get(f"2_{stage}")
            if measured_2 is not None:
                resolved[f"2_{stage}_f"] = dict(measured_2)
            else:
                resolved[f"2_{stage}_f"] = dict(calculated_2)
            resolved[f"2_{stage}"] = calculated_2

        return resolved, active_stages
