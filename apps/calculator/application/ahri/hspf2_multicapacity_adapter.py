"""Product-specific AHRI HSPF2 application parsing and summary mapping."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from core.calculators.capability import AhriHspf2Request

AHRI_HSPF2_DUAL_POINT_ORDER = (
    "H0Low",
    "H1Low",
    "H1Full",
    "H2Low",
    "H2Full",
    "H3Low",
    "H3Full",
    "H4Full",
)
AHRI_HSPF2_TRIPLE_POINT_ORDER = (
    "H0Low",
    "H1Low",
    "H2Low",
    "H3Low",
    "H1Full",
    "H2Full",
    "H3Full",
    "H2Boost",
    "H3Boost",
    "H4Boost",
)


@dataclass(frozen=True)
class AhriHspf2Options:
    region: str = "IV"
    measured_h42: bool = True
    measured_h12: bool = False
    measured_h22: bool = False
    h1n_same_speed_as_h32: bool = False
    minimum_speed_limited: bool = True
    product_classification: str = "variable_capacity"
    measured_h4_full: bool = False
    measured_h2_low: bool = True
    measured_h2_boost: bool = True
    measured_h3_low: bool = True
    low_stage_lockout_enabled: bool = False
    defrost_mode: str = "explicit_override"


@dataclass(frozen=True)
class MultiCapacityHspf2Summary:
    hspf2: float
    raw_hspf2: float
    published_hspf2: float
    total_heating_kbtu: float
    compressor_energy_kwh: float
    resistance_energy_kwh: float
    total_energy_kwh: float
    normalized_heating_aggregate: float
    normalized_compressor_energy_wh: float
    normalized_resistance_energy_wh: float
    normalized_total_energy_wh: float
    heating_load_hours: float
    product_classification: str
    point_sources: Mapping[str, str]
    bin_details: tuple[Mapping[str, object], ...]


class MultiCapacityHspf2InputError(ValueError):
    def __init__(self, field_errors: Mapping[str, str]) -> None:
        super().__init__("Invalid AHRI multi-capacity HSPF2 input")
        self.field_errors = dict(field_errors)


def calculate_multicapacity_hspf2(
    executor,
    text_values: Mapping[str, str],
    *,
    options: AhriHspf2Options,
) -> MultiCapacityHspf2Summary | None:
    product = options.product_classification
    if product not in {"dual_stage", "triple_capacity_northern"}:
        raise MultiCapacityHspf2InputError({"product": "지원하지 않는 제품 형식"})
    if options.region != "IV":
        raise MultiCapacityHspf2InputError({"region": "Region IV 필요"})
    points_order = (
        AHRI_HSPF2_DUAL_POINT_ORDER
        if product == "dual_stage"
        else AHRI_HSPF2_TRIPLE_POINT_ORDER
    )
    optional_points = _optional_point_state(options)
    active_points = [
        point for point in points_order if optional_points.get(point, True)
    ]
    required = ["a2_capacity", "cut_out_c", "cut_in_c", "cd_low", "cd_full"]
    if product == "triple_capacity_northern":
        required.append("cd_boost")
        required.extend(
            f"{stage}_{bound}_c"
            for stage in ("low", "full", "boost")
            for bound in ("min", "max")
        )
    if product == "dual_stage" and options.low_stage_lockout_enabled:
        required.append("low_stage_lockout_temp_c")
    if options.defrost_mode == "explicit_override":
        required.append("defrost_factor")
    elif options.defrost_mode == "calculated_from_timing":
        required.extend(("defrost_t_test_minutes", "defrost_t_max_minutes"))
    elif options.defrost_mode != "none":
        raise MultiCapacityHspf2InputError(
            {"defrost_mode": "지원하지 않는 제상 모드"}
        )
    for point in active_points:
        required.extend((f"capacity_{point}", f"power_{point}"))
    stripped = {key: str(text_values.get(key, "")).strip() for key in required}
    if not all(stripped.values()):
        return None
    numeric: dict[str, float] = {}
    errors: dict[str, str] = {}
    for key, text in stripped.items():
        try:
            numeric[key] = _parse_numeric(text)
        except ValueError:
            errors[key] = "숫자 입력 필요"
    for key, value in numeric.items():
        if (
            key.startswith(("capacity_", "power_")) or key == "a2_capacity"
        ) and value <= 0:
            errors[key] = "0 초과 필요"
        if key.startswith("cd_") and value < 0:
            errors[key] = "0 이상 필요"
    if product == "triple_capacity_northern":
        for stage in ("low", "full", "boost"):
            low_key, high_key = f"{stage}_min_c", f"{stage}_max_c"
            if (
                low_key in numeric
                and high_key in numeric
                and numeric[low_key] > numeric[high_key]
            ):
                errors[low_key] = "하한은 상한 이하 필요"
                errors[high_key] = "상한은 하한 이상 필요"
    if errors:
        raise MultiCapacityHspf2InputError(errors)
    points = {
        point: (numeric[f"capacity_{point}"], numeric[f"power_{point}"])
        for point in active_points
    }
    points["AFull"] = (numeric["a2_capacity"], 1.0)
    parameters: dict[str, object] = {
        "t_off": _c_to_f(numeric["cut_out_c"]),
        "t_on": _c_to_f(numeric["cut_in_c"]),
        "cd_low": numeric["cd_low"],
        "cd_full": numeric["cd_full"],
        "defrost_mode": options.defrost_mode,
    }
    if options.defrost_mode == "explicit_override":
        parameters["defrost_factor"] = numeric["defrost_factor"]
    elif options.defrost_mode == "calculated_from_timing":
        parameters["defrost_t_test_minutes"] = numeric[
            "defrost_t_test_minutes"
        ]
        parameters["defrost_t_max_minutes"] = numeric[
            "defrost_t_max_minutes"
        ]
    if product == "dual_stage":
        parameters.update(
            {
                "h2_low_tested": options.measured_h2_low,
                "h4_full_tested": options.measured_h4_full,
                "low_stage_lockout_enabled": options.low_stage_lockout_enabled,
            }
        )
        if options.low_stage_lockout_enabled:
            parameters["low_stage_lockout_temp_f"] = _c_to_f(
                numeric["low_stage_lockout_temp_c"]
            )
    else:
        h2_low_tested = options.measured_h2_low and not options.measured_h3_low
        parameters.update(
            {
                "h2_low_tested": h2_low_tested,
                "h2_boost_tested": options.measured_h2_boost,
                "h3_low_tested": options.measured_h3_low,
                "cd_boost": numeric["cd_boost"],
                "stage_ranges_f": {
                    stage: (
                        _c_to_f(numeric[f"{stage}_min_c"]),
                        _c_to_f(numeric[f"{stage}_max_c"]),
                    )
                    for stage in ("low", "full", "boost")
                },
            }
        )
    result = executor(
        "ahri210240.hspf2",
        AhriHspf2Request(
            points,
            product_classification=product,
            parameters=parameters,
        ),
    )
    metadata = _required_mapping(_required_mapping(result, "summary"), "metadata")
    point_sources = metadata.get("point_sources", {})
    if not isinstance(point_sources, Mapping):
        raise ValueError("Invalid AHRI HSPF2 core result: point_sources")
    return MultiCapacityHspf2Summary(
        hspf2=_required_float(result, "HSPF2"),
        raw_hspf2=_required_float(result, "raw_hspf2"),
        published_hspf2=_required_float(result, "published_hspf2"),
        total_heating_kbtu=_required_float(result, "total_heating_btu") / 1000.0,
        compressor_energy_kwh=(
            _required_float(result, "total_compressor_energy_wh") / 1000.0
        ),
        resistance_energy_kwh=(
            _required_float(result, "total_resistance_energy_wh") / 1000.0
        ),
        total_energy_kwh=_required_float(result, "total_energy_wh") / 1000.0,
        normalized_heating_aggregate=_required_float(
            result, "normalized_heating_aggregate"
        ),
        normalized_compressor_energy_wh=_required_float(
            result, "normalized_compressor_energy_wh"
        ),
        normalized_resistance_energy_wh=_required_float(
            result, "normalized_resistance_energy_wh"
        ),
        normalized_total_energy_wh=_required_float(
            result, "normalized_total_energy_wh"
        ),
        heating_load_hours=_required_float(metadata, "heating_load_hours"),
        product_classification=str(result.get("product_classification", product)),
        point_sources={str(key): str(value) for key, value in point_sources.items()},
        bin_details=_required_bin_details(result),
    )


def _optional_point_state(options: AhriHspf2Options) -> dict[str, bool]:
    if options.product_classification == "dual_stage":
        return {
            "H2Low": options.measured_h2_low,
            "H4Full": options.measured_h4_full,
        }
    return {
        "H2Low": options.measured_h2_low and not options.measured_h3_low,
        "H2Boost": options.measured_h2_boost,
        "H3Low": options.measured_h3_low,
    }


def _parse_numeric(value: str) -> float:
    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("numeric cell is missing")
    parsed = float(text)
    if not math.isfinite(parsed):
        raise ValueError("numeric cell must be finite")
    return parsed


def _c_to_f(value: float) -> float:
    return value * 9.0 / 5.0 + 32.0


def _required_float(result: Mapping[str, object], key: str) -> float:
    try:
        return float(result[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid AHRI HSPF2 core result: {key}") from exc


def _required_mapping(
    result: Mapping[str, object], key: str
) -> Mapping[str, object]:
    value = result.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid AHRI HSPF2 core result: {key}")
    return value


def _required_bin_details(
    result: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    rows = result.get("bin_details")
    if not isinstance(rows, (list, tuple)) or any(
        not isinstance(row, Mapping) for row in rows
    ):
        raise ValueError("Invalid AHRI HSPF2 core result: bin_details")
    return tuple(dict(row) for row in rows)
