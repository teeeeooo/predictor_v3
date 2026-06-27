"""Adapter-owned unit normalization for calculator inputs.

This module is the single conversion site between ML canonical units
(capacity = W, power = W) and calculator-native units, which vary per
profile. Calculator engines, region configs, UI table models, and ML
callers must not perform unit conversion themselves; they go through
this adapter.

First slice scope:

- Only ``ahri_usa_seer2`` is supported. Other profile ids raise
  ``ValueError`` so callers fail fast instead of silently emitting
  mis-converted values.
- ``ml_prediction`` source: input capacity and power must both be in W.
  Capacity is converted to Btu/h with factor ``3.412141633``; power
  stays in W (AHRI SEER2 native power unit is already W).
- ``manual_candidate`` / ``fixture`` source: input is treated as
  already in profile-native units (AHRI SEER2: capacity = Btu/h,
  power = W); no conversion is performed and any other unit fails
  fast.
- The function returns ``(normalized_points, units_trace)`` where
  ``units_trace`` records ``source_units``, ``target_units``, and
  whether conversion was applied.

EN14825 (kW), ISO16358 / KS C 9306 (W, W) and AHRI HSPF2 conversions
are deferred to follow-up slices and are explicitly out of scope here.
"""

from typing import Any, Dict, Mapping, Tuple


W_TO_BTU_PER_HOUR = 3.412141633


_PROFILE_NATIVE_UNITS = {
    "ahri_usa_seer2": {"capacity": "Btu/h", "power": "W"},
}

_ML_CANONICAL_UNITS = {"capacity": "W", "power": "W"}

ALLOWED_SOURCE_VALUES = ("manual_candidate", "ml_prediction", "fixture")


def supported_profile_ids() -> Tuple[str, ...]:
    """Return the profile ids the unit adapter currently supports."""
    return tuple(_PROFILE_NATIVE_UNITS.keys())


def profile_native_units(profile_id: str) -> Dict[str, str]:
    """Return the ``{capacity, power}`` unit mapping for a supported profile."""
    if profile_id not in _PROFILE_NATIVE_UNITS:
        raise ValueError(
            f"Unsupported calculator_unit_adapter profile: {profile_id!r}. "
            f"Supported profiles: {sorted(_PROFILE_NATIVE_UNITS)}."
        )
    return dict(_PROFILE_NATIVE_UNITS[profile_id])


def _validate_source(source: str) -> None:
    if source not in ALLOWED_SOURCE_VALUES:
        raise ValueError(
            f"Unknown source value: {source!r}. Allowed: "
            f"{ALLOWED_SOURCE_VALUES}."
        )


def expected_source_units(profile_id: str, source: str) -> Dict[str, str]:
    """Return the unit mapping a caller must provide for ``(profile, source)``."""
    if profile_id not in _PROFILE_NATIVE_UNITS:
        raise ValueError(
            f"Unsupported calculator_unit_adapter profile: {profile_id!r}. "
            f"Supported profiles: {sorted(_PROFILE_NATIVE_UNITS)}."
        )
    _validate_source(source)
    if source == "ml_prediction":
        return dict(_ML_CANONICAL_UNITS)
    return dict(_PROFILE_NATIVE_UNITS[profile_id])


def _convert_capacity(point_key: str, value: float, src: str, tgt: str) -> float:
    if src == tgt:
        return value
    if src == "W" and tgt == "Btu/h":
        return value * W_TO_BTU_PER_HOUR
    raise ValueError(
        f"Unsupported capacity unit conversion for point {point_key!r}: "
        f"{src!r} -> {tgt!r}. This slice only supports W -> Btu/h."
    )


def _convert_power(point_key: str, value: float, src: str, tgt: str) -> float:
    if src == tgt:
        return value
    raise ValueError(
        f"Unsupported power unit conversion for point {point_key!r}: "
        f"{src!r} -> {tgt!r}. AHRI SEER2 native power unit is W; this "
        f"slice does not convert power units."
    )


def normalize_points_to_profile_native(
    profile_id: str,
    points: Mapping[str, Mapping[str, Any]],
    source: str,
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Any]]:
    """Convert input points into the calculator-native units of a profile.

    Args:
        profile_id: Calculator profile id. Currently only
            ``"ahri_usa_seer2"`` is supported; other profiles fail fast.
        points: Mapping of ``point_key -> {capacity, power, capacity_unit,
            power_unit}``.
        source: One of ``manual_candidate`` / ``ml_prediction`` /
            ``fixture``. Determines the expected source units:

            - ``ml_prediction`` -> capacity in W, power in W.
            - ``manual_candidate`` / ``fixture`` -> profile-native
              capacity and power (AHRI SEER2: Btu/h, W).

    Returns:
        ``(normalized_points, units_trace)`` where ``normalized_points``
        maps each input key to ``{"capacity": float, "power": float}``
        in profile-native units and ``units_trace`` is::

            {
                "source_units": {"capacity": ..., "power": ...},
                "target_units": {"capacity": ..., "power": ...},
                "conversion_applied": bool,
            }

    Raises:
        ValueError: on unsupported profile, unknown source, mismatched
            unit, non-positive value, or unsupported unit conversion.
        TypeError: if ``points`` is not a mapping or an entry is not a
            mapping.
        KeyError: if a point entry is missing ``capacity_unit`` or
            ``power_unit``.
    """
    expected_units = expected_source_units(profile_id, source)
    target_units = dict(_PROFILE_NATIVE_UNITS[profile_id])

    if not isinstance(points, Mapping):
        raise TypeError("points must be a mapping of point_key -> point dict")

    normalized: Dict[str, Dict[str, float]] = {}
    for point_key, raw_point in points.items():
        if not isinstance(raw_point, Mapping):
            raise TypeError(
                f"Point {point_key!r} must be a mapping with capacity / "
                f"power / capacity_unit / power_unit keys; got "
                f"{type(raw_point).__name__}."
            )
        if "capacity_unit" not in raw_point or "power_unit" not in raw_point:
            raise KeyError(
                f"Point {point_key!r} must specify capacity_unit and "
                f"power_unit explicitly."
            )

        capacity = float(raw_point["capacity"])
        power = float(raw_point["power"])
        if capacity <= 0 or power <= 0:
            raise ValueError(
                f"Point {point_key!r} must have positive capacity and "
                f"power: capacity={capacity}, power={power}"
            )

        cap_unit = raw_point["capacity_unit"]
        pow_unit = raw_point["power_unit"]
        if cap_unit != expected_units["capacity"]:
            raise ValueError(
                f"Point {point_key!r} capacity_unit must be "
                f"{expected_units['capacity']!r} when source is "
                f"{source!r}; got {cap_unit!r}."
            )
        if pow_unit != expected_units["power"]:
            raise ValueError(
                f"Point {point_key!r} power_unit must be "
                f"{expected_units['power']!r} when source is "
                f"{source!r}; got {pow_unit!r}."
            )

        normalized[point_key] = {
            "capacity": _convert_capacity(
                point_key, capacity, cap_unit, target_units["capacity"]
            ),
            "power": _convert_power(
                point_key, power, pow_unit, target_units["power"]
            ),
        }

    units_trace: Dict[str, Any] = {
        "source_units": dict(expected_units),
        "target_units": dict(target_units),
        "conversion_applied": expected_units != target_units,
    }
    return normalized, units_trace
