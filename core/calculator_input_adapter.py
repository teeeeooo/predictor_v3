"""Adapter-owned CalculatorInputEnvelope helpers.

This module converts an upstream candidate/prediction input (whether from a
manual candidate-like dict or a future ``PredictedPointsEnvelope``) into a
``CalculatorInputEnvelope`` dict that matches
``docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md``.

It is intentionally narrow:

- Only the ``ahri_usa_seer2`` profile is supported in this first slice.
- The point set is fixed to ``A_Full, B_Full, B_Low, E_Int, F_Low``.
- Units are not converted; the adapter explicitly requires capacity in Btu/h
  and power in W and fails fast otherwise.
- Extra point keys, extra inner keys, or unknown ``source`` values fail fast
  so the envelope contract stays strict until ML callers stabilize.

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

_ALLOWED_INNER_POINT_KEYS = {"capacity", "power"}

ALLOWED_SOURCE_VALUES = ("manual_candidate", "ml_prediction", "fixture")


def _coerce_capacity_power(point_key: str, raw_point: Any) -> Dict[str, float]:
    """Return ``{"capacity": float, "power": float}`` after strict validation.

    Accept either a ``(capacity, power)`` sequence or a
    ``{"capacity": ..., "power": ...}`` mapping. Extra inner keys, missing
    keys, malformed sequences, and non-positive values all fail fast.
    """
    if isinstance(raw_point, Mapping):
        extra = set(raw_point.keys()) - _ALLOWED_INNER_POINT_KEYS
        if extra:
            raise ValueError(
                f"Point {point_key!r} mapping has unexpected keys: {sorted(extra)}. "
                f"Allowed inner keys: {sorted(_ALLOWED_INNER_POINT_KEYS)}."
            )
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
    return {"capacity": capacity, "power": power}


def _validate_units(profile_id: str, units: Optional[Mapping[str, str]]) -> Dict[str, str]:
    """Reject mismatched or unexpected units to keep the first slice unit-safe."""
    expected = _EXPECTED_UNITS_BY_PROFILE[profile_id]
    if units is None:
        return dict(expected)
    if not isinstance(units, Mapping):
        raise TypeError("units must be a mapping of {capacity, power} → unit string")
    extra = set(units.keys()) - set(expected.keys())
    if extra:
        raise ValueError(
            f"Unexpected unit keys for {profile_id!r}: {sorted(extra)}. "
            f"Allowed: {sorted(expected.keys())}."
        )
    for key, expected_unit in expected.items():
        provided = units.get(key, expected_unit)
        if provided != expected_unit:
            raise ValueError(
                f"Unsupported unit for {key!r}: expected {expected_unit!r}, got {provided!r}. "
                f"Unit conversion is intentionally not handled in this slice."
            )
    return dict(expected)


def _validate_source(source: str) -> str:
    if source not in ALLOWED_SOURCE_VALUES:
        raise ValueError(
            f"Unknown source value: {source!r}. Allowed values: "
            f"{ALLOWED_SOURCE_VALUES}."
        )
    return source


_UNITS_TRACE_REQUIRED_KEYS = {"source_units", "target_units", "conversion_applied"}


def _validate_units_trace(
    profile_id: str, units_trace: Optional[Mapping[str, Any]]
) -> Dict[str, Any]:
    """Validate a caller-provided ``units_trace`` or build a no-op default.

    The default trace records ``source_units == target_units ==
    profile-native`` and ``conversion_applied=False``, which matches
    the contract for manual / fixture sources that already arrive in
    profile-native units. ``target_units`` must always equal the
    profile-native unit mapping; otherwise ``measured_inputs`` would
    not be calculator-ready.
    """
    expected_target = _EXPECTED_UNITS_BY_PROFILE[profile_id]
    if units_trace is None:
        return {
            "source_units": dict(expected_target),
            "target_units": dict(expected_target),
            "conversion_applied": False,
        }
    if not isinstance(units_trace, Mapping):
        raise TypeError("units_trace must be a mapping when provided")
    missing = _UNITS_TRACE_REQUIRED_KEYS - set(units_trace.keys())
    if missing:
        raise KeyError(
            f"units_trace missing required keys: {sorted(missing)}"
        )
    extra = set(units_trace.keys()) - _UNITS_TRACE_REQUIRED_KEYS
    if extra:
        raise ValueError(
            f"units_trace has unexpected keys: {sorted(extra)}. "
            f"Allowed: {sorted(_UNITS_TRACE_REQUIRED_KEYS)}."
        )
    source_units = units_trace["source_units"]
    target_units = units_trace["target_units"]
    if not isinstance(source_units, Mapping) or not isinstance(target_units, Mapping):
        raise TypeError(
            "units_trace['source_units'] and units_trace['target_units'] "
            "must be mappings"
        )
    if dict(target_units) != expected_target:
        raise ValueError(
            f"units_trace target_units {dict(target_units)!r} must match "
            f"profile-native units {expected_target!r}"
        )
    if not isinstance(units_trace["conversion_applied"], bool):
        raise TypeError("units_trace['conversion_applied'] must be a bool")
    return {
        "source_units": dict(source_units),
        "target_units": dict(target_units),
        "conversion_applied": units_trace["conversion_applied"],
    }


def build_calculator_input_envelope(
    profile_id: str,
    points: Mapping[str, Any],
    units: Optional[Mapping[str, str]] = None,
    source: str = "manual_candidate",
    options: Optional[Mapping[str, Any]] = None,
    units_trace: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a CalculatorInputEnvelope for a supported calculator profile.

    Args:
        profile_id: Currently only ``"ahri_usa_seer2"`` is supported.
        points: Mapping that contains exactly the required AHRI SEER2 test
            points (``A_Full``, ``B_Full``, ``B_Low``, ``E_Int``, ``F_Low``).
            Each value may be either ``(capacity, power)`` or
            ``{"capacity": ..., "power": ...}``. Extra point keys fail fast.
        units: Optional ``{"capacity": "Btu/h", "power": "W"}`` mapping. The
            adapter does NOT convert units; mismatches or extra unit keys
            fail fast.
        source: One of ``manual_candidate``, ``ml_prediction``, ``fixture``.
        options: Optional caller-owned options dict copied into the envelope.
        units_trace: Optional ``{source_units, target_units,
            conversion_applied}`` mapping describing where the input
            values came from. When omitted a no-op trace is recorded
            (``source_units == target_units == profile-native``,
            ``conversion_applied=False``). ``target_units`` must match
            profile-native or validation fails.

    Returns:
        Dict matching the design doc shape:

        ``{
            calculator_profile_id, standard, region, mode, metric,
            measured_inputs, options
        }``

        ``measured_inputs`` is a dict of
        ``{point_key: {"capacity": float, "power": float}}``. Pass it through
        :func:`measured_inputs_as_test_points` to obtain the tuple form
        accepted by ``AHRICalculator.calculate_seer2``.
    """
    if profile_id not in _REQUIRED_POINTS_BY_PROFILE:
        raise ValueError(
            f"Unsupported calculator input envelope profile: {profile_id!r}"
        )
    if not isinstance(points, Mapping):
        raise TypeError("points must be a mapping of point_key → (capacity, power)")
    if options is not None and not isinstance(options, Mapping):
        raise TypeError("options must be a mapping when provided")

    required = _REQUIRED_POINTS_BY_PROFILE[profile_id]
    missing = [key for key in required if key not in points]
    if missing:
        raise KeyError(f"Missing required points for {profile_id!r}: {missing}")
    extra = [key for key in points.keys() if key not in required]
    if extra:
        raise ValueError(
            f"Unexpected point keys for {profile_id!r}: {sorted(extra)}. "
            f"Allowed points: {list(required)}."
        )

    measured_inputs: Dict[str, Dict[str, float]] = {}
    for key in required:
        measured_inputs[key] = _coerce_capacity_power(key, points[key])

    resolved_units = _validate_units(profile_id, units)
    resolved_source = _validate_source(source)
    resolved_units_trace = _validate_units_trace(profile_id, units_trace)
    profile = resolve_calculator_profile(profile_id=profile_id)

    envelope_options: Dict[str, Any] = {
        "units": resolved_units,
        "source": resolved_source,
        "units_trace": resolved_units_trace,
    }
    if options:
        for key, value in options.items():
            if key in envelope_options:
                raise ValueError(
                    f"options must not redefine reserved key {key!r}; pass via "
                    f"the dedicated parameter instead."
                )
            envelope_options[key] = value

    return {
        "calculator_profile_id": profile.profile_id,
        "standard": profile.standard,
        "region": profile.region,
        "mode": profile.mode,
        "metric": profile.metric,
        "measured_inputs": measured_inputs,
        "options": envelope_options,
    }


def measured_inputs_as_test_points(envelope: Mapping[str, Any]) -> Dict[str, tuple]:
    """Convert ``envelope["measured_inputs"]`` into the calculator tuple form.

    Calculators like ``AHRICalculator.calculate_seer2`` still accept
    ``{point_key: (capacity, power)}``. This helper performs that one
    flattening step without changing the calculator public API.
    """
    measured = envelope.get("measured_inputs")
    if not isinstance(measured, Mapping):
        raise KeyError("envelope is missing measured_inputs mapping")
    return {key: (value["capacity"], value["power"]) for key, value in measured.items()}
