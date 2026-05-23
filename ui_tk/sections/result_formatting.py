"""Pure user-facing result summary formatting for Tkinter ISO metrics."""

from __future__ import annotations

from typing import Mapping

from ui_tk.result_models import ResultSummary

__all__ = ["summarize_cspf_result", "summarize_hspf_result"]


def _value(result: Mapping[str, object], aliases: tuple[str, ...]) -> float | None:
    for key in aliases:
        raw_value = result.get(key)
        if raw_value is not None:
            return float(raw_value)
    return None


def _metric_value(result: Mapping[str, object], key: str) -> str:
    value = _value(result, (key,))
    return "-" if value is None else f"{value:.3f}"


def _kwh_value(
    result: Mapping[str, object],
    *,
    kwh_aliases: tuple[str, ...],
    wh_aliases: tuple[str, ...],
) -> str:
    value = _value(result, kwh_aliases)
    if value is None:
        value = _value(result, wh_aliases)
        if value is not None:
            value /= 1000.0
    return "-" if value is None else f"{value:.1f}"


def summarize_cspf_result(result: Mapping[str, object]) -> ResultSummary:
    """Map CSPF core aliases into a stable, kWh-based summary card."""
    return ResultSummary(
        title="CSPF",
        fields=(
            ("CSPF", _metric_value(result, "cspf")),
            (
                "CSTL [kWh]",
                _kwh_value(
                    result,
                    kwh_aliases=("annual_cooling_kwh", "cstl_kwh", "cstl"),
                    wh_aliases=("cstl_wh",),
                ),
            ),
            (
                "CSEC [kWh]",
                _kwh_value(
                    result,
                    kwh_aliases=("annual_power_kwh", "csec_kwh", "csec"),
                    wh_aliases=("csec_wh",),
                ),
            ),
        ),
    )


def summarize_hspf_result(result: Mapping[str, object]) -> ResultSummary:
    """Map HSPF core aliases into a stable, kWh-based summary card."""
    return ResultSummary(
        title="HSPF",
        fields=(
            ("HSPF", _metric_value(result, "hspf")),
            (
                "HSTL [kWh]",
                _kwh_value(
                    result,
                    kwh_aliases=("hstl_kwh", "hstl"),
                    wh_aliases=("hstl_wh",),
                ),
            ),
            (
                "HSEC [kWh]",
                _kwh_value(
                    result,
                    kwh_aliases=("hsec_kwh", "hsec"),
                    wh_aliases=("hsec_wh",),
                ),
            ),
        ),
    )
