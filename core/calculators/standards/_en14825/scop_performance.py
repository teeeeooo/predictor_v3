"""EN 14825 SCOP declared performance and temperature curves."""

from __future__ import annotations

from .performance import EN14825PerformanceCurve


class SCOPPerformanceCurve:
    def __init__(self, performance: EN14825PerformanceCurve) -> None:
        self._performance = performance

    def _build_scop_points(
        self,
        point_resolution: dict,
        climate_data: dict,
        p_design_h: float,
        cd: float,
    ) -> dict:
        t_design_h = float(climate_data["t_design_h_c"])
        points = point_resolution["points"]
        contract = point_resolution["contract"]
        resolved = {}
        for key, source_point in points.items():
            if source_point.get("inactive"):
                resolved[key] = dict(source_point)
                resolved[key]["key"] = key
                continue
            point = dict(source_point)
            load = self._performance._heating_part_load(
                point["temp_c"], p_design_h, t_design_h
            )
            point_performance = self._performance._scop_pl_at_declared_point(
                point, load, cd
            )
            point.update(
                {
                    "key": key,
                    "load": load,
                    "cop_dc": point_performance["cop_dc"],
                    "cop_pl": point_performance["cop_pl"],
                    "cr": point_performance["cr"],
                    "degradation_factor": point_performance[
                        "degradation_factor"
                    ],
                    "value": point_performance["cop_pl"],
                }
            )
            resolved[key] = point
        return {
            "points": resolved,
            "capacity_curve": self._scop_capacity_curve_points(
                resolved, contract["curve_point_keys"]
            ),
            "coppl_curve": self._scop_coppl_curve_points(
                resolved, contract["curve_point_keys"]
            ),
        }

    def _scop_capacity_curve_points(
        self, points: dict, curve_point_keys: tuple
    ) -> list:
        by_temp = {}
        for key in curve_point_keys:
            point = points[key]
            if point.get("inactive"):
                continue
            temp = point["temp_c"]
            if temp not in by_temp:
                by_temp[temp] = {
                    "key": key,
                    "temp_c": temp,
                    "value": point["capacity"],
                    "capacity": point["capacity"],
                }
        return sorted(by_temp.values(), key=lambda point: point["temp_c"])

    def _scop_coppl_curve_points(
        self, points: dict, curve_point_keys: tuple
    ) -> list:
        by_temp = {}
        for key in curve_point_keys:
            point = points[key]
            if point.get("inactive"):
                continue
            temp = point["temp_c"]
            if temp not in by_temp:
                by_temp[temp] = {
                    "key": key,
                    "temp_c": temp,
                    "value": point["cop_pl"],
                    "cop_pl": point["cop_pl"],
                }
        return sorted(by_temp.values(), key=lambda point: point["temp_c"])

    def _capacity_at_temp_for_scop(
        self, tj: float, scop_points: dict
    ) -> tuple:
        return self._performance._interpolate_from_points(
            tj, scop_points["capacity_curve"]
        )

    def _coppl_at_temp_for_scop(self, tj: float, scop_points: dict) -> tuple:
        return self._performance._interpolate_from_points(
            tj, scop_points["coppl_curve"], extrapolate_upper=True
        )
