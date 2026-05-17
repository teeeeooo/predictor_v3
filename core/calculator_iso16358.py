"""ISO 16358 CSPF/HSPF common standard calculator.

Step 3a implements the ISO 16358-1 CSPF path only. HSPF remains a Step 3b
contract and intentionally raises ``NotImplementedError`` here.
"""

import json
import os
from decimal import Decimal, ROUND_HALF_UP


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

        self.points_config = self.config.get("points", {})
        self.derived_rules = self.config.get("derived_rules", {})
        self.bin_hours = self.config.get("bin_hours", [])

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

    def calculate_hspf(self, measured_inputs: dict) -> dict:
        raise NotImplementedError(
            "ISO16358Calculator.calculate_hspf is not yet implemented in the new series."
        )
