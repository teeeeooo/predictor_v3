"""Compatibility shim for the application-owned calculator profile resolver."""

from __future__ import annotations

from apps.calculator.application.profile_resolver import (
    METRIC_SECTIONS_BY_REGION,
    MODE_HONG_KONG,
    MODE_ISO_ISEER_2POINT,
    MODE_SASO_T3,
    REGION_BY_LABEL,
    calculation_mode_labels,
    region_labels,
    resolve_calculation_mode_profile_id,
    resolve_profile_id,
    resolve_two_point_profile_id,
    supported_metrics_for,
    two_point_profile_labels,
)

__all__ = [
    "METRIC_SECTIONS_BY_REGION",
    "MODE_HONG_KONG",
    "MODE_ISO_ISEER_2POINT",
    "MODE_SASO_T3",
    "REGION_BY_LABEL",
    "calculation_mode_labels",
    "region_labels",
    "resolve_calculation_mode_profile_id",
    "resolve_profile_id",
    "resolve_two_point_profile_id",
    "supported_metrics_for",
    "two_point_profile_labels",
]
