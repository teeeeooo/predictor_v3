"""ISO input normalization and rounding compatibility."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class ISOInputPreparationMixin:
    def _round_test_value(self, value: float) -> int:
        return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _prepare_measured_inputs(self, measured_inputs: dict) -> dict:
        if not self.round_test_values:
            return measured_inputs

        prepared = {}
        for point_key, point_data in measured_inputs.items():
            if not isinstance(point_data, dict):
                prepared[point_key] = point_data
                continue

            prepared[point_key] = {}
            for data_key, value in point_data.items():
                if data_key in ("capacity", "power"):
                    try:
                        prepared[point_key][data_key] = self._round_test_value(value)
                    except (InvalidOperation, ValueError, TypeError):
                        prepared[point_key][data_key] = value
                else:
                    prepared[point_key][data_key] = value

        return prepared

    def _round_iso_boundary_temperature(self, value: float) -> float:
        if self.iso_boundary_temperature_rounding is None:
            return value
        if self.iso_boundary_temperature_rounding == "excel_round_0":
            return float(
                Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
        raise ValueError(
            "Unsupported iso_boundary_temperature_rounding: "
            f"{self.iso_boundary_temperature_rounding}."
        )
