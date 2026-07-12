"""ISO 16358 configuration loading and shared calculation context."""

from __future__ import annotations

import json
import os


CONTEXT_ATTRIBUTES = (
    "config",
    "t_100_load",
    "t_0_load",
    "Cd",
    "building_load_source",
    "reference_point",
    "power_interpolation_method",
    "iso_boundary_temperature_rounding",
    "round_test_values",
    "rounding_method",
    "points_config",
    "derived_rules",
    "bin_hours",
)


class ISO16358ConfigContext:
    def __init__(self, config_path: str) -> None:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        with open(config_path, "r", encoding="utf-8") as config_file:
            self.config = json.load(config_file)
        self.config.pop("_comment", None)

        self.t_100_load = self.config.get("t_100_load", 35.0)
        self.t_0_load = self.config.get("t_0_load", 20.0)
        self.Cd = self.config.get("Cd", 0.25)
        self.building_load_source = self.config.get(
            "building_load_source", "measured"
        )
        self.reference_point = self.config.get("reference_point", "35_full")
        self.power_interpolation_method = self.config.get(
            "power_interpolation_method", "capacity_linear"
        )
        self.iso_boundary_temperature_rounding = self.config.get(
            "iso_boundary_temperature_rounding", None
        )
        self.round_test_values = self.config.get("round_test_values", False)
        self.rounding_method = self.config.get("rounding_method", None)
        self.points_config = self.config.get("points", {})
        self.derived_rules = self.config.get("derived_rules", {})
        self.bin_hours = self.config.get("bin_hours", [])


class ISOEngineContext:
    """Let formula mixins read a single shared configuration context."""

    def __init__(self, context: ISO16358ConfigContext) -> None:
        self._context = context

    def __getattr__(self, name: str):
        try:
            return getattr(self._context, name)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__!s} object has no attribute {name!r}"
            ) from None
