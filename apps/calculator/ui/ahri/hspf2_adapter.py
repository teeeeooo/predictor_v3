"""Thin AHRI HSPF2 main UI-to-core adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from apps.calculator.ui.table_grid_model import parse_numeric_cell
from core.calculator_dispatcher import create_calculator_for_profile

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
        required_fields = [*self._NUMERIC_KEYS, "a2_capacity", "a2_power"]
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
        points["A2"] = (numeric["a2_capacity"], numeric["a2_power"])
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
        return AhriHspf2Summary(hspf2=self._required_float(result, "HSPF2"))

    @staticmethod
    def _celsius_to_fahrenheit(value: float) -> float:
        return value * 9.0 / 5.0 + 32.0

    @staticmethod
    def _required_float(result: Mapping[str, object], key: str) -> float:
        try:
            return float(result[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid AHRI HSPF2 core result: {key}") from exc
