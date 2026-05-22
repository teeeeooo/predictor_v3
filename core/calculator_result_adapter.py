"""Adapter-owned calculator result envelope helpers.

This module wraps existing calculator return dictionaries without changing
calculator public APIs. It is intentionally narrow until ML / inverse-search
callers prove the next envelope slice.
"""

from typing import Any, Dict, Mapping, Optional, Sequence

from core.calculator_profiles import resolve_calculator_profile


_RESULT_CONTRACTS = {
    "ahri_usa_seer2": {
        "metric": "SEER2",
        "value_key": "SEER2",
        "units": "Btu/Wh",
        "diagnostic_keys": ("bin_details",),
    },
}


def wrap_calculator_result_envelope(
    profile_id: str,
    raw_result: Mapping[str, Any],
    warnings: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Wrap a calculator result dict in a normalized result envelope.

    The first implementation slice supports only ``ahri_usa_seer2`` and keeps
    the original calculator result available under ``raw_result``.
    """
    if not isinstance(raw_result, Mapping):
        raise TypeError("raw_result must be a mapping")

    contract = _RESULT_CONTRACTS.get(profile_id)
    if contract is None:
        raise ValueError(f"Unsupported calculator result envelope profile: {profile_id!r}")

    profile = resolve_calculator_profile(profile_id=profile_id)
    value_key = contract["value_key"]
    if value_key not in raw_result:
        raise KeyError(f"raw_result is missing required metric key: {value_key!r}")

    diagnostics = {
        key: raw_result[key]
        for key in contract["diagnostic_keys"]
        if key in raw_result
    }

    return {
        "calculator_profile_id": profile.profile_id,
        "calculator_id": profile.calculator_id,
        "metric": contract["metric"],
        "value": raw_result[value_key],
        "units": contract["units"],
        "raw_result": raw_result,
        "diagnostics": diagnostics,
        "warnings": list(warnings or []),
    }
