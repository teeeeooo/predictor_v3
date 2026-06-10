"""Pure helpers for the Tkinter ISO 16358 calculator sections.

No Tkinter or PyQt imports belong here. Section classes own widgets,
entry reads, resolver calls, calculator calls, and result callbacks.
"""

from __future__ import annotations

from typing import Mapping, Tuple

from apps.calculator.ui.sections.result_formatting import (
    summarize_cspf_result,
    summarize_hspf_result,
)


def build_cspf_input(
    *,
    full_capacity: float,
    full_power: float,
    half_capacity: float,
    half_power: float,
    declared_capacity: float,
) -> Tuple[Mapping[str, Mapping[str, float]], float]:
    measured = {
        "35_full": {
            "capacity": full_capacity,
            "power": full_power,
        },
        "35_half": {
            "capacity": half_capacity,
            "power": half_power,
        },
    }
    return measured, declared_capacity


def build_hspf_input(
    *,
    full_capacity: float,
    full_power: float,
    half_capacity: float,
    half_power: float,
    rated_heating_capacity: float | None = None,
) -> Mapping[str, object]:
    measured = {
        "7_full": {
            "capacity": full_capacity,
            "power": full_power,
        },
        "7_half": {
            "capacity": half_capacity,
            "power": half_power,
        },
    }
    if rated_heating_capacity is not None:
        measured["rated_heating_capacity"] = rated_heating_capacity
    return measured


def format_cspf_result(result: Mapping[str, object]) -> str:
    """Retained text formatter for clipboard/compatibility consumers."""
    return summarize_cspf_result(result).as_text()


def format_hspf_result(result: Mapping[str, object]) -> str:
    """Retained text formatter for clipboard/compatibility consumers."""
    return summarize_hspf_result(result).as_text()
