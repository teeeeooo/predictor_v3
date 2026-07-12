"""EN 14825 SEER declared-point validation and curve construction."""

from __future__ import annotations

from .context import EN14825ConfigContext
from .performance import EN14825PerformanceCurve


class SEERPointResolver:
    def __init__(
        self,
        context: EN14825ConfigContext,
        performance: EN14825PerformanceCurve,
    ) -> None:
        self._context = context
        self._performance = performance

    def _validate_test_points(self, test_points: dict):
        for key in ("A", "B", "C", "D"):
            if key not in test_points:
                raise ValueError(f"Missing test point: {key}")
            capacity, power = test_points[key]
            if capacity <= 0 or power <= 0:
                raise ValueError(
                    f"Invalid value at {key}: capa={capacity}, power={power}"
                )

    def _build_cooling_eerpl_points(
        self,
        test_points: dict,
        p_design_c: float,
        t_design_c: float,
        cd: float,
    ) -> list:
        point_temps = self._context._get_seer_test_point_temps()
        points = []
        for key in ("D", "C", "B", "A"):
            temp = float(point_temps[key])
            capacity, power = test_points[key]
            load = self._performance._cooling_condition_load(
                temp, p_design_c, t_design_c
            )
            point = self._performance._eer_pl_at_declared_point(
                float(capacity),
                float(power),
                load,
                cd,
                apply_degradation=(key != "A"),
            )
            points.append(
                {
                    "key": key,
                    "temp_c": temp,
                    "value": point["eer_pl"],
                    "load": load,
                    "capacity": float(capacity),
                    "power": float(power),
                    "eer_dc": point["eer_dc"],
                    "cr": point["cr"],
                    "degradation_factor": point["degradation_factor"],
                }
            )
        return points
