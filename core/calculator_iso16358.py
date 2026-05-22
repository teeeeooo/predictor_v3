"""ISO 16358 CSPF/HSPF common standard calculator."""

import json
import os
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


class ISO16358Calculator:
    """ISO 16358 common calculator, without KS or AS/NZS responsibilities."""

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.config.pop("_comment", None)

        self.t_100_load = self.config.get("t_100_load", 35.0)
        self.t_0_load = self.config.get("t_0_load", 20.0)
        self.Cd = self.config.get("Cd", 0.25)
        self.building_load_source = self.config.get("building_load_source", "measured")
        self.reference_point = self.config.get("reference_point", "35_full")
        self.power_interpolation_method = self.config.get(
            "power_interpolation_method", "capacity_linear"
        )
        self.iso_boundary_temperature_rounding = self.config.get(
            "iso_boundary_temperature_rounding", None
        )
        self.round_test_values = self.config.get("round_test_values", False)
        self.rounding_method = self.config.get("rounding_method", None)

        self.points_config = self.config.get("points", {})
        self.derived_rules = self.config.get("derived_rules", {})
        self.bin_hours = self.config.get("bin_hours", [])

    def _round_test_value(self, value: float) -> int:
        return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _prepare_measured_inputs(self, measured_inputs: dict) -> dict:
        if not self.round_test_values:
            return measured_inputs

        prepared = {}
        for point_key, point_data in measured_inputs.items():
            if not isinstance(point_data, dict):
                prepared[point_key] = point_data
                continue

            prepared[point_key] = {}
            for data_key, value in point_data.items():
                if data_key in ("capacity", "power"):
                    try:
                        prepared[point_key][data_key] = self._round_test_value(value)
                    except (InvalidOperation, ValueError, TypeError):
                        prepared[point_key][data_key] = value
                else:
                    prepared[point_key][data_key] = value

        return prepared

    def _round_iso_boundary_temperature(self, value: float) -> float:
        if self.iso_boundary_temperature_rounding is None:
            return value
        if self.iso_boundary_temperature_rounding == "excel_round_0":
            return float(
                Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        raise ValueError(
            "Unsupported iso_boundary_temperature_rounding: "
            f"{self.iso_boundary_temperature_rounding}."
        )

    def _has_cspf_test_profile(self) -> bool:
        return "cspf_test_profile" in self.config

    def _get_cspf_profile_cd(self) -> float:
        if "Cd" in self.config:
            return float(self.config["Cd"])
        profile = self.config.get("cspf_test_profile", {}).get("climate_profile")
        return 0.27 if profile == "T3" else 0.25

    def _get_active_load_levels(self) -> list:
        profile_cfg = self.config.get("cspf_test_profile", {})
        selection = profile_cfg.get("test_selection")
        if selection == "with_optional_test":
            return ["full", "half", "min"]
        return ["full", "half"]

    def _get_cspf_temperature_segments(self) -> list:
        profile = self.config.get("cspf_test_profile", {}).get("climate_profile")
        if profile == "T3":
            return [{"boundary": 35.0, "high": [46, 35], "low": [35, 29]}]
        return [{"boundary": None, "high": [35, 29]}]

    def _resolve_cspf_profile_points(self, measured: dict) -> dict:
        profile_cfg = self.config.get("cspf_test_profile", {})
        climate = profile_cfg.get("climate_profile")
        selection = profile_cfg.get("test_selection")

        resolved = {k: dict(v) if isinstance(v, dict) else v for k, v in measured.items()}

        def _set_point(key, cap, pwr):
            if key not in resolved:
                resolved[key] = {"capacity": cap, "power": pwr}

        if climate == "T1":
            _set_point(
                "29_full",
                resolved["35_full"]["capacity"] * 1.077,
                resolved["35_full"]["power"] * 0.914,
            )
            _set_point(
                "29_half",
                resolved["35_half"]["capacity"] * 1.077,
                resolved["35_half"]["power"] * 0.914,
            )
            if selection == "with_optional_test":
                _set_point(
                    "29_min",
                    resolved["35_min"]["capacity"] * 1.077,
                    resolved["35_min"]["power"] * 0.914,
                )
        elif climate == "T3":
            _set_point(
                "46_half",
                resolved["35_half"]["capacity"] * 0.859,
                resolved["35_half"]["power"] * 1.25,
            )
            _set_point(
                "29_full",
                resolved["35_full"]["capacity"] * 1.077,
                resolved["35_full"]["power"] * 0.914,
            )
            _set_point(
                "29_half",
                resolved["35_half"]["capacity"] * 1.077,
                resolved["35_half"]["power"] * 0.914,
            )
            if selection == "with_optional_test":
                _set_point(
                    "46_min",
                    resolved["35_min"]["capacity"] * 0.859,
                    resolved["35_min"]["power"] * 1.25,
                )
                _set_point(
                    "29_min",
                    resolved["35_min"]["capacity"] * 1.077,
                    resolved["35_min"]["power"] * 0.914,
                )

        return resolved

    def resolve_points(self, measured_inputs: dict) -> dict:
        if self._has_cspf_test_profile():
            return self._resolve_cspf_profile_points(measured_inputs)

        resolved = {}
        for point_key, point_type in self.points_config.items():
            if point_type != "measure":
                continue
            if point_key not in measured_inputs:
                raise ValueError(f"필수 측정값 누락: '{point_key}' 포인트 데이터가 없습니다.")

            point_data = measured_inputs[point_key]
            if not isinstance(point_data, dict):
                raise ValueError(
                    f"Invalid measured point '{point_key}': expected dict with capacity and power."
                )

            validated_point = dict(point_data)
            for numeric_key in ("capacity", "power"):
                if numeric_key not in point_data:
                    raise ValueError(
                        f"Invalid measured point '{point_key}': "
                        f"missing required field '{numeric_key}'."
                    )
                try:
                    numeric_value = float(point_data[numeric_key])
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Invalid measured point '{point_key}': {numeric_key} must be numeric."
                    ) from None
                if numeric_value <= 0:
                    raise ValueError(
                        f"Invalid measured point '{point_key}': {numeric_key} must be positive."
                    )
                validated_point[numeric_key] = numeric_value
            resolved[point_key] = validated_point

        for _ in range(len(self.points_config)):
            for point_key, point_type in self.points_config.items():
                if point_type != "default" or point_key in resolved:
                    continue
                rule = self.derived_rules.get(point_key)
                if not rule:
                    continue
                source_key = rule.get("source")
                if source_key not in resolved:
                    continue
                source_data = resolved[source_key]
                resolved[point_key] = {
                    "capacity": source_data["capacity"] * rule.get("capacity_factor", 1.0),
                    "power": source_data["power"] * rule.get("power_factor", 1.0),
                }

        unresolved = [
            k for k, t in self.points_config.items()
            if t == "default" and k not in resolved
        ]
        if unresolved:
            raise ValueError(
                f"해결되지 않은 default 포인트: {unresolved}. 순환 참조 또는 source 누락을 확인하세요."
            )

        return resolved

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

    def _calculate_cspf_profile(self, measured: dict, load_reference: float) -> dict:
        resolved = self._resolve_cspf_profile_points(measured)
        cd = self._get_cspf_profile_cd()
        delta_t = self.t_100_load - self.t_0_load
        if delta_t == 0:
            raise ValueError("t_100_load and t_0_load cannot be equal.")

        cstl = 0.0
        csec = 0.0
        bin_details = []
        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            detail = self._calculate_cspf_bin(idx, tj, nj, load_reference, delta_t, resolved, cd)
            cstl += detail["cstl_bin"]
            csec += detail["csec_bin"]
            bin_details.append(detail)

        return self._build_cspf_result(cstl, csec, bin_details)

    def _calculate_cspf_bin(
        self,
        idx: int,
        tj: float,
        nj: float,
        load_reference: float,
        delta_t: float,
        resolved_points: dict,
        cd: float,
    ) -> dict:
        if nj <= 0:
            return self._empty_cspf_bin(idx, tj, nj, 0.0)

        load = load_reference * (tj - self.t_0_load) / delta_t
        if load <= 0:
            return self._empty_cspf_bin(idx, tj, nj, load)

        interpolated = self.interpolate(tj, resolved_points)
        loads = [
            (data["capacity"], data["power"], load_type)
            for load_type, data in interpolated.items()
        ]
        loads.sort(key=lambda item: item[0])
        if not loads:
            return self._empty_cspf_bin(idx, tj, nj, load)

        lowest_cap, lowest_pow, _ = loads[0]
        highest_cap, highest_pow, _ = loads[-1]
        cooling_output = load

        if load <= lowest_cap:
            if lowest_cap <= 0:
                power = 0.0
            else:
                cycling_ratio = load / lowest_cap
                part_load_factor = max(1e-6, 1.0 - cd * (1.0 - cycling_ratio))
                power = (cycling_ratio * lowest_pow) / part_load_factor
        elif load > highest_cap:
            cooling_output = highest_cap
            power = highest_pow
        else:
            power = None
            for i in range(len(loads) - 1):
                c1, p1, lower_type = loads[i]
                c2, p2, upper_type = loads[i + 1]
                if c1 < load <= c2:
                    if self.power_interpolation_method == "iso_boundary_eer":
                        power = self._iso_boundary_eer_power(
                            tj, load, resolved_points, lower_type, upper_type
                        )
                    if power is not None:
                        break
                    if c2 == c1:
                        power = p1
                    else:
                        power = p1 + (p2 - p1) * (load - c1) / (c2 - c1)
                    break
            if power is None:
                power = highest_pow

        eer = cooling_output / power if power > 0 else None
        return {
            "bin_no": idx,
            "tj": tj,
            "nj": nj,
            "lc": load,
            "capacity": cooling_output,
            "power": power,
            "eer": eer,
            "cstl_bin": cooling_output * nj,
            "csec_bin": power * nj,
        }

    def _empty_cspf_bin(self, idx: int, tj: float, nj: float, load: float) -> dict:
        return {
            "bin_no": idx,
            "tj": tj,
            "nj": nj,
            "lc": load,
            "capacity": 0.0,
            "power": 0.0,
            "eer": None,
            "cstl_bin": 0.0,
            "csec_bin": 0.0,
        }

    def _build_cspf_result(self, cstl: float, csec: float, bin_details: list) -> dict:
        if csec <= 0:
            return {
                "cspf": 0.0,
                "annual_cooling_kwh": 0.0,
                "annual_power_kwh": 0.0,
                "bin_details": bin_details,
            }
        return {
            "cspf": round(cstl / csec, 3),
            "annual_cooling_kwh": round(cstl / 1000.0, 3),
            "annual_power_kwh": round(csec / 1000.0, 3),
            "bin_details": bin_details,
        }

    def calculate_cspf(
        self,
        measured_inputs: dict,
        declared_capacity: float = None,
    ) -> dict:
        if self._has_cspf_test_profile():
            resolved = self._resolve_cspf_profile_points(measured_inputs)
            load_reference = resolved[self.reference_point]["capacity"]
            return self._calculate_cspf_profile(measured_inputs, load_reference)

        resolved_points = self.resolve_points(measured_inputs)
        if self.building_load_source == "declared":
            if declared_capacity is None or declared_capacity <= 0:
                raise ValueError(
                    "building_load_source가 'declared'인 지역은 "
                    "declared_capacity(표기 정격 능력)를 입력해야 합니다."
                )
            load_reference = declared_capacity
        else:
            if self.reference_point not in resolved_points:
                raise ValueError(
                    f"Reference point '{self.reference_point}' not found in resolved points. "
                    f"Check config['reference_point'] or input data."
                )
            load_reference = resolved_points[self.reference_point]["capacity"]

        delta_t = self.t_100_load - self.t_0_load
        if delta_t == 0:
            raise ValueError("t_100_load and t_0_load cannot be equal.")

        cstl = 0.0
        csec = 0.0
        bin_details = []
        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            detail = self._calculate_cspf_bin(
                idx, tj, nj, load_reference, delta_t, resolved_points, self.Cd
            )
            cstl += detail["cstl_bin"]
            csec += detail["csec_bin"]
            bin_details.append(detail)

        return self._build_cspf_result(cstl, csec, bin_details)

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

    def _variable_heating_performance(self, tj: float, measured_inputs: dict) -> dict:
        stage_points = self._heating_stage_points(measured_inputs)
        high_minus_7 = self._point_at_temp(stage_points["high"], -7.0, "high")
        high_2 = self._point_at_temp(stage_points["high"], 2.0, "high")
        high_7 = self._point_at_temp(stage_points["high"], 7.0, "high")
        _, cap_high_7, power_high_7 = high_7

        if cap_high_7 == 0 or power_high_7 == 0:
            raise ValueError("7C high-stage capacity and power must be non-zero.")

        if tj >= 2.0:
            high = self._linear_heating_point(tj, high_2, high_7)
        else:
            high = self._linear_heating_point(tj, high_minus_7, high_2)

        _, cap_half_7, power_half_7 = self._point_at_temp(
            stage_points["half"], 7.0, "half"
        )
        _, cap_min_7, power_min_7 = self._point_at_temp(
            stage_points["min"], 7.0, "min"
        )

        capacity_ratio = high["capacity"] / cap_high_7
        power_ratio = high["power"] / power_high_7
        return {
            "high": high,
            "half": {
                "capacity": cap_half_7 * capacity_ratio,
                "power": power_half_7 * power_ratio,
            },
            "min": {
                "capacity": cap_min_7 * capacity_ratio,
                "power": power_min_7 * power_ratio,
            },
        }

    def _variable_heating_bin(
        self,
        tj: float,
        load: float,
        hours: float,
        measured_inputs: dict,
        aux_cop: float = 1.0
    ) -> dict:
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        performance = self._variable_heating_performance(tj, measured_inputs)
        cap_high = performance["high"]["capacity"]
        power_high = performance["high"]["power"]
        cap_half = performance["half"]["capacity"]
        power_half = performance["half"]["power"]
        cap_min = performance["min"]["capacity"]
        power_min = performance["min"]["power"]

        auxiliary_heat = 0.0
        heat_pump_capacity = load
        if load > cap_high:
            operating_case = "shortage"
            heat_pump_capacity = cap_high
            heat_pump_power = power_high
            auxiliary_heat = load - cap_high
        elif load > cap_half:
            operating_case = "interpolate_high_half"
            if cap_high == cap_half:
                heat_pump_power = power_high
            else:
                heat_pump_power = (
                    power_half
                    + (load - cap_half)
                    / (cap_high - cap_half)
                    * (power_high - power_half)
                )
        elif load > cap_min:
            operating_case = "interpolate_half_min"
            if cap_half == cap_min:
                heat_pump_power = power_half
            else:
                heat_pump_power = (
                    power_min
                    + (load - cap_min)
                    / (cap_half - cap_min)
                    * (power_half - power_min)
                )
        else:
            operating_case = "cyclic_min"
            if cap_min <= 0:
                heat_pump_power = 0.0
            else:
                CR = load / cap_min
                PLF = max(1e-6, 1.0 - self.Cd * (1.0 - CR))
                heat_pump_power = (power_min * CR) / PLF

        heat_pump_energy = heat_pump_power * hours
        auxiliary_energy = auxiliary_heat * hours / aux_cop
        bin_load = load * hours
        bin_energy = heat_pump_energy + auxiliary_energy
        return {
            "tj": tj,
            "hours": hours,
            "load": load,
            "cap_high": cap_high,
            "power_high": power_high,
            "cap_half": cap_half,
            "power_half": power_half,
            "cap_min": cap_min,
            "power_min": power_min,
            "available_capacity": cap_high,
            "heat_pump_capacity": heat_pump_capacity,
            "compressor_heat": heat_pump_capacity,
            "compressor_energy": heat_pump_energy,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_heat": auxiliary_heat,
            "auxiliary_energy": auxiliary_energy,
            "bin_load": bin_load,
            "bin_energy": bin_energy,
            "operating_case": operating_case,
        }

    def _iso_hspf_capacity_curve(self, tj: float, stage: str, resolved: dict, frost: bool) -> float:
        """
        ISO 16358-2 heating capacity curve evaluation.
        """
        p7 = resolved[f"7_{stage}"]
        pm7 = resolved[f"-7_{stage}"]

        if not frost:
            # non-frost: tj <= -7.0 or tj >= 5.5
            return pm7["capacity"] + (p7["capacity"] - pm7["capacity"]) * (tj + 7.0) / 14.0
        else:
            # frost: -7.0 < tj < 5.5
            p2 = resolved.get(f"2_{stage}_f", resolved[f"2_{stage}"])
            return pm7["capacity"] + (p2["capacity"] - pm7["capacity"]) * (tj + 7.0) / 9.0

    def _iso_hspf_power_curve(self, tj: float, stage: str, resolved: dict, frost: bool) -> float:
        """
        ISO 16358-2 heating power curve evaluation.
        """
        p7 = resolved[f"7_{stage}"]
        pm7 = resolved[f"-7_{stage}"]

        if not frost:
            # non-frost: tj <= -7.0 or tj >= 5.5
            return pm7["power"] + (p7["power"] - pm7["power"]) * (tj + 7.0) / 14.0
        else:
            # frost: -7.0 < tj < 5.5
            p2 = resolved.get(f"2_{stage}_f", resolved[f"2_{stage}"])
            return pm7["power"] + (p2["power"] - pm7["power"]) * (tj + 7.0) / 9.0

    def _iso_hspf_capacity_line(self, stage: str, resolved: dict, frost: bool) -> tuple:
        if frost:
            t1, t2 = -7.0, 2.0
        else:
            t1, t2 = -7.0, 7.0
        c1 = self._iso_hspf_capacity_curve(t1, stage, resolved, frost)
        c2 = self._iso_hspf_capacity_curve(t2, stage, resolved, frost)
        slope = (c2 - c1) / (t2 - t1)
        intercept = c1 - slope * t1
        return slope, intercept

    def _iso_hspf_intersection_temp(
        self,
        stage: str,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
        load_slope, load_intercept = load_line
        capacity_slope, capacity_intercept = self._iso_hspf_capacity_line(
            stage, resolved, frost
        )
        denominator = load_slope - capacity_slope
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF load line and capacity line are parallel.")
        return (capacity_intercept - load_intercept) / denominator

    def _iso_hspf_boundary_cop(
        self,
        temp: float,
        stage: str,
        resolved: dict,
        frost: bool
    ) -> float:
        # ISO 16358-2 boundary COP at the load-line / capacity-line intersection
        # temperature `temp` (e.g. tk, tj, tg, th, ta, tf).  Both capacity and
        # power are taken from the same stage curve and frost branch so the
        # ratio represents the actual operating COP at that boundary point.
        capacity = self._iso_hspf_capacity_curve(temp, stage, resolved, frost)
        power = self._iso_hspf_power_curve(temp, stage, resolved, frost)
        if power <= 0:
            raise ValueError("ISO 16358-2 HSPF boundary power must be positive.")
        return capacity / power

    def _iso_hspf_boundary_point(
        self,
        stage: str,
        resolved: dict,
        frost: bool,
        load_line: tuple,
    ) -> dict:
        # Resolve the boundary point where the load line intersects the
        # selected stage capacity line.  Returns temperature plus the capacity
        # / power / load / COP at that intersection, all derived from the same
        # stage curves so callers can use them consistently for Formula
        # 44/45/47/48/49/50 endpoint interpolation.
        temp = self._iso_hspf_intersection_temp(stage, resolved, frost, load_line)
        capacity = self._iso_hspf_capacity_curve(temp, stage, resolved, frost)
        power = self._iso_hspf_power_curve(temp, stage, resolved, frost)
        load_slope, load_intercept = load_line
        load = load_slope * temp + load_intercept
        if power <= 0:
            raise ValueError("ISO 16358-2 HSPF boundary power must be positive.")
        return {
            "temp": temp,
            "stage": stage,
            "frost": frost,
            "capacity": capacity,
            "power": power,
            "load_at_boundary": load,
            "cop": capacity / power,
        }

    def _iso_hspf_min_half_power_by_formula_44_48(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
        # ISO 16358-2 Formula 44 (non-frost) / Formula 48 (frost):
        #   COP_mh(tj) = COP_min(tk) + (COP_half(tj') - COP_min(tk))
        #                              * (tj - tk) / (tj' - tk)
        # where tk = load/min-capacity intersection, tj' = load/half-capacity
        # intersection.  The rewrite below uses the half boundary as the base
        # term, which is algebraically identical to the spec form.
        min_temp = self._iso_hspf_intersection_temp("min", resolved, frost, load_line)
        half_temp = self._iso_hspf_intersection_temp("half", resolved, frost, load_line)
        denominator = min_temp - half_temp
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF min and half boundary temperatures are equal.")

        cop_min = self._iso_hspf_boundary_cop(min_temp, "min", resolved, frost)
        cop_half = self._iso_hspf_boundary_cop(half_temp, "half", resolved, frost)
        cop_mh = cop_half + (cop_min - cop_half) * (tj - half_temp) / denominator
        if cop_mh <= 0:
            raise ValueError("ISO 16358-2 HSPF min-half branch COP must be positive.")
        return bl_h / cop_mh

    def _iso_hspf_half_full_power_by_formula_45_49(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> dict:
        # ISO 16358-2 Formula 45 (non-frost) / Formula 49 (frost):
        #   COP_hf(tj) = COP_full(ta) + (COP_half(tj') - COP_full(ta))
        #                              * (tj - ta) / (tj' - ta)
        # ta = load/full-capacity intersection, tj' = load/half-capacity
        # intersection.  The rewrite using cop_full as the base is identical.
        half_temp = self._iso_hspf_intersection_temp("half", resolved, frost, load_line)
        full_temp = self._iso_hspf_intersection_temp("full", resolved, frost, load_line)
        denominator = half_temp - full_temp
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF half and full boundary temperatures are equal.")

        cop_half = self._iso_hspf_boundary_cop(half_temp, "half", resolved, frost)
        cop_full = self._iso_hspf_boundary_cop(full_temp, "full", resolved, frost)
        cop_hf = cop_full + (cop_half - cop_full) * (tj - full_temp) / denominator
        if cop_hf <= 0:
            raise ValueError("ISO 16358-2 HSPF half-full branch COP must be positive.")

        pi_half = self._iso_hspf_capacity_curve(tj, "half", resolved, frost)
        pi_full = self._iso_hspf_capacity_curve(tj, "full", resolved, frost)
        if bl_h < pi_half - 1e-5 or bl_h > pi_full + 1e-5:
            raise ValueError(f"Load {bl_h} is outside the half ({pi_half}) to full ({pi_full}) capacity range.")

        branch_id = "formula49_half_full_frost" if frost else "formula45_half_full"

        return {
            "P_hf": bl_h / cop_hf,
            "branch": branch_id,
            "cop_half": cop_half,
            "cop_full": cop_full,
            "cop_hf": cop_hf,
        }

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

    def _iso_hspf_common_load_line(
        self,
        hspf_cfg: dict,
        rated_heating_capacity: float
    ) -> dict:
        load_line_cfg = hspf_cfg.get("load_line", {})
        if load_line_cfg.get("source") != "rated_heating_capacity":
            source = load_line_cfg.get("source")
            raise ValueError(
                f"Unsupported or missing load_line source '{source}' for ISO 16358-2 HSPF."
            )
        required_fields = (
            "zero_load_temp",
            "full_load_temp",
            "rated_capacity_factor",
        )
        if any(field not in load_line_cfg for field in required_fields):
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )

        zero_load_temp = float(load_line_cfg["zero_load_temp"])
        full_load_temp = float(load_line_cfg["full_load_temp"])
        rated_capacity_factor = float(load_line_cfg["rated_capacity_factor"])
        if zero_load_temp == full_load_temp:
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: zero_load_temp and full_load_temp must differ."
            )
        if rated_capacity_factor <= 0:
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: rated_capacity_factor must be positive."
            )

        l_h_ref = rated_heating_capacity * rated_capacity_factor
        denominator = zero_load_temp - full_load_temp
        return {
            "zero_load_temp": zero_load_temp,
            "full_load_temp": full_load_temp,
            "rated_capacity_factor": rated_capacity_factor,
            "l_h_ref": l_h_ref,
            "line": (
                -l_h_ref / denominator,
                l_h_ref * zero_load_temp / denominator,
            ),
        }

    def _iso_hspf_has_non_frost_extended_candidate(self, resolved: dict) -> bool:
        return (
            "7_ext" in resolved
            and "-7_ext" in resolved
        )

    def _iso_hspf_has_frost_extended_candidate(self, resolved: dict) -> bool:
        return self._iso_hspf_has_extended_candidate(resolved) or (
            "-7_ext" in resolved and "2_ext_f" in resolved
        )

    def _iso_hspf_common_extended_frost_curve(
        self,
        tj: float,
        resolved: dict
    ) -> dict:
        ext_m7 = self._iso_hspf_extended_minus7_default(resolved)
        ext_2 = resolved.get("2_ext_f", resolved.get("2_ext"))
        return {
            "capacity": ext_m7["capacity"]
            + (ext_2["capacity"] - ext_m7["capacity"]) * (tj + 7.0) / 9.0,
            "power": ext_m7["power"]
            + (ext_2["power"] - ext_m7["power"]) * (tj + 7.0) / 9.0,
        }

    def _iso_hspf_common_stage_snapshot(
        self,
        tj: float,
        resolved: dict,
        active_stages: list,
        frost: bool
    ) -> dict:
        snapshot = {}
        for stage in ("min", "half", "full"):
            if stage not in active_stages:
                continue
            snapshot[stage] = {
                "capacity": self._iso_hspf_capacity_curve(
                    tj, stage, resolved, frost
                ),
                "power": self._iso_hspf_power_curve(tj, stage, resolved, frost),
            }

        if frost and self._iso_hspf_has_frost_extended_candidate(resolved):
            snapshot["ext"] = self._iso_hspf_common_extended_frost_curve(
                tj, resolved
            )
        elif (not frost) and self._iso_hspf_has_non_frost_extended_candidate(resolved):
            snapshot["ext"] = {
                "capacity": self._iso_hspf_capacity_curve(
                    tj, "ext", resolved, False
                ),
                "power": self._iso_hspf_power_curve(tj, "ext", resolved, False),
            }
        return snapshot

    def _iso_hspf_select_common_branch(
        self,
        bl_h: float,
        snapshot: dict,
        active_stages: list,
        frost: bool
    ) -> str:
        lowest_stage = "min" if "min" in active_stages else "half"
        if bl_h <= snapshot[lowest_stage]["capacity"]:
            return "cycling"
        if "min" in active_stages and bl_h <= snapshot["half"]["capacity"]:
            return "min_half_formula48" if frost else "min_half_formula44"
        if bl_h <= snapshot["full"]["capacity"]:
            return "half_full_formula49" if frost else "half_full_formula45"
        if "ext" in snapshot and bl_h <= snapshot["ext"]["capacity"]:
            return "full_extended_formula50" if frost else "full_extended_formula47"
        return "saturated"

    def _iso_hspf_stage_pair_power_by_x(
        self,
        bl_h: float,
        low_stage: dict,
        high_stage: dict
    ) -> dict:
        low_capacity = low_stage["capacity"]
        high_capacity = high_stage["capacity"]
        denominator = high_capacity - low_capacity
        if denominator == 0:
            raise ValueError(
                "ISO 16358-2 HSPF stage capacities must differ for interpolation."
            )

        x = (bl_h - low_capacity) / denominator
        power = low_stage["power"] + x * (high_stage["power"] - low_stage["power"])
        return {"X": x, "P_j": power}

    def _iso_hspf_calculate_common_branch_power(
        self,
        branch: str,
        tj: float,
        bl_h: float,
        snapshot: dict,
        active_stages: list,
        cd: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> dict:
        if branch == "cycling":
            lowest_stage = "min" if "min" in active_stages else "half"
            capacity = snapshot[lowest_stage]["capacity"]
            power = snapshot[lowest_stage]["power"]
            x = bl_h / capacity
            plf = 1.0 - cd * (1.0 - x)
            if plf <= 0:
                raise ValueError("ISO 16358-2 HSPF cycling PLF must be positive.")
            p_j = x * power / plf
            return {
                "case": "cycling",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": {
                    "X": x,
                    "PLF": plf,
                    "cycling_stage": lowest_stage,
                },
            }

        if branch in ("min_half_formula44", "min_half_formula48"):
            p_j = self._iso_hspf_min_half_power_by_formula_44_48(
                tj, bl_h, resolved, frost, load_line
            )
            return {
                "case": "min_half_interpolation_frost"
                if branch == "min_half_formula48"
                else "min_half_interpolation",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": {
                    "branch": branch,
                },
            }

        if branch in ("half_full_formula45", "half_full_formula49"):
            formula_result = self._iso_hspf_half_full_power_by_formula_45_49(
                tj, bl_h, resolved, frost, load_line
            )
            p_j = formula_result["P_hf"]
            trace = {
                key: value for key, value in formula_result.items()
                if key != "P_hf"
            }
            return {
                "case": "formula49_half_full_frost"
                if branch == "half_full_formula49"
                else "formula45_half_full",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        if branch == "full_extended_formula47":
            formula_result = self._iso_hspf_formula47_full_extended_non_frost_power(
                tj, bl_h, resolved, load_line
            )
            p_j = formula_result["P_fe"]
            trace = {
                key: value for key, value in formula_result.items()
                if key != "P_fe"
            }
            return {
                "case": "formula47_full_extended",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        if branch == "full_extended_formula50":
            formula_result = self._iso_hspf_formula50_full_extended_frost_power(
                tj, bl_h, resolved, load_line
            )
            p_j = formula_result["P_fe"]
            trace = {
                "branch": "formula50_full_extended_frost",
                "P_fe": p_j,
                "pi_ext_f": snapshot["ext"]["capacity"],
                "p_ext_f": snapshot["ext"]["power"],
                "backup_heat": 0.0,
            }
            trace.update({
                key: value for key, value in formula_result.items()
                if key != "P_fe"
            })
            return {
                "case": "formula50_full_extended_frost",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        available_stage = "ext" if "ext" in snapshot else "full"
        available_capacity = snapshot[available_stage]["capacity"]
        available_power = snapshot[available_stage]["power"]
        return {
            "case": "saturated",
            "P_j": available_power,
            "pi_j": available_capacity,
            "heat_pump_energy_rate": available_power,
            "auxiliary_heat_rate": max(0.0, bl_h - available_capacity),
            "trace": {
                "saturated_stage": available_stage,
                "backup_heat": max(0.0, bl_h - available_capacity),
            },
        }

    def _iso_hspf_evaluate_common_bin(
        self,
        bin_data: dict,
        resolved: dict,
        active_stages: list,
        load_line_info: dict,
        frost_boundaries: dict,
        cd: float,
        aux_cop: float
    ) -> dict:
        tj = float(bin_data.get("tj", 0))
        nj = float(bin_data.get("nj", 0))
        if nj <= 0:
            return {}

        zero_load_temp = load_line_info["zero_load_temp"]
        full_load_temp = load_line_info["full_load_temp"]
        bl_h = load_line_info["l_h_ref"] * (zero_load_temp - tj) / (
            zero_load_temp - full_load_temp
        )
        if bl_h <= 0:
            return {}

        frost_lower = float(frost_boundaries.get("lower", -7.0))
        frost_upper = float(frost_boundaries.get("upper", 5.5))
        frost = frost_lower < tj < frost_upper
        snapshot = self._iso_hspf_common_stage_snapshot(
            tj, resolved, active_stages, frost
        )
        branch = self._iso_hspf_select_common_branch(
            bl_h, snapshot, active_stages, frost
        )
        branch_result = self._iso_hspf_calculate_common_branch_power(
            branch,
            tj,
            bl_h,
            snapshot,
            active_stages,
            cd,
            resolved,
            frost,
            load_line_info["line"],
        )

        heat_pump_energy = branch_result["heat_pump_energy_rate"] * nj
        auxiliary_energy = branch_result["auxiliary_heat_rate"] * nj / aux_cop
        detail = {
            "tj": tj,
            "nj": nj,
            "bl_h": bl_h,
            "frost": frost,
            "pi_j": branch_result["pi_j"],
            "P_j": branch_result["P_j"],
            "case": branch_result["case"],
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_energy": auxiliary_energy,
            "E_j": heat_pump_energy + auxiliary_energy,
        }
        detail.update(branch_result["trace"])
        detail["frost"] = frost
        return detail

    def calculate_hspf_iso16358_common(
        self,
        measured_inputs: dict,
        rated_heating_capacity: float,
        aux_cop: float = 1.0
    ) -> dict:
        """
        ISO 16358-2 HSPF common engine.
        """
        if rated_heating_capacity <= 0:
            raise ValueError("rated_heating_capacity must be positive.")

        hspf_cfg = self.config.get("hspf", {})
        correction_cfg = hspf_cfg.get("correction", {})
        if aux_cop == 1.0:
            aux_cop = float(correction_cfg.get("aux_cop", 1.0))
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")
        cd = float(correction_cfg.get("cd", self.Cd))

        points = self._iso_hspf_normalize_common_points(measured_inputs)
        resolved, active_stages = self._iso_hspf_resolve_common_points(
            points, hspf_cfg
        )
        load_line_info = self._iso_hspf_common_load_line(
            hspf_cfg, rated_heating_capacity
        )
        frost_boundaries = hspf_cfg.get("frost_boundaries", {})

        hstl, hsec = 0.0, 0.0
        bin_details = []
        bin_hours_key = hspf_cfg.get("bin_hours_key", "hspf_bin_hours")

        for bin_data in self.config.get(bin_hours_key, []):
            detail = self._iso_hspf_evaluate_common_bin(
                bin_data,
                resolved,
                active_stages,
                load_line_info,
                frost_boundaries,
                cd,
                aux_cop,
            )
            if not detail:
                continue

            hstl += detail["bl_h"] * detail["nj"]
            hsec += detail["E_j"]
            bin_details.append(detail)

        if hsec <= 0:
            return {
                "hspf": 0.0,
                "hstl_wh": hstl,
                "hsec_wh": hsec,
                "heat_pump_energy_wh": 0.0,
                "auxiliary_energy_wh": 0.0,
                "bin_details": bin_details,
            }

        hspf_val = hstl / hsec
        hp_energy_total = sum(d["heat_pump_energy"] for d in bin_details)
        aux_energy_total = sum(d["auxiliary_energy"] for d in bin_details)

        return {
            "hspf": round(hspf_val, 3),
            "hstl_wh": hstl,
            "hsec_wh": hsec,
            "heat_pump_energy_wh": hp_energy_total,
            "auxiliary_energy_wh": aux_energy_total,
            "bin_details": bin_details,
        }

    def calculate_hspf(self, measured_inputs: dict, aux_cop: float = 1.0) -> dict:
        measured_inputs = self._prepare_measured_inputs(measured_inputs)
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        profile = self.config.get("hspf", {}).get("profile")
        if profile == "iso16358_2_hspf":
            rated_heating_capacity = measured_inputs.get("rated_heating_capacity")
            if rated_heating_capacity is None:
                load_line_cfg = self.config.get("hspf", {}).get("load_line", {})
                source = load_line_cfg.get("source")
                if source == "rated_heating_capacity":
                    raise ValueError(
                        "rated_heating_capacity must be provided explicitly in "
                        "measured_inputs for ISO 16358-2 HSPF."
                    )
                raise ValueError(
                    f"Unsupported or missing load_line source '{source}' for ISO 16358-2 HSPF."
                )

            return self.calculate_hspf_iso16358_common(
                measured_inputs=measured_inputs,
                rated_heating_capacity=float(rated_heating_capacity),
                aux_cop=aux_cop,
            )

        hstl = 0.0
        hsec = 0.0
        bin_details = []

        for bin_data in self.bin_hours:
            tj = float(bin_data.get("tj", 0))
            hours = float(bin_data.get("nj", bin_data.get("hours", 0)))
            if hours <= 0:
                continue

            load = float(bin_data.get("load", bin_data.get("heating_load", 0)))
            if load <= 0:
                continue

            if self._has_variable_heating_points(measured_inputs):
                detail = self._variable_heating_bin(
                    tj, load, hours, measured_inputs, aux_cop
                )
            else:
                performance = self.interpolate_heating(tj, measured_inputs)
                available_capacity = max(0.0, performance["capacity"])
                compressor_heat = min(load, available_capacity)
                compressor_energy = max(0.0, performance["power"]) * hours
                auxiliary = self.calc_auxiliary_heat(
                    load, available_capacity, hours, aux_cop
                )
                bin_load = load * hours
                bin_energy = compressor_energy + auxiliary["auxiliary_energy"]
                detail = {
                    "tj": tj,
                    "hours": hours,
                    "load": load,
                    "available_capacity": available_capacity,
                    "compressor_heat": compressor_heat,
                    "compressor_energy": compressor_energy,
                    "heat_pump_energy": compressor_energy,
                    "auxiliary_heat": auxiliary["auxiliary_heat"],
                    "auxiliary_energy": auxiliary["auxiliary_energy"],
                    "bin_load": bin_load,
                    "bin_energy": bin_energy,
                }

            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        if hsec <= 0:
            return {
                "hspf": 0.0,
                "HSPF": 0.0,
                "HSTL": hstl,
                "HSEC": hsec,
                "bin_details": bin_details,
            }

        hspf = hstl / hsec
        heat_pump_energy = sum(
            item.get("heat_pump_energy", item.get("compressor_energy", 0.0))
            for item in bin_details
        )
        auxiliary_energy = sum(
            item.get("auxiliary_energy", 0.0) for item in bin_details
        )
        return {
            "hspf": hspf,
            "HSPF": hspf,
            "hstl": hstl,
            "HSTL": hstl,
            "hsec": hsec,
            "HSEC": hsec,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_energy": auxiliary_energy,
            "bin_details": bin_details,
        }
