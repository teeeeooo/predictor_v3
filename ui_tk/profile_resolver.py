"""UI-facing region/metric → calculator profile_id resolver.

This module is pure Python: it imports neither Tkinter nor PyQt. It is
the single place where the Tkinter shell maps the (region label,
metric section) pair the user sees to the internal ``profile_id``
that ``core.calculator_dispatcher.create_calculator_for_profile``
expects. ``profile_id`` / ``calculator_id`` / ``config_path`` are
never exposed in the UI; they live only here.
"""

from __future__ import annotations

from typing import Mapping, Tuple


REGION_BY_LABEL: Mapping[str, str] = {
    "Hong Kong": "hong_kong",
}

METRIC_SECTIONS_BY_REGION: Mapping[str, Tuple[str, ...]] = {
    "hong_kong": ("CSPF", "HSPF"),
}

_PROFILE_BY_REGION_METRIC: Mapping[Tuple[str, str], str] = {
    ("hong_kong", "cspf"): "hong_kong_cspf",
    ("hong_kong", "hspf"): "hong_kong_hspf",
}


def region_labels() -> Tuple[str, ...]:
    """Return the user-visible region labels supported by the MVP."""
    return tuple(REGION_BY_LABEL.keys())


def _normalize_region(region: str) -> str:
    """Accept either the display label (``"Hong Kong"``) or the internal
    key (``"hong_kong"``) and return the internal key."""
    return REGION_BY_LABEL.get(region, region).casefold()


def supported_metrics_for(region: str) -> Tuple[str, ...]:
    """Return the metric section names a region supports."""
    region_key = _normalize_region(region)
    return METRIC_SECTIONS_BY_REGION.get(region_key, ())


def resolve_profile_id(region: str, metric: str) -> str:
    """Map ``(region, metric_section)`` to an internal ``profile_id``.

    Raises ``ValueError`` for combinations the MVP does not wire.
    """
    region_key = _normalize_region(region)
    metric_key = metric.casefold()
    profile = _PROFILE_BY_REGION_METRIC.get((region_key, metric_key))
    if profile is None:
        raise ValueError(
            f"Unsupported (region, metric) pair for MVP: "
            f"({region!r}, {metric!r})"
        )
    return profile
