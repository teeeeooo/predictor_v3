"""Outbound gateway for SASO T3 core calculator execution."""

from __future__ import annotations

from collections.abc import Mapping
from core.calculators.capability import Iso16358CspfRequest, execute_standard_calculation


def calculate_saso_t3_cspf(
    measured: Mapping[str, Mapping[str, float]],
    *,
    profile_id: str,
    test_selection: str,
) -> Mapping[str, object]:
    """Apply the SASO test selection override and run the core CSPF calculator."""
    return execute_standard_calculation(
        "iso16358.cspf",
        Iso16358CspfRequest(profile_id, measured, test_selection=test_selection),
    )
