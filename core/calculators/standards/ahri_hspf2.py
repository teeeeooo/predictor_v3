"""Stable AHRI 210/240 HSPF2 public facade."""

import warnings

from ._ahri.hspf2_context import HSPF2ConfigContext
from ._ahri.hspf2_performance import HSPF2VariablePerformance
from ._ahri.hspf2_points import HSPF2PointResolver
from ._ahri.hspf2_variable import HSPF2VariableCapacityEngine


class AHRIHSPF2Calculator:
    """Compatibility facade for variable-capacity and legacy HSPF2 paths."""

    def __init__(self, config_path: str):
        self._context = HSPF2ConfigContext(config_path)
        for attribute in (
            "config",
            "bin_temps",
            "bin_hours",
            "canonical_hspf2_bin_tables",
            "test_point_schema",
            "test_point_aliases",
            "test_point_temps",
            "constants",
            "defaults",
        ):
            setattr(self, attribute, getattr(self._context, attribute))
        self._point_resolver = HSPF2PointResolver(self.test_point_schema, self.test_point_aliases)
        self._performance = HSPF2VariablePerformance()
        self._variable_engine = HSPF2VariableCapacityEngine(self._context, self._point_resolver)

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return self._performance.safe_div(num, den, fallback)

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        return self._performance.linear(x, x1, y1, x2, y2)

    def _round_nearest_025(self, value: float) -> float:
        return self._performance.round_nearest_025(value)

    def _get_region_iv_heating_bin_table(self) -> dict:
        return self._context.region_iv_heating_bin_table()

    def _get_point(self, test_points: dict, key: str) -> tuple:
        return self._point_resolver.get_point(test_points, key)

    def _schema_keys(self) -> set:
        return self._point_resolver.schema_keys()

    def _match_key_case_insensitive(self, key: str, candidates) -> str:
        return self._point_resolver.match_key_case_insensitive(key, candidates)

    def get_test_point_schema(self, mode: str = None) -> dict:
        return self._point_resolver.get_test_point_schema(mode)

    def legacy_to_canonical(self, test_points: dict) -> dict:
        return self._point_resolver.legacy_to_canonical(test_points)

    def canonical_to_internal_usage(self, test_points: dict) -> dict:
        return self._point_resolver.canonical_to_internal_usage(test_points)

    def _validate_canonical_full_load_points(self, test_points: dict) -> tuple:
        canonical_points = self.legacy_to_canonical(test_points)
        h12 = self._get_point(canonical_points, "H12")
        h22 = self._get_point(canonical_points, "H22")
        h32 = self._get_point(canonical_points, "H32")
        try:
            h42 = self._get_point(canonical_points, "H42")
            h42_source = "provided"
        except ValueError:
            schema = self.test_point_schema["heating"]
            h22_temp = schema["H22"]["outdoor_db_f"]
            h32_temp = schema["H32"]["outdoor_db_f"]
            h42_temp = schema["H42"]["outdoor_db_f"]
            q_h22, p_h22 = h22
            q_h32, p_h32 = h32
            h42 = (
                self._linear(h42_temp, h32_temp, q_h32, h22_temp, q_h22),
                self._linear(h42_temp, h32_temp, p_h32, h22_temp, p_h22),
            )
            h42_source = "extrapolated"
        points = {"H12": h12, "H22": h22, "H32": h32, "H42": h42}
        for key, (capacity, power) in points.items():
            if capacity <= 0 or power <= 0:
                raise ValueError(
                    f"Invalid canonical test point {key}: capacity={capacity}, power={power}"
                )
        return points, h42_source

    def _canonical_capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        schema = self.test_point_schema["heating"]
        h12_temp = schema["H12"]["outdoor_db_f"]
        h22_temp = schema["H22"]["outdoor_db_f"]
        h32_temp = schema["H32"]["outdoor_db_f"]
        h42_temp = schema["H42"]["outdoor_db_f"]
        q_h12, p_h12 = full_points["H12"]
        q_h22, p_h22 = full_points["H22"]
        q_h32, p_h32 = full_points["H32"]
        q_h42, p_h42 = full_points["H42"]
        if temp_f >= h22_temp:
            q_tj = self._linear(temp_f, h22_temp, q_h22, h12_temp, q_h12)
            p_tj = self._linear(temp_f, h22_temp, p_h22, h12_temp, p_h12)
        elif temp_f >= h32_temp:
            q_tj = self._linear(temp_f, h32_temp, q_h32, h22_temp, q_h22)
            p_tj = self._linear(temp_f, h32_temp, p_h32, h22_temp, p_h22)
        else:
            q_tj = self._linear(temp_f, h42_temp, q_h42, h32_temp, q_h32)
            p_tj = self._linear(temp_f, h42_temp, p_h42, h32_temp, p_h32)
        return max(0.0, q_tj), max(0.0, p_tj)

    def _canonical_low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        point_temps = {"H11": 47, "H2V": 35, "H31": 17}
        points = []
        for key in ("H11", "H2V", "H31"):
            value = low_points.get(key)
            if value is None:
                continue
            capacity, power = value
            if capacity <= 0 or power <= 0:
                raise ValueError(
                    f"Invalid canonical low-speed test point {key}: capacity={capacity}, power={power}"
                )
            points.append((point_temps[key], capacity, power))
        if len(points) < 2:
            return None, None
        points.sort(reverse=True)
        for idx in range(len(points) - 1):
            high_temp, q_high, p_high = points[idx]
            low_temp, q_low, p_low = points[idx + 1]
            if high_temp >= temp_f >= low_temp:
                return max(0.0, self._linear(temp_f, high_temp, q_high, low_temp, q_low)), max(
                    0.0, self._linear(temp_f, high_temp, p_high, low_temp, p_low)
                )
        if temp_f > points[0][0]:
            x1, q1, p1 = points[0]
            x2, q2, p2 = points[1]
        else:
            x1, q1, p1 = points[-2]
            x2, q2, p2 = points[-1]
        return max(0.0, self._linear(temp_f, x1, q1, x2, q2)), max(
            0.0, self._linear(temp_f, x1, p1, x2, p2)
        )

    def _validate_full_load_points(self, test_points: dict) -> dict:
        return self._point_resolver.validate_legacy_full_load_points(test_points)

    def _capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        h1_temp = self.test_point_temps.get("H1_full", 47)
        h2_temp = self.test_point_temps.get("H2_full", 17)
        h3_temp = self.test_point_temps.get("H3_full", 5)
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

    def _get_positive_point(self, test_points: dict, key: str) -> tuple:
        return self._point_resolver.positive_point(test_points, key)

    def _require_ahri_kwargs(self, kwargs: dict) -> tuple:
        return self._context._require_ahri_kwargs(kwargs)

    def _cert_low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        return self._performance.low_capacity_power_at_temp(temp_f, low_points)

    def _cert_minimum_limited_low_capacity_power_at_temp(
        self, temp_f: float, low_points: dict, h2int_point: tuple, int_point_at_temp: tuple
    ) -> tuple:
        return self._performance.minimum_limited_low_capacity_power_at_temp(
            temp_f, low_points, h2int_point, int_point_at_temp
        )

    def _cert_full_capacity_power_at_temp(
        self, temp_f: float, full_points: dict, nominal_point: tuple, h4_point: tuple = None
    ) -> tuple:
        return self._performance.full_capacity_power_at_temp(
            temp_f, full_points, nominal_point, h4_point
        )

    def _cert_intermediate_capacity_power_at_temp(
        self, temp_f: float, h2int_point: tuple, low_points: dict, full_points: dict
    ) -> tuple:
        return self._performance.intermediate_capacity_power_at_temp(
            temp_f, h2int_point, low_points, full_points
        )

    def _cert_delta_at_bin(self, temp_f: float, cop: float, t_off: float, t_on: float) -> float:
        return self._performance.delta_at_bin(temp_f, cop, t_off, t_on)

    def _resolve_h12_full_capacity_point(
        self, canonical_points: dict, full_points: dict, h1_nom: tuple, **kwargs
    ):
        return self._point_resolver._resolve_h12(canonical_points, full_points, h1_nom, kwargs)

    def _resolve_h22_full_capacity_point(self, canonical_points: dict, full_points: dict):
        return self._point_resolver._resolve_h22(canonical_points, full_points)

    def _calculate_hspf2_v3_ahri(self, test_points: dict, **kwargs) -> dict:
        return self._variable_engine.calculate(test_points, **kwargs)

    def _building_load_at_temp(self, temp_f: float, design_load: float) -> float:
        balance_temp = self.constants.get("balance_temp_f", 65)
        design_temp = self.constants.get("design_temp_f", 5)
        load = design_load * self._safe_div(balance_temp - temp_f, balance_temp - design_temp)
        return max(0.0, load)

    def _building_load_v3(
        self, temp_f: float, q_h1_calc: float, c_vs: float, t_zl: float, t_od: float
    ) -> float:
        return self._performance.building_load(temp_f, q_h1_calc, c_vs, t_zl, t_od)

    def calculate_hspf2_v2(self, test_points: dict, **kwargs) -> dict:
        full_points = self._validate_full_load_points(test_points)
        if len(self.bin_temps) != len(self.bin_hours):
            raise ValueError("bin_temps and bin_hours must have the same length.")
        q_h3, _ = full_points["H3_Full"]
        design_load = kwargs.get("design_load_btu", q_h3)
        aux_cop = kwargs.get("aux_cop", self.defaults.get("aux_cop", 1.0))
        aux_eer = aux_cop * 3.412
        total_heating_btu = 0.0
        total_energy_wh = 0.0
        bin_details = []
        for i, temp_f in enumerate(self.bin_temps):
            hours = self.bin_hours[i]
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

    def calculate_hspf2_v3(self, test_points: dict, **kwargs) -> dict:
        return self._variable_engine.calculate(test_points, **kwargs)

    def calculate_hspf2(self, test_points: dict, **kwargs) -> dict:
        return self.calculate_hspf2_v3(test_points, **kwargs)
