"""Shared 2026 primitives for product-specific multi-capacity HSPF2 engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .numeric import linear_interpolate, round_nearest_005, safe_div

RESISTANCE_BTU_PER_WH = 3.412


@dataclass(frozen=True)
class MultiCapacitySeasonalContext:
    bin_temps: tuple[float, ...]
    fractional_hours: tuple[float, ...]
    heating_load_hours: float
    slope_factor: float
    zero_load_temp_f: float
    design_temp_f: float
    t_off: float
    t_on: float
    defrost_factor: float
    defrost_source: str


def seasonal_context(config_context, options: Mapping[str, object]) -> MultiCapacitySeasonalContext:
    table = config_context.region_iv_heating_bin_table()
    t_off = float(options.get("t_off", -40.0))
    t_on = float(options.get("t_on", -40.0))
    if t_on < t_off:
        raise ValueError(f"t_on({t_on}) must be >= t_off({t_off})")
    heating_load_hours = float(table["heating_load_hours"])
    if heating_load_hours <= 0:
        raise ValueError("Region IV heating_load_hours must be positive")
    factor, source = resolve_defrost_factor(options)
    return MultiCapacitySeasonalContext(
        bin_temps=tuple(float(value) for value in table["bin_temps_f"]),
        fractional_hours=tuple(float(value) for value in table["fractional_bin_hours"]),
        heating_load_hours=heating_load_hours,
        slope_factor=float(table.get("heating_load_line_slope_factor", 1.15)),
        zero_load_temp_f=float(table.get("zero_load_temp_f", 55.0)),
        design_temp_f=float(table.get("outdoor_design_temp_f", 5.0)),
        t_off=t_off,
        t_on=t_on,
        defrost_factor=factor,
        defrost_source=source,
    )


def resolve_defrost_factor(options: Mapping[str, object]) -> tuple[float, str]:
    mode = options.get("defrost_mode")
    if mode is None:
        mode = "explicit_override" if "fdef_override" in options else "none"
    mode = str(mode).strip().lower()
    if mode == "none":
        return 1.0, "none"
    if mode == "explicit_override":
        factor = float(options.get("defrost_factor", options.get("fdef_override", 1.0)))
        if factor <= 0:
            raise ValueError("Defrost factor must be positive")
        return factor, "explicit_override"
    if mode == "calculated_from_timing":
        raw_test = float(options["defrost_t_test_minutes"])
        raw_max = float(options["defrost_t_max_minutes"])
        if raw_test <= 0 or raw_max <= 90:
            raise ValueError("Invalid defrost timing inputs")
        t_test = max(raw_test, 90.0)
        t_max = min(raw_max, 720.0)
        return 1.0 + 0.03 * (1.0 - safe_div(t_test - 90.0, t_max - 90.0)), mode
    raise ValueError(f"Unsupported defrost mode: {mode!r}")


def positive_point(
    test_points: Mapping[str, object],
    name: str,
    *aliases: str,
    required: bool = True,
) -> tuple[float, float] | None:
    candidates = (name, *aliases)
    lowered = {str(key).casefold(): value for key, value in test_points.items()}
    value = None
    for candidate in candidates:
        if candidate in test_points:
            value = test_points[candidate]
            break
        value = lowered.get(candidate.casefold())
        if value is not None:
            break
    if value is None and not required:
        return None
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(f"Missing AHRI HSPF2 test point: {name}")
    capacity, power = float(value[0]), float(value[1])
    if capacity <= 0 or power <= 0:
        raise ValueError(f"Invalid AHRI HSPF2 point {name}: capacity={capacity}, power={power}")
    return capacity, power


def building_load(temp_f: float, q_a_full: float, context: MultiCapacitySeasonalContext) -> float:
    value = q_a_full * context.slope_factor * safe_div(
        context.zero_load_temp_f - temp_f,
        context.zero_load_temp_f - context.design_temp_f,
    )
    return max(0.0, value)


def low_curve(temp_f: float, points: Mapping[str, tuple[float, float]]) -> tuple[float, float]:
    if temp_f >= 40.0:
        high, low = (62.0, points["H0Low"]), (47.0, points["H1Low"])
    elif temp_f > 17.0:
        high, low = (35.0, points["H2Low"]), (17.0, points["H3Low"])
    else:
        high, low = (47.0, points["H1Low"]), (17.0, points["H3Low"])
    return (
        max(0.0, linear_interpolate(temp_f, low[0], low[1][0], high[0], high[1][0])),
        max(0.0, linear_interpolate(temp_f, low[0], low[1][1], high[0], high[1][1])),
    )


def full_curve(
    temp_f: float,
    points: Mapping[str, tuple[float, float]],
    h4_point: tuple[float, float] | None,
) -> tuple[float, float]:
    if h4_point is None:
        anchors = (points["H3Full"], points["H1Full"], 17.0, 47.0)
        if 17.0 < temp_f < 45.0:
            anchors = (points["H3Full"], points["H2Full"], 17.0, 35.0)
    elif temp_f >= 45.0:
        anchors = (points["H3Full"], points["H1Full"], 17.0, 47.0)
    elif temp_f >= 17.0:
        anchors = (points["H3Full"], points["H2Full"], 17.0, 35.0)
    else:
        anchors = (h4_point, points["H3Full"], 5.0, 17.0)
    low, high, low_temp, high_temp = anchors
    return (
        max(0.0, linear_interpolate(temp_f, low_temp, low[0], high_temp, high[0])),
        max(0.0, linear_interpolate(temp_f, low_temp, low[1], high_temp, high[1])),
    )


def availability(temp_f: float, capacity: float, power: float, context: MultiCapacitySeasonalContext) -> float:
    cop = safe_div(capacity, power * RESISTANCE_BTU_PER_WH)
    if temp_f <= context.t_off or cop < 1.0:
        return 0.0
    if temp_f <= context.t_on:
        return 0.5
    return 1.0


def effective_cd(value: object, default: float = 0.25) -> float:
    parsed = default if value is None else float(value)
    if parsed < 0:
        raise ValueError("Degradation coefficient must be non-negative")
    return min(parsed, default)


def _seasonalize_bin_details(
    rows: list[dict], heating_load_hours: float
) -> list[dict]:
    seasonalized: list[dict] = []
    for source in rows:
        row = dict(source)
        for key in ("q_comp", "q_aux", "q_j", "e_comp", "e_aux", "E_j"):
            value = row.get(key)
            if value is None:
                continue
            row[f"normalized_{key}"] = value
            row[f"seasonal_{key}"] = float(value) * heating_load_hours
        seasonalized.append(row)
    return seasonalized


def assemble_result(
    *,
    product: str,
    formula_path: str,
    context: MultiCapacitySeasonalContext,
    total_heating: float,
    compressor_energy: float,
    resistance_energy: float,
    bin_details: list[dict],
    metadata: Mapping[str, object],
) -> dict:
    normalized_total_energy = compressor_energy + resistance_energy
    if total_heating <= 0 or normalized_total_energy <= 0:
        raise ValueError("Multi-capacity HSPF2 normalized aggregates must be positive")
    raw_base = total_heating / normalized_total_energy
    raw = raw_base * context.defrost_factor
    published = round_nearest_005(raw)
    hours = context.heating_load_hours
    seasonal_heating = total_heating * hours
    seasonal_compressor_energy = compressor_energy * hours
    seasonal_resistance_energy = resistance_energy * hours
    seasonal_total_energy = normalized_total_energy * hours
    return {
        "HSPF2": published,
        "raw_hspf2": raw,
        "raw_hspf2_base": raw_base,
        "published_hspf2": published,
        "presentation_value": published,
        "normalized_heating_aggregate": total_heating,
        "normalized_compressor_energy_wh": compressor_energy,
        "normalized_resistance_energy_wh": resistance_energy,
        "normalized_total_energy_wh": normalized_total_energy,
        "total_load": seasonal_heating,
        "total_heating_btu": seasonal_heating,
        "total_compressor_energy_wh": seasonal_compressor_energy,
        "total_resistance_energy_wh": seasonal_resistance_energy,
        "total_energy": seasonal_total_energy,
        "total_energy_wh": seasonal_total_energy,
        "product_classification": product,
        "bin_details": _seasonalize_bin_details(bin_details, hours),
        "summary": {
            "metadata": {
                "formula_path": formula_path,
                "product_classification": product,
                "heating_load_hours": hours,
                "aggregate_basis": "fractional_bin_hours_normalized",
                "seasonal_total_basis": "normalized_aggregate_times_heating_load_hours",
                "defrost": {
                    "mode": context.defrost_source,
                    "fdef_used": context.defrost_factor,
                },
                "t_off": context.t_off,
                "t_on": context.t_on,
                **dict(metadata),
            }
        },
    }
