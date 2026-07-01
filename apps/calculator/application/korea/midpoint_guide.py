"""UI-neutral midpoint guide helpers for KS C 9306 calculator screens."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MidpointGuide:
    """CSPF/HSPF midpoint design guide values for UI display."""

    current_tc: float
    recommended_tc: float
    recommended_mid_capacity: float


@dataclass(frozen=True)
class CspfGuideConfig:
    """KS C 9306 CSPF guide constants isolated from the Tk view."""

    min_test_temp: float = 29.0
    full_test_temp: float = 35.0
    zero_load_temp: float = 23.0
    full_load_temp: float = 35.0
    full_capacity_factor_35_to_29: float = 1.077
    half_capacity_factor_35_to_29: float = 1.077
    min_capacity_factor_29_to_35: float = 0.9285


def calculate_cspf_midpoint_guide(
    *,
    declared_capacity: float,
    full_capacity: float,
    half_capacity: float,
    min_capacity: float,
    config: CspfGuideConfig | None = None,
) -> MidpointGuide:
    """Calculate CSPF midpoint guide values from single-screen inputs."""
    cfg = config or CspfGuideConfig()
    load_line = _line_from_points(
        cfg.zero_load_temp,
        0.0,
        cfg.full_load_temp,
        declared_capacity,
    )
    full_line = _line_from_points(
        cfg.min_test_temp,
        full_capacity * cfg.full_capacity_factor_35_to_29,
        cfg.full_test_temp,
        full_capacity,
    )
    half_line = _line_from_points(
        cfg.min_test_temp,
        half_capacity * cfg.half_capacity_factor_35_to_29,
        cfg.full_test_temp,
        half_capacity,
    )
    min_line = _line_from_points(
        cfg.min_test_temp,
        min_capacity,
        cfg.full_test_temp,
        min_capacity * cfg.min_capacity_factor_29_to_35,
    )
    ta = _intersection_temperature(min_line, load_line)
    tb = _intersection_temperature(full_line, load_line)
    current_tc = _intersection_temperature(half_line, load_line)
    recommended_tc = (ta + tb) / 2.0
    recommended_mid_capacity = _value_at(load_line, recommended_tc)
    return MidpointGuide(
        current_tc=current_tc,
        recommended_tc=recommended_tc,
        recommended_mid_capacity=recommended_mid_capacity,
    )


def _line_from_points(t1: float, y1: float, t2: float, y2: float) -> tuple[float, float]:
    if t1 == t2:
        raise ValueError("line temperatures must differ")
    slope = (y2 - y1) / (t2 - t1)
    return slope, y1 - slope * t1


def _intersection_temperature(
    first: tuple[float, float],
    second: tuple[float, float],
) -> float:
    first_slope, first_intercept = first
    second_slope, second_intercept = second
    denominator = first_slope - second_slope
    if denominator == 0:
        raise ValueError("parallel lines do not have a midpoint guide intersection")
    return (second_intercept - first_intercept) / denominator


def _value_at(line: tuple[float, float], temperature: float) -> float:
    slope, intercept = line
    return slope * temperature + intercept
