# core/calculator_iso16358.py

import json
import os
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

class ISO16358Calculator:
    """
    ISO 16358 기반 동적 효율(CSPF) 계산 엔진
    지역별 JSON 설정 파일을 바탕으로 N-Point(2-point, 3-point 등) 모델을 동적으로 처리합니다.
    """
    
    def __init__(self, config_path: str):
        """
        주어진 JSON 설정 파일 경로를 읽어 계산기의 동적 규칙을 초기화합니다.
        
        Args:
            config_path (str): 지역별 설정 파일 경로 (예: "data/region_configs/thailand.json")
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        # 메타데이터(_comment 등) 명시적 제거
        self.config.pop("_comment", None)
            
        # 설정된 기본 환경 변수 파싱
        self.t_100_load = self.config.get("t_100_load", 35.0)
        self.t_0_load = self.config.get("t_0_load", 20.0)
        self.Cd = self.config.get("Cd", 0.25)
        self.building_load_source = self.config.get("building_load_source", "measured")
        self.reference_point = self.config.get("reference_point", "35_full")
        self.round_test_values = self.config.get("round_test_values", False)
        self.rounding_method = self.config.get("rounding_method", None)
        self.power_interpolation_method = self.config.get("power_interpolation_method", "capacity_linear")
        self.iso_boundary_temperature_rounding = self.config.get("iso_boundary_temperature_rounding", None)
        self.half_capacity_recommendation = self.config.get("half_capacity_recommendation", {})
        
        # 포인트 활성화 및 파생 규칙, 온도 Bin 테이블 파싱
        self.points_config = self.config.get("points", {})
        self.derived_rules = self.config.get("derived_rules", {})
        self.bin_hours = self.config.get("bin_hours", [])

    def _round_test_value(self, value: float) -> int:
        """
        KS C 9306 시험값 정수 반올림용 helper입니다.
        Python round()의 bankers rounding을 피하기 위해 ROUND_HALF_UP을 사용합니다.
        """
        return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _round_iso_boundary_temperature(self, value: float) -> float:
        if self.iso_boundary_temperature_rounding is None:
            return value
        if self.iso_boundary_temperature_rounding == "excel_round_0":
            return float(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        raise ValueError(
            "Unsupported iso_boundary_temperature_rounding: "
            f"{self.iso_boundary_temperature_rounding}."
        )

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
        
        resolved = {k: v for k, v in measured.items()}
        
        def _set_point(key, cap, pwr):
            if key not in resolved:
                resolved[key] = {"capacity": cap, "power": pwr}

        if climate == "T1":
            _set_point("29_full", resolved["35_full"]["capacity"] * 1.077, resolved["35_full"]["power"] * 0.914)
            _set_point("29_half", resolved["35_half"]["capacity"] * 1.077, resolved["35_half"]["power"] * 0.914)
            if selection == "with_optional_test":
                _set_point("29_min", resolved["35_min"]["capacity"] * 1.077, resolved["35_min"]["power"] * 0.914)
        
        elif climate == "T3":
            _set_point("46_half", resolved["35_half"]["capacity"] * 0.859, resolved["35_half"]["power"] * 1.25)
            _set_point("29_full", resolved["35_full"]["capacity"] * 1.077, resolved["35_full"]["power"] * 0.914)
            _set_point("29_half", resolved["35_half"]["capacity"] * 1.077, resolved["35_half"]["power"] * 0.914)
            if selection == "with_optional_test":
                _set_point("46_min", resolved["35_min"]["capacity"] * 0.859, resolved["35_min"]["power"] * 1.25)
                _set_point("29_min", resolved["35_min"]["capacity"] * 1.077, resolved["35_min"]["power"] * 0.914)
        
        return resolved

    def resolve_points(self, measured_inputs: dict) -> dict:
        """
        입력된 측정값(measure)과 JSON의 파생 규칙(default)을 해석하여
        계산에 필요한 모든 포인트의 딕셔너리를 완성합니다.
        
        Args:
            measured_inputs (dict): UI에서 입력받은 측정값
        Returns:
            dict: 모든 포인트가 채워진 딕셔너리
        """
        if self._has_cspf_test_profile():
            return self._resolve_cspf_profile_points(measured_inputs)

        resolved = {}

        # 1. "measure" 포인트 우선 처리
        for point_key, point_type in self.points_config.items():
            if point_type == "measure":
                if point_key not in measured_inputs:
                    raise ValueError(f"필수 측정값 누락: '{point_key}' 포인트 데이터가 없습니다.")

                point_data = measured_inputs[point_key]
                if not isinstance(point_data, dict):
                    raise ValueError(
                        f"Invalid measured point '{point_key}': expected dict with capacity and power."
                    )

                for required_key in ("capacity", "power"):
                    if required_key not in point_data:
                        raise ValueError(
                            f"Invalid measured point '{point_key}': "
                            f"missing required field '{required_key}'."
                        )

                validated_point = dict(point_data)
                for numeric_key in ("capacity", "power"):
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

        # 2. "default" 포인트 처리 (연쇄 파생 규칙 대응 루프)
        for _ in range(len(self.points_config)):
            for point_key, point_type in self.points_config.items():
                if point_type == "default" and point_key not in resolved:
                    rule = self.derived_rules.get(point_key)
                    if not rule:
                        continue
                    
                    source_key = rule.get("source")
                    if source_key in resolved:
                        source_data = resolved[source_key]
                        cap_factor = rule.get("capacity_factor", 1.0)
                        pow_factor = rule.get("power_factor", 1.0)
                        
                        resolved[point_key] = {
                            "capacity": source_data["capacity"] * cap_factor,
                            "power": source_data["power"] * pow_factor
                        }
                        if self.round_test_values:
                            resolved[point_key]["capacity"] = self._round_test_value(resolved[point_key]["capacity"])
                            resolved[point_key]["power"] = self._round_test_value(resolved[point_key]["power"])

        # 3. 순환 참조 감지 및 에러 처리
        unresolved = [
            k for k, t in self.points_config.items()
            if t == "default" and k not in resolved
        ]
        if unresolved:
            raise ValueError(f"해결되지 않은 default 포인트: {unresolved}. 순환 참조 또는 source 누락을 확인하세요.")

        return resolved

    def interpolate(self, tj: float, resolved_points: dict) -> dict:
        """
        주어진 외기온도(tj)에서의 부하 조건별 능력과 소비전력을 독립적으로 선형 보간/외삽합니다.
        
        Args:
            tj (float): 계산할 Bin 온도
            resolved_points (dict): resolve_points()에서 완성된 포인트 딕셔너리
            
        Returns:
            dict: 온도 tj에서의 부하 조건별 성능
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
                
            if load_type not in grouped:
                grouped[load_type] = []
            grouped[load_type].append((temp, data["capacity"], data["power"]))

        interpolated = {}

        for load_type, points in grouped.items():
            points.sort(key=lambda x: x[0])  # 온도 기준 오름차순 정렬
            
            if len(points) == 1:
                interpolated[load_type] = {"capacity": points[0][1], "power": points[0][2]}
                continue

            if tj <= points[0][0]:
                t1, c1, p1 = points[0]
                t2, c2, p2 = points[1]
                c_tj = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
                p_tj = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
                interpolated[load_type] = {"capacity": c_tj, "power": p_tj}
                continue
            if tj >= points[-1][0]:
                t1, c1, p1 = points[-2]
                t2, c2, p2 = points[-1]
                c_tj = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
                p_tj = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
                interpolated[load_type] = {"capacity": c_tj, "power": p_tj}
                continue

            # 정상 범위 내 선형 보간
            for i in range(len(points) - 1):
                t1, c1, p1 = points[i]
                t2, c2, p2 = points[i+1]
                if t1 <= tj <= t2:
                    c_tj = c1 + (c2 - c1) * (tj - t1) / (t2 - t1)
                    p_tj = p1 + (p2 - p1) * (tj - t1) / (t2 - t1)
                    interpolated[load_type] = {"capacity": c_tj, "power": p_tj}
                    break

        return interpolated

    def _performance_line(self, resolved_points: dict, load_type: str) -> tuple:
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

    def _ks_intersection_power(
        self,
        tj: float,
        L_c_ref: float,
        resolved_points: dict,
        lower_type: str,
        upper_type: str
    ) -> float:
        lower_line = self._performance_line(resolved_points, lower_type)
        upper_line = self._performance_line(resolved_points, upper_type)
        if lower_line is None or upper_line is None:
            return None

        load_slope = L_c_ref / (self.t_100_load - self.t_0_load)
        load_intercept = -load_slope * self.t_0_load

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

    def _iso_boundary_temperature(
        self,
        ref_capacity: float,
        capacity_35: float,
        capacity_29: float
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
        tj: float
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
        Lc: float,
        resolved_points: dict,
        lower_type: str,
        upper_type: str
    ) -> float:
        profile_cfg = self.config.get("cspf_test_profile", {})
        if profile_cfg and profile_cfg.get("climate_profile") == "T3":
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

            t_upper, eer_upper = upper_boundary
            t_lower, eer_lower = lower_boundary
            if t_upper == t_lower:
                return None

            eer_tj = eer_lower + (eer_upper - eer_lower) / (t_upper - t_lower) * (
                tj - t_lower
            )
            if eer_tj <= 0:
                return None
            return Lc / eer_tj

        if {lower_type, upper_type} != {"half", "full"}:
            return None

        t_upper, eer_upper = self._iso_boundary_eer(resolved_points, upper_type)
        t_lower, eer_lower = self._iso_boundary_eer(resolved_points, lower_type)
        if t_upper == t_lower:
            return None

        eer_tj = eer_lower + (eer_upper - eer_lower) / (t_upper - t_lower) * (
            tj - t_lower
        )
        if eer_tj <= 0:
            return None
        return Lc / eer_tj

    def recommend_35_half_capacity(self, phi_full_35: float, phi_min_29: float) -> dict:
        """
        35°C 중간 운전 능력 목표값 산정을 위한 독립 helper입니다.
        CSPF 본계산에는 사용하지 않습니다.
        """
        if phi_full_35 <= 0 or phi_min_29 <= 0:
            raise ValueError("phi_full_35 and phi_min_29 must be positive.")

        config = self.half_capacity_recommendation
        if not config or not config.get("enabled", False):
            raise ValueError("half_capacity_recommendation config is required and must be enabled.")

        min_test_temp = config.get("min_test_temp")
        full_test_temp = config.get("full_test_temp")
        factor = config.get("min_capacity_ratio_35_to_29")
        if min_test_temp is None or full_test_temp is None or factor is None:
            raise ValueError("half_capacity_recommendation config is incomplete.")
        if full_test_temp != self.t_100_load:
            raise ValueError("half_capacity_recommendation full_test_temp must match t_100_load.")
        if full_test_temp == min_test_temp:
            raise ValueError("full_test_temp and min_test_temp cannot be equal (division by zero).")
        if full_test_temp == self.t_0_load:
            raise ValueError("full_test_temp and t_0_load cannot be equal (division by zero).")
        if factor == 0:
            raise ValueError("min_capacity_ratio_35_to_29 cannot be zero (division by zero).")

        phi_min_35 = phi_min_29 / factor
        min_slope = (phi_min_35 - phi_min_29) / (full_test_temp - min_test_temp)
        min_intercept = phi_min_29 - min_slope * min_test_temp

        load_slope = phi_full_35 / (full_test_temp - self.t_0_load)
        load_intercept = -load_slope * self.t_0_load

        denominator = load_slope - min_slope
        if denominator == 0:
            raise ValueError("Cannot calculate T_min because load and minimum capacity are parallel.")

        T_min = (min_intercept - load_intercept) / denominator
        T_mid = (T_min + full_test_temp) / 2.0
        building_load_at_T_mid = phi_full_35 * (T_mid - self.t_0_load) / (full_test_temp - self.t_0_load)
        delta = factor - 1.0
        temp_factor_at_T_mid = 1.0 + delta * (full_test_temp - T_mid) / (full_test_temp - min_test_temp)
        if temp_factor_at_T_mid == 0:
            raise ValueError("temp_factor_at_T_mid cannot be zero (division by zero).")
        recommended_phi_half_35 = building_load_at_T_mid / temp_factor_at_T_mid

        return {
            "T_min": T_min,
            "T_mid": T_mid,
            "building_load_at_T_mid": building_load_at_T_mid,
            "recommended_phi_half_35": recommended_phi_half_35
        }

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

    def _has_ks_c9306_hspf_input(self, measured_inputs: dict) -> bool:
        hspf_config = self.config.get("hspf", {})
        if not isinstance(hspf_config, dict):
            return False
        return hspf_config.get("profile") == "ks_c_9306_hspf"

    def _ks_hspf_input(self, measured_inputs: dict) -> dict:
        if "ks_c_9306_hspf" not in measured_inputs:
            raise ValueError("Missing ks_c_9306_hspf input.")
        hspf_input = measured_inputs["ks_c_9306_hspf"]
        if not isinstance(hspf_input, dict):
            raise ValueError("Invalid KS C 9306 HSPF ks_c_9306_hspf: must be dict.")
        return hspf_input

    def _ks_hspf_config(self) -> dict:
        hspf_config = self.config.get("hspf", {})
        if not isinstance(hspf_config, dict):
            return {}
        return hspf_config

    def _ks_hspf_profile_point_path(self, temp_key: str, point_name: str) -> tuple:
        stage_map = {
            "full": "rated",
            "rated": "rated",
            "half": "intermediate",
            "intermediate": "intermediate",
            "min": "min",
            "minimum": "min",
            "max": "max",
            "maximum": "max",
            "extended": "max",
        }
        if point_name == "defrost":
            return "max", "def"
        stage = stage_map.get(point_name)
        if stage is None:
            raise ValueError(f"Unsupported KS C 9306 HSPF profile point: {point_name}.")
        return stage, temp_key

    def _ks_hspf_required_points(self) -> dict:
        hspf_config = self._ks_hspf_config()
        required_points = hspf_config.get("required_points", {})
        if isinstance(required_points, dict) and required_points:
            return required_points
        return {}

    def _validate_ks_hspf_positive_number(self, value, field_path: str) -> None:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid KS C 9306 HSPF {field_path}: must be positive number."
            ) from None
        if numeric_value <= 0:
            raise ValueError(
                f"Invalid KS C 9306 HSPF {field_path}: must be positive number."
            )

    def _validate_ks_c9306_hspf_input(self, hspf_input: dict) -> None:
        for quantity in ("capacity", "power"):
            quantity_data = hspf_input.get(quantity)
            if quantity_data is None:
                raise ValueError(f"Missing KS C 9306 HSPF {quantity} input.")
            if not isinstance(quantity_data, dict):
                raise ValueError(
                    f"Invalid KS C 9306 HSPF {quantity}: must be dict."
                )

            for temp_key, point_names in self._ks_hspf_required_points().items():
                for point_name in point_names:
                    stage, point = self._ks_hspf_profile_point_path(
                        temp_key, point_name
                    )
                    stage_data = quantity_data.get(stage)
                    if stage_data is None:
                        raise ValueError(
                            f"Missing KS C 9306 HSPF {quantity}.{stage} input."
                        )
                    if not isinstance(stage_data, dict):
                        raise ValueError(
                            f"Invalid KS C 9306 HSPF {quantity}.{stage}: must be dict."
                        )
                    if point not in stage_data:
                        raise ValueError(
                            f"Missing KS C 9306 HSPF {quantity}.{stage}.{point} input."
                        )

            for stage, stage_data in quantity_data.items():
                if stage_data is None:
                    continue
                if not isinstance(stage_data, dict):
                    raise ValueError(
                        f"Invalid KS C 9306 HSPF {quantity}.{stage}: must be dict."
                    )
                for point, value in stage_data.items():
                    self._validate_ks_hspf_positive_number(
                        value,
                        f"{quantity}.{stage}.{point}"
                    )

        correction = hspf_input.get("correction")
        if correction is not None:
            if not isinstance(correction, dict):
                raise ValueError(
                    "Invalid KS C 9306 HSPF correction: must be dict."
                )
            for key in ("capacity_def_over_nof", "power_def_over_nof"):
                if key in correction:
                    self._validate_ks_hspf_positive_number(
                        correction[key],
                        f"correction.{key}"
                    )
            if "cd" in correction:
                try:
                    cd = float(correction["cd"])
                except (TypeError, ValueError):
                    raise ValueError(
                        "Invalid KS C 9306 HSPF correction.cd: must be >= 0 and < 1."
                    ) from None
                if cd < 0 or cd >= 1:
                    raise ValueError(
                        "Invalid KS C 9306 HSPF correction.cd: must be >= 0 and < 1."
                    )

        load_line = hspf_input.get("load_line")
        if load_line is not None:
            if not isinstance(load_line, dict):
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: must be dict."
                )
            has_slope = "slope" in load_line
            has_intercept = "intercept" in load_line
            if not has_slope or not has_intercept:
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: slope and intercept are required together."
                )
            try:
                slope = float(load_line["slope"])
                float(load_line["intercept"])
            except (TypeError, ValueError):
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: slope and intercept must be numeric."
                ) from None
            if slope == 0:
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line.slope: must be non-zero."
                )

    def _ks_hspf_correction(self, hspf_input: dict, key: str, default: float) -> float:
        correction = hspf_input.get("correction") or {}
        if key in correction:
            return float(correction[key])
        config_correction = self._ks_hspf_config().get("correction", {})
        if isinstance(config_correction, dict) and key in config_correction:
            return float(config_correction[key])
        return float(default)

    def _ks_hspf_minus7_factor(self, quantity: str, stage: str) -> float:
        stage_to_rule = {
            "min": "min_-7",
            "intermediate": "half_-7",
            "rated": "full_-7",
        }
        rule_key = stage_to_rule.get(stage)
        rules = self._ks_hspf_config().get("derived_rules", {})
        if isinstance(rules, dict) and rule_key in rules:
            rule = rules[rule_key]
            factor_key = "capacity_factor" if quantity == "capacity" else "power_factor"
            if factor_key in rule:
                return float(rule[factor_key])
        return 0.601 if quantity == "capacity" else 0.801

    def _ks_hspf_stage_value(
        self,
        hspf_input: dict,
        quantity: str,
        stage: str,
        point: str,
        required: bool = True
    ) -> float:
        quantity_data = hspf_input.get(quantity, {})
        stage_data = quantity_data.get(stage, {})
        if point in stage_data:
            return float(stage_data[point])

        if point == "-7" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                factor = self._ks_hspf_minus7_factor(quantity, stage)
                return float(stage_data["7"]) * factor

        if point == "2" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                value_minus7 = self._ks_hspf_stage_value(
                    hspf_input, quantity, stage, "-7"
                )
                value_7 = float(stage_data["7"])
                return self._ks_hspf_linear(
                    2.0, -7.0, value_minus7, 7.0, value_7
                )

        if required:
            raise ValueError(
                f"Missing KS C 9306 HSPF {quantity}.{stage}.{point} input."
            )
        return None

    def _ks_hspf_linear(self, tj: float, t1: float, v1: float, t2: float, v2: float) -> float:
        if t2 == t1:
            raise ValueError("Interpolation temperatures cannot be equal.")
        return v1 + (v2 - v1) * (tj - t1) / (t2 - t1)

    def _ks_hspf_is_frost_region(self, tj: float) -> bool:
        return -7.0 < tj < 5.5

    def _ks_hspf_capacity_curve(
        self,
        tj: float,
        hspf_input: dict,
        stage: str,
        frost: bool = None
    ) -> float:
        if frost is None:
            frost = self._ks_hspf_is_frost_region(tj)

        if stage == "max":
            cap_minus7 = self._ks_hspf_stage_value(hspf_input, "capacity", "max", "-7")
            cap_def = self._ks_hspf_stage_value(hspf_input, "capacity", "max", "def")
            return self._ks_hspf_linear(tj, -7.0, cap_minus7, 2.0, cap_def)

        cap_minus7 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "-7")
        if frost:
            cap_2 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "2")
            ratio = self._ks_hspf_correction(
                hspf_input, "capacity_def_over_nof", 1.0 / 1.12
            )
            cap_2 = cap_2 * ratio
            return self._ks_hspf_linear(tj, -7.0, cap_minus7, 2.0, cap_2)

        cap_7 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "7")
        return self._ks_hspf_linear(tj, -7.0, cap_minus7, 7.0, cap_7)

    def _ks_hspf_power_curve(
        self,
        tj: float,
        hspf_input: dict,
        stage: str,
        frost: bool = None
    ) -> float:
        if frost is None:
            frost = self._ks_hspf_is_frost_region(tj)

        if stage == "max":
            power_minus7 = self._ks_hspf_stage_value(hspf_input, "power", "max", "-7")
            power_def = self._ks_hspf_stage_value(hspf_input, "power", "max", "def")
            return self._ks_hspf_linear(tj, -7.0, power_minus7, 2.0, power_def)

        power_minus7 = self._ks_hspf_stage_value(hspf_input, "power", stage, "-7")
        if frost:
            power_2 = self._ks_hspf_stage_value(hspf_input, "power", stage, "2")
            ratio = self._ks_hspf_correction(
                hspf_input, "power_def_over_nof", 1.0 / 1.06
            )
            power_2 = power_2 * ratio
            return self._ks_hspf_linear(tj, -7.0, power_minus7, 2.0, power_2)

        power_7 = self._ks_hspf_stage_value(hspf_input, "power", stage, "7")
        return self._ks_hspf_linear(tj, -7.0, power_minus7, 7.0, power_7)

    def _ks_hspf_stage_curves(self, tj: float, hspf_input: dict) -> dict:
        return {
            "min": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "min"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "min"),
            },
            "intermediate": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "intermediate"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "intermediate"),
            },
            "rated": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "rated"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "rated"),
            },
            "max": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "max"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "max"),
            },
        }

    def _ks_hspf_interpolate_power_for_load(
        self,
        load: float,
        lower_capacity: float,
        lower_power: float,
        upper_capacity: float,
        upper_power: float
    ) -> float:
        if upper_capacity == lower_capacity:
            return upper_power
        return (
            lower_power
            + (load - lower_capacity)
            / (upper_capacity - lower_capacity)
            * (upper_power - lower_power)
        )

    def _ks_hspf_load_line(self, hspf_input: dict) -> tuple:
        load_line = hspf_input.get("load_line")
        if not isinstance(load_line, dict):
            return None
        if "slope" not in load_line or "intercept" not in load_line:
            return None
        return float(load_line["slope"]), float(load_line["intercept"])

    def _ks_hspf_config_load_line(self, measured_inputs: dict) -> tuple:
        load_line = self._ks_hspf_config().get("load_line")
        if not isinstance(load_line, dict):
            return None
        if "source" not in load_line:
            raise ValueError("Invalid KS C 9306 HSPF load_line: source is required.")
        required_fields = ("zero_load_temp", "full_load_temp", "rated_capacity_factor")
        if any(field not in load_line for field in required_fields):
            raise ValueError(
                "Invalid KS C 9306 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )

        # KS C 9306 HSPF load line
        # Spec text: BLh(0) = BLc(35) x 0.82 (cooling reference)
        # However, official calculation sheet does NOT require cooling rated capacity input.
        # Implementation uses rated_heating_capacity based on official sheet behavior.
        # WARNING: Do NOT change to rated_cooling_capacity without full verification.
        source = load_line["source"]
        allowed_sources = {
            "rated_heating_capacity",
            "rated_cooling_capacity",
            "declared_capacity",
        }
        if source not in allowed_sources:
            raise ValueError(
                f"Invalid KS C 9306 HSPF load_line source: {source}."
            )
        reference_capacity = measured_inputs.get(source)
        if reference_capacity is None:
            return None

        zero_load_temp = float(load_line["zero_load_temp"])
        full_load_temp = float(load_line["full_load_temp"])
        if zero_load_temp == full_load_temp:
            raise ValueError("KS C 9306 HSPF load line temperatures cannot be equal.")
        full_load = float(reference_capacity) * float(load_line["rated_capacity_factor"])
        slope = full_load / (full_load_temp - zero_load_temp)
        intercept = -slope * zero_load_temp
        return slope, intercept

    def _ks_hspf_bin_load(
        self,
        bin_data: dict,
        tj: float,
        hspf_input: dict,
        measured_inputs: dict
    ) -> float:
        if "load" in bin_data:
            return float(bin_data["load"])
        if "heating_load" in bin_data:
            return float(bin_data["heating_load"])

        load_line = (
            self._ks_hspf_load_line(hspf_input)
            or self._ks_hspf_config_load_line(measured_inputs)
        )
        if load_line is None:
            raise ValueError(
                "Missing KS C 9306 HSPF bin load and load line configuration."
            )
        slope, intercept = load_line
        return max(0.0, slope * tj + intercept)

    def _ks_hspf_capacity_line(
        self,
        hspf_input: dict,
        stage: str,
        frost: bool
    ) -> tuple:
        if stage == "max":
            t1 = -7.0
            t2 = 2.0
        elif frost:
            t1 = -7.0
            t2 = 2.0
        else:
            t1 = -7.0
            t2 = 7.0

        c1 = self._ks_hspf_capacity_curve(t1, hspf_input, stage, frost)
        c2 = self._ks_hspf_capacity_curve(t2, hspf_input, stage, frost)
        slope = (c2 - c1) / (t2 - t1)
        intercept = c1 - slope * t1
        return slope, intercept

    def _ks_hspf_intersection_temp(
        self,
        hspf_input: dict,
        stage: str,
        frost: bool,
        load_line: tuple
    ) -> float:
        load_slope, load_intercept = load_line
        capacity_slope, capacity_intercept = self._ks_hspf_capacity_line(
            hspf_input, stage, frost
        )
        denominator = load_slope - capacity_slope
        if denominator == 0:
            raise ValueError("Load line and capacity line are parallel.")
        return (capacity_intercept - load_intercept) / denominator

    def _ks_hspf_power_by_intersection(
        self,
        tj: float,
        hspf_input: dict,
        case_name: str,
        load_line: tuple
    ) -> float:
        frost = self._ks_hspf_is_frost_region(tj)

        if case_name == "minimum_intermediate":
            min_temp = self._ks_hspf_intersection_temp(
                hspf_input, "min", frost, load_line
            )
            intermediate_temp = self._ks_hspf_intersection_temp(
                hspf_input, "intermediate", frost, load_line
            )
            min_power = self._ks_hspf_power_curve(
                min_temp, hspf_input, "min", frost
            )
            intermediate_power = self._ks_hspf_power_curve(
                intermediate_temp, hspf_input, "intermediate", frost
            )
            return self._ks_hspf_linear(
                tj, intermediate_temp, intermediate_power, min_temp, min_power
            )

        if case_name == "intermediate_rated":
            rated_temp = self._ks_hspf_intersection_temp(
                hspf_input, "rated", frost, load_line
            )
            intermediate_temp = self._ks_hspf_intersection_temp(
                hspf_input, "intermediate", frost, load_line
            )
            rated_power = self._ks_hspf_power_curve(
                rated_temp, hspf_input, "rated", frost
            )
            intermediate_power = self._ks_hspf_power_curve(
                intermediate_temp, hspf_input, "intermediate", frost
            )
            return self._ks_hspf_linear(
                tj, rated_temp, rated_power, intermediate_temp, intermediate_power
            )

        if case_name == "rated_maximum":
            rated_temp = self._ks_hspf_intersection_temp(
                hspf_input, "rated", True, load_line
            )
            max_temp = self._ks_hspf_intersection_temp(
                hspf_input, "max", True, load_line
            )
            rated_power = self._ks_hspf_power_curve(
                rated_temp, hspf_input, "rated", True
            )
            max_power = self._ks_hspf_power_curve(
                max_temp, hspf_input, "max", True
            )
            return self._ks_hspf_linear(
                tj, max_temp, max_power, rated_temp, rated_power
            )

        raise ValueError(f"Unsupported KS HSPF intersection case: {case_name}")

    def _ks_hspf_bin(
        self,
        tj: float,
        load: float,
        hours: float,
        hspf_input: dict,
        aux_cop: float = 1.0
    ) -> dict:
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        max_stage = {
            "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "max"),
            "power": self._ks_hspf_power_curve(tj, hspf_input, "max"),
        }

        auxiliary_heat = 0.0
        heat_pump_capacity = load
        capacity_load_ratio = 1.0
        part_load_factor = 1.0
        available_capacity = max_stage["capacity"]
        load_line = self._ks_hspf_load_line(hspf_input)
        min_stage = {"capacity": None, "power": None}
        intermediate_stage = {"capacity": None, "power": None}
        rated_stage = {"capacity": None, "power": None}

        if tj <= 2.0 and load > max_stage["capacity"]:
            operating_case = "maximum_shortage"
            heat_pump_capacity = max_stage["capacity"]
            heat_pump_power = max_stage["power"]
            auxiliary_heat = load - max_stage["capacity"]
        else:
            rated_stage = {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "rated"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "rated"),
            }
            available_capacity = max(max_stage["capacity"], rated_stage["capacity"])
            if load > available_capacity:
                operating_case = "maximum_shortage"
                heat_pump_capacity = available_capacity
                if max_stage["capacity"] >= rated_stage["capacity"]:
                    heat_pump_power = max_stage["power"]
                else:
                    heat_pump_power = rated_stage["power"]
                auxiliary_heat = load - available_capacity
            elif load > rated_stage["capacity"]:
                operating_case = "rated_maximum"
                if load_line is None:
                    heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                        load,
                        rated_stage["capacity"],
                        rated_stage["power"],
                        max_stage["capacity"],
                        max_stage["power"],
                    )
                else:
                    heat_pump_power = self._ks_hspf_power_by_intersection(
                        tj, hspf_input, operating_case, load_line
                    )
            else:
                intermediate_stage = {
                    "capacity": self._ks_hspf_capacity_curve(
                        tj, hspf_input, "intermediate"
                    ),
                    "power": self._ks_hspf_power_curve(
                        tj, hspf_input, "intermediate"
                    ),
                }
                if load > intermediate_stage["capacity"]:
                    operating_case = "intermediate_rated"
                    if load_line is None:
                        heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                            load,
                            intermediate_stage["capacity"],
                            intermediate_stage["power"],
                            rated_stage["capacity"],
                            rated_stage["power"],
                        )
                    else:
                        heat_pump_power = self._ks_hspf_power_by_intersection(
                            tj, hspf_input, operating_case, load_line
                        )
                else:
                    min_stage = {
                        "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "min"),
                        "power": self._ks_hspf_power_curve(tj, hspf_input, "min"),
                    }
                    if load > min_stage["capacity"]:
                        operating_case = "minimum_intermediate"
                        if load_line is None:
                            heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                                load,
                                min_stage["capacity"],
                                min_stage["power"],
                                intermediate_stage["capacity"],
                                intermediate_stage["power"],
                            )
                        else:
                            heat_pump_power = self._ks_hspf_power_by_intersection(
                                tj, hspf_input, operating_case, load_line
                            )
                    else:
                        operating_case = "cyclic_minimum"
                        if min_stage["capacity"] <= 0:
                            heat_pump_power = 0.0
                            capacity_load_ratio = 0.0
                        else:
                            capacity_load_ratio = load / min_stage["capacity"]
                            cd = self._ks_hspf_correction(hspf_input, "cd", self.Cd)
                            part_load_factor = max(
                                1e-6,
                                1.0 - cd * (1.0 - capacity_load_ratio)
                            )
                            heat_pump_power = (
                                min_stage["power"]
                                * capacity_load_ratio
                                / part_load_factor
                            )

        heat_pump_energy = heat_pump_power * hours
        auxiliary_energy = auxiliary_heat * hours / aux_cop
        bin_load = load * hours
        bin_energy = heat_pump_energy + auxiliary_energy
        return {
            "tj": tj,
            "hours": hours,
            "load": load,
            "cap_min": min_stage["capacity"],
            "power_min": min_stage["power"],
            "cap_intermediate": intermediate_stage["capacity"],
            "power_intermediate": intermediate_stage["power"],
            "cap_rated": rated_stage["capacity"],
            "power_rated": rated_stage["power"],
            "cap_max": max_stage["capacity"],
            "power_max": max_stage["power"],
            "available_capacity": available_capacity,
            "heat_pump_capacity": heat_pump_capacity,
            "compressor_heat": heat_pump_capacity,
            "compressor_energy": heat_pump_energy,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_heat": auxiliary_heat,
            "auxiliary_energy": auxiliary_energy,
            "capacity_load_ratio": capacity_load_ratio,
            "part_load_factor": part_load_factor,
            "load_line_used": load_line is not None,
            "bin_load": bin_load,
            "bin_energy": bin_energy,
            "operating_case": operating_case,
        }

    def _calculate_ks_c9306_hspf(
        self,
        measured_inputs: dict,
        aux_cop: float = 1.0
    ) -> dict:
        hspf_input = self._ks_hspf_input(measured_inputs)
        self._validate_ks_c9306_hspf_input(hspf_input)
        hstl = 0.0
        hsec = 0.0
        bin_details = []
        hspf_config = self._ks_hspf_config()
        bin_hours_key = hspf_config.get("bin_hours_key")
        bin_hours = self.config.get(bin_hours_key, self.bin_hours) if bin_hours_key else self.bin_hours

        for bin_data in bin_hours:
            tj = float(bin_data.get("tj", 0))
            hours = float(bin_data.get("nj", bin_data.get("hours", 0)))
            if hours <= 0:
                continue

            load = self._ks_hspf_bin_load(
                bin_data, tj, hspf_input, measured_inputs
            )
            if load <= 0:
                continue

            detail = self._ks_hspf_bin(tj, load, hours, hspf_input, aux_cop)
            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        if hsec <= 0:
            return {"hspf": 0.0, "HSPF": 0.0, "HSTL": hstl, "HSEC": hsec, "bin_details": bin_details}

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
            "bin_details": bin_details
        }

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
        capacity = self._iso_hspf_capacity_curve(temp, stage, resolved, frost)
        power = self._iso_hspf_power_curve(temp, stage, resolved, frost)
        if power <= 0:
            raise ValueError("ISO 16358-2 HSPF boundary power must be positive.")
        return capacity / power

    def _iso_hspf_min_half_power_by_formula_44_48(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
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

    def _iso_hspf_minus7_fallback_factors(self, hspf_cfg: dict) -> tuple:
        minus7_fallback = hspf_cfg.get("external_calculator_minus7_fallback_override", {})
        capacity_factor = minus7_fallback.get("minus7_capacity_factor", 0.64)
        power_factor = minus7_fallback.get("minus7_power_factor", 0.82)
        return float(capacity_factor), float(power_factor)

    def calculate_hspf_iso16358_common(
        self,
        measured_inputs: dict,
        rated_heating_capacity: float,
        aux_cop: float = 1.0
    ) -> dict:
        """
        ISO 16358-2 HSPF common engine (v1: Full/Half stages only).
        """
        # 1. Validation for rated_heating_capacity
        if rated_heating_capacity <= 0:
            raise ValueError("rated_heating_capacity must be positive.")

        # Extract only point dictionaries for resolution
        points_for_resolution = {}
        for k, v in measured_inputs.items():
            if isinstance(v, dict) and "capacity" in v and "power" in v:
                points_for_resolution[k] = v

        # 1. Validation for required measured points
        required_points = ["7_full", "7_half"]
        for p_key in required_points:
            if p_key not in points_for_resolution:
                raise ValueError(f"ISO 16358-2 HSPF requires '{p_key}' measured inputs.")
            p_data = points_for_resolution[p_key]
            # Ensure capacity and power are positive numbers
            if not isinstance(p_data["capacity"], (int, float)) or p_data["capacity"] <= 0:
                raise ValueError(f"Measured point '{p_key}' capacity must be a positive number.")
            if not isinstance(p_data["power"], (int, float)) or p_data["power"] <= 0:
                raise ValueError(f"Measured point '{p_key}' power must be a positive number.")
        for p_key, p_data in points_for_resolution.items():
            if not isinstance(p_data["capacity"], (int, float)) or p_data["capacity"] <= 0:
                raise ValueError(f"Measured point '{p_key}' capacity must be a positive number.")
            if not isinstance(p_data["power"], (int, float)) or p_data["power"] <= 0:
                raise ValueError(f"Measured point '{p_key}' power must be a positive number.")

        hspf_cfg = self.config.get("hspf", {})
        correction_cfg = hspf_cfg.get("correction", {})
        if aux_cop == 1.0:
            aux_cop = correction_cfg.get("aux_cop", 1.0)
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        # 2. Point Resolution - Start with only the validated point dictionaries
        resolved = {k: dict(v) for k, v in points_for_resolution.items()}
        minus7_capacity_factor, minus7_power_factor = (
            self._iso_hspf_minus7_fallback_factors(hspf_cfg)
        )
        
        active_stages = ["full", "half"]
        if "7_min" in resolved:
            active_stages.append("min")

        # Step 1: -7°C derived point (if not measured)
        for stage in active_stages:
            key_m7 = f"-7_{stage}"
            key_7 = f"7_{stage}"
            if key_m7 not in resolved:
                resolved[key_m7] = {
                    "capacity": resolved[key_7]["capacity"] * minus7_capacity_factor,
                    "power": resolved[key_7]["power"] * minus7_power_factor
                }
        
        # Step 2: 2°C point generation (Footnote d / Footnote c)
        # Footnote c: measured 2_half must be re-calculated using footnote d even if it exists.
        # Footnote d: Pi_x(2) = Pi_x(-7) + [Pi_x(7) - Pi_x(-7)] * 9/14
        for stage in active_stages:
            key_2 = f"2_{stage}"
            key_2_f = f"2_{stage}_f"
            key_7 = f"7_{stage}"
            key_m7 = f"-7_{stage}"

            if key_2 in resolved:
                resolved[key_2_f] = dict(resolved[key_2])
            
            calculated_2 = {
                "capacity": resolved[key_m7]["capacity"] + (resolved[key_7]["capacity"] - resolved[key_m7]["capacity"]) * 9.0 / 14.0,
                "power": resolved[key_m7]["power"] + (resolved[key_7]["power"] - resolved[key_m7]["power"]) * 9.0 / 14.0
            }
            if key_2_f not in resolved:
                resolved[key_2_f] = dict(calculated_2)
            resolved[key_2] = dict(calculated_2)

        # 3. Load line parameters
        load_line_cfg = hspf_cfg.get("load_line", {})
        if load_line_cfg.get("source") != "rated_heating_capacity":
            source = load_line_cfg.get("source")
            raise ValueError(f"Unsupported or missing load_line source '{source}' for ISO 16358-2 HSPF.")
        required_load_line_fields = [
            "zero_load_temp",
            "full_load_temp",
            "rated_capacity_factor",
        ]
        if any(field not in load_line_cfg for field in required_load_line_fields):
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )
        zero_load_temp = float(load_line_cfg["zero_load_temp"])
        full_load_temp = float(load_line_cfg["full_load_temp"])
        rated_capacity_factor = float(load_line_cfg["rated_capacity_factor"])
        if zero_load_temp == full_load_temp:
            raise ValueError("Invalid ISO 16358-2 HSPF load_line: zero_load_temp and full_load_temp must differ.")
        if rated_capacity_factor <= 0:
            raise ValueError("Invalid ISO 16358-2 HSPF load_line: rated_capacity_factor must be positive.")
        
        L_h_ref = rated_heating_capacity * rated_capacity_factor
        load_line = (
            -L_h_ref / (zero_load_temp - full_load_temp),
            L_h_ref * zero_load_temp / (zero_load_temp - full_load_temp),
        )
        frost_boundaries = hspf_cfg.get("frost_boundaries", {})
        frost_lower = float(frost_boundaries.get("lower", -7.0))
        frost_upper = float(frost_boundaries.get("upper", 5.5))
        
        # 4. Bin calculation
        hstl, hsec = 0.0, 0.0
        bin_details = []
        bin_hours_key = hspf_cfg.get("bin_hours_key", "hspf_bin_hours")
        hspf_bin_hours = self.config.get(bin_hours_key, [])

        for bin_data in hspf_bin_hours:
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            
            if nj <= 0:
                continue
            
            # BL_h(tj) = L_h_ref * (t_0 - tj) / (t_0 - t_100)
            bl_h = L_h_ref * (zero_load_temp - tj) / (zero_load_temp - full_load_temp)
            
            if bl_h <= 0:
                continue
            
            # Frost determination
            frost = frost_lower < tj < frost_upper
            
            # Capacity and Power curves for Full and Half
            pi_full = self._iso_hspf_capacity_curve(tj, "full", resolved, frost)
            p_full = self._iso_hspf_power_curve(tj, "full", resolved, frost)
            pi_half = self._iso_hspf_capacity_curve(tj, "half", resolved, frost)
            p_half = self._iso_hspf_power_curve(tj, "half", resolved, frost)
            has_min_stage = "min" in active_stages
            if has_min_stage:
                pi_min = self._iso_hspf_capacity_curve(tj, "min", resolved, frost)
                p_min = self._iso_hspf_power_curve(tj, "min", resolved, frost)
            else:
                pi_min = None
                p_min = None
            
            pi_lowest = pi_min if has_min_stage else pi_half
            p_lowest = p_min if has_min_stage else p_half
            
            case = "skip"
            hp_energy = 0.0
            aux_energy = 0.0
            p_j = 0.0
            
            if bl_h <= pi_lowest:
                # Case A: Cycling
                case = "cycling"
                X = bl_h / pi_lowest
                cd = hspf_cfg.get("correction", {}).get("cd", self.Cd)
                plf = 1.0 - cd * (1.0 - X)
                hp_energy = (X * p_lowest / plf) * nj
                p_j = X * p_lowest / plf
            elif has_min_stage and bl_h <= pi_half:
                case = "min_half_interpolation_frost" if frost else "min_half_interpolation"
                p_interp = self._iso_hspf_min_half_power_by_formula_44_48(
                    tj, bl_h, resolved, frost, load_line
                )
                hp_energy = p_interp * nj
                p_j = p_interp
            elif bl_h <= pi_full:
                # Case B: Interpolation
                case = "interpolation"
                # Capacity-linear power interpolation
                p_interp = p_half + (p_full - p_half) * (bl_h - pi_half) / (pi_full - pi_half)
                hp_energy = p_interp * nj
                p_j = p_interp
            else:
                # Case C: Saturated
                case = "saturated"
                hp_energy = p_full * nj
                p_j = p_full
                aux_heat = bl_h - pi_full
                aux_energy = aux_heat * nj / aux_cop
                
            hstl += bl_h * nj
            hsec += hp_energy + aux_energy
            
            bin_details.append({
                "tj": tj,
                "nj": nj,
                "bl_h": bl_h,
                "pi_j": pi_full if bl_h > pi_full else bl_h, # HP output
                "P_j": p_j,
                "case": case,
                "heat_pump_energy": hp_energy,
                "auxiliary_energy": aux_energy,
                "E_j": hp_energy + aux_energy
            })

        if hsec <= 0:
            return {
                "hspf": 0.0,
                "hstl_wh": hstl,
                "hsec_wh": hsec,
                "heat_pump_energy_wh": 0.0,
                "auxiliary_energy_wh": 0.0,
                "bin_details": bin_details
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
            "bin_details": bin_details
        }

    def calculate_hspf(self, measured_inputs: dict, aux_cop: float = 1.0) -> dict:
        measured_inputs = self._prepare_measured_inputs(measured_inputs)
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        profile = self.config.get("hspf", {}).get("profile")
        if profile == "iso16358_2_hspf":
            # Resolve rated_heating_capacity from measured_inputs
            rated_heating_capacity = measured_inputs.get("rated_heating_capacity")
            if rated_heating_capacity is None:
                load_line_cfg = self.config.get("hspf", {}).get("load_line", {})
                source = load_line_cfg.get("source")
                if source == "rated_heating_capacity":
                    raise ValueError("rated_heating_capacity must be provided explicitly in measured_inputs for ISO 16358-2 HSPF.")
                else:
                    raise ValueError(f"Unsupported or missing load_line source '{source}' for ISO 16358-2 HSPF.")

            return self.calculate_hspf_iso16358_common(
                measured_inputs=measured_inputs,
                rated_heating_capacity=float(rated_heating_capacity),
                aux_cop=aux_cop
            )

        if self._has_ks_c9306_hspf_input(measured_inputs):
            return self._calculate_ks_c9306_hspf(measured_inputs, aux_cop)

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
                    "bin_energy": bin_energy
                }

            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        if hsec <= 0:
            return {"hspf": 0.0, "HSPF": 0.0, "HSTL": hstl, "HSEC": hsec, "bin_details": bin_details}

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
            "bin_details": bin_details
        }

    def _profile_capacity_power_at(self, points: dict, load_type: str, tj: float, high_val: int, low_val: int) -> tuple:
        p_35 = points[f"{high_val}_{load_type}"]
        p_29 = points[f"{low_val}_{load_type}"]
        
        c = p_35["capacity"] + (p_29["capacity"] - p_35["capacity"]) / (low_val - high_val) * (tj - high_val)
        p = p_35["power"] + (p_29["power"] - p_35["power"]) / (low_val - high_val) * (tj - high_val)
        return c, p

    def _calculate_cspf_profile(self, measured: dict, L_c_ref: float) -> dict:
        resolved = self._resolve_cspf_profile_points(measured)
        cd = self._get_cspf_profile_cd()
        
        cstl, csec = 0.0, 0.0
        delta_t = self.t_100_load - self.t_0_load
        bin_details = []
        
        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            if nj <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": 0.0,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue
            
            Lc = L_c_ref * (tj - self.t_0_load) / delta_t
            if Lc <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue

            interp = self.interpolate(tj, resolved)
            loads = [(data["capacity"], data["power"], load_type) for load_type, data in interp.items()]
            loads.sort(key=lambda x: x[0])
            
            lowest_cap, lowest_pow, lowest_type = loads[0]
            highest_cap, highest_pow, highest_type = loads[-1]
            
            cooling_output = Lc
            P_tj = 0.0
            
            if Lc <= lowest_cap:
                # 1. Minimum capacity cycling regime
                X = Lc / lowest_cap
                PLF = max(1e-6, 1.0 - cd * (1.0 - X))
                P_tj = (X * lowest_pow) / PLF
            elif Lc > highest_cap:
                # 2. Saturated / Full limit regime (BL > Full Cap)
                cooling_output = highest_cap
                P_tj = highest_pow
            else:
                # 3. Intermediate interpolation regime
                # Use interpolation method
                P_tj = None
                if self.power_interpolation_method == "ks_intersection":
                    P_tj = self._ks_intersection_power(tj, L_c_ref, resolved, lowest_type, highest_type)
                elif self.power_interpolation_method == "iso_boundary_eer":
                    try:
                        profile_cfg = self.config.get("cspf_test_profile", {})
                        if profile_cfg.get("climate_profile") == "T3":
                            for i in range(len(loads) - 1):
                                c1, _, lower_type = loads[i]
                                c2, _, upper_type = loads[i + 1]
                                if c1 < Lc <= c2:
                                    P_tj = self._iso_boundary_eer_power(
                                        tj, Lc, resolved, lower_type, upper_type
                                    )
                                    break
                        else:
                            P_tj = self._iso_boundary_eer_power(
                                tj, Lc, resolved, lowest_type, highest_type
                            )
                    except:
                        P_tj = None
                
                if P_tj is None:
                    # Piecewise direct capacity-power linear interpolation
                    for i in range(len(loads) - 1):
                        c1, p1, _ = loads[i]
                        c2, p2, _ = loads[i+1]
                        if c1 < Lc <= c2:
                            if c2 == c1:
                                P_tj = p1
                            else:
                                P_tj = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                            break
                    
                    if P_tj is None:
                        P_tj = highest_pow
            
            cstl += cooling_output * nj
            csec += P_tj * nj
            
            eer = None
            if P_tj > 0:
                eer = cooling_output / P_tj
                
            bin_details.append({
                "bin_no": idx,
                "tj": tj,
                "nj": nj,
                "lc": Lc,
                "capacity": cooling_output,
                "power": P_tj,
                "eer": eer,
                "cstl_bin": cooling_output * nj,
                "csec_bin": P_tj * nj
            })
            
        if csec <= 0:
            return {"cspf": 0.0, "annual_cooling_kwh": 0.0, "annual_power_kwh": 0.0, "bin_details": bin_details}
            
        return {"cspf": round(cstl / csec, 3), "annual_cooling_kwh": round(cstl / 1000.0, 3), "annual_power_kwh": round(csec / 1000.0, 3), "bin_details": bin_details}

    def calculate_cspf(self, measured_inputs: dict, declared_capacity: float = None) -> dict:
        """
        지역별 설정과 측정값을 융합하여 최종 연간 CSPF 효율 및 전력량을 계산합니다.
        
        Args:
            measured_inputs (dict): UI를 통해 입력받은 실측 포인트 딕셔너리
            declared_capacity (float, optional): 제조사 선언 표기 정격 능력 (W).
                building_load_source가 'declared'인 경우 필수 입력.
            
        Returns:
            dict: CSPF 점수, 연간 냉방량(kWh), 연간 소비전력(kWh)
        """
        measured_inputs = self._prepare_measured_inputs(measured_inputs)
        
        if self._has_cspf_test_profile():
            resolved = self._resolve_cspf_profile_points(measured_inputs)
            # Use reference point from config if available, else 35_full
            ref_key = self.reference_point
            L_c_ref = resolved[ref_key]["capacity"]
            return self._calculate_cspf_profile(measured_inputs, L_c_ref)
            
        resolved_points = self.resolve_points(measured_inputs)
        
        if self.building_load_source == "declared":
            if declared_capacity is None or declared_capacity <= 0:
                raise ValueError(
                    "building_load_source가 'declared'인 지역은 "
                    "declared_capacity(표기 정격 능력)를 입력해야 합니다."
                )
            if self.round_test_values:
                declared_capacity = self._round_test_value(declared_capacity)
            L_c_ref = declared_capacity
        else:
            ref_key = self.reference_point
            if ref_key not in resolved_points:
                raise ValueError(
                    f"Reference point '{ref_key}' not found in resolved points. "
                    f"Check config['reference_point'] or input data."
                )
            L_c_ref = resolved_points[ref_key]["capacity"]
        
        # division by zero 방어
        delta_t = self.t_100_load - self.t_0_load
        if delta_t == 0:
            raise ValueError("t_100_load and t_0_load cannot be equal (division by zero).")
        
        cstl = 0.0  
        csec = 0.0  
        bin_details = []

        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            if nj <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": 0.0,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue

            # a. 건물 냉방 부하 계산 (온도별 능력이 아닌, 고정된 L_c_ref 및 방어된 delta_t 사용)
            Lc = L_c_ref * (tj - self.t_0_load) / delta_t

            if Lc <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue

            # 해당 온도의 부하 조건별 능력/전력 동적 보간
            interp_tj = self.interpolate(tj, resolved_points)
            if "full" not in interp_tj:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue  

            loads = [(data["capacity"], data["power"], load_type) for load_type, data in interp_tj.items()]
            loads.sort(key=lambda x: x[0])
            
            if not loads:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0
                })
                continue
                
            lowest_cap, lowest_pow, _ = loads[0]
            highest_cap, highest_pow, _ = loads[-1]

            # d. 부하 구간 판단 및 소비전력(P_tj) 계산
            cooling_output = Lc
            if Lc <= lowest_cap:
                if lowest_cap <= 0:
                    P_tj = 0.0
                else:
                    X = Lc / lowest_cap
                    # PLF 음수 방어 (1e-6으로 최소값 보장)
                    PLF = max(1e-6, 1.0 - self.Cd * (1.0 - X))
                    P_tj = (X * lowest_pow) / PLF if PLF > 0 else 0.0
            elif Lc > highest_cap:
                cooling_output = highest_cap
                P_tj = highest_pow
            else:
                P_tj = 0.0
                for i in range(len(loads) - 1):
                    c1, p1, _ = loads[i]
                    c2, p2, _ = loads[i+1]
                    if c1 < Lc <= c2:
                        lower_type = loads[i][2]
                        upper_type = loads[i+1][2]
                        ks_power = None
                        if self.power_interpolation_method == "ks_intersection":
                            ks_power = self._ks_intersection_power(
                                tj, L_c_ref, resolved_points, lower_type, upper_type
                            )
                        if ks_power is not None:
                            P_tj = ks_power
                        elif self.power_interpolation_method == "iso_boundary_eer":
                            iso_power = self._iso_boundary_eer_power(
                                tj, Lc, resolved_points, lower_type, upper_type
                            )
                            if iso_power is not None:
                                P_tj = iso_power
                            elif c2 == c1:
                                P_tj = p1
                            else:
                                P_tj = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                        elif c2 == c1:
                            P_tj = p1
                        else:
                            P_tj = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                        break

            # e. 연간 누적
            cstl += cooling_output * nj
            csec += P_tj * nj

            eer = None
            if P_tj > 0:
                eer = cooling_output / P_tj
                
            bin_details.append({
                "bin_no": idx,
                "tj": tj,
                "nj": nj,
                "lc": Lc,
                "capacity": cooling_output,
                "power": P_tj,
                "eer": eer,
                "cstl_bin": cooling_output * nj,
                "csec_bin": P_tj * nj
            })

        if csec <= 0:
            return {"cspf": 0.0, "annual_cooling_kwh": 0.0, "annual_power_kwh": 0.0, "bin_details": bin_details}

        return {
            "cspf": round(cstl / csec, 3),
            "annual_cooling_kwh": round(cstl / 1000.0, 3),
            "annual_power_kwh": round(csec / 1000.0, 3),
            "bin_details": bin_details
        }
