"""EN 14825 SCOP climate, bin, and operational-hour configuration."""

from __future__ import annotations

from .context import EN14825ConfigContext


class SCOPClimateContext:
    def __init__(self, context: EN14825ConfigContext) -> None:
        self._context = context

    def _normalize_climate(self, climate: str) -> str:
        if not isinstance(climate, str):
            raise ValueError("climate must be one of: average, warmer, colder")
        climate_key = climate.strip().lower()
        aliases = {
            "avg": "average",
            "a": "average",
            "w": "warmer",
            "c": "colder",
        }
        return aliases.get(climate_key, climate_key)

    def _get_scop_climate_data(self, climate: str) -> dict:
        climate_key = self._normalize_climate(climate)
        climates = self._context.scop_config.get("climates", {})
        if climate_key not in climates:
            raise ValueError(
                f"Unknown SCOP climate: {climate}. "
                f"Expected one of {sorted(climates.keys())}"
            )
        climate_data = climates[climate_key]
        temps = climate_data.get("heating_bin_temps_c", [])
        hours = climate_data.get("heating_bin_hours", [])
        if len(temps) != len(hours):
            raise ValueError(
                f"SCOP climate {climate_key} bin temperature/hour length mismatch."
            )
        if any(hour < 0 for hour in hours):
            raise ValueError(
                f"SCOP climate {climate_key} bin hours must not contain negative values."
            )
        expected_total = climate_data.get("heating_bin_hours_total")
        if expected_total is not None and sum(hours) != expected_total:
            raise ValueError(
                f"SCOP climate {climate_key} bin hour total mismatch: "
                f"actual={sum(hours)}, expected={expected_total}"
            )
        return climate_data

    def _get_scop_operational_hours(
        self, climate: str, appliance_type: str
    ) -> dict:
        climate_key = self._normalize_climate(climate)
        hours_by_type = self._context.scop_config.get("operational_hours", {})
        if appliance_type not in hours_by_type:
            raise ValueError(
                f"Unknown SCOP appliance_type: {appliance_type}. "
                f"Expected one of {sorted(hours_by_type.keys())}"
            )
        try:
            return hours_by_type[appliance_type][climate_key]
        except KeyError as exc:
            raise ValueError(
                f"Missing SCOP operational hours for {appliance_type}/{climate_key}"
            ) from exc

    def _get_scop_point_contract(self) -> dict:
        try:
            return self._context.scop_config["point_contract"]
        except KeyError as exc:
            raise ValueError("Missing SCOP point contract config.") from exc

    def _get_scop_standard_point_temps(self) -> dict:
        schema = self._context.scop_config.get("heating_test_point_schema", {})
        point_temps = {}
        for key in ("A", "B", "C", "D"):
            try:
                point_temps[key] = float(schema[key]["outdoor_db_c"])
            except KeyError as exc:
                raise ValueError(
                    f"Missing SCOP schema temperature for point {key}"
                ) from exc
        return point_temps

    def _first_nonzero_heating_bin_temp(self, climate_data: dict) -> float:
        for temp, hours in zip(
            climate_data.get("heating_bin_temps_c", []),
            climate_data.get("heating_bin_hours", []),
        ):
            if hours > 0:
                return float(temp)
        raise ValueError("SCOP climate has no nonzero heating bin hours.")
