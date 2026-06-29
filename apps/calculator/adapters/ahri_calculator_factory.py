"""Outbound factories for AHRI calculator construction."""

from __future__ import annotations

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)


def create_ahri_seer2_calculator():
    """Create the core AHRI SEER2 calculator through the app outbound boundary."""
    return create_calculator_for_profile(profile_id="ahri_usa_seer2")


def create_ahri_hspf2_calculator():
    """Create the core AHRI HSPF2 calculator through the app outbound boundary."""
    return create_calculator_for_profile(profile_id="ahri_usa_hspf2")
