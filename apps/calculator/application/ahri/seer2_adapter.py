"""Thin AHRI SEER2 UI-to-core adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Protocol

from apps.calculator.adapters.ahri_calculator_factory import (
    create_ahri_seer2_calculator,
)
from core.calculators.capability import AhriSeer2Request, execute_standard_calculation

AHRI_SEER2_POINT_ORDER = ("A_Full", "B_Full", "B_Low", "E_Int", "F_Low")
AHRI_SEER2_TEMPERATURES_C = {
    "A_Full": 35.0,
    "B_Full": 27.8,
    "B_Low": 27.8,
    "E_Int": 23.9,
    "F_Low": 17.2,
}


def parse_numeric_cell(value: str) -> float:
    """Parse numeric text after trimming whitespace and thousands commas."""
    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("numeric cell is missing")
    try:
        parsed = float(text)
    except ValueError as exc:
        raise ValueError(f"invalid numeric cell value: {value!r}") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"numeric cell must be finite: {value!r}")
    return parsed


class _Seer2Calculator(Protocol):
    config: Mapping[str, object]

    def calculate_seer2(
        self,
        test_points: Mapping[str, tuple[float, float]],
        system_type: str = "HP",
        p_w_off: float = 0.0,
        cd_low: float | None = None,
    ) -> Mapping[str, object]: ...


class AhriSeer2InputError(ValueError):
    """Non-empty SEER2 input fields that cannot be calculated."""

    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI SEER2 input")
        self.field_errors = dict(field_errors)


@dataclass(frozen=True)
class AhriSeer2Summary:
    seer2: float
    total_cooling_kbtu: float
    total_energy_kwh: float
    eer2_by_point: Mapping[str, float]
    bin_details: tuple[Mapping[str, object], ...] = ()


class AhriSeer2Adapter:
    """Parse the UI matrix and call the existing SEER2 calculator contract."""

    def __init__(
        self,
        capability_executor=execute_standard_calculation,
        *,
        calculator_config: Mapping[str, object] | None = None,
    ) -> None:
        self._calculator = None if calculator_config is not None else create_ahri_seer2_calculator()
        self._calculator_config = calculator_config
        self._execute = capability_executor

    def calculate(
        self,
        text_values: Mapping[str, str],
        *,
        system_type: str,
    ) -> AhriSeer2Summary | None:
        if system_type not in {"HP", "AC"}:
            raise AhriSeer2InputError({"system_type": "HP 또는 AC 필요"})

        field_errors: dict[str, str] = {}
        points: dict[str, tuple[float, float]] = {}
        incomplete = False
        for point in AHRI_SEER2_POINT_ORDER:
            capacity_key = f"capacity_{point}"
            power_key = f"power_{point}"
            capacity_text = text_values.get(capacity_key, "").strip()
            power_text = text_values.get(power_key, "").strip()
            if not capacity_text or not power_text:
                incomplete = True
                continue
            try:
                capacity = parse_numeric_cell(capacity_text)
            except ValueError:
                field_errors[capacity_key] = "숫자 입력 필요"
                continue
            try:
                power = parse_numeric_cell(power_text)
            except ValueError:
                field_errors[power_key] = "숫자 입력 필요"
                continue
            if capacity <= 0:
                field_errors[capacity_key] = "0 초과 필요"
            if power <= 0:
                field_errors[power_key] = "0 초과 필요"
            points[point] = (capacity, power)

        if field_errors:
            raise AhriSeer2InputError(field_errors)
        if incomplete:
            return None

        result = self._execute(
            "ahri210240.seer2",
            AhriSeer2Request(points, system_type=system_type),
        )
        cooling_season_hours = self._cooling_season_hours()
        return AhriSeer2Summary(
            seer2=self._required_float(result, "SEER2"),
            total_cooling_kbtu=(
                self._required_float(result, "total_cooling_Btu")
                * cooling_season_hours
                / 1000.0
            ),
            total_energy_kwh=(
                self._required_float(result, "total_energy_Wh")
                * cooling_season_hours
                / 1000.0
            ),
            eer2_by_point={
                point: points[point][0] / points[point][1]
                for point in AHRI_SEER2_POINT_ORDER
            },
            bin_details=self._required_bin_details(result),
        )

    def _cooling_season_hours(self) -> float:
        key = "cooling_season_hours"
        try:
            config = self._calculator_config or self._calculator.config
            constants = config["constants"]
            if not isinstance(constants, Mapping):
                raise TypeError("constants must be a mapping")
            value = float(constants[key])
            if value <= 0:
                raise ValueError("must be positive")
            return value
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid AHRI SEER2 calculator config: {key}"
            ) from exc

    @staticmethod
    def _required_float(result: Mapping[str, object], key: str) -> float:
        try:
            return float(result[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid AHRI SEER2 core result: {key}") from exc

    @staticmethod
    def _required_bin_details(
        result: Mapping[str, object],
    ) -> tuple[Mapping[str, object], ...]:
        rows = result.get("bin_details")
        if not isinstance(rows, (list, tuple)):
            raise ValueError("Invalid AHRI SEER2 core result: bin_details")
        if any(not isinstance(row, Mapping) for row in rows):
            raise ValueError("Invalid AHRI SEER2 core result: bin_details")
        return tuple(dict(row) for row in rows)
