"""Product-aware AHRI HSPF2 UI-to-capability adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from apps.calculator.application.ahri.hspf2_multicapacity_adapter import (
    AhriHspf2Options,
    MultiCapacityHspf2InputError,
    calculate_multicapacity_hspf2,
)
from core.calculators.capability import AhriHspf2Request, execute_standard_calculation

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
    "H0Low": 16.7,
    "H1Low": 8.3,
    "H1Full": 8.3,
    "H2Low": 1.7,
    "H2Full": 1.7,
    "H2Boost": 1.7,
    "H3Low": -8.3,
    "H3Full": -8.3,
    "H3Boost": -8.3,
    "H4Full": -15.0,
    "H4Boost": -15.0,
}
AHRI_HSPF2_OPTIONAL_POINTS = ("H42", "H12", "H22")
AHRI_HSPF2_HIDDEN_DEFAULTS = {
    "defrost_t_test_minutes": 90.0,
    "defrost_t_max_minutes": 720.0,
}
_A2_CORE_POWER_PLACEHOLDER = 1.0


def parse_numeric_cell(value: str) -> float:
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


class AhriHspf2InputError(ValueError):
    """Non-empty HSPF2 UI fields that cannot be calculated."""

    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI HSPF2 input")
        self.field_errors = dict(field_errors)


@dataclass(frozen=True)
class AhriHspf2Summary:
    hspf2: float
    total_heating_kbtu: float
    total_energy_kwh: float
    h12_source: str
    h22_source: str
    h42_source: str
    bin_details: tuple[Mapping[str, object], ...] = ()
    raw_hspf2: float | None = None
    published_hspf2: float | None = None
    product_classification: str = "variable_capacity"
    compressor_energy_kwh: float | None = None
    resistance_energy_kwh: float | None = None
    point_sources: Mapping[str, str] | None = None


class AhriHspf2Adapter:
    """Parse only the active product surface and preserve the variable path."""

    _NUMERIC_KEYS = ("cd", "defrost_credit", "cut_out_c", "cut_in_c")

    def __init__(self, capability_executor=execute_standard_calculation) -> None:
        self._execute = capability_executor

    def calculate(
        self,
        text_values: Mapping[str, str],
        *,
        options: AhriHspf2Options,
    ) -> AhriHspf2Summary | None:
        if options.product_classification != "variable_capacity":
            try:
                summary = calculate_multicapacity_hspf2(
                    self._execute,
                    text_values,
                    options=options,
                )
            except MultiCapacityHspf2InputError as exc:
                raise AhriHspf2InputError(exc.field_errors) from exc
            if summary is None:
                return None
            return AhriHspf2Summary(
                hspf2=summary.hspf2,
                total_heating_kbtu=summary.total_heating_kbtu,
                total_energy_kwh=summary.total_energy_kwh,
                h12_source=summary.point_sources.get("H1Full", "measured"),
                h22_source=summary.point_sources.get("H2Full", "measured"),
                h42_source=summary.point_sources.get(
                    "H4Full", summary.point_sources.get("H4Boost", "not provided")
                ),
                bin_details=summary.bin_details,
                raw_hspf2=summary.raw_hspf2,
                published_hspf2=summary.published_hspf2,
                product_classification=summary.product_classification,
                compressor_energy_kwh=summary.compressor_energy_kwh,
                resistance_energy_kwh=summary.resistance_energy_kwh,
                point_sources=summary.point_sources,
            )
        return self._calculate_variable(text_values, options=options)

    def _calculate_variable(
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
        result = self._execute(
            "ahri210240.hspf2",
            AhriHspf2Request(
                points,
                parameters={
                    "t_off": self._celsius_to_fahrenheit(numeric["cut_out_c"]),
                    "t_on": self._celsius_to_fahrenheit(numeric["cut_in_c"]),
                    "c_d_heating": numeric["cd"],
                    "fdef_override": numeric["defrost_credit"],
                    "h1n_same_speed_as_h3": options.h1n_same_speed_as_h32,
                    "minimum_speed_limited": options.minimum_speed_limited,
                    **AHRI_HSPF2_HIDDEN_DEFAULTS,
                },
            ),
        )
        metadata = self._required_mapping(
            self._required_mapping(result, "summary"), "metadata"
        )
        return AhriHspf2Summary(
            hspf2=self._required_float(result, "HSPF2"),
            total_heating_kbtu=self._required_float(result, "total_heating_btu") / 1000.0,
            total_energy_kwh=self._required_float(result, "total_energy_wh") / 1000.0,
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
        if options.product_classification == "variable_capacity":
            enabled_optional = {
                "H42": options.measured_h42,
                "H12": options.measured_h12,
                "H22": options.measured_h22,
            }
            points = [
                point
                for point in AHRI_HSPF2_POINT_ORDER
                if enabled_optional.get(point, True)
            ]
        elif options.product_classification == "dual_stage":
            points = [
                point
                for point in (
                    "H0Low", "H1Low", "H1Full", "H2Low", "H2Full",
                    "H3Low", "H3Full", "H4Full",
                )
                if point not in {"H2Low", "H4Full"}
                or (
                    point == "H2Low" and options.measured_h2_low
                    or point == "H4Full" and options.measured_h4_full
                )
            ]
        else:
            points = [
                point
                for point in (
                    "H0Low", "H1Low", "H1Full", "H2Boost", "H2Full",
                    "H3Low", "H3Full", "H3Boost", "H4Boost",
                )
                if point not in {"H2Boost", "H3Low"}
                or (
                    point == "H2Boost" and options.measured_h2_boost
                    or point == "H3Low" and options.measured_h3_low
                )
            ]
        cops: dict[str, float] = {}
        for point in points:
            try:
                capacity = parse_numeric_cell(str(text_values.get(f"capacity_{point}", "")))
                power = parse_numeric_cell(str(text_values.get(f"power_{point}", "")))
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
    def _required_mapping(result: Mapping[str, object], key: str) -> Mapping[str, object]:
        value = result.get(key)
        if not isinstance(value, Mapping):
            raise ValueError(f"Invalid AHRI HSPF2 core result: {key}")
        return value

    @staticmethod
    def _required_bin_details(result: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
        rows = result.get("bin_details")
        if not isinstance(rows, (list, tuple)) or any(not isinstance(row, Mapping) for row in rows):
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
