"""Legacy HSPF2 v2 calculation owner."""

import warnings


class HSPF2LegacyEngine:
    def __init__(self, context, point_resolver):
        self.context = context
        self.point_resolver = point_resolver

    @staticmethod
    def _safe_div(num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def _capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        h1_temp = self.context.test_point_temps.get("H1_full", 47)
        h2_temp = self.context.test_point_temps.get("H2_full", 17)
        h3_temp = self.context.test_point_temps.get("H3_full", 5)
        q_h1, p_h1 = full_points["H1_Full"]
        q_h2, p_h2 = full_points["H2_Full"]
        q_h3, p_h3 = full_points["H3_Full"]
        if temp_f >= h2_temp:
            q_tj = self._linear(temp_f, h2_temp, q_h2, h1_temp, q_h1)
            p_tj = self._linear(temp_f, h2_temp, p_h2, h1_temp, p_h1)
        else:
            q_tj = self._linear(temp_f, h3_temp, q_h3, h2_temp, q_h2)
            p_tj = self._linear(temp_f, h3_temp, p_h3, h2_temp, p_h2)
        return max(0.0, q_tj), max(0.0, p_tj)

    def _building_load_at_temp(self, temp_f: float, design_load: float) -> float:
        balance_temp = self.context.constants.get("balance_temp_f", 65)
        design_temp = self.context.constants.get("design_temp_f", 5)
        load = design_load * self._safe_div(
            balance_temp - temp_f, balance_temp - design_temp
        )
        return max(0.0, load)

    def calculate(self, test_points: dict, **kwargs) -> dict:
        full_points = self.point_resolver.validate_legacy_full_load_points(test_points)
        if len(self.context.bin_temps) != len(self.context.bin_hours):
            raise ValueError("bin_temps and bin_hours must have the same length.")
        q_h3, _ = full_points["H3_Full"]
        design_load = kwargs.get("design_load_btu", q_h3)
        aux_cop = kwargs.get("aux_cop", self.context.defaults.get("aux_cop", 1.0))
        aux_eer = aux_cop * 3.412
        total_heating_btu = 0.0
        total_energy_wh = 0.0
        bin_details = []
        for i, temp_f in enumerate(self.context.bin_temps):
            hours = self.context.bin_hours[i]
            if hours <= 0:
                continue
            building_load = self._building_load_at_temp(temp_f, design_load)
            q_full, p_full = self._capacity_power_at_temp(temp_f, full_points)
            if building_load <= 0:
                case = 0
                q_delivered = compressor_energy = q_aux = e_aux = 0.0
            elif building_load <= q_full:
                case = 1
                load_ratio = self._safe_div(building_load, q_full)
                q_delivered = building_load * hours
                compressor_energy = p_full * load_ratio * hours
                q_aux = e_aux = 0.0
            else:
                case = 2
                q_delivered = building_load * hours
                compressor_energy = p_full * hours
                q_aux = (building_load - q_full) * hours
                e_aux = self._safe_div(q_aux, aux_eer)
            e_j = compressor_energy + e_aux
            total_heating_btu += q_delivered
            total_energy_wh += e_j
            bin_details.append(
                {
                    "bin": i + 1,
                    "temp_F": temp_f,
                    "hours": hours,
                    "case": case,
                    "building_load": round(building_load, 2),
                    "q_full": round(q_full, 2),
                    "p_full": round(p_full, 2),
                    "q_j": round(q_delivered, 2),
                    "E_j": round(e_j, 2),
                    "q_aux": round(q_aux, 2),
                    "e_aux": round(e_aux, 2),
                    "aux_ratio": round(self._safe_div(e_aux, e_j), 4) if e_j > 0 else 0.0,
                }
            )
        if total_energy_wh <= 0:
            raise ValueError("HSPF2 calculation error: total_energy_wh must be > 0.")
        if total_heating_btu <= 0:
            raise ValueError("HSPF2 calculation error: total_heating_Btu must be > 0.")
        hspf2 = self._safe_div(total_heating_btu, total_energy_wh)
        if hspf2 < 2 or hspf2 > 20:
            warnings.warn(f"HSPF2 sanity warning: calculated value is outside 2-20 range ({hspf2:.3f})")
        return {
            "HSPF2": round(hspf2, 3),
            "total_heating_Btu": round(total_heating_btu, 3),
            "total_energy_Wh": round(total_energy_wh, 3),
            "bin_details": bin_details,
        }
