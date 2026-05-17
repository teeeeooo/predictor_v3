"""Adapter-owned CalculatorInputEnvelope helpers.

This module converts an upstream candidate/prediction input (whether from a
manual candidate-like dict or a future ``PredictedPointsEnvelope``) into a
``CalculatorInputEnvelope`` dict that can be passed straight into the
``ahri_usa_seer2`` calculator without changing the calculator's public API.

It is intentionally narrow:

- Only the ``ahri_usa_seer2`` profile is supported in this first slice.
- The point set is fixed to ``A_Full, B_Full, B_Low, E_Int, F_Low``.
- Units are not converted; the adapter explicitly requires capacity in Btu/h
  and power in W and fails fast otherwise.

ML / inverse-search callers should layer on top of this envelope instead of
fanning out new calculator entry points.
"""

from typing import Any, Dict, Mapping, Optional

from core.calculator_profiles import resolve_calculator_profile


_REQUIRED_POINTS_BY_PROFILE = {
    "ahri_usa_seer2": ("A_Full", "B_Full", "B_Low", "E_Int", "F_Low"),
}

_EXPECTED_UNITS_BY_PROFILE = {
    "ahri_usa_seer2": {"capacity": "Btu/h", "power": "W"},
}


def _coerce_capacity_power(point_key: str, raw_point: Any) -> tuple:
    """Accept either (cap, pow) sequence or {capacity, power} dict and return floats."""
    if isinstance(raw_point, Mapping):
        if "capacity" not in raw_point or "power" not in raw_point:
            raise KeyError(
                f"Point {point_key!r} dict must contain 'capacity' and 'power' keys."
            )
        capacity = raw_point["capacity"]
        power = raw_point["power"]
    elif isinstance(raw_point, (list, tuple)) and len(raw_point) == 2:
        capacity, power = raw_point
    else:
        raise TypeError(
            f"Point {point_key!r} must be a (capacity, power) sequence or a "
            f"{{'capacity', 'power'}} mapping; got {type(raw_point).__name__}."
        )

    capacity = float(capacity)
    power = float(power)
    if capacity <= 0 or power <= 0:
        raise ValueError(
            f"Point {point_key!r} must have positive capacity and power: "
            f"capacity={capacity}, power={power}"
        )
    return capacity, power


def _validate_units(profile_id: str, units: Optional[Mapping[str, str]]) -> Dict[str, str]:
    """Reject mismatched units to keep the first slice unit-safe."""
    expected = _EXPECTED_UNITS_BY_PROFILE[profile_id]
    if units is None:
        return dict(expected)
    if not isinstance(units, Mapping):
        raise TypeError("units must be a mapping of {capacity, power} → unit string")
    for key, expected_unit in expected.items():
        provided = units.get(key, expected_unit)
        if provided != expected_unit:
            raise ValueError(
                f"Unsupported unit for {key!r}: expected {expected_unit!r}, got {provided!r}. "
                f"Unit conversion is intentionally not handled in this slice."
            )
    return dict(expected)


def build_calculator_input_envelope(
    profile_id: str,
    points: Mapping[str, Any],
    units: Optional[Mapping[str, str]] = None,
    source: str = "manual",
) -> Dict[str, Any]:
    """Build a CalculatorInputEnvelope for a supported calculator profile.

    Args:
        profile_id: Currently only ``"ahri_usa_seer2"`` is supported.
        points: Mapping that contains the required AHRI SEER2 test points
            (``A_Full``, ``B_Full``, ``B_Low``, ``E_Int``, ``F_Low``). Each value
            may be either ``(capacity, power)`` or
            ``{"capacity": ..., "power": ...}``.
        units: Optional ``{"capacity": "Btu/h", "power": "W"}`` mapping. The
            adapter does NOT convert units; mismatches fail fast.
        source: Free-form provenance tag (``"manual"``, ``"predicted"``, ...).

    Returns:
        Dict with ``calculator_profile_id``, ``calculator_id``, ``test_points``,
        ``units``, and ``source`` keys. ``test_points`` is a dict of
        ``{point_key: (capacity, power)}`` and can be passed straight to
        ``AHRICalculator.calculate_seer2(test_points=...)``.
    """
    if profile_id not in _REQUIRED_POINTS_BY_PROFILE:
        raise ValueError(
            f"Unsupported calculator input envelope profile: {profile_id!r}"
        )
    if not isinstance(points, Mapping):
        raise TypeError("points must be a mapping of point_key → (capacity, power)")

    required = _REQUIRED_POINTS_BY_PROFILE[profile_id]
    missing = [key for key in required if key not in points]
    if missing:
        raise KeyError(f"Missing required points for {profile_id!r}: {missing}")

    test_points: Dict[str, tuple] = {}
    for key in required:
        test_points[key] = _coerce_capacity_power(key, points[key])

    resolved_units = _validate_units(profile_id, units)
    profile = resolve_calculator_profile(profile_id=profile_id)

    return {
        "calculator_profile_id": profile.profile_id,
        "calculator_id": profile.calculator_id,
        "test_points": test_points,
        "units": resolved_units,
        "source": source,
    }
