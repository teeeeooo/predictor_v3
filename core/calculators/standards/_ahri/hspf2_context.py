"""HSPF2 configuration loading and seasonal context construction."""

from dataclasses import dataclass
import json
import os
from typing import Any, Mapping


@dataclass(frozen=True)
class HSPF2SeasonalContext:
    """Validated Region IV and runtime values consumed by the v3 engine."""

    bin_table: Mapping[str, Any]
    bin_temps: list
    fractional_bin_hours: list
    bin_hours: list
    heating_load_hours: float
    variable_capacity_slope_factor: float
    zero_load_temp_f: float
    outdoor_design_temp_f: float
    c_d_heating: float
    auxiliary_eer: float
    fdef_override: float
    t_off: float
    t_on: float
    t_test: float
    t_max: float
    raw_t_test: float
    raw_t_max: float
    minimum_speed_limited: bool
    case_i_low_source: str


class HSPF2ConfigContext:
    """Own loaded HSPF2 config state and effective calculation defaults."""

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

        self.bin_temps = self.config["bin_data"]["bin_temps"]
        self.bin_hours = self.config["bin_data"]["bin_hours"]
        self.canonical_hspf2_bin_tables = self.config.get("canonical_hspf2_bin_tables", {})
        self.test_point_schema = self.config.get("test_point_schema", {})
        self.test_point_aliases = self.config.get("test_point_aliases", {})
        self.test_point_temps = self.config.get("test_point_temps", {})
        self.constants = self.config.get("constants", {})
        self.defaults = self.config.get("defaults", {})
        for key, value in {
            "t_off": -40.0,
            "t_on": -40.0,
            "fdef_override": 1.0,
        }.items():
            if key not in self.defaults:
                self.defaults[key] = value

    def region_iv_heating_bin_table(self) -> dict:
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

    def _require_ahri_kwargs(self, kwargs: dict) -> tuple:
        missing = [
            key
            for key in ("defrost_t_test_minutes", "defrost_t_max_minutes")
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
        return t_off, t_on, max(raw_t_test, 90), min(raw_t_max, 720), raw_t_test, raw_t_max

    def seasonal_context(self, kwargs: dict) -> HSPF2SeasonalContext:
        t_off, t_on, t_test, t_max, raw_t_test, raw_t_max = self._require_ahri_kwargs(kwargs)
        bin_table = self.region_iv_heating_bin_table()
        bin_temps = bin_table["bin_temps_f"]
        fractional_bin_hours = bin_table["fractional_bin_hours"]
        heating_load_hours = bin_table["heating_load_hours"]
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
        return HSPF2SeasonalContext(
            bin_table=bin_table,
            bin_temps=bin_temps,
            fractional_bin_hours=fractional_bin_hours,
            bin_hours=[frac * heating_load_hours for frac in fractional_bin_hours],
            heating_load_hours=heating_load_hours,
            variable_capacity_slope_factor=bin_table.get("variable_capacity_slope_factor", 1.07),
            zero_load_temp_f=bin_table.get("zero_load_temp_f", 55),
            outdoor_design_temp_f=bin_table.get("outdoor_design_temp_f", 5),
            c_d_heating=kwargs.get("c_d_heating", self.defaults.get("c_d_heating", 0.25)),
            auxiliary_eer=kwargs.get("aux_cop", self.defaults.get("aux_cop", 1.0)) * 3.412,
            fdef_override=kwargs.get("fdef_override", self.defaults.get("fdef_override", 1.0)),
            t_off=t_off,
            t_on=t_on,
            t_test=t_test,
            t_max=t_max,
            raw_t_test=raw_t_test,
            raw_t_max=raw_t_max,
            minimum_speed_limited=minimum_speed_limited,
            case_i_low_source=("eq_11_189_194" if minimum_speed_limited else "eq_11_187_188"),
        )
