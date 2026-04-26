"""
core/calculator_ahri_hspf2.py
AHRI 210/240 HSPF2 calculation module scaffold.

The HSPF2 rules are intentionally kept separate from the SEER2 engine until the
heating path is validated. Shared helpers are duplicated locally for now.
"""

import json
import os
import warnings
from decimal import Decimal, ROUND_HALF_UP


class AHRIHSPF2Calculator:
    """AHRI 210/240 HSPF2 calculator scaffold for variable-capacity systems."""

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.bin_temps = self.config["bin_data"]["bin_temps"]
        self.bin_hours = self.config["bin_data"]["bin_hours"]
        self.canonical_hspf2_bin_tables = self.config.get("canonical_hspf2_bin_tables", {})
        self.test_point_schema = self.config.get("test_point_schema", {})
        self.test_point_aliases = self.config.get("test_point_aliases", {})
        self.test_point_temps = self.config.get("test_point_temps", {})
        self.constants = self.config.get("constants", {})
        self.defaults = self.config.get("defaults", {})

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def _round_nearest_025(self, value: float) -> float:
        step = Decimal("0.025")
        rounded_units = (Decimal(str(value)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return float(rounded_units * step)

    def _get_region_iv_heating_bin_table(self) -> dict:
        try:
            table = self.canonical_hspf2_bin_tables["heating"]["region_iv"]
        except KeyError as exc:
            raise ValueError("Missing canonical Region IV heating bin table for HSPF2 v3.") from exc

        bin_temps = table.get("bin_temps_f", [])
        fractional_hours = table.get("fractional_bin_hours", [])
        if len(bin_temps) != len(fractional_hours):
            raise ValueError("Region IV bin_temps_f and fractional_bin_hours must have the same length.")
        if not bin_temps:
            raise ValueError("Region IV bin table must not be empty.")
        if any(hours < 0 for hours in fractional_hours):
            raise ValueError("Region IV fractional_bin_hours must not contain negative values.")

        expected_sum = table.get("fractional_bin_hours_sum")
        if expected_sum is not None:
            actual_sum = round(sum(fractional_hours), 3)
            if actual_sum != round(expected_sum, 3):
                raise ValueError(
                    f"Region IV fractional bin hour sum mismatch: actual={actual_sum}, expected={expected_sum}"
                )

        return table

    def _get_point(self, test_points: dict, key: str) -> tuple:
        if key in test_points:
            return test_points[key]

        key_lower = key.lower()
        for candidate_key, value in test_points.items():
            if candidate_key.lower() == key_lower:
                return value

        raise ValueError(f"Missing test point: {key}")

    def _schema_keys(self) -> set:
        keys = set()
        for mode_points in self.test_point_schema.values():
            if isinstance(mode_points, dict):
                keys.update(mode_points.keys())
        return keys

    def _match_key_case_insensitive(self, key: str, candidates) -> str:
        if key in candidates:
            return key

        key_lower = key.lower()
        for candidate in candidates:
            if candidate.lower() == key_lower:
                return candidate

        return key

    def get_test_point_schema(self, mode: str = None) -> dict:
        if mode is None:
            return self.test_point_schema
        return self.test_point_schema.get(mode, {})

    def legacy_to_canonical(self, test_points: dict) -> dict:
        legacy_map = self.test_point_aliases.get("legacy_to_canonical", {})
        schema_keys = self._schema_keys()
        canonical_points = {}

        for key, value in test_points.items():
            legacy_key = self._match_key_case_insensitive(key, legacy_map.keys())
            canonical_key = legacy_map.get(legacy_key, key)
            canonical_key = self._match_key_case_insensitive(canonical_key, schema_keys)

            if canonical_key in canonical_points and canonical_points[canonical_key] != value:
                raise ValueError(
                    f"Conflicting test point values for canonical key {canonical_key}: "
                    f"{canonical_points[canonical_key]} vs {value}"
                )
            canonical_points[canonical_key] = value

        return canonical_points

    def canonical_to_internal_usage(self, test_points: dict) -> dict:
        canonical_points = self.legacy_to_canonical(test_points)
        internal_map = self.test_point_aliases.get("canonical_to_internal_hspf2_v2", {})
        internal_points = {}

        for key, value in canonical_points.items():
            canonical_key = self._match_key_case_insensitive(key, internal_map.keys())
            internal_key = internal_map.get(canonical_key, key)

            if internal_key in internal_points and internal_points[internal_key] != value:
                raise ValueError(
                    f"Conflicting test point values for internal key {internal_key}: "
                    f"{internal_points[internal_key]} vs {value}"
                )
            internal_points[internal_key] = value

        return internal_points

    def _validate_canonical_full_load_points(self, test_points: dict) -> tuple:
        canonical_points = self.legacy_to_canonical(test_points)

        h12 = self._get_point(canonical_points, "H12")
        h32 = self._get_point(canonical_points, "H32")
        try:
            h42 = self._get_point(canonical_points, "H42")
            h42_source = "provided"
        except ValueError:
            h12_temp = self.test_point_schema["heating"]["H12"]["outdoor_db_f"]
            h32_temp = self.test_point_schema["heating"]["H32"]["outdoor_db_f"]
            h42_temp = self.test_point_schema["heating"]["H42"]["outdoor_db_f"]

            q_h12, p_h12 = h12
            q_h32, p_h32 = h32
            h42 = (
                self._linear(h42_temp, h12_temp, q_h12, h32_temp, q_h32),
                self._linear(h42_temp, h12_temp, p_h12, h32_temp, p_h32),
            )
            h42_source = "extrapolated"

        points = {
            "H12": h12,
            "H32": h32,
            "H42": h42,
        }
        for key, (capacity, power) in points.items():
            if capacity <= 0 or power <= 0:
                raise ValueError(f"Invalid canonical test point {key}: capacity={capacity}, power={power}")

        return points, h42_source

    def _canonical_capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        h12_temp = self.test_point_schema["heating"]["H12"]["outdoor_db_f"]
        h32_temp = self.test_point_schema["heating"]["H32"]["outdoor_db_f"]
        h42_temp = self.test_point_schema["heating"]["H42"]["outdoor_db_f"]

        q_h12, p_h12 = full_points["H12"]
        q_h32, p_h32 = full_points["H32"]
        q_h42, p_h42 = full_points["H42"]

        if temp_f >= h12_temp:
            q_tj = self._linear(temp_f, h32_temp, q_h32, h12_temp, q_h12)
            p_tj = self._linear(temp_f, h32_temp, p_h32, h12_temp, p_h12)
        elif temp_f >= h32_temp:
            q_tj = self._linear(temp_f, h32_temp, q_h32, h12_temp, q_h12)
            p_tj = self._linear(temp_f, h32_temp, p_h32, h12_temp, p_h12)
        else:
            q_tj = self._linear(temp_f, h42_temp, q_h42, h32_temp, q_h32)
            p_tj = self._linear(temp_f, h42_temp, p_h42, h32_temp, p_h32)

        return max(0.0, q_tj), max(0.0, p_tj)

    def _canonical_low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        # TODO(P2): H11/H21/H31은 predictor_v3 canonical low-speed 임시 명칭이다.
        # AHRI Table 8 alias 및 35 F point의 H2Low/H2Int 매핑은 full path에서 재검토한다.
        low_point_temps = {
            "H11": 47,
            "H21": 35,
            "H31": 17,
        }
        points = []
        for key in ("H11", "H21", "H31"):
            value = low_points.get(key)
            if value is None:
                continue

            capacity, power = value
            if capacity <= 0 or power <= 0:
                raise ValueError(f"Invalid canonical low-speed test point {key}: capacity={capacity}, power={power}")
            points.append((low_point_temps[key], capacity, power))

        if len(points) < 2:
            return None, None

        points.sort(reverse=True)
        for idx in range(len(points) - 1):
            high_temp, q_high, p_high = points[idx]
            low_temp, q_low, p_low = points[idx + 1]
            if high_temp >= temp_f >= low_temp:
                q_tj = self._linear(temp_f, high_temp, q_high, low_temp, q_low)
                p_tj = self._linear(temp_f, high_temp, p_high, low_temp, p_low)
                return max(0.0, q_tj), max(0.0, p_tj)

        # TODO(P2): Low-speed 외삽 허용 범위는 AHRI full path 정리 시 확정한다.
        if temp_f > points[0][0]:
            x1, q1, p1 = points[0]
            x2, q2, p2 = points[1]
        else:
            x1, q1, p1 = points[-2]
            x2, q2, p2 = points[-1]

        q_tj = self._linear(temp_f, x1, q1, x2, q2)
        p_tj = self._linear(temp_f, x1, p1, x2, p2)
        return max(0.0, q_tj), max(0.0, p_tj)

    def _validate_full_load_points(self, test_points: dict) -> dict:
        points = {
            "H1_Full": self._get_point(test_points, "H1_Full"),
            "H2_Full": self._get_point(test_points, "H2_Full"),
            "H3_Full": self._get_point(test_points, "H3_Full"),
        }

        for key, (capacity, power) in points.items():
            if capacity <= 0 or power <= 0:
                raise ValueError(f"Invalid test point {key}: capacity={capacity}, power={power}")

        return points

    def _capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        h1_temp = self.test_point_temps.get("H1_full", 47)
        h2_temp = self.test_point_temps.get("H2_full", 17)
        h3_temp = self.test_point_temps.get("H3_full", 5)

        q_h1, p_h1 = full_points["H1_Full"]
        q_h2, p_h2 = full_points["H2_Full"]
        q_h3, p_h3 = full_points["H3_Full"]

        if temp_f >= h1_temp:
            q_tj = self._linear(temp_f, h2_temp, q_h2, h1_temp, q_h1)
            p_tj = self._linear(temp_f, h2_temp, p_h2, h1_temp, p_h1)
        elif temp_f >= h2_temp:
            q_tj = self._linear(temp_f, h2_temp, q_h2, h1_temp, q_h1)
            p_tj = self._linear(temp_f, h2_temp, p_h2, h1_temp, p_h1)
        else:
            q_tj = self._linear(temp_f, h3_temp, q_h3, h2_temp, q_h2)
            p_tj = self._linear(temp_f, h3_temp, p_h3, h2_temp, p_h2)

        return max(0.0, q_tj), max(0.0, p_tj)

    def _building_load_at_temp(self, temp_f: float, design_load: float) -> float:
        balance_temp = self.constants.get("balance_temp_f", 65)
        design_temp = self.constants.get("design_temp_f", 5)
        load = design_load * self._safe_div(balance_temp - temp_f, balance_temp - design_temp)
        return max(0.0, load)

    def _building_load_v3(
        self,
        temp_f: float,
        q_h1_calc: float,
        c_vs: float,
        t_zl: float,
        t_od: float,
    ) -> float:
        """
        AHRI 210/240 Eq. 11.104 건물 부하선 (variable capacity 전용).

        현재 단계에서는 q_h1_calc를 H12 capacity로 대체 사용한다.
        이는 v3 simplified canonical path의 임시 구현이며,
        추후 H1_calc/H2Int/H3Full 기반 AHRI full variable-capacity path에서 재검토한다.
        """
        denom = t_zl - t_od
        load = q_h1_calc * c_vs * self._safe_div(t_zl - temp_f, denom)
        return max(0.0, load)

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
                q_delivered = 0.0
                compressor_energy = 0.0
                q_aux = 0.0
                e_aux = 0.0
            elif building_load <= q_full:
                case = 1
                load_ratio = self._safe_div(building_load, q_full)
                q_delivered = building_load * hours
                compressor_energy = p_full * load_ratio * hours
                q_aux = 0.0
                e_aux = 0.0
            else:
                case = 2
                q_delivered = building_load * hours
                compressor_energy = p_full * hours
                q_aux = (building_load - q_full) * hours
                e_aux = self._safe_div(q_aux, aux_eer)

            E_j = compressor_energy + e_aux
            total_heating_btu += q_delivered
            total_energy_wh += E_j

            bin_details.append({
                "bin": i + 1,
                "temp_F": temp_f,
                "hours": hours,
                "case": case,
                "building_load": round(building_load, 2),
                "q_full": round(q_full, 2),
                "p_full": round(p_full, 2),
                "q_j": round(q_delivered, 2),
                "E_j": round(E_j, 2),
                "q_aux": round(q_aux, 2),
                "e_aux": round(e_aux, 2),
                "aux_ratio": round(self._safe_div(e_aux, E_j), 4) if E_j > 0 else 0.0,
            })

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
        """
        Canonical-schema HSPF2 calculation path.

        This intentionally keeps the current v2 simplified full-load model while
        moving input handling to AHRI Analytics canonical heating keys.
        """
        full_points, h42_source = self._validate_canonical_full_load_points(test_points)
        canonical_points = self.legacy_to_canonical(test_points)
        low_points = {
            "H11": canonical_points.get("H11"),
            "H21": canonical_points.get("H21"),
            "H31": canonical_points.get("H31"),
        }
        bin_table = self._get_region_iv_heating_bin_table()
        c_d = self.defaults.get("cd_default_low", 0.25)
        bin_temps = bin_table["bin_temps_f"]
        fractional_bin_hours = bin_table["fractional_bin_hours"]
        hlh = bin_table["heating_load_hours"]
        bin_hours = [frac * hlh for frac in fractional_bin_hours]

        # NOTE(AHRI 210/240 Section 11.2.2.3, Eq. 11.104):
        # q_H1_calc는 Heating Load Line의 기준 capacity 인자이다.
        # 현재 v3는 Standard 시스템용 simplified canonical fallback으로
        # H12 capacity(47 F H1_Full)를 q_H1_calc로 그대로 사용한다.
        # H32/H42는 Tj 성능 보간/외삽에만 사용하며 q_H1_calc 보정에는
        # 사용하지 않는다. Full variable-capacity path에서는 H1_calc
        # 결정 로직을 별도로 재검토한다.
        h1_full_capacity_btu, _ = full_points["H12"]
        q_h1_calc = h1_full_capacity_btu
        assert q_h1_calc > 0
        assert q_h1_calc == h1_full_capacity_btu
        c_vs  = bin_table.get("variable_capacity_slope_factor", 1.07)
        t_zl  = bin_table.get("zero_load_temp_f", 55)
        t_od  = bin_table.get("outdoor_design_temp_f", 5)
        t_obo = self.constants.get("t_OBO", 45)
        defrost_control_type = self.constants.get("defrost_control_type", "demand")
        defrost_t_test_minutes = self.constants.get("defrost_t_test_minutes", 90)
        defrost_t_max_minutes = self.constants.get("defrost_t_max_minutes", 720)
        aux_cop = kwargs.get("aux_cop", self.defaults.get("aux_cop", 1.0))
        aux_eer = aux_cop * 3.412

        def _calculate_f_def(constants: dict) -> float:
            # AHRI 210/240 Eq. 11.107: Ttest/Tmax는 온도가 아니라
            # defrost termination 사이 시간[minutes]이다. 따라서 F_def는
            # bin temperature 함수가 아니라 장비/시험조건 기반 상수이다.
            if constants.get("defrost_control_type") != "demand":
                return 1.0

            t_test = max(constants.get("defrost_t_test_minutes", 90), 90)
            t_max = min(constants.get("defrost_t_max_minutes", 720), 720)
            if t_max <= 90:
                # Eq. 11.107 denominator (Tmax - 90) division 방지.
                # 유효한 demand defrost 시간 범위가 아니므로 credit 미적용.
                return 1.0

            return 1.0 + 0.03 * (1.0 - self._safe_div(t_test - 90, t_max - 90))

        total_heating_btu = 0.0
        total_energy_wh = 0.0
        bin_details = []

        for i, temp_f in enumerate(bin_temps):
            hours = bin_hours[i]
            if hours <= 0:
                continue

            building_load = self._building_load_v3(
                temp_f, q_h1_calc, c_vs, t_zl, t_od
            )
            q_full_raw, p_full = self._canonical_capacity_power_at_temp(temp_f, full_points)
            q_low_raw, p_low_tj = self._canonical_low_capacity_power_at_temp(temp_f, low_points)
            is_frost_region = temp_f <= t_obo
            f_def = _calculate_f_def(self.constants)
            defrost_model = "default_linear_placeholder"
            if 17 < temp_f < t_obo:
                f_frost_capacity = 0.98 + (temp_f - 17) * self._safe_div(1.0 - 0.98, t_obo - 17)
            else:
                f_frost_capacity = 1.0
            q_full_adj = q_full_raw * f_frost_capacity * f_def
            q_low_adj = q_low_raw * f_frost_capacity * f_def if q_low_raw is not None else None
            q_full = q_full_adj
            q_low_tj = q_low_adj
            # NOTE: f_frost_capacity는 AHRI F_def 정식 구현 전의 conservative
            # frost capacity placeholder이다. 이 계수는 heat pump capacity
            # q_full_raw/q_low_raw에만 적용하고, supplemental resistance heat에는
            # 적용하지 않는다.
            # NOTE(AHRI 210/240-2026 Eq. 11.107): F_def는 Demand-defrost
            # enhancement factor이다. Ttest/Tmax는 시간[minutes]이며,
            # heat pump capacity에만 적용하고 전력에는 적용하지 않는다.
            # NOTE(AHRI E13.12): 우선 보정 후보는 heat pump capacity
            # Q_h(Tj) = Q_h_raw(Tj) * F_def 위치이다. 소비 전력(P) 보정
            # 또는 COP 보정 여부는 아직 확정하지 않는다.

            # case 0: BL <= 0 (compressor off)
            # Case I: BL <= q_low_tj (low speed cycling)
            # Case II: q_low_tj < BL < q_full (modulating)
            # Case S: BL <= q_full fallback (simplified full cycling + PLF correction)
            # Case III: BL > q_full (full load + auxiliary heat)
            if building_load <= 0:
                case = 0
                operating_case = "Case 0"
                plr = None
                plf = None
                q_comp = 0.0
                q_delivered = 0.0
                compressor_energy = 0.0
                q_aux = 0.0
                e_aux = 0.0
            elif q_low_tj is not None and building_load <= q_low_tj:
                case = 1
                operating_case = "Case I"
                # Low speed cycling.
                plr = self._safe_div(building_load, q_low_tj)
                plf = 1.0 - c_d * (1.0 - plr)
                plf = max(plf, 0.001)
                q_delivered = building_load * hours
                q_comp = q_delivered
                compressor_energy = p_low_tj * plr * hours / plf
                q_aux = 0.0
                e_aux = 0.0
            elif q_low_tj is not None and q_low_tj < building_load < q_full and q_full != q_low_tj:
                case = 1
                operating_case = "Case II"
                x_low = self._safe_div(q_full - building_load, q_full - q_low_tj)
                x_full = 1.0 - x_low
                plr = None
                plf = None
                q_delivered = building_load * hours
                q_comp = q_delivered
                compressor_energy = (p_low_tj * x_low + p_full * x_full) * hours
                q_aux = 0.0
                e_aux = 0.0
            elif building_load <= q_full:
                case = 1
                operating_case = "Case S"
                # PLR: part load ratio (= HLF in AHRI simplified path)
                plr = self._safe_div(building_load, q_full)
                # PLF: part load factor, cycling degradation 보정
                # PLF = 1 - Cd * (1 - PLR)
                # 현재는 v3 simplified full-point path 적용.
                # TODO(P2): q_Low 기반 AHRI full Case I/II로 교체 필요.
                plf = 1.0 - c_d * (1.0 - plr)
                plf = max(plf, 0.001)  # 0 나누기 방지
                q_delivered = building_load * hours
                q_comp = q_delivered
                compressor_energy = p_full * plr * hours / plf
                q_aux = 0.0
                e_aux = 0.0
            else:
                case = 2
                operating_case = "Case III"
                plr = None
                plf = None
                # NOTE(AHRI E13.12): Demand-defrost credit은 heat pump
                # capacity에만 적용 후보로 둔다. supplemental resistance heat
                # q_aux/e_aux에는 해당 credit을 적용하지 말 것.
                q_comp = q_full * hours
                q_delivered = building_load * hours
                compressor_energy = p_full * hours
                q_aux = (building_load - q_full) * hours
                e_aux = self._safe_div(q_aux, aux_eer)

            E_j = compressor_energy + e_aux
            total_heating_btu += q_delivered
            total_energy_wh += E_j

            bin_details.append({
                "bin": i + 1,
                "temp_F": temp_f,
                "hours": hours,
                "case": case,
                "operating_case": operating_case,
                "C_D": c_d,
                "is_frost_region": is_frost_region,
                "f_def": f_def,
                "defrost_control_type": defrost_control_type,
                "defrost_t_test_minutes": defrost_t_test_minutes,
                "defrost_t_max_minutes": defrost_t_max_minutes,
                "f_frost_capacity": round(f_frost_capacity, 6),
                "defrost_model": defrost_model,
                "building_load": round(building_load, 2),
                "q_full_raw": round(q_full_raw, 2),
                "q_full_adj": round(q_full_adj, 2),
                "q_low_raw": round(q_low_raw, 2) if q_low_raw is not None else None,
                "q_low_adj": round(q_low_adj, 2) if q_low_adj is not None else None,
                "q_full": round(q_full, 2),
                "p_full": round(p_full, 2),
                "plr": round(plr, 6) if plr is not None else None,
                "plf": round(plf, 6) if plf is not None else None,
                "q_comp": round(q_comp, 2),
                "q_j": round(q_delivered, 2),
                "e_comp": round(compressor_energy, 2),
                "E_j": round(E_j, 2),
                "q_aux": round(q_aux, 2),
                "e_aux": round(e_aux, 2),
                "aux_ratio": round(self._safe_div(e_aux, E_j), 4) if E_j > 0 else 0.0,
            })

        if total_energy_wh <= 0:
            raise ValueError("HSPF2 calculation error: total_energy_wh must be > 0.")
        if total_heating_btu <= 0:
            raise ValueError("HSPF2 calculation error: total_heating_Btu must be > 0.")

        raw_hspf2 = self._safe_div(total_heating_btu, total_energy_wh)
        if raw_hspf2 < 2 or raw_hspf2 > 20:
            warnings.warn(f"HSPF2 sanity warning: calculated value is outside 2-20 range ({raw_hspf2:.3f})")

        return {
            "raw_hspf2": raw_hspf2,
            "rounded_hspf2": self._round_nearest_025(raw_hspf2),
            "HSPF2": self._round_nearest_025(raw_hspf2),
            "total_load": round(total_heating_btu, 3),
            "total_energy": round(total_energy_wh, 3),
            "total_heating_btu": round(total_heating_btu, 3),
            "total_energy_wh": round(total_energy_wh, 3),
            "h42_source": h42_source,
            "bin_table": {
                "region": bin_table.get("region"),
                "source": bin_table.get("source", {}),
                "heating_load_hours": hlh,
                "fractional_bin_hours_sum": round(sum(fractional_bin_hours), 3),
            },
            "summary": {
                "heating_load_line": {
                    "q_h1_calc": q_h1_calc,
                    "q_h1_calc_source": "H12 capacity (47 F H1_Full) simplified canonical fallback",
                    "H1_Full_capacity": h1_full_capacity_btu,
                    "C_vs": c_vs,
                    "t_zl": t_zl,
                    "t_od": t_od,
                },
            },
            "bin_details": bin_details,
        }

    def calculate_hspf2(self, test_points: dict, **kwargs) -> dict:
        """
        AHRI 210/240 HSPF2 entry point.

        The first validated implementation is kept in calculate_hspf2_v2() so
        earlier behavior remains traceable during stabilization.
        """
        internal_test_points = self.canonical_to_internal_usage(test_points)
        return self.calculate_hspf2_v2(internal_test_points, **kwargs)
