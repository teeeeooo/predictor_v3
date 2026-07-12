"""Current AHRI variable-capacity SEER2 seasonal engine."""


class SEER2VariableCapacityEngine:
    def __init__(self, config: dict):
        self.config = config
        self.bin_temps = config["bin_data"]["bin_temps"]
        self.bin_hours = config["bin_data"]["bin_hours"]
        temps = config["test_point_temps"]
        self.t_A = temps["temp_A_full"]
        self.t_B = temps["temp_B_full"]
        self.t_F = temps["temp_F_low"]
        self.t_E = temps.get("temp_E_int", 87)
        self.sf = config["constants"]["sf"]
        self.v_factor_map = config["constants"]["v_factor"]
        self.cd_default_low = config["defaults"]["cd_default_low"]

    @staticmethod
    def _safe_div(num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _compute_intermediate_slopes(self, test_points):
        q_A, P_A = test_points["A_Full"]
        q_B, P_B = test_points["B_Full"]
        q_Blow, P_Blow = test_points["B_Low"]
        q_E, P_E = test_points["E_Int"]
        q_F, P_F = test_points["F_Low"]
        q_Low_E = q_F + (q_Blow - q_F) * self._safe_div(
            self.t_E - self.t_F, self.t_B - self.t_F
        )
        P_Low_E = P_F + (P_Blow - P_F) * self._safe_div(
            self.t_E - self.t_F, self.t_B - self.t_F
        )
        q_Full_E = q_B + (q_A - q_B) * self._safe_div(
            self.t_E - self.t_B, self.t_A - self.t_B
        )
        P_Full_E = P_B + (P_A - P_B) * self._safe_div(
            self.t_E - self.t_B, self.t_A - self.t_B
        )
        n_cq = max(0.0, min(1.0, self._safe_div(q_E - q_Low_E, q_Full_E - q_Low_E)))
        n_ce = max(0.0, min(1.0, self._safe_div(P_E - P_Low_E, P_Full_E - P_Low_E)))
        m_cq = self._safe_div(q_Blow - q_F, self.t_B - self.t_F) * (
            1 - n_cq
        ) + self._safe_div(q_A - q_B, self.t_A - self.t_B) * n_cq
        m_ce = self._safe_div(P_Blow - P_F, self.t_B - self.t_F) * (
            1 - n_ce
        ) + self._safe_div(P_A - P_B, self.t_A - self.t_B) * n_ce
        return m_cq, m_ce

    def _compute_intermediate_at_temp(self, tj, q_E, P_E, m_cq, m_ce):
        return max(0.0, q_E + m_cq * (tj - self.t_E)), max(
            0.0, P_E + m_ce * (tj - self.t_E)
        )

    def _calculate_case1(self, building_load, q_low, p_low, hours, cd):
        clf = self._safe_div(building_load, q_low)
        plf = 1.0 - cd * (1.0 - clf)
        return clf * q_low * hours, self._safe_div(clf * p_low * hours, plf)

    def _calculate_case2(self, building_load, q_low, q_high, eer_low, eer_high, hours):
        eer_bin = eer_low + self._safe_div(eer_high - eer_low, q_high - q_low) * (
            building_load - q_low
        )
        eer_bin = max(min(eer_low, eer_high), min(eer_bin, max(eer_low, eer_high)))
        return building_load * hours, self._safe_div(building_load * hours, eer_bin), eer_bin

    def calculate(self, test_points, system_type="HP", p_w_off=0.0, cd_low=None):
        cd_low = cd_low if cd_low is not None else self.cd_default_low
        sys_key = system_type.upper()
        if sys_key not in self.v_factor_map:
            raise ValueError(
                f"Invalid system_type: {system_type}. 허용값: {list(self.v_factor_map.keys())}"
            )
        v_factor = self.v_factor_map[sys_key]
        q_A, P_A = test_points["A_Full"]
        q_B, P_B = test_points["B_Full"]
        q_Blow, P_Blow = test_points["B_Low"]
        q_E, P_E = test_points["E_Int"]
        q_F, P_F = test_points["F_Low"]
        eer2_a_full = self._safe_div(q_A, P_A)
        eer2_b_low = self._safe_div(q_Blow, P_Blow)
        m_cq, m_ce = self._compute_intermediate_slopes(test_points)
        sum_q_j, sum_e_j = 0.0, 0.0
        bin_details = []
        for i, tj in enumerate(self.bin_temps):
            hours = self.bin_hours[i]
            q_low = q_F + (q_Blow - q_F) * self._safe_div(
                tj - self.t_F, self.t_B - self.t_F
            )
            p_low = P_F + (P_Blow - P_F) * self._safe_div(
                tj - self.t_F, self.t_B - self.t_F
            )
            q_full = q_B + (q_A - q_B) * self._safe_div(
                tj - self.t_B, self.t_A - self.t_B
            )
            p_full = P_B + (P_A - P_B) * self._safe_div(
                tj - self.t_B, self.t_A - self.t_B
            )
            q_int, p_int = self._compute_intermediate_at_temp(tj, q_E, P_E, m_cq, m_ce)
            q_int = max(q_low, min(q_int, q_full))
            if p_int <= 0:
                raise ValueError(f"Invalid intermediate power: temp={tj}, P_Int={p_int}")
            eer_low = self._safe_div(q_low, p_low)
            eer_int = self._safe_div(q_int, p_int)
            eer_full = self._safe_div(q_full, p_full)
            building_load = self._safe_div(tj - 65.0, self.t_A - 65.0) * (q_A / self.sf) * v_factor
            eer_int_bin = None
            if building_load <= q_low:
                case = 1
                q_j, e_j = self._calculate_case1(building_load, q_low, p_low, hours, cd_low)
            elif building_load < q_int:
                case = 2.1
                q_j, e_j, eer_int_bin = self._calculate_case2(
                    building_load, q_low, q_int, eer_low, eer_int, hours
                )
            elif building_load < q_full:
                case = 2.2
                q_j, e_j, eer_int_bin = self._calculate_case2(
                    building_load, q_int, q_full, eer_int, eer_full, hours
                )
            else:
                case = 3
                q_j, e_j = q_full * hours, p_full * hours
            sum_q_j += q_j
            sum_e_j += e_j
            bin_details.append(
                {
                    "bin": i + 1,
                    "temp_F": tj,
                    "BL": round(building_load, 2),
                    "q_Low": round(q_low, 2),
                    "q_Int": round(q_int, 2),
                    "q_Full": round(q_full, 2),
                    "P_Int": round(p_int, 2),
                    "EER_Low": round(eer_low, 2),
                    "EER_Int": round(eer_int, 2),
                    "EER_Full": round(eer_full, 2),
                    "EER_IntBin": round(eer_int_bin, 2) if eer_int_bin else None,
                    "case": case,
                    "q_j": round(q_j, 2),
                    "E_j": round(e_j, 2),
                }
            )
        seer2 = self._safe_div(sum_q_j, sum_e_j)
        return {
            "SEER2": round(seer2, 3),
            "EER2_A_Full": round(eer2_a_full, 3),
            "EER2_B_Low": round(eer2_b_low, 3),
            "total_cooling_Btu": round(sum_q_j, 3),
            "total_energy_Wh": round(sum_e_j, 3),
            "system_type": system_type,
            "bin_details": bin_details,
        }
