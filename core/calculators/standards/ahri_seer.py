"""Stable AHRI 210/240 Appendix M SEER public facade."""

import json

from ._ahri_m.seer_variable import AppendixMSeerEngine


class AHRISeerCalculator:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)
        self._engine = AppendixMSeerEngine(self.config)

    def calculate_seer(self, test_points, *, c_d_cooling=None):
        return self._engine.calculate(test_points, c_d_cooling=c_d_cooling)
