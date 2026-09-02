"""Stable AHRI 210/240-2017 Appendix M HSPF public facade."""

import json

from ._ahri_m.hspf_variable import AppendixMHspfEngine


class AHRIHspfCalculator:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)
        self._engine = AppendixMHspfEngine(self.config)

    def calculate_hspf(self, test_points, **kwargs):
        return self._engine.calculate(test_points, **kwargs)
