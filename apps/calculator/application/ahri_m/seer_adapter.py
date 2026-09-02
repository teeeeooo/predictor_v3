"""AHRI 210/240 Appendix M SEER application adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Mapping

from core.calculators.capability import AhriSeerRequest, execute_standard_calculation

AHRI_M_SEER_POINT_ORDER = ("A2", "B2", "EV", "B1", "F1")
AHRI_M_SEER_TEMPERATURES_C = {"A2": 35.0, "B2": 27.8, "EV": 30.6, "B1": 27.8, "F1": 19.4}


def _parse(value: str) -> float:
    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("missing")
    number = float(text)
    if not math.isfinite(number):
        raise ValueError("non-finite")
    return number


class AhriSeerInputError(ValueError):
    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI Appendix M SEER input")
        self.field_errors = dict(field_errors)


@dataclass(frozen=True)
class AhriSeerSummary:
    raw_seer: float
    published_seer: float
    seasonal_cooling_numerator: float
    seasonal_energy_denominator: float
    eer_by_point: Mapping[str, float]
    bin_details: tuple[Mapping[str, object], ...]


class AhriSeerAdapter:
    def __init__(self, capability_executor=execute_standard_calculation) -> None:
        self._execute = capability_executor

    def calculate(self, text_values: Mapping[str, str]) -> AhriSeerSummary | None:
        required = ["cd", *[f"{kind}_{point}" for point in AHRI_M_SEER_POINT_ORDER for kind in ("capacity", "power")]]
        stripped = {key: str(text_values.get(key, "")).strip() for key in required}
        if not all(stripped.values()):
            return None
        errors = {}
        numeric = {}
        for key, value in stripped.items():
            try:
                numeric[key] = _parse(value)
            except (ValueError, TypeError):
                errors[key] = "숫자 입력 필요"
        for key, value in numeric.items():
            if key != "cd" and value <= 0:
                errors[key] = "0 초과 필요"
        if "cd" in numeric and not 0 <= numeric["cd"] < 1:
            errors["cd"] = "0 이상 1 미만 필요"
        if errors:
            raise AhriSeerInputError(errors)
        points = {point: (numeric[f"capacity_{point}"], numeric[f"power_{point}"]) for point in AHRI_M_SEER_POINT_ORDER}
        result = self._execute("ahri210240.seer", AhriSeerRequest(points, c_d_cooling=numeric["cd"]))
        return AhriSeerSummary(
            raw_seer=self._required_float(result, "raw_seer"),
            published_seer=self._required_float(result, "published_seer"),
            seasonal_cooling_numerator=self._required_float(result, "seasonal_cooling_numerator"),
            seasonal_energy_denominator=self._required_float(result, "seasonal_energy_denominator"),
            eer_by_point={point: points[point][0] / points[point][1] for point in AHRI_M_SEER_POINT_ORDER},
            bin_details=self._required_rows(result),
        )

    @staticmethod
    def _required_float(result, key):
        try:
            return float(result[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid AHRI Appendix M SEER core result: {key}") from exc

    @staticmethod
    def _required_rows(result):
        rows = result.get("bin_details")
        if not isinstance(rows, (list, tuple)) or any(not isinstance(row, Mapping) for row in rows):
            raise ValueError("Invalid AHRI Appendix M SEER core result: bin_details")
        return tuple(dict(row) for row in rows)
