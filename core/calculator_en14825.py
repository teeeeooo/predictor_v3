#calculator_en14825.py

"""
EN 14825:2012 SEER/SCOP 계산 엔진
대상: Non-ducted, Air-to-Air, Variable capacity 1:1 (Reversible)
제약: numpy/pandas 금지, 순수 파이썬만 사용
참고 규격: BS EN 14825:2012 (E)
"""

import json
import os

# ── 냉방 빈 데이터 (Table 36) ─────────────────────────────
COOLING_BIN_TEMPS = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
COOLING_BIN_HOURS = [205, 227, 225, 225, 216, 215, 218, 197, 178, 158, 137, 109, 88, 63, 39, 31, 24, 17, 13, 9, 4, 3, 1, 0]

# ── 냉방 설계조건 (Table 2, Air-to-air) ──────────────────
T_DESIGN_C = 35   # 설계 외기온도 (°C)
H_CE       = 350  # 등가 냉방시간 (h), Annex D Table D.1

# ── 테스트 포인트 외기온도 (Table 2) ─────────────────────
T_A = 35  # 조건A: 100% 부하
T_B = 30  # 조건B:  74% 부하
T_C = 25  # 조건C:  47% 부하
T_D = 20  # 조건D:  21% 부하

# ── 대기전력 운전 시간 — Reversible 기준 (Annex D) ───────
H_TO  = 221    # thermostat-off 시간 (h), Table D.1
H_SB  = 2142   # standby 시간 (h), Table D.1
H_CK  = 2672   # crankcase heater 시간 (h), Table D.3 Reversible
H_OFF = 0      # off 시간 (h), Table D.1 Reversible = 0

# ── 열화계수 기본값 (규격 6.4.2.1) ───────────────────────
CD_DEFAULT = 0.25

class EN14825Calculator:
    """EN 14825:2012 SEER/SCOP 계산기"""

    def __init__(self, scop_config_path: str = None):
        if scop_config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scop_config_path = os.path.join(base_dir, "data", "region_configs", "en14825_scop.json")

        self.scop_config_path = scop_config_path
        self.scop_config = self._load_scop_config(scop_config_path)

    def _load_scop_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"SCOP config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def _validate_test_points(self, test_points: dict):
        """테스트 포인트 데이터의 무결성 검증 (피드백 4)"""
        required_keys = ["A", "B", "C", "D"]
        for k in required_keys:
            if k not in test_points:
                raise ValueError(f"Missing test point: {k}")
            capa, power = test_points[k]
            if capa <= 0 or power <= 0:
                raise ValueError(f"Invalid value at {k}: capa={capa}, power={power}")

    def _get_part_load_ratio(self, tj: float, t_design_c: float) -> float:
        """
        빈 온도 Tj에서의 부분부하율 계산 (규격 식 4)
        Part load ratio = (Tj - 16) / (T_design_c - 16)
        """
        ratio = (tj - 16.0) / (t_design_c - 16.0)
        return min(ratio, 1.0)  # 조건A 온도 초과 시 1.0으로 제한

    def _interpolate_capa_and_power(self, tj: float, test_points: dict) -> tuple:
        """빈 온도 Tj에서 능력(kW)과 소비전력(kW)을 각각 독립 선형보간."""
        t_a, t_b, t_c, t_d = T_A, T_B, T_C, T_D

        if tj >= t_a:
            return test_points["A"]
        if tj <= t_d:
            return test_points["D"]

        if t_d < tj <= t_c:
            ratio = (tj - t_d) / (t_c - t_d)
            lo, hi = test_points["D"], test_points["C"]
        elif t_c < tj <= t_b:
            ratio = (tj - t_c) / (t_b - t_c)
            lo, hi = test_points["C"], test_points["B"]
        else:  # t_b < tj < t_a
            ratio = (tj - t_b) / (t_a - t_b)
            lo, hi = test_points["B"], test_points["A"]

        capa  = lo[0] + ratio * (hi[0] - lo[0])
        power = lo[1] + ratio * (hi[1] - lo[1])
        return (capa, power)

    def _get_pc_and_eer_pl(self, tj: float, test_points: dict, p_design_c: float, t_design_c: float, cd: float) -> tuple:
        """
        빈 온도 Tj에서의 실제 적용 부하(Pc) 및 EERpl 동시 산출.
        (피드백 1, 2, 3, 5, 6 반영)

        Returns:
            (pc, eer_pl) 튜플
        """
        # 해당 빈의 요구 부하 (raw 값)
        plr = self._get_part_load_ratio(tj, t_design_c)
        pc_raw  = p_design_c * plr

        if tj <= T_D:
            # ② Tj <= 20°C: 조건D가 최소 운전 step
            capa_avail, power_active = test_points["D"]
            
            # [피드백 2] 요구 부하(Pc)는 장비의 최소 능력(Qmin)을 초과할 수 없음
            pc = min(pc_raw, capa_avail)
            
            cr = pc / capa_avail if capa_avail > 0 else 0.0
            cr = min(cr, 1.0)
            
            eer_dc = capa_avail / power_active
            
            # [피드백 5] Cd 패널티 팩터가 극단값에서 음수가 되지 않도록 방어
            factor = max(0.0, 1.0 - cd * (1.0 - cr))
            eer_pl = eer_dc * factor
        else:
            # ① Tj > 20°C: 능력/전력 각각 보간 후 확인
            capa_avail, power_active = self._interpolate_capa_and_power(tj, test_points)
            
            # [피드백 3] 0 이하 전력에 대한 방어 로직
            if power_active <= 0:
                raise ValueError(f"Invalid interpolated power at Tj={tj}: {power_active}")
                
            # [피드백 1] Capacity Limit 반영: 장비 능력이 부하에 못 미치면 풀로드 운전 처리
            if capa_avail < pc_raw:
                pc = capa_avail
            else:
                pc = pc_raw
                
            eer_pl = capa_avail / power_active

        return pc, eer_pl

    # [버그 2 수정]: p_design_c 인자 추가 및 내부 할당 코드 삭제
    def _calculate_seer_on(
        self,
        test_points: dict,
        p_design_c: float,
        t_design_c: float,
        cd: float,
    ) -> float:
        """
        SEERon 계산 (규격 식 3)
        """
        numerator   = 0.0  # Σ(hj × Pc(Tj))
        denominator = 0.0  # Σ(hj × Pc(Tj) / EERpl(Tj))

        for tj, hj in zip(COOLING_BIN_TEMPS, COOLING_BIN_HOURS):
            if hj == 0:
                continue

            # [피드백 6] 계산을 한 번만 하도록 _get_pc_and_eer_pl 호출 구조로 통일
            pc, eer_pl = self._get_pc_and_eer_pl(tj, test_points, p_design_c, t_design_c, cd)

            if pc <= 0:
                continue

            if eer_pl <= 0:
                raise ValueError(f"Calculated EERpl is <= 0 at Tj={tj}")

            numerator   += hj * pc
            denominator += hj * (pc / eer_pl)

        if denominator == 0:
            raise ValueError("SEERon 계산 오류: 분모가 0입니다. test_points 값을 확인하세요.")

        return numerator / denominator

    # [버그 1 수정]: 들여쓰기 4칸 정렬
    def calculate_seer(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                       p_design_c: float, # A포인트와 분리하여 독립적으로 받음
                       t_design_c: float = T_DESIGN_C, cd: float = CD_DEFAULT) -> dict:
        """
        EN 14825 SEER 계산
        """
        self._validate_test_points(test_points)

        # 1. 연간 냉방수요 Qc (kWh) — 입력받은 설계 부하 사용
        qc_kwh = p_design_c * H_CE
        
        # 2. SEERon 계산 — 보간 로직에 p_design_c 전달
        seer_on = self._calculate_seer_on(test_points, p_design_c, t_design_c, cd)        
       
        standby_kwh = (H_TO * p_to) + (H_SB * p_sb) + (H_CK * p_ck) + (H_OFF * p_off)
        
        active_kwh   = qc_kwh / seer_on
        total_kwh    = active_kwh + standby_kwh
        seer = qc_kwh / total_kwh

        return {
            "seer":     round(seer, 3),
            "seer_on":  round(seer_on, 3),
            "qc_kwh":   round(qc_kwh, 2),
        }

    def _normalize_climate(self, climate: str) -> str:
        if not isinstance(climate, str):
            raise ValueError("climate must be one of: average, warmer, colder")
        climate_key = climate.strip().lower()
        aliases = {
            "avg": "average",
            "a": "average",
            "w": "warmer",
            "c": "colder",
        }
        return aliases.get(climate_key, climate_key)

    def _get_scop_climate_data(self, climate: str) -> dict:
        climate_key = self._normalize_climate(climate)
        climates = self.scop_config.get("climates", {})
        if climate_key not in climates:
            raise ValueError(f"Unknown SCOP climate: {climate}. Expected one of {sorted(climates.keys())}")

        climate_data = climates[climate_key]
        temps = climate_data.get("heating_bin_temps_c", [])
        hours = climate_data.get("heating_bin_hours", [])
        if len(temps) != len(hours):
            raise ValueError(f"SCOP climate {climate_key} bin temperature/hour length mismatch.")
        if any(h < 0 for h in hours):
            raise ValueError(f"SCOP climate {climate_key} bin hours must not contain negative values.")

        expected_total = climate_data.get("heating_bin_hours_total")
        if expected_total is not None and sum(hours) != expected_total:
            raise ValueError(
                f"SCOP climate {climate_key} bin hour total mismatch: "
                f"actual={sum(hours)}, expected={expected_total}"
            )

        return climate_data

    def _get_scop_operational_hours(self, climate: str, appliance_type: str) -> dict:
        climate_key = self._normalize_climate(climate)
        hours_by_type = self.scop_config.get("operational_hours", {})
        if appliance_type not in hours_by_type:
            raise ValueError(
                f"Unknown SCOP appliance_type: {appliance_type}. "
                f"Expected one of {sorted(hours_by_type.keys())}"
            )
        try:
            return hours_by_type[appliance_type][climate_key]
        except KeyError as exc:
            raise ValueError(f"Missing SCOP operational hours for {appliance_type}/{climate_key}") from exc

    def _parse_scop_point(self, test_points: dict, key: str) -> dict:
        if key not in test_points:
            raise ValueError(f"Missing SCOP test point: {key}")

        value = test_points[key]
        if isinstance(value, dict):
            if "capacity" not in value or "power" not in value:
                raise ValueError(f"SCOP test point {key} must include capacity and power.")
            capacity = float(value["capacity"])
            power = float(value["power"])
            temp_c = value.get("temp_c", value.get("outdoor_db_c"))
        else:
            capacity, power = value
            capacity = float(capacity)
            power = float(power)
            temp_c = None

        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid SCOP test point {key}: capacity={capacity}, power={power}")

        return {
            "capacity": capacity,
            "power": power,
            "cop_pl": self._safe_div(capacity, power),
            "temp_c": float(temp_c) if temp_c is not None else None,
        }

    def _get_scop_point_temp(
        self,
        key: str,
        point: dict,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> float:
        if point.get("temp_c") is not None:
            return point["temp_c"]

        schema = self.scop_config.get("heating_test_point_schema", {})
        if key in ("A", "B", "C", "D"):
            try:
                return float(schema[key]["outdoor_db_c"])
            except KeyError as exc:
                raise ValueError(f"Missing SCOP schema temperature for point {key}") from exc

        if key == "Tbiv":
            return float(tbiv_temp_c if tbiv_temp_c is not None else climate_data["tbiv_max_c"])
        if key == "TOL":
            return float(tol_temp_c if tol_temp_c is not None else climate_data["tol_max_c"])

        raise ValueError(f"Unknown SCOP test point key: {key}")

    def _validate_scop_points(
        self,
        test_points: dict,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        required_keys = ("A", "B", "C", "D", "TOL", "Tbiv")
        points = {}
        for key in required_keys:
            point = self._parse_scop_point(test_points, key)
            point["temp_c"] = self._get_scop_point_temp(key, point, climate_data, tbiv_temp_c, tol_temp_c)
            points[key] = point

        if points["Tbiv"]["temp_c"] > climate_data["tbiv_max_c"]:
            raise ValueError(
                f"Tbiv exceeds climate maximum: {points['Tbiv']['temp_c']} > {climate_data['tbiv_max_c']}"
            )
        if points["TOL"]["temp_c"] > climate_data["tol_max_c"]:
            raise ValueError(
                f"TOL exceeds climate maximum: {points['TOL']['temp_c']} > {climate_data['tol_max_c']}"
            )
        if points["TOL"]["temp_c"] > points["Tbiv"]["temp_c"]:
            raise ValueError(
                f"TOL must be <= Tbiv for SCOP heating calculation: "
                f"TOL={points['TOL']['temp_c']}, Tbiv={points['Tbiv']['temp_c']}"
            )
        if climate_data.get("label") == "Colder" and points["TOL"]["temp_c"] < -20:
            raise ValueError(
                "EN 14825 colder climate with TOL below -20°C requires an additional -15°C "
                "capacity/COPPL calculation point. This input schema does not include that point yet."
            )

        return points

    def _heating_part_load(self, tj: float, p_design_h: float, t_design_h: float) -> float:
        if p_design_h <= 0:
            raise ValueError(f"p_design_h must be > 0 for SCOP calculation: {p_design_h}")
        if t_design_h == 16:
            raise ValueError("t_design_h cannot be 16°C for SCOP heating load line.")

        ph = p_design_h * (tj - 16.0) / (t_design_h - 16.0)
        return max(0.0, ph)

    def _scop_capacity_cop_at_temp(self, tj: float, points: dict) -> tuple:
        tol_temp = points["TOL"]["temp_c"]
        if tj < tol_temp:
            return 0.0, 0.0, "below_tol_heat_pump_off"

        pairs = []
        for key, point in points.items():
            pairs.append((point["temp_c"], point["capacity"], point["cop_pl"], key))
        pairs.sort(key=lambda item: item[0])

        if tj <= pairs[0][0]:
            _, capacity, cop_pl, key = pairs[0]
            return capacity, cop_pl, f"clamped_to_{key}"

        if tj >= pairs[-1][0]:
            _, capacity, cop_pl, key = pairs[-1]
            return capacity, cop_pl, f"clamped_to_{key}"

        for i in range(len(pairs) - 1):
            t1, c1, cop1, k1 = pairs[i]
            t2, c2, cop2, k2 = pairs[i + 1]
            if t1 <= tj <= t2:
                capacity = self._linear(tj, t1, c1, t2, c2)
                cop_pl = self._linear(tj, t1, cop1, t2, cop2)
                return max(0.0, capacity), max(0.0, cop_pl), f"linear_{k1}_{k2}"

        raise ValueError(f"SCOP interpolation failed at Tj={tj}")

    def _scop_bin_energy_terms(self, ph: float, pdh: float, cop_pl: float) -> tuple:
        if ph <= 0:
            return 0.0, 0.0, 0.0, "no_heating_load"
        if pdh <= 0 or cop_pl <= 0:
            return 0.0, 0.0, ph, "electric_backup_only"

        elbu = max(0.0, ph - pdh)
        heat_pump_load = ph - elbu
        operating_case = "capacity_shortfall_with_backup" if elbu > 0 else "heat_pump_covers_load"
        return cop_pl, heat_pump_load, elbu, operating_case

    def _calculate_scop_on(self, points: dict, climate_data: dict, p_design_h: float, cd: float) -> dict:
        temps = climate_data["heating_bin_temps_c"]
        hours = climate_data["heating_bin_hours"]
        t_design_h = float(climate_data["t_design_h_c"])

        numerator = 0.0
        denominator = 0.0
        bin_details = []

        for tj, hj in zip(temps, hours):
            if hj <= 0:
                continue

            ph = self._heating_part_load(float(tj), p_design_h, t_design_h)
            if ph <= 0:
                continue

            pdh, cop_pl, interpolation = self._scop_capacity_cop_at_temp(float(tj), points)
            cop_bin, heat_pump_load, elbu, operating_case = self._scop_bin_energy_terms(ph, pdh, cop_pl)
            if heat_pump_load > 0 and cop_bin <= 0:
                raise ValueError(f"SCOP COPPL must be > 0 at Tj={tj}")

            numerator += hj * ph
            denominator += hj * (self._safe_div(heat_pump_load, cop_bin) + elbu)

            bin_details.append({
                "temp_c": tj,
                "hours": hj,
                "ph": round(ph, 6),
                "pdh": round(pdh, 6),
                "cop_pl": round(cop_pl, 6) if cop_pl > 0 else 0.0,
                "equivalent_power": round(self._safe_div(pdh, cop_pl), 6) if cop_pl > 0 else 0.0,
                "cop_bin": round(cop_bin, 6) if cop_bin > 0 else 0.0,
                "heat_pump_load": round(heat_pump_load, 6),
                "elbu": round(elbu, 6),
                "operating_case": operating_case,
                "interpolation": interpolation,
            })

        if numerator <= 0:
            raise ValueError("SCOPon calculation error: heating demand numerator must be > 0.")
        if denominator <= 0:
            raise ValueError("SCOPon calculation error: energy denominator must be > 0.")

        return {
            "scop_on": numerator / denominator,
            "active_heating_kwh": numerator,
            "active_energy_kwh": denominator,
            "bin_details": bin_details,
        }

    def calculate_scop(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_h: float,
        climate: str,
        cd: float = None,
        appliance_type: str = None,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        """
        EN 14825 / EU 206/2012 SCOP calculation path.

        Required test_points: A, B, C, D, TOL, Tbiv.
        Each value may be either (capacity, power) or
        {"capacity": kW, "power": kW, "temp_c": optional outdoor dry-bulb}.
        """
        climate_key = self._normalize_climate(climate)
        climate_data = self._get_scop_climate_data(climate_key)
        defaults = self.scop_config.get("defaults", {})
        if cd is None:
            cd = defaults.get("degradation_coefficient", CD_DEFAULT)
        if appliance_type is None:
            appliance_type = defaults.get("appliance_type", "reversible")

        points = self._validate_scop_points(test_points, climate_data, tbiv_temp_c, tol_temp_c)
        operational_hours = self._get_scop_operational_hours(climate_key, appliance_type)
        scop_on_data = self._calculate_scop_on(points, climate_data, p_design_h, cd)

        q_h = p_design_h * operational_hours["h_he"]
        if q_h <= 0:
            raise ValueError(f"Reference annual heating demand must be > 0: {q_h}")

        standby_kwh = (
            operational_hours["h_to"] * p_to
            + operational_hours["h_sb"] * p_sb
            + operational_hours["h_ck"] * p_ck
            + operational_hours["h_off"] * p_off
        )
        active_kwh = self._safe_div(q_h, scop_on_data["scop_on"])
        total_kwh = active_kwh + standby_kwh
        if total_kwh <= 0:
            raise ValueError("SCOP calculation error: total annual heating energy must be > 0.")

        scop = q_h / total_kwh
        return {
            "scop": round(scop, 3),
            "SCOP": round(scop, 3),
            "scop_on": round(scop_on_data["scop_on"], 3),
            "qh_kwh": round(q_h, 3),
            "active_kwh": round(active_kwh, 3),
            "standby_kwh": round(standby_kwh, 3),
            "total_kwh": round(total_kwh, 3),
            "climate": climate_key,
            "appliance_type": appliance_type,
            "p_design_h": p_design_h,
            "operational_hours": operational_hours,
            "source": self.scop_config.get("source", {}),
            "bin_details": scop_on_data["bin_details"],
            "unimplemented_notes": [
                "The current API treats user-entered A/B/C/D/TOL/Tbiv capacity and power as already resolved part-load declared points for EN 14825 Clause 7.4.",
                "If raw capacity-control step data is required, Clause 7.4.2.2 variable-capacity closest-step and +/-10% logic needs an expanded input schema.",
                "SCOPnet from Equation (10) is not returned because the requested output is SCOP.",
            ],
        }

if __name__ == "__main__":
    # 검증용 예시: 5kW 기기, 조건A EER=3.0 가정
    calc = EN14825Calculator()
    test_pts = {
        "A": (5.000, 5.000 / 3.00),  # EER 3.0
        "B": (3.700, 3.700 / 3.50),  # EER 3.5
        "C": (2.350, 2.350 / 4.10),  # EER 4.1
        "D": (1.050, 1.050 / 4.80),  # EER 4.8
    }
    
    # [버그 3 수정]: p_design_c 인자 추가
    result = calc.calculate_seer(
        test_points=test_pts,
        p_to=0.030,   # thermostat-off 소비전력 (kW)
        p_sb=0.005,   # standby (kW)
        p_ck=0.010,   # crankcase heater (kW)
        p_off=0.000,  # off (reversible이므로 0)
        p_design_c=5.000 # 5kW 기기로 가정
    )
    print("=== EN 14825 SEER 계산 결과 ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
