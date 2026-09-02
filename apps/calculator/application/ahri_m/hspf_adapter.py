"""AHRI 210/240-2017 Appendix M HSPF application adapter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Mapping

from core.calculators.capability import AhriHspfRequest, execute_standard_calculation

AHRI_M_HSPF_POINT_ORDER = ("H01", "H11", "H1N", "H2V", "H32", "H12", "H22")
AHRI_M_HSPF_REQUIRED_POINTS = ("H01", "H11", "H1N", "H2V", "H32")
AHRI_M_HSPF_OPTIONAL_POINTS = ("H12", "H22")
AHRI_M_HSPF_TEMPERATURES_C = {"H01": 16.7, "H11": 8.3, "H1N": 8.3, "H2V": 1.7, "H32": -8.3, "H12": 8.3, "H22": 1.7}


def _parse(value: str) -> float:
    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("missing")
    number = float(text)
    if not math.isfinite(number):
        raise ValueError("non-finite")
    return number


class AhriHspfInputError(ValueError):
    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI Appendix M HSPF input")
        self.field_errors = dict(field_errors)


@dataclass(frozen=True)
class AhriHspfOptions:
    measured_h12: bool = False
    measured_h22: bool = False
    h1n_same_speed_as_h32: bool = False
    automatic_cutout: bool = True
    demand_defrost: bool = False


@dataclass(frozen=True)
class AhriHspfSummary:
    raw_hspf: float
    published_hspf: float
    dhr_min_raw: float
    dhr_min_standardized: float
    heating_load_aggregate: float
    compressor_energy_aggregate: float
    resistance_energy_aggregate: float
    defrost_credit: float
    h12_source: str
    h22_source: str
    bin_details: tuple[Mapping[str, object], ...]


class AhriHspfAdapter:
    def __init__(self, capability_executor=execute_standard_calculation) -> None:
        self._execute = capability_executor

    def calculate(self, text_values: Mapping[str, str], *, options: AhriHspfOptions) -> AhriHspfSummary | None:
        errors = {}
        numeric = {}
        points = {}
        for point in AHRI_M_HSPF_REQUIRED_POINTS:
            pair = self._pair(text_values, point, errors=errors)
            if pair is None:
                if errors:
                    continue
                return None
            points[point] = pair
        for point, enabled in (("H12", options.measured_h12), ("H22", options.measured_h22)):
            if not enabled:
                continue
            pair = self._pair(text_values, point, errors=errors)
            if pair is None and not errors:
                return None
            if pair is not None:
                points[point] = pair
        numeric_keys = ("cd",)
        if options.demand_defrost:
            numeric_keys += ("defrost_test_minutes", "defrost_max_minutes")
        if options.automatic_cutout:
            numeric_keys += ("cut_out_c", "cut_in_c")
        for key in numeric_keys:
            text = str(text_values.get(key, "")).strip()
            if not text:
                if errors:
                    continue
                return None
            try:
                numeric[key] = _parse(text)
            except (ValueError, TypeError):
                errors[key] = "숫자 입력 필요"
        if "cd" in numeric and not 0 <= numeric["cd"] < 1:
            errors["cd"] = "0 이상 1 미만 필요"
        if options.demand_defrost and {"defrost_test_minutes", "defrost_max_minutes"} <= numeric.keys():
            if numeric["defrost_test_minutes"] <= 0:
                errors["defrost_test_minutes"] = "0 초과 필요"
            if numeric["defrost_max_minutes"] <= 90:
                errors["defrost_max_minutes"] = "90분 초과 필요"
            if numeric["defrost_test_minutes"] > numeric["defrost_max_minutes"]:
                errors["defrost_test_minutes"] = "Defrost Test는 Defrost Max 이하 필요"
        if options.automatic_cutout and {"cut_out_c", "cut_in_c"} <= numeric.keys() and numeric["cut_in_c"] < numeric["cut_out_c"]:
            errors["cut_in_c"] = "Cut In은 Cut Out 이상 필요"
        if errors:
            raise AhriHspfInputError(errors)
        params = {
            "h1n_same_speed_as_h32": options.h1n_same_speed_as_h32,
            "c_d_heating": numeric["cd"],
            "demand_defrost": options.demand_defrost,
        }
        if options.demand_defrost:
            params["defrost_test_minutes"] = numeric["defrost_test_minutes"]
            params["defrost_max_minutes"] = numeric["defrost_max_minutes"]
        if options.automatic_cutout:
            params["t_off"] = self._c_to_f(numeric["cut_out_c"])
            params["t_on"] = self._c_to_f(numeric["cut_in_c"])
        result = self._execute("ahri210240.hspf", AhriHspfRequest(points, parameters=params))
        metadata = self._mapping(self._mapping(result, "summary"), "metadata")
        return AhriHspfSummary(
            raw_hspf=self._float(result, "raw_hspf"),
            published_hspf=self._float(result, "published_hspf"),
            dhr_min_raw=self._float(result, "dhr_min_raw"),
            dhr_min_standardized=self._float(result, "dhr_min_standardized"),
            heating_load_aggregate=self._float(result, "seasonal_heating_load_numerator"),
            compressor_energy_aggregate=self._float(result, "seasonal_compressor_energy_denominator"),
            resistance_energy_aggregate=self._float(result, "seasonal_resistance_energy_denominator"),
            defrost_credit=self._float(result, "f_def"),
            h12_source=str(metadata["h12_source"]), h22_source=str(metadata["h22_source"]),
            bin_details=self._rows(result),
        )

    def compute_display_cops(self, text_values: Mapping[str, str], *, options: AhriHspfOptions) -> dict[str, float]:
        active = set(AHRI_M_HSPF_REQUIRED_POINTS)
        if options.measured_h12: active.add("H12")
        if options.measured_h22: active.add("H22")
        values = {}
        for point in AHRI_M_HSPF_POINT_ORDER:
            if point not in active: continue
            try:
                q = _parse(str(text_values.get(f"capacity_{point}", "")))
                p = _parse(str(text_values.get(f"power_{point}", "")))
            except (ValueError, TypeError):
                continue
            if q > 0 and p > 0: values[point] = q / p
        return values

    @staticmethod
    def _pair(values, point, *, errors):
        ckey, pkey = f"capacity_{point}", f"power_{point}"
        ctext, ptext = str(values.get(ckey, "")).strip(), str(values.get(pkey, "")).strip()
        if not ctext and not ptext:
            return None
        if not ctext or not ptext:
            errors[ckey if not ctext else pkey] = "Capacity와 Power를 함께 입력"
            return None
        try:
            c, p = _parse(ctext), _parse(ptext)
        except (ValueError, TypeError):
            try: _parse(ctext)
            except (ValueError, TypeError): errors[ckey] = "숫자 입력 필요"
            try: _parse(ptext)
            except (ValueError, TypeError): errors[pkey] = "숫자 입력 필요"
            return None
        if c <= 0: errors[ckey] = "0 초과 필요"
        if p <= 0: errors[pkey] = "0 초과 필요"
        return None if c <= 0 or p <= 0 else (c, p)

    @staticmethod
    def _c_to_f(value): return value * 9.0 / 5.0 + 32.0
    @staticmethod
    def _float(result, key):
        try: return float(result[key])
        except (KeyError, TypeError, ValueError) as exc: raise ValueError(f"Invalid AHRI Appendix M HSPF core result: {key}") from exc
    @staticmethod
    def _mapping(result, key):
        value = result.get(key)
        if not isinstance(value, Mapping): raise ValueError(f"Invalid AHRI Appendix M HSPF core result: {key}")
        return value
    @staticmethod
    def _rows(result):
        rows = result.get("bin_details")
        if not isinstance(rows, (list, tuple)) or any(not isinstance(row, Mapping) for row in rows): raise ValueError("Invalid AHRI Appendix M HSPF core result: bin_details")
        return tuple(dict(row) for row in rows)
