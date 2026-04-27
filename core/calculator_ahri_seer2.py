"""
core/calculator_ahri_seer2.py
AHRI 210/240-2026 기준 Variable Speed (Air-to-Air, Non-ducted) 냉방 SEER2 계산 모듈
안전성 및 유지보수성을 극대화한 Refactored Version
"""

import json

config_data = {
  "standard": "AHRI 210/240-2023",
  "mode": "cooling",
  "unit_system": "imperial",
  "bin_data": {
    "bin_temps": [67, 72, 77, 82, 87, 92, 97, 102],
    "bin_hours": [0.214, 0.231, 0.216, 0.161, 0.104, 0.052, 0.018, 0.004]
  },
  "test_point_temps": {
    "temp_A_full": 95,
    "temp_B_full": 82,
    "temp_B_low": 82,
    "temp_E_int": 87,
    "temp_F_low": 67
  },
  "constants": {
    "sf": 1.1,
    "v_factor": {
        "HP": 0.93,
        "AC": 1.0
    }
  },
  "defaults": {
    "cd_default_low": 0.25,
    "cd_default_full": 0.25
  }
}
with open('usa.json', 'w') as f:
    json.dump(config_data, f)

class AHRICalculator:
    """AHRI 210/240-2026 SEER2 계산기 (Variable Capacity 시스템 대상)"""

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        self.bin_temps = self.config['bin_data']['bin_temps']
        self.bin_hours = self.config['bin_data']['bin_hours']
        
        temps = self.config['test_point_temps']
        self.t_A = temps['temp_A_full']  # 95
        self.t_B = temps['temp_B_full']  # 82
        self.t_F = temps['temp_F_low']   # 67
        self.t_E = temps.get('temp_E_int', 87) # 87
        
        self.sf = self.config['constants']['sf']
        self.v_factor_map = self.config['constants']['v_factor']
        self.cd_default_low = self.config['defaults']['cd_default_low']

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _compute_intermediate_slopes(self, test_points):
        q_A, P_A = test_points["A_Full"]
        q_B, P_B = test_points["B_Full"]
        q_Blow, P_Blow = test_points["B_Low"]
        q_E, P_E = test_points["E_Int"]
        q_F, P_F = test_points["F_Low"]

        q_Low_E = q_F + (q_Blow - q_F) * self._safe_div(self.t_E - self.t_F, self.t_B - self.t_F)
        P_Low_E = P_F + (P_Blow - P_F) * self._safe_div(self.t_E - self.t_F, self.t_B - self.t_F)
        q_Full_E = q_B + (q_A - q_B) * self._safe_div(self.t_E - self.t_B, self.t_A - self.t_B)
        P_Full_E = P_B + (P_A - P_B) * self._safe_div(self.t_E - self.t_B, self.t_A - self.t_B)

        N_Cq = self._safe_div(q_E - q_Low_E, q_Full_E - q_Low_E)
        N_CE = self._safe_div(P_E - P_Low_E, P_Full_E - P_Low_E)

        N_Cq = max(0.0, min(1.0, N_Cq))
        N_CE = max(0.0, min(1.0, N_CE))

        M_Cq = self._safe_div(q_Blow - q_F, self.t_B - self.t_F) * (1 - N_Cq) + self._safe_div(q_A - q_B, self.t_A - self.t_B) * N_Cq
        M_CE = self._safe_div(P_Blow - P_F, self.t_B - self.t_F) * (1 - N_CE) + self._safe_div(P_A - P_B, self.t_A - self.t_B) * N_CE

        return M_Cq, M_CE

    def _compute_intermediate_at_temp(self, tj: float, q_E: float, P_E: float, M_Cq: float, M_CE: float):
        q_Int_tj = q_E + M_Cq * (tj - self.t_E)
        P_Int_tj = P_E + M_CE * (tj - self.t_E)
        return max(0.0, q_Int_tj), max(0.0, P_Int_tj)

    def _calculate_case1(self, BL: float, q_Low: float, P_Low: float, nj: float, cd: float):
        CLF = self._safe_div(BL, q_Low)
        PLF = 1.0 - cd * (1.0 - CLF)
        q_j = CLF * q_Low * nj
        E_j = self._safe_div(CLF * P_Low * nj, PLF)
        return q_j, E_j

    def _calculate_case2_low_int(self, BL: float, q_Low: float, q_Int: float, EER_Low: float, EER_Int: float, nj: float):
        EER_IntBin = EER_Low + self._safe_div(EER_Int - EER_Low, q_Int - q_Low) * (BL - q_Low)
        eer_min = min(EER_Low, EER_Int)
        eer_max = max(EER_Low, EER_Int)
        EER_IntBin = max(eer_min, min(EER_IntBin, eer_max))
        return BL * nj, self._safe_div(BL * nj, EER_IntBin), EER_IntBin

    def _calculate_case2_int_full(self, BL: float, q_Int: float, q_Full: float, EER_Int: float, EER_Full: float, nj: float):
        EER_IntBin = EER_Int + self._safe_div(EER_Full - EER_Int, q_Full - q_Int) * (BL - q_Int)
        eer_min = min(EER_Int, EER_Full)
        eer_max = max(EER_Int, EER_Full)
        EER_IntBin = max(eer_min, min(EER_IntBin, eer_max))
        return BL * nj, self._safe_div(BL * nj, EER_IntBin), EER_IntBin

    def _calculate_case3(self, q_Full: float, P_Full: float, nj: float):
        return q_Full * nj, P_Full * nj

    def calculate_seer2(self, test_points, system_type="HP", p_w_off=0.0, cd_low=None):
        cd_low = cd_low if cd_low is not None else self.cd_default_low
        
        sys_key = system_type.upper()
        if sys_key not in self.v_factor_map:
            raise ValueError(f"Invalid system_type: {system_type}. 허용값: {list(self.v_factor_map.keys())}")
        v_factor = self.v_factor_map[sys_key]
        
        q_A, P_A = test_points["A_Full"]
        q_B, P_B = test_points["B_Full"]
        q_Blow, P_Blow = test_points["B_Low"]
        q_E, P_E = test_points["E_Int"]
        q_F, P_F = test_points["F_Low"]

        EER2_A_Full = self._safe_div(q_A, P_A)
        EER2_B_Low = self._safe_div(q_Blow, P_Blow)
        
        M_Cq, M_CE = self._compute_intermediate_slopes(test_points)
        
        sum_q_j, sum_E_j = 0.0, 0.0
        bin_details = []
        zero_load_t = 65.0

        for i, tj in enumerate(self.bin_temps):
            nj = self.bin_hours[i]
            
            q_Low_tj = q_F + (q_Blow - q_F) * self._safe_div(tj - self.t_F, self.t_B - self.t_F)
            P_Low_tj = P_F + (P_Blow - P_F) * self._safe_div(tj - self.t_F, self.t_B - self.t_F)
            
            q_Full_tj = q_B + (q_A - q_B) * self._safe_div(tj - self.t_B, self.t_A - self.t_B)
            P_Full_tj = P_B + (P_A - P_B) * self._safe_div(tj - self.t_B, self.t_A - self.t_B)
            
            q_Int_tj, P_Int_tj = self._compute_intermediate_at_temp(tj, q_E, P_E, M_Cq, M_CE)

            q_Int_tj = max(q_Low_tj, min(q_Int_tj, q_Full_tj))
            # P_Int 클램핑 제거 및 ValueError 방어 로직 추가
            if P_Int_tj <= 0:
                raise ValueError(f"Invalid intermediate power: temp={tj}, P_Int={P_Int_tj}")

            EER_Low_tj = self._safe_div(q_Low_tj, P_Low_tj)
            EER_Int_tj = self._safe_div(q_Int_tj, P_Int_tj)
            EER_Full_tj = self._safe_div(q_Full_tj, P_Full_tj)

            BL_tj = self._safe_div(tj - zero_load_t, self.t_A - zero_load_t) * (q_A / self.sf) * v_factor
            
            EER_IntBin = None

            if BL_tj <= q_Low_tj:
                case = 1
                q_j, E_j = self._calculate_case1(BL_tj, q_Low_tj, P_Low_tj, nj, cd_low)
            elif BL_tj < q_Int_tj:
                case = 2.1
                q_j, E_j, EER_IntBin = self._calculate_case2_low_int(BL_tj, q_Low_tj, q_Int_tj, EER_Low_tj, EER_Int_tj, nj)
            elif BL_tj < q_Full_tj:
                case = 2.2
                q_j, E_j, EER_IntBin = self._calculate_case2_int_full(BL_tj, q_Int_tj, q_Full_tj, EER_Int_tj, EER_Full_tj, nj)
            else:
                case = 3
                q_j, E_j = self._calculate_case3(q_Full_tj, P_Full_tj, nj)
                
            sum_q_j += q_j
            sum_E_j += E_j
            
            bin_details.append({
                "bin": i + 1,
                "temp_F": tj,
                "BL": round(BL_tj, 2),
                "q_Low": round(q_Low_tj, 2),
                "q_Int": round(q_Int_tj, 2),
                "q_Full": round(q_Full_tj, 2),
                "P_Int": round(P_Int_tj, 2),
                "EER_Low": round(EER_Low_tj, 2),
                "EER_Int": round(EER_Int_tj, 2),
                "EER_Full": round(EER_Full_tj, 2),
                "EER_IntBin": round(EER_IntBin, 2) if EER_IntBin else None,
                "case": case,
                "q_j": round(q_j, 2),
                "E_j": round(E_j, 2),
            })
            
        SEER2 = self._safe_div(sum_q_j, sum_E_j)
        
        return {
            "SEER2": round(SEER2, 3),
            "EER2_A_Full": round(EER2_A_Full, 3),
            "EER2_B_Low": round(EER2_B_Low, 3),
            "total_cooling_Btu": round(sum_q_j, 3),
            "total_energy_Wh": round(sum_E_j, 3),
            "system_type": system_type,
            "bin_details": bin_details
        }
