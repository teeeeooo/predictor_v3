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

        if len(self.bin_temps) != len(self.bin_hours):
            raise ValueError("bin_temps and bin_hours must have the same length.")

        q_h42, _ = full_points["H42"]
        design_load = kwargs.get("design_load_btu", q_h42)
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
            q_full, p_full = self._canonical_capacity_power_at_temp(temp_f, full_points)

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

        raw_hspf2 = self._safe_div(total_heating_btu, total_energy_wh)
        if raw_hspf2 < 2 or raw_hspf2 > 20:
            warnings.warn(f"HSPF2 sanity warning: calculated value is outside 2-20 range ({raw_hspf2:.3f})")

        return {
            "raw_hspf2": raw_hspf2,
            "rounded_hspf2": self._round_nearest_025(raw_hspf2),
            "total_load": round(total_heating_btu, 3),
            "total_energy": round(total_energy_wh, 3),
            "h42_source": h42_source,
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
