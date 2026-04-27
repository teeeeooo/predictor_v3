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
        _hspf2_defaults = {
            "t_off": -40.0,
            "t_on": -40.0,
            "fdef_override": 1.0,
        }
        for key, value in _hspf2_defaults.items():
            if key not in self.defaults:
                self.defaults[key] = value

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
        h22 = self._get_point(canonical_points, "H22")  # required per AHRI 210/240-2026
        h32 = self._get_point(canonical_points, "H32")
        try:
            h42 = self._get_point(canonical_points, "H42")
            h42_source = "provided"
        except ValueError:
            h22_temp = self.test_point_schema["heating"]["H22"]["outdoor_db_f"]
            h32_temp = self.test_point_schema["heating"]["H32"]["outdoor_db_f"]
            h42_temp = self.test_point_schema["heating"]["H42"]["outdoor_db_f"]

            q_h22, p_h22 = h22
            q_h32, p_h32 = h32
            h42 = (
                self._linear(h42_temp, h32_temp, q_h32, h22_temp, q_h22),
                self._linear(h42_temp, h32_temp, p_h32, h22_temp, p_h22),
            )
            h42_source = "extrapolated"

        points = {
            "H12": h12,
            "H22": h22,
            "H32": h32,
            "H42": h42,
        }
        for key, (capacity, power) in points.items():
            if capacity <= 0 or power <= 0:
                raise ValueError(f"Invalid canonical test point {key}: capacity={capacity}, power={power}")

        return points, h42_source

    def _canonical_capacity_power_at_temp(self, temp_f: float, full_points: dict) -> tuple:
        h12_temp = self.test_point_schema["heating"]["H12"]["outdoor_db_f"]
        h22_temp = self.test_point_schema["heating"]["H22"]["outdoor_db_f"]
        h32_temp = self.test_point_schema["heating"]["H32"]["outdoor_db_f"]
        h42_temp = self.test_point_schema["heating"]["H42"]["outdoor_db_f"]

        q_h12, p_h12 = full_points["H12"]
        q_h22, p_h22 = full_points["H22"]
        q_h32, p_h32 = full_points["H32"]
        q_h42, p_h42 = full_points["H42"]

        if temp_f >= h12_temp:
            q_tj = self._linear(temp_f, h22_temp, q_h22, h12_temp, q_h12)
            p_tj = self._linear(temp_f, h22_temp, p_h22, h12_temp, p_h12)
        elif temp_f >= h22_temp:
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
        low_point_temps = {
            "H11": 47,
            "H2V": 35,
            "H31": 17,
        }
        points = []
        for key in ("H11", "H2V", "H31"):
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

    def _get_positive_point(self, test_points: dict, key: str) -> tuple:
        capacity, power = self._get_point(test_points, key)
        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid canonical test point {key}: capacity={capacity}, power={power}")
        return capacity, power

    def _require_ahri_kwargs(self, kwargs: dict) -> tuple:
        missing = [
            key for key in (
                "defrost_t_test_minutes",
                "defrost_t_max_minutes",
            )
            if key not in kwargs
        ]
        if missing:
            raise ValueError(
                "HSPF2 v3 AHRI path requires explicit Appendix J/defrost inputs: "
                + ", ".join(missing)
            )

        t_off = kwargs.get("t_off", self.defaults.get("t_off", -40.0))
        t_on = kwargs.get("t_on", self.defaults.get("t_on", -40.0))
        if t_on < t_off:
            raise ValueError(f"t_on({t_on}) must be >= t_off({t_off})")

        raw_t_test = kwargs["defrost_t_test_minutes"]
        raw_t_max = kwargs["defrost_t_max_minutes"]
        if raw_t_test <= 0 or raw_t_max <= 90:
            raise ValueError(
                "Invalid demand defrost inputs: "
                f"defrost_t_test_minutes={raw_t_test} must be > 0, "
                f"defrost_t_max_minutes={raw_t_max} must be > 90"
            )

        t_test = max(raw_t_test, 90)
        t_max = min(raw_t_max, 720)

        return t_off, t_on, t_test, t_max, raw_t_test, raw_t_max

    def _cert_low_capacity_power_at_temp(self, temp_f: float, low_points: dict) -> tuple:
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_low = q_h1_low + (q_h0_low - q_h1_low) * self._safe_div(temp_f - 47, 62 - 47)
        p_low = p_h1_low + (p_h0_low - p_h1_low) * self._safe_div(temp_f - 47, 62 - 47)
        return max(0.0, q_low), max(0.0, p_low)

    def _cert_minimum_limited_low_capacity_power_at_temp(
        self,
        temp_f: float,
        low_points: dict,
        h2int_point: tuple,
        int_point_at_temp: tuple,
    ) -> tuple:
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_h2_int, p_h2_int = h2int_point
        q_int, p_int = int_point_at_temp

        # AHRI 210/240-2026 Eq.11.189 through Eq.11.194.
        if temp_f >= 47:
            q_low = q_h1_low + (q_h0_low - q_h1_low) * self._safe_div(temp_f - 47, 62 - 47)
            p_low = p_h1_low + (p_h0_low - p_h1_low) * self._safe_div(temp_f - 47, 62 - 47)
        elif temp_f >= 35:
            q_low = q_h2_int + (q_h1_low - q_h2_int) * self._safe_div(temp_f - 35, 47 - 35)
            p_low = p_h2_int + (p_h1_low - p_h2_int) * self._safe_div(temp_f - 35, 47 - 35)
        else:
            q_low = q_int
            p_low = p_int

        return max(0.0, q_low), max(0.0, p_low)

    def _cert_full_capacity_power_at_temp(
        self,
        temp_f: float,
        full_points: dict,
        nominal_point: tuple,
        h4_point: tuple = None,
    ) -> tuple:
        q_h1_full, p_h1_full = full_points["H12"]
        q_h1_nom, p_h1_nom = nominal_point
        q_h2_full, p_h2_full = full_points["H22"]
        q_h3_full, p_h3_full = full_points["H32"]

        if temp_f >= 45:
            q_base = self._linear(temp_f, 17, q_h3_full, 47, q_h1_full)
            p_base = self._linear(temp_f, 17, p_h3_full, 47, p_h1_full)
            q_full = q_base * self._safe_div(q_h1_nom, q_h1_full, 1.0)
            p_full = p_base * self._safe_div(p_h1_nom, p_h1_full, 1.0)
        elif temp_f > 17:
            q_full = self._linear(temp_f, 17, q_h3_full, 35, q_h2_full)
            p_full = self._linear(temp_f, 17, p_h3_full, 35, p_h2_full)
        elif h4_point is not None and temp_f > 5:
            q_h4_full, p_h4_full = h4_point
            q_full = q_h4_full + (q_h3_full - q_h4_full) * self._safe_div(temp_f - 5, 17 - 5)
            p_full = p_h4_full + (p_h3_full - p_h4_full) * self._safe_div(temp_f - 5, 17 - 5)
        elif h4_point is not None and temp_f <= 5:
            q_h4_full, p_h4_full = h4_point
            # AHRI 210/240-2026 Eq.11.217 and Eq.11.218.
            q_full = q_h4_full + (q_h1_full - q_h3_full) * self._safe_div(temp_f - 5, 47 - 17)
            p_full = p_h4_full + (p_h1_full - p_h3_full) * self._safe_div(temp_f - 5, 47 - 17)
        else:
            q_full = self._linear(temp_f, 17, q_h3_full, 47, q_h1_full)
            p_full = self._linear(temp_f, 17, p_h3_full, 47, p_h1_full)

        return max(0.0, q_full), max(0.0, p_full)

    def _cert_intermediate_capacity_power_at_temp(
        self,
        temp_f: float,
        h2int_point: tuple,
        low_points: dict,
        full_points: dict,
    ) -> tuple:
        q_h2_int, p_h2_int = h2int_point
        q_low_35, p_low_35 = self._cert_low_capacity_power_at_temp(35, low_points)
        q_h0_low, p_h0_low = low_points["H01"]
        q_h1_low, p_h1_low = low_points["H11"]
        q_h2_full, p_h2_full = full_points["H22"]
        q_h3_full, p_h3_full = full_points["H32"]

        n_hq = self._safe_div(q_h2_int - q_low_35, q_h2_full - q_low_35)
        n_he = self._safe_div(p_h2_int - p_low_35, p_h2_full - p_low_35)
        if not (0.0 <= n_hq <= 1.0 and 0.0 <= n_he <= 1.0):
            raise ValueError(
                "HSPF2 v3 AHRI path requires H2Int capacity/power between Low(35F) and H2Full: "
                f"N_Hq={n_hq}, N_HE={n_he}"
            )
        m_hq = (
            self._safe_div(q_h0_low - q_h1_low, 62 - 47) * (1.0 - n_hq)
            + self._safe_div(q_h2_full - q_h3_full, 35 - 17) * n_hq
        )
        m_he = (
            self._safe_div(p_h0_low - p_h1_low, 62 - 47) * (1.0 - n_he)
            + self._safe_div(p_h2_full - p_h3_full, 35 - 17) * n_he
        )
        q_int = q_h2_int + m_hq * (temp_f - 35)
        p_int = p_h2_int + m_he * (temp_f - 35)
        return max(0.0, q_int), max(0.0, p_int), {
            "method": "ahri_210_240_2026_eq_11_199_to_11_204",
            "N_Hq": n_hq,
            "N_HE": n_he,
            "M_Hq": m_hq,
            "M_HE": m_he,
            "q_low_35": q_low_35,
            "p_low_35": p_low_35,
        }

    def _cert_delta_at_bin(self, temp_f: float, cop: float, t_off: float, t_on: float) -> float:
        if temp_f <= t_off or cop < 1.0:
            return 0.0
        if temp_f <= t_on:
            return 0.5
        return 1.0

    def _calculate_hspf2_v3_ahri(self, test_points: dict, **kwargs) -> dict:
        canonical_points = self.legacy_to_canonical(test_points)
        t_off, t_on, t_test, t_max, raw_t_test, raw_t_max = self._require_ahri_kwargs(kwargs)
        required_points = ("H01", "H11", "H1N", "H2Int", "H32", "A2")
        missing = [key for key in required_points if key not in canonical_points]
        if missing:
            raise ValueError(
                "HSPF2 v3 AHRI path requires canonical AHRI test points: "
                + ", ".join(missing)
            )

        full_points = {
            "H32": self._get_positive_point(canonical_points, "H32"),
        }
        h4_point = None
        h42_source = "not_provided"
        if "H42" in canonical_points:
            h4_point = self._get_positive_point(canonical_points, "H42")
            h42_source = "provided"

        low_points = {
            "H01": self._get_positive_point(canonical_points, "H01"),
            "H11": self._get_positive_point(canonical_points, "H11"),
        }
        h1_nom = self._get_positive_point(canonical_points, "H1N")
        if "H12" in canonical_points:
            full_points["H12"] = self._get_positive_point(canonical_points, "H12")
            h12_source = "tested"
        else:
            q_h1_nom, p_h1_nom = h1_nom
            if kwargs.get("h1n_same_speed_as_h3", False):
                full_points["H12"] = (q_h1_nom, p_h1_nom)
                h12_source = "eq_11_183"
            else:
                q_h3_full, p_h3_full = full_points["H32"]
                if q_h3_full == 0 or p_h3_full == 0:
                    raise ValueError("Invalid H3Full for Eq.11.185/11.186 fallback")

                unit_type = kwargs.get("unit_type", kwargs.get("system_type", "split"))
                if str(unit_type).lower() in ("single_package", "single-package", "package", "packaged"):
                    csf = 0.0262
                else:
                    csf = 0.0204

                psf = 0.00455
                full_points["H12"] = (
                    q_h3_full * (1 + 30 * csf),
                    p_h3_full * (1 + 30 * psf),
                )
                h12_source = "eq_11_185"
        if "H22" in canonical_points:
            full_points["H22"] = self._get_positive_point(canonical_points, "H22")
            h22_source = "tested"
            h22_tested = True
            h22_for_slope_source = "tested"
            h22_high_anchor_source = None
            h22_high_anchor_capacity = None
            h22_high_anchor_power = None
        else:
            q_h3_full, p_h3_full = full_points["H32"]
            q_h1_full_calc, p_h1_full_calc = full_points["H12"]
            # AHRI 210/240-2026 Eq.11.44 and Eq.11.50 for missing H22 optional test.
            full_points["H22"] = (
                0.90 * (q_h3_full + 0.6 * (q_h1_full_calc - q_h3_full)),
                0.985 * (p_h3_full + 0.6 * (p_h1_full_calc - p_h3_full)),
            )
            h22_source = "eq_11_44_11_50"
            h22_tested = False
            h22_for_slope_source = "eq_11_44_11_50"
            h22_high_anchor_source = "h1full_calc"
            h22_high_anchor_capacity = q_h1_full_calc
            h22_high_anchor_power = p_h1_full_calc
        h22_capacity, h22_power = full_points["H22"]
        h2_int = self._get_positive_point(canonical_points, "H2Int")
        q_a_full, _ = self._get_positive_point(canonical_points, "A2")

        bin_table = self._get_region_iv_heating_bin_table()
        bin_temps = bin_table["bin_temps_f"]
        fractional_bin_hours = bin_table["fractional_bin_hours"]
        hlh = bin_table["heating_load_hours"]
        bin_hours = [frac * hlh for frac in fractional_bin_hours]
        c_vs = bin_table.get("variable_capacity_slope_factor", 1.07)
        t_zl = bin_table.get("zero_load_temp_f", 55)
        t_od = bin_table.get("outdoor_design_temp_f", 5)
        c_d_heating = kwargs.get("c_d_heating", self.defaults.get("c_d_heating", 0.25))
        aux_eer = kwargs.get("aux_cop", self.defaults.get("aux_cop", 1.0)) * 3.412
        fdef_override = kwargs.get("fdef_override", self.defaults.get("fdef_override", 1.0))
        minimum_speed_limited = bool(
            kwargs.get(
                "does_comp_limit_min_spd",
                kwargs.get(
                    "comp_limit_min_spd",
                    kwargs.get(
                        "minimum_speed_limited",
                        kwargs.get("is_minimum_speed_limited", False),
                    ),
                ),
            )
        )
        case_i_low_source = "eq_11_189_194" if minimum_speed_limited else "eq_11_187_188"

        f_def_seasonal = 1.0 + 0.03 * (1.0 - self._safe_div(t_test - 90, t_max - 90))
        total_heating_btu = 0.0
        total_energy_wh = 0.0
        bin_details = []

        for i, temp_f in enumerate(bin_temps):
            hours = bin_hours[i]
            fractional_hours = fractional_bin_hours[i]
            if hours <= 0:
                continue

            building_load = self._building_load_v3(temp_f, q_a_full, c_vs, t_zl, t_od)
            q_full, p_full = self._cert_full_capacity_power_at_temp(temp_f, full_points, h1_nom, h4_point)
            q_int, p_int, int_meta = self._cert_intermediate_capacity_power_at_temp(
                temp_f,
                h2_int,
                low_points,
                full_points,
            )
            if minimum_speed_limited:
                q_low, p_low = self._cert_minimum_limited_low_capacity_power_at_temp(
                    temp_f,
                    low_points,
                    h2_int,
                    (q_int, p_int),
                )
            else:
                q_low, p_low = self._cert_low_capacity_power_at_temp(temp_f, low_points)

            cop_low = self._safe_div(q_low, p_low * 3.412) if p_low > 0 else 0.0
            cop_full = self._safe_div(q_full, p_full * 3.412) if p_full > 0 else 0.0
            cop_int = self._safe_div(q_int, p_int * 3.412) if p_int > 0 else 0.0

            if building_load <= 0:
                operating_case = "Case 0"
                delta_j = 1.0
                hlf = None
                plf = 1.0
                cop_bin = None
                q_comp = 0.0
                e_comp = 0.0
                q_aux = 0.0
                e_aux = 0.0
            elif building_load <= q_low:
                operating_case = "Case I"
                hlf = self._safe_div(building_load, q_low)
                plf = max(0.01, 1.0 - c_d_heating * (1.0 - hlf))
                delta_j = self._cert_delta_at_bin(temp_f, cop_low, t_off, t_on)
                cop_bin = cop_low
                q_comp = building_load * delta_j * hours
                e_comp = p_low * hlf * delta_j * hours / plf
                q_aux = building_load * (1.0 - delta_j) * hours
                e_aux = self._safe_div(q_aux, aux_eer)
            elif q_low < building_load < q_full:
                operating_case = "Case II"
                hlf = None
                plf = 1.0
                valid_case_ii_points = (
                    q_low <= q_int < q_full
                    if minimum_speed_limited
                    else q_low < q_int < q_full
                )
                if not valid_case_ii_points:
                    raise ValueError(
                        "HSPF2 v3 AHRI Case II requires q_low < q_int < q_full at every Case II bin: "
                        f"temp_f={temp_f}, q_low={q_low}, q_int={q_int}, q_full={q_full}"
                    )
                if q_int > q_low and building_load <= q_int:
                    cop_bin = cop_low + self._safe_div(building_load - q_low, q_int - q_low) * (cop_int - cop_low)
                else:
                    cop_bin = cop_int + self._safe_div(building_load - q_int, q_full - q_int) * (cop_full - cop_int)
                delta_j = self._cert_delta_at_bin(temp_f, cop_bin, t_off, t_on)
                q_comp = building_load * delta_j * hours
                e_comp = self._safe_div(building_load, cop_bin * 3.412) * delta_j * hours
                q_aux = building_load * (1.0 - delta_j) * hours
                e_aux = self._safe_div(q_aux, aux_eer)
            else:
                operating_case = "Case III"
                hlf = 1.0
                plf = 1.0
                cop_bin = cop_full
                delta_j = self._cert_delta_at_bin(temp_f, cop_full, t_off, t_on)
                q_comp = q_full * delta_j * hours
                e_comp = p_full * delta_j * hours
                q_aux = max(0.0, building_load - q_full * delta_j) * hours
                e_aux = self._safe_div(q_aux, aux_eer)

            q_j = q_comp + q_aux
            E_j = e_comp + e_aux
            total_heating_btu += q_j
            total_energy_wh += E_j

            bin_details.append({
                "bin_no": i + 1,
                "bin": i + 1,
                "temp_F": temp_f,
                "hours": hours,
                "fractional_hours": fractional_hours,
                "operating_case": operating_case,
                "building_load": round(building_load, 2),
                "delta_j": delta_j,
                "HLF_j": round(hlf, 6) if hlf is not None else None,
                "PLF_j": round(plf, 6),
                "q_low": round(q_low, 2),
                "p_low": round(p_low, 2),
                "q_int": round(q_int, 2),
                "p_int": round(p_int, 2),
                "q_full": round(q_full, 2),
                "p_full": round(p_full, 2),
                "COP_low": round(cop_low, 6),
                "COP_int": round(cop_int, 6),
                "COP_full": round(cop_full, 6),
                "COP_bin": round(cop_bin, 6) if cop_bin is not None else None,
                "q_comp": round(q_comp, 2),
                "e_comp": round(e_comp, 2),
                "q_aux": round(q_aux, 2),
                "e_aux": round(e_aux, 2),
                "q_j": round(q_j, 2),
                "E_j": round(E_j, 2),
                "aux_ratio": round(self._safe_div(e_aux, E_j), 4) if E_j > 0 else 0.0,
                "debug_info": {
                    "formula_path": "ahri_210_240_2026_variable_capacity_heating",
                    "full_capacity_method": (
                        "eq_11_209_11_210" if temp_f >= 45
                        else "eq_11_213_11_214" if temp_f > 17
                        else "h4full_low_temp_line" if h4_point is not None
                        else "no_h4full_h1full_h3full_line"
                    ),
                    "low_capacity_method": case_i_low_source,
                    "intermediate_capacity_method": int_meta["method"],
                    "intermediate_metadata": {
                        key: round(value, 6) if isinstance(value, float) else value
                        for key, value in int_meta.items()
                    },
                },
            })

        if total_energy_wh <= 0:
            raise ValueError("HSPF2 AHRI calculation error: total_energy_wh must be > 0.")
        if total_heating_btu <= 0:
            raise ValueError("HSPF2 AHRI calculation error: total_heating_btu must be > 0.")

        raw_hspf2_base = self._safe_div(total_heating_btu, total_energy_wh)
        seasonal_defrost_multiplier_applied = False
        raw_hspf2 = raw_hspf2_base * fdef_override
        rounded_hspf2 = self._round_nearest_025(raw_hspf2)
        return {
            "raw_hspf2": raw_hspf2,
            "raw_hspf2_base": raw_hspf2_base,
            "rounded_hspf2": rounded_hspf2,
            "HSPF2": rounded_hspf2,
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
                "ahri_210_240_2026_ready": True,
                "total_heating_btu": round(total_heating_btu, 3),
                "total_energy_wh": round(total_energy_wh, 3),
                "raw_hspf2_base": raw_hspf2_base,
                "f_def_seasonal": f_def_seasonal,
                "raw_hspf2": raw_hspf2,
                "rounded_hspf2": rounded_hspf2,
                "metadata": {
                    "formula_path": "ahri_210_240_2026_variable_capacity_heating",
                    "region": bin_table.get("region"),
                    "heating_load_hours": hlh,
                    "h12_source": h12_source,
                    "h22_source": h22_source,
                    "h22_capacity": h22_capacity,
                    "h22_power": h22_power,
                    "h22_tested": h22_tested,
                    "h22_for_slope_source": h22_for_slope_source,
                    "h22_high_anchor_source": h22_high_anchor_source,
                    "h22_high_anchor_capacity": h22_high_anchor_capacity,
                    "h22_high_anchor_power": h22_high_anchor_power,
                    "minimum_speed_limited": minimum_speed_limited,
                    "case_i_low_source": case_i_low_source,
                    "t_off": t_off,
                    "t_on": t_on,
                    "t_off_used": t_off,
                    "t_on_used": t_on,
                    "c_d_heating": c_d_heating,
                    "defrost_control_type": "demand",
                    "defrost_t_test_minutes": t_test,
                    "defrost_t_max_minutes": t_max,
                    "defrost": {
                        "mode": "override",
                        "fdef_used": fdef_override,
                        "f_def_seasonal": f_def_seasonal,
                        "raw_hspf2_base": raw_hspf2_base,
                        "raw_hspf2": raw_hspf2,
                        "seasonal_defrost_multiplier_applied": seasonal_defrost_multiplier_applied,
                        "t_test_input": raw_t_test,
                        "t_max_input": raw_t_max,
                        "t_test_used": t_test,
                        "t_max_used": t_max,
                        "fdef_override": fdef_override,
                        "clamped": raw_t_test != t_test or raw_t_max != t_max,
                    },
                    "t_OBO": 45,
                },
                "heating_load_line": {
                    "q_h1_calc": q_a_full,
                    "q_h1_calc_source": "A2_cooling_capacity_95F",
                    "q_h1_calc_scope": "variable_capacity_afull_anchor_eq11106",
                    "C_vs": c_vs,
                    "t_zl": t_zl,
                    "t_od": t_od,
                },
            },
            "bin_details": bin_details,
        }

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
        AHRI 210/240-2026 HSPF2 calculation path for the current predictor_v3 scope.

        Scope: Region IV, non-ducted single-split variable-capacity air-to-air
        heat pump with electric resistance auxiliary heat.
        """
        return self._calculate_hspf2_v3_ahri(test_points, **kwargs)

    def calculate_hspf2(self, test_points: dict, **kwargs) -> dict:
        """
        AHRI 210/240 HSPF2 entry point.

        v3 is the production path for the current predictor_v3 HSPF2 scope.
        calculate_hspf2_v2() remains available as a legacy reference path.
        """
        return self.calculate_hspf2_v3(test_points, **kwargs)
