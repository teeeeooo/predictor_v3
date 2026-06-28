"""Application adapter for core calculator construction."""

from __future__ import annotations

from typing import Optional

from core.calculators.dispatcher import create_calculator_for_profile as _create_core_calculator


def create_calculator_for_profile(
    profile_id: Optional[str] = None,
    standard: Optional[str] = None,
    region: Optional[str] = None,
    metric: Optional[str] = None,
    mode: Optional[str] = None,
):
    """Delegate calculator construction to the core dispatcher."""
    return _create_core_calculator(
        profile_id=profile_id,
        standard=standard,
        region=region,
        metric=metric,
        mode=mode,
    )
