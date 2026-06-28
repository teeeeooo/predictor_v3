"""Application-owned calculator UI label to profile_id resolver.

This module is pure Python and UI-runtime-neutral. Tk sections may import it,
but it must not import Tkinter, PySide, widget classes, or UI panels.
"""

from __future__ import annotations

from typing import Mapping, Tuple


MODE_HONG_KONG = "Hong Kong"
MODE_ISO_ISEER_2POINT = "ISO / ISEER 2-point"
MODE_SASO_T3 = "SASO T3"


REGION_BY_LABEL: Mapping[str, str] = {
    MODE_HONG_KONG: "hong_kong",
}

METRIC_SECTIONS_BY_REGION: Mapping[str, Tuple[str, ...]] = {
    "hong_kong": ("CSPF", "HSPF"),
}

_PROFILE_BY_REGION_METRIC: Mapping[Tuple[str, str], str] = {
    ("hong_kong", "cspf"): "hong_kong_cspf",
    ("hong_kong", "hspf"): "hong_kong_hspf",
}

_TWO_POINT_PROFILE_BY_LABEL: Mapping[str, str] = {
    "ISO 16358-1": "iso_t1_default_2point_cspf",
    "India ISEER": "india_iseer_cspf",
}

_PROFILE_BY_CALCULATION_MODE_LABEL: Mapping[str, str] = {
    MODE_SASO_T3: "saso_t3_cspf",
}


def calculation_mode_labels() -> Tuple[str, ...]:
    """Return user-visible ISO profile selector labels."""
    return (MODE_ISO_ISEER_2POINT, MODE_HONG_KONG, MODE_SASO_T3)


def region_labels() -> Tuple[str, ...]:
    """Return the user-visible region labels supported by the MVP."""
    return tuple(REGION_BY_LABEL.keys())


def two_point_profile_labels() -> Tuple[str, ...]:
    """Return user-visible profile labels for ISO/ISEER 2-point mode."""
    return tuple(_TWO_POINT_PROFILE_BY_LABEL.keys())


def _normalize_region(region: str) -> str:
    """Accept either the display label or internal key and return the key."""
    return REGION_BY_LABEL.get(region, region).casefold()


def supported_metrics_for(region: str) -> Tuple[str, ...]:
    """Return the metric section names a region supports."""
    region_key = _normalize_region(region)
    return METRIC_SECTIONS_BY_REGION.get(region_key, ())


def resolve_profile_id(region: str, metric: str) -> str:
    """Map ``(region, metric_section)`` to an internal ``profile_id``."""
    region_key = _normalize_region(region)
    metric_key = metric.casefold()
    profile = _PROFILE_BY_REGION_METRIC.get((region_key, metric_key))
    if profile is None:
        raise ValueError(
            f"Unsupported (region, metric) pair for MVP: "
            f"({region!r}, {metric!r})"
        )
    return profile


def resolve_two_point_profile_id(profile_label: str) -> str:
    """Map a 2-point result profile label to an internal ``profile_id``."""
    profile = _TWO_POINT_PROFILE_BY_LABEL.get(profile_label)
    if profile is None:
        raise ValueError(f"Unsupported ISO/ISEER 2-point profile: {profile_label!r}")
    return profile


def resolve_calculation_mode_profile_id(mode_label: str) -> str:
    """Map a single-profile calculation mode label to an internal profile_id."""
    profile = _PROFILE_BY_CALCULATION_MODE_LABEL.get(mode_label)
    if profile is None:
        raise ValueError(f"Unsupported single-profile calculation mode: {mode_label!r}")
    return profile
