"""Stable AHRI 210/240 SEER2 public facade and default configuration."""

import json

from ._ahri.seer2_variable import SEER2VariableCapacityEngine


def get_default_ahri_seer2_config() -> dict:
    return {
        "standard": "AHRI 210/240-2023",
        "mode": "cooling",
        "unit_system": "imperial",
        "bin_data": {
            "bin_temps": [67, 72, 77, 82, 87, 92, 97, 102],
            "bin_hours": [0.214, 0.231, 0.216, 0.161, 0.104, 0.052, 0.018, 0.004],
        },
        "test_point_temps": {
            "temp_A_full": 95,
            "temp_B_full": 82,
            "temp_B_low": 82,
            "temp_E_int": 87,
            "temp_F_low": 67,
        },
        "constants": {
            "sf": 1.1,
            "v_factor": {"HP": 0.93, "AC": 1.0},
        },
        "defaults": {
            "cd_default_low": 0.25,
            "cd_default_full": 0.25,
        },
    }


class AHRICalculator:
    """Compatibility facade for the current variable-capacity SEER2 path."""

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)
        self._variable_engine = SEER2VariableCapacityEngine(self.config)
        for attribute in (
            "bin_temps",
            "bin_hours",
            "t_A",
            "t_B",
            "t_F",
            "t_E",
            "sf",
            "v_factor_map",
            "cd_default_low",
        ):
            setattr(self, attribute, getattr(self._variable_engine, attribute))

    def calculate_seer2(self, test_points, system_type="HP", p_w_off=0.0, cd_low=None):
        return self._variable_engine.calculate(test_points, system_type, p_w_off, cd_low)
