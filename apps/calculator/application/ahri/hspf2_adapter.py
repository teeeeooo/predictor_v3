"""Thin AHRI HSPF2 main UI-to-core adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Protocol

from core.calculators.dispatcher import create_calculator_for_profile

AHRI_HSPF2_POINT_ORDER = (
    "H01",
    "H11",
    "H1N",
    "H2Int",
    "H32",
    "H42",
    "H12",
    "H22",
)
AHRI_HSPF2_TEMPERATURES_C = {
    "H01": 16.7,
    "H11": 8.3,
    "H1N": 8.3,
    "H2Int": 1.7,
    "H32": -8.3,
    "H42": -15.0,
    "H12": 8.3,
    "H22": 1.7,
}
AHRI_HSPF2_OPTIONAL_POINTS = ("H42", "H12", "H22")
AHRI_HSPF2_HIDDEN_DEFAULTS = {
    "defrost_t_test_minutes": 90.0,
    "defrost_t_max_minutes": 720.0,
}
# A2 power is not used by the HSPF2 formula. This positive placeholder only
# satisfies the current core point-tuple validation contract.
_A2_CORE_POWER_PLACEHOLDER = 1.0


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


class _Hspf2Calculator(Protocol):
    def calculate_hspf2(
        self,
        test_points: Mapping[str, tuple[float, float]],
        **kwargs: object,
    ) -> Mapping[str, object]: ...


class AhriHspf2InputError(ValueError):
    """Non-empty HSPF2 UI fields that cannot be calculated."""

    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI HSPF2 input")
        self.field_errors = dict(field_errors)


@dataclass(frozen=True)
class AhriHspf2Options:
    region: str = "IV"
    measured_h42: bool = True
    measured_h12: bool = False
    measured_h22: bool = False
    h1n_same_speed_as_h32: bool = False
    minimum_speed_limited: bool = True


@dataclass(frozen=True)
class AhriHspf2Summary:
    hspf2: float
    total_heating_kbtu: float
    total_energy_kwh: float
    h12_source: str
    h22_source: str
    h42_source: str
    bin_details: tuple[Mapping[str, object], ...] = ()


class AhriHspf2Adapter:
    """Parse UI text, omit inactive points, inject defaults, and call core."""

    _NUMERIC_KEYS = ("cd", "defrost_credit", "cut_out_c", "cut_in_c")

    def __init__(self, calculator: _Hspf2Calculator | None = None) -> None:
        self._calculator = calculator or create_calculator_for_profile(
            profile_id="ahri_usa_hspf2"
        )

    def calculate(
        self,
        text_values: Mapping[str, str],
        *,
        options: AhriHspf2Options,
    ) -> AhriHspf2Summary | None:
        if options.region != "IV":
            raise AhriHspf2InputError({"region": "Region IV 필요"})

        active_optional = {
            "H42": options.measured_h42,
            "H12": options.measured_h12,
            "H22": options.measured_h22,
        }
        required_fields = [*self._NUMERIC_KEYS, "a2_capacity"]
        active_points: list[str] = []
        for point in AHRI_HSPF2_POINT_ORDER:
            if point in active_optional and not active_optional[point]:
                continue
            active_points.append(point)
            required_fields.extend((f"capacity_{point}", f"power_{point}"))

        stripped = {key: str(text_values.get(key, "")).strip() for key in required_fields}
        if not all(stripped.values()):
            return None

        numeric: dict[str, float] = {}
        errors: dict[str, str] = {}
        for key, value in stripped.items():
            try:
                numeric[key] = parse_numeric_cell(value)
            except ValueError:
                errors[key] = "숫자 입력 필요"
        for key in required_fields:
            if key in numeric and key not in self._NUMERIC_KEYS and numeric[key] <= 0:
                errors[key] = "0 초과 필요"
        if numeric.get("cd", 0.0) < 0:
            errors["cd"] = "0 이상 필요"
        if numeric.get("defrost_credit", 0.0) <= 0:
            errors["defrost_credit"] = "0 초과 필요"
        if errors:
            raise AhriHspf2InputError(errors)

        points = {
            point: (numeric[f"capacity_{point}"], numeric[f"power_{point}"])
            for point in active_points
        }
        points["A2"] = (numeric["a2_capacity"], _A2_CORE_POWER_PLACEHOLDER)
        result = self._calculator.calculate_hspf2(
            points,
            t_off=self._celsius_to_fahrenheit(numeric["cut_out_c"]),
            t_on=self._celsius_to_fahrenheit(numeric["cut_in_c"]),
            c_d_heating=numeric["cd"],
            fdef_override=numeric["defrost_credit"],
            h1n_same_speed_as_h3=options.h1n_same_speed_as_h32,
            minimum_speed_limited=options.minimum_speed_limited,
            **AHRI_HSPF2_HIDDEN_DEFAULTS,
        )
        metadata = self._required_mapping(
            self._required_mapping(result, "summary"), "metadata"
        )
        return AhriHspf2Summary(
            hspf2=self._required_float(result, "HSPF2"),
            total_heating_kbtu=(
                self._required_float(result, "total_heating_btu") / 1000.0
            ),
            total_energy_kwh=(
                self._required_float(result, "total_energy_wh") / 1000.0
            ),
            h12_source=self._calculated_source(metadata, "h12_source"),
            h22_source=self._calculated_source(metadata, "h22_source"),
            h42_source=self._h42_source(result),
            bin_details=self._required_bin_details(result),
        )

    def compute_display_cops(
        self,
        text_values: Mapping[str, str],
        *,
        options: AhriHspf2Options,
    ) -> dict[str, float]:
        """Return valid display-only COP values without changing core input."""
        enabled_optional = {
            "H42": options.measured_h42,
            "H12": options.measured_h12,
            "H22": options.measured_h22,
        }
        pairs = {
            point: (f"capacity_{point}", f"power_{point}")
            for point in AHRI_HSPF2_POINT_ORDER
            if enabled_optional.get(point, True)
        }
        cops: dict[str, float] = {}
        for point, (capacity_key, power_key) in pairs.items():
            try:
                capacity = parse_numeric_cell(str(text_values.get(capacity_key, "")))
                power = parse_numeric_cell(str(text_values.get(power_key, "")))
            except ValueError:
                continue
            if capacity > 0 and power > 0:
                cops[point] = capacity / power
        return cops

    @staticmethod
    def _celsius_to_fahrenheit(value: float) -> float:
        return value * 9.0 / 5.0 + 32.0

    @staticmethod
    def _required_float(result: Mapping[str, object], key: str) -> float:
        try:
            return float(result[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid AHRI HSPF2 core result: {key}") from exc

    @staticmethod
    def _required_mapping(
        result: Mapping[str, object], key: str
    ) -> Mapping[str, object]:
        value = result.get(key)
        if not isinstance(value, Mapping):
            raise ValueError(f"Invalid AHRI HSPF2 core result: {key}")
        return value

    @staticmethod
    def _required_bin_details(
        result: Mapping[str, object],
    ) -> tuple[Mapping[str, object], ...]:
        rows = result.get("bin_details")
        if not isinstance(rows, (list, tuple)):
            raise ValueError("Invalid AHRI HSPF2 core result: bin_details")
        if any(not isinstance(row, Mapping) for row in rows):
            raise ValueError("Invalid AHRI HSPF2 core result: bin_details")
        return tuple(dict(row) for row in rows)

    @staticmethod
    def _calculated_source(metadata: Mapping[str, object], key: str) -> str:
        value = metadata.get(key)
        if value == "tested":
            return "measured"
        if isinstance(value, str) and value:
            return "calculated"
        raise ValueError(f"Invalid AHRI HSPF2 core result: {key}")

    @staticmethod
    def _h42_source(result: Mapping[str, object]) -> str:
        value = result.get("h42_source")
        if value == "provided":
            return "measured"
        if value == "not_provided":
            return "not provided"
        raise ValueError("Invalid AHRI HSPF2 core result: h42_source")
