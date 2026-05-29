"""Section-local result snapshots for Tkinter result detail surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultSnapshot:
    """Raw calculation result retained by a section after formatting rows."""

    label: str
    points: list[dict]
    summary: dict
    bin_details: list[dict] | None
    status: str | None = None


def point_snapshot(
    label: str, measured: Mapping[str, Mapping[str, float]], key: str
) -> dict:
    point = measured.get(key, {})
    capacity = point.get("capacity")
    power = point.get("power")
    eer = None
    if capacity is not None and power is not None and power > 0:
        eer = capacity / power
    return {
        "point": label,
        "capacity": capacity,
        "power": power,
        "eer": eer,
    }


def cspf_summary(result: Mapping[str, object]) -> dict:
    return {
        "cspf": _first_number(result, ("cspf",)),
        "cstl_kwh": _first_number(
            result, ("annual_cooling_kwh", "cstl_kwh", "cstl")
        ),
        "csec_kwh": _first_number(
            result, ("annual_power_kwh", "csec_kwh", "csec")
        ),
    }


def bin_details_snapshot(result: Mapping[str, object]) -> list[dict] | None:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return None
    return [dict(item) for item in raw if isinstance(item, Mapping)]


def _first_number(result: Mapping[str, object], aliases: tuple[str, ...]) -> float | None:
    for key in aliases:
        value = result.get(key)
        if value is not None:
            return float(value)
    return None
