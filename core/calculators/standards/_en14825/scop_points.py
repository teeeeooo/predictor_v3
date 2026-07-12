"""EN 14825 SCOP declared-point contract resolution."""

from __future__ import annotations

from .performance import EN14825PerformanceCurve
from .scop_context import SCOPClimateContext


class SCOPPointResolver:
    def __init__(
        self,
        climate: SCOPClimateContext,
        performance: EN14825PerformanceCurve,
    ) -> None:
        self._climate = climate
        self._performance = performance

    def _parse_scop_point(self, test_points: dict, key: str) -> dict:
        if key not in test_points:
            raise ValueError(f"Missing SCOP test point: {key}")
        value = test_points[key]
        if isinstance(value, dict):
            if "capacity" not in value or "power" not in value:
                raise ValueError(
                    f"SCOP test point {key} must include capacity and power."
                )
            capacity = float(value["capacity"])
            power = float(value["power"])
            temp_c = value.get("temp_c", value.get("outdoor_db_c"))
        else:
            capacity, power = value
            capacity = float(capacity)
            power = float(power)
            temp_c = None
        if capacity <= 0 or power <= 0:
            raise ValueError(
                f"Invalid SCOP test point {key}: capacity={capacity}, power={power}"
            )
        return {
            "capacity": capacity,
            "power": power,
            "cop_pl": self._performance._safe_div(capacity, power),
            "temp_c": float(temp_c) if temp_c is not None else None,
        }

    def _conditional_scop_point_required(
        self,
        temp_c: float,
        source_key: str,
        active_standard_temps: dict,
        first_nonzero_bin_temp: float,
    ) -> bool:
        if source_key is not None:
            return False
        if temp_c == first_nonzero_bin_temp:
            return True
        if temp_c < first_nonzero_bin_temp:
            upper_temps = [
                temp
                for temp in active_standard_temps.values()
                if temp >= first_nonzero_bin_temp
            ]
            if not upper_temps:
                return False
            return temp_c < first_nonzero_bin_temp < min(upper_temps)
        return True

    def _resolve_scop_point_contract(
        self,
        climate_key: str,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        contract = self._climate._get_scop_point_contract()
        standard_points = tuple(
            contract.get("standard_points", ("A", "B", "C", "D"))
        )
        conditional_points = tuple(
            contract.get("conditional_points", ("TOL", "Tbiv"))
        )
        active_standard_points = tuple(
            contract.get("climate_standard_points", {}).get(
                climate_key, standard_points
            )
        )
        standard_temps = self._climate._get_scop_standard_point_temps()
        active_standard_temps = {
            key: standard_temps[key]
            for key in active_standard_points
            if key in standard_temps
        }
        resolved_temps = {key: standard_temps[key] for key in standard_points}
        resolved_temps["Tbiv"] = float(
            tbiv_temp_c
            if tbiv_temp_c is not None
            else climate_data["tbiv_max_c"]
        )
        resolved_temps["TOL"] = float(
            tol_temp_c if tol_temp_c is not None else climate_data["tol_max_c"]
        )

        required = list(active_standard_points)
        mapped = {}
        inactive = [
            key for key in standard_points if key not in active_standard_points
        ]
        first_nonzero = self._climate._first_nonzero_heating_bin_temp(
            climate_data
        )
        for key in conditional_points:
            temp_c = resolved_temps[key]
            source_key = None
            for point_key, point_temp in active_standard_temps.items():
                if temp_c == point_temp:
                    source_key = point_key
                    break
            if source_key is not None:
                mapped[key] = source_key
                continue
            if self._conditional_scop_point_required(
                temp_c, source_key, active_standard_temps, first_nonzero
            ):
                required.append(key)
            else:
                inactive.append(key)

        curve_point_keys = tuple(
            key
            for key in required
            if key in standard_points or key in conditional_points
        )
        return {
            "active_standard_points": active_standard_points,
            "required_independent_points": tuple(required),
            "mapped_points": mapped,
            "inactive_points": tuple(inactive),
            "resolved_temperatures": resolved_temps,
            "curve_point_keys": curve_point_keys,
        }

    def _validate_scop_points(
        self,
        test_points: dict,
        climate_key: str,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        contract = self._resolve_scop_point_contract(
            climate_key, climate_data, tbiv_temp_c, tol_temp_c
        )
        points = {}
        for key in contract["required_independent_points"]:
            point = self._parse_scop_point(test_points, key)
            point["temp_c"] = contract["resolved_temperatures"][key]
            points[key] = point
        for key, source_key in contract["mapped_points"].items():
            if source_key not in points:
                raise ValueError(
                    f"Mapped SCOP point {key} source is missing: {source_key}"
                )
            point = dict(points[source_key])
            point["temp_c"] = contract["resolved_temperatures"][key]
            point["mapped_from"] = source_key
            points[key] = point
        for key in contract["inactive_points"]:
            if key not in points:
                points[key] = {
                    "temp_c": contract["resolved_temperatures"][key],
                    "inactive": True,
                }

        if points["Tbiv"]["temp_c"] > climate_data["tbiv_max_c"]:
            raise ValueError(
                f"Tbiv exceeds climate maximum: {points['Tbiv']['temp_c']} > "
                f"{climate_data['tbiv_max_c']}"
            )
        if points["TOL"]["temp_c"] > climate_data["tol_max_c"]:
            raise ValueError(
                f"TOL exceeds climate maximum: {points['TOL']['temp_c']} > "
                f"{climate_data['tol_max_c']}"
            )
        if points["TOL"]["temp_c"] > points["Tbiv"]["temp_c"]:
            raise ValueError(
                "TOL must be <= Tbiv for SCOP heating calculation: "
                f"TOL={points['TOL']['temp_c']}, Tbiv={points['Tbiv']['temp_c']}"
            )
        return {"points": points, "contract": contract}
