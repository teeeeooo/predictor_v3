"""
core/calculator_ahri_hspf2.py
AHRI 210/240 HSPF2 calculation module scaffold.

The HSPF2 rules are intentionally kept separate from the SEER2 engine until the
heating path is validated. Shared helpers are duplicated locally for now.
"""

import json
import os


class AHRIHSPF2Calculator:
    """AHRI 210/240 HSPF2 calculator scaffold for variable-capacity systems."""

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.bin_temps = self.config["bin_data"]["bin_temps"]
        self.bin_hours = self.config["bin_data"]["bin_hours"]
        self.test_point_temps = self.config.get("test_point_temps", {})
        self.constants = self.config.get("constants", {})
        self.defaults = self.config.get("defaults", {})

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def calculate_hspf2(self, test_points: dict, **kwargs) -> dict:
        """
        Placeholder entry point for AHRI 210/240 HSPF2.

        The file and config are prepared now so the architecture is symmetric
        with SEER2. The numerical HSPF2 method should be implemented in the
        dedicated heating task after the required rating equations are fixed.
        """
        raise NotImplementedError("AHRI HSPF2 calculation is not implemented yet.")
