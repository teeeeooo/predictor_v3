#calculator_en14825.py

"""
EN 14825:2012 SEER/SCOP 계산 엔진
대상: Non-ducted, Air-to-Air, Variable capacity 1:1 (Reversible)
제약: numpy/pandas 금지, 순수 파이썬만 사용
참고 규격: BS EN 14825:2012 (E)
"""

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