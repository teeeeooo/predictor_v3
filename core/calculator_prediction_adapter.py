"""Adapter-owned PredictedPointsEnvelope helpers.

This module is the upstream counterpart to
``core.calculator_input_adapter``. It validates a
``PredictedPointsEnvelope`` (shape defined in
``docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md``) and
converts it into a ``CalculatorInputEnvelope`` ready for the calculator
layer.

It is intentionally narrow:

- Only the ``ahri_usa_seer2`` profile is supported in this first slice.
- ``source`` is locked to the design vocabulary
  (``manual_candidate / ml_prediction / fixture``).
- ``model_target`` is locked to ``cooling / heating / multi``.
- Units are not converted; capacity must be ``Btu/h`` and power must be
  ``W`` for AHRI SEER2. Other units fail fast.

ML / inverse-search callers should produce a
``PredictedPointsEnvelope`` here, then call
:func:`predicted_points_to_calculator_input_envelope` to obtain the
calculator-input form. The calculator public API stays unchanged.
"""

from typing import Any, Dict, Mapping, Optional

from core.calculator_input_adapter import (
    ALLOWED_SOURCE_VALUES,
    build_calculator_input_envelope,
)
from core.calculator_profiles import resolve_calculator_profile


_REQUIRED_POINTS_BY_PROFILE = {
    "ahri_usa_seer2": ("A_Full", "B_Full", "B_Low", "E_Int", "F_Low"),
}

_EXPECTED_UNITS_BY_PROFILE = {
    "ahri_usa_seer2": {"capacity_unit": "Btu/h", "power_unit": "W"},
}

_ALLOWED_INNER_POINT_KEYS = {"capacity", "power", "capacity_unit", "power_unit"}

ALLOWED_MODEL_TARGETS = ("cooling", "heating", "multi")
ALLOWED_METADATA_KEYS = {"model_version", "candidate_id"}


def _validate_source(source: str) -> str:
    if source not in ALLOWED_SOURCE_VALUES:
        raise ValueError(
            f"Unknown source value: {source!r}. Allowed values: "
            f"{ALLOWED_SOURCE_VALUES}."
        )
    return source


def _validate_model_target(model_target: str) -> str:
    if model_target not in ALLOWED_MODEL_TARGETS:
        raise ValueError(
            f"Unknown model_target value: {model_target!r}. Allowed: "
            f"{ALLOWED_MODEL_TARGETS}."
        )
    return model_target


def _validate_metadata(metadata: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if metadata is None:
        return {"model_version": None, "candidate_id": None}
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping when provided")
    extra = set(metadata.keys()) - ALLOWED_METADATA_KEYS
    if extra:
        raise ValueError(
            f"Unexpected metadata keys: {sorted(extra)}. Allowed: "
            f"{sorted(ALLOWED_METADATA_KEYS)}."
        )
    return {
        "model_version": metadata.get("model_version"),
        "candidate_id": metadata.get("candidate_id"),
    }


def _validate_point(
    profile_id: str, point_key: str, raw_point: Any
) -> Dict[str, Any]:
    if not isinstance(raw_point, Mapping):
        raise TypeError(
            f"Point {point_key!r} must be a mapping with capacity / power / "
            f"capacity_unit / power_unit keys; got {type(raw_point).__name__}."
        )

    extra = set(raw_point.keys()) - _ALLOWED_INNER_POINT_KEYS
    if extra:
        raise ValueError(
            f"Point {point_key!r} mapping has unexpected keys: {sorted(extra)}. "
            f"Allowed inner keys: {sorted(_ALLOWED_INNER_POINT_KEYS)}."
        )

    for required_key in _ALLOWED_INNER_POINT_KEYS:
        if required_key not in raw_point:
            raise KeyError(
                f"Point {point_key!r} is missing required key {required_key!r}."
            )

    capacity = float(raw_point["capacity"])
    power = float(raw_point["power"])
    if capacity <= 0 or power <= 0:
        raise ValueError(
            f"Point {point_key!r} must have positive capacity and power: "
            f"capacity={capacity}, power={power}"
        )

    expected_units = _EXPECTED_UNITS_BY_PROFILE[profile_id]
    if raw_point["capacity_unit"] != expected_units["capacity_unit"]:
        raise ValueError(
            f"Point {point_key!r} capacity_unit must be "
            f"{expected_units['capacity_unit']!r}; got {raw_point['capacity_unit']!r}. "
            f"Unit conversion is intentionally not handled in this slice."
        )
    if raw_point["power_unit"] != expected_units["power_unit"]:
        raise ValueError(
            f"Point {point_key!r} power_unit must be "
            f"{expected_units['power_unit']!r}; got {raw_point['power_unit']!r}. "
            f"Unit conversion is intentionally not handled in this slice."
        )

    return {
        "capacity": capacity,
        "power": power,
        "capacity_unit": raw_point["capacity_unit"],
        "power_unit": raw_point["power_unit"],
    }


def build_predicted_points_envelope(
    profile_id: str,
    points: Mapping[str, Any],
    source: str = "manual_candidate",
    model_target: str = "cooling",
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build and validate a ``PredictedPointsEnvelope`` for a profile.

    Args:
        profile_id: Currently only ``"ahri_usa_seer2"`` is supported. The
            value is used to look up the required point set and expected
            per-point units.
        points: Mapping of point_id → dict with ``capacity`` / ``power`` /
            ``capacity_unit`` / ``power_unit`` keys.
        source: One of ``manual_candidate``, ``ml_prediction``, ``fixture``.
        model_target: One of ``cooling``, ``heating``, ``multi``. Must be
            consistent with the profile mode (``cooling`` profiles reject
            ``heating`` targets and vice versa).
        metadata: Optional ``{model_version, candidate_id}`` mapping.

    Returns:
        Validated PredictedPointsEnvelope dict in the design-doc shape.
    """
    if profile_id not in _REQUIRED_POINTS_BY_PROFILE:
        raise ValueError(
            f"Unsupported predicted points envelope profile: {profile_id!r}"
        )
    if not isinstance(points, Mapping):
        raise TypeError("points must be a mapping of point_id → point dict")

    resolved_source = _validate_source(source)
    resolved_model_target = _validate_model_target(model_target)
    resolved_metadata = _validate_metadata(metadata)

    profile = resolve_calculator_profile(profile_id=profile_id)
    if resolved_model_target != "multi" and resolved_model_target != profile.mode:
        raise ValueError(
            f"model_target {resolved_model_target!r} is inconsistent with "
            f"profile mode {profile.mode!r} for {profile_id!r}."
        )

    required = _REQUIRED_POINTS_BY_PROFILE[profile_id]
    missing = [key for key in required if key not in points]
    if missing:
        raise KeyError(
            f"Missing required points for {profile_id!r}: {missing}"
        )
    extra = [key for key in points.keys() if key not in required]
    if extra:
        raise ValueError(
            f"Unexpected point keys for {profile_id!r}: {sorted(extra)}. "
            f"Allowed: {list(required)}."
        )

    validated_points: Dict[str, Dict[str, Any]] = {}
    for key in required:
        validated_points[key] = _validate_point(profile_id, key, points[key])

    return {
        "source": resolved_source,
        "model_target": resolved_model_target,
        "points": validated_points,
        "metadata": resolved_metadata,
    }


def predicted_points_to_calculator_input_envelope(
    envelope: Mapping[str, Any],
    profile_id: str,
) -> Dict[str, Any]:
    """Convert a validated ``PredictedPointsEnvelope`` into a
    ``CalculatorInputEnvelope`` for the given profile.

    No unit conversion is performed. ``source`` from the predicted-points
    envelope is preserved and placed into ``options["source"]`` of the
    calculator-input envelope. ``metadata`` (``candidate_id`` /
    ``model_version``) is copied through ``options`` as well.
    """
    if not isinstance(envelope, Mapping):
        raise TypeError("envelope must be a mapping")
    if "points" not in envelope or "source" not in envelope:
        raise KeyError(
            "envelope must contain at least 'points' and 'source' keys; "
            "did you forget to run build_predicted_points_envelope first?"
        )

    points = envelope["points"]
    if not isinstance(points, Mapping):
        raise TypeError("envelope['points'] must be a mapping")

    capacity_power_only: Dict[str, Dict[str, float]] = {}
    for key, raw_point in points.items():
        capacity_power_only[key] = {
            "capacity": raw_point["capacity"],
            "power": raw_point["power"],
        }

    metadata = envelope.get("metadata") or {}
    options: Dict[str, Any] = {}
    if metadata.get("candidate_id") is not None:
        options["candidate_id"] = metadata["candidate_id"]
    if metadata.get("model_version") is not None:
        options["model_version"] = metadata["model_version"]
    if envelope.get("model_target") is not None:
        options["model_target"] = envelope["model_target"]

    return build_calculator_input_envelope(
        profile_id=profile_id,
        points=capacity_power_only,
        source=envelope["source"],
        options=options or None,
    )
