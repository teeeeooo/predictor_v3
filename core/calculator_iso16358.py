# core/calculator_iso16358.py

import json
import os
from decimal import Decimal, ROUND_HALF_UP

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
                    prepared[point_key][data_key] = self._round_test_value(value)
                else:
                    prepared[point_key][data_key] = value

        return prepared

    def resolve_points(self, measured_inputs: dict) -> dict:
        """
        입력된 측정값(measure)과 JSON의 파생 규칙(default)을 해석하여
        계산에 필요한 모든 포인트의 딕셔너리를 완성합니다.
        
        Args:
            measured_inputs (dict): UI에서 입력받은 측정값
        Returns:
            dict: 모든 포인트가 채워진 딕셔너리
        """
        resolved = {}

        # 1. "measure" 포인트 우선 처리
        for point_key, point_type in self.points_config.items():
            if point_type == "measure":
                if point_key in measured_inputs:
                    resolved[point_key] = measured_inputs[point_key]
                else:
                    raise ValueError(f"필수 측정값 누락: '{point_key}' 포인트 데이터가 없습니다.")

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

        for bin_data in self.bin_hours:
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            if nj <= 0:
                continue

            # a. 건물 냉방 부하 계산 (온도별 능력이 아닌, 고정된 L_c_ref 및 방어된 delta_t 사용)
            Lc = L_c_ref * (tj - self.t_0_load) / delta_t

            if Lc <= 0:
                continue

            # 해당 온도의 부하 조건별 능력/전력 동적 보간
            interp_tj = self.interpolate(tj, resolved_points)
            if "full" not in interp_tj:
                continue  

            loads = [(data["capacity"], data["power"], load_type) for load_type, data in interp_tj.items()]
            loads.sort(key=lambda x: x[0])
            
            if not loads:
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
                        elif c2 == c1:
                            P_tj = p1
                        else:
                            P_tj = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                        break

            # e. 연간 누적
            cstl += cooling_output * nj
            csec += P_tj * nj

        if csec <= 0:
            return {"cspf": 0.0, "annual_cooling_kwh": 0.0, "annual_power_kwh": 0.0}

        return {
            "cspf": round(cstl / csec, 3),
            "annual_cooling_kwh": round(cstl / 1000.0, 3),
            "annual_power_kwh": round(csec / 1000.0, 3)
        }
