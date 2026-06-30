"""Validation helpers for the ML feature catalog."""

from __future__ import annotations

from collections.abc import Iterable

from core.ml.feature_catalog_projection import UI_VISIBLE_ROLES


ALLOWED_ROLES = frozenset({"input", "auto", "result", "derived", "one_hot", "hidden"})
ALLOWED_ZERO_FILL_POLICIES = frozenset({"disallow", "mode_missing_allowed"})
MODE_MISSING_ALLOWED_FEATURES = frozenset(
    {"Cooling Capa", "Cooling Power", "Heating Capa", "Heating Power"}
)
SEASONAL_OUTPUT_NAMES = frozenset({"CSPF", "HSPF", "CSEC", "HSEC", "HSPF2"})


def validate_feature_catalog(catalog) -> list[str]:
    """Return validation errors for catalog-only rules."""
    errors: list[str] = []
    headers = set(catalog.headers)
    required = set(catalog.required_headers)
    missing_headers = sorted(required - headers)
    unknown_headers = sorted(headers - required)
    if missing_headers:
        errors.append(f"missing required header(s): {', '.join(missing_headers)}")
    if unknown_headers:
        errors.append(f"unknown header(s): {', '.join(unknown_headers)}")

    _validate_unique(
        errors,
        "feature_id",
        (row.feature_id for row in catalog.rows if row.active),
    )
    _validate_unique(
        errors,
        "ml_name",
        (row.ml_name for row in catalog.rows if row.active and row.ml_name),
    )
    _validate_unique(
        errors,
        "ui_key",
        (
            row.ui_key
            for row in catalog.rows
            if row.active and row.role in UI_VISIBLE_ROLES and row.ui_key
        ),
    )

    for row in catalog.rows:
        prefix = f"feature_id={row.feature_id or '<blank>'}"
        if row.role not in ALLOWED_ROLES:
            errors.append(f"{prefix}: invalid role '{row.role}'")
        if row.zero_fill_policy not in ALLOWED_ZERO_FILL_POLICIES:
            errors.append(f"{prefix}: invalid zero_fill_policy '{row.zero_fill_policy}'")
        if (
            row.zero_fill_policy == "mode_missing_allowed"
            and row.ml_name not in MODE_MISSING_ALLOWED_FEATURES
        ):
            errors.append(f"{prefix}: mode_missing_allowed is not allowed for '{row.ml_name}'")
        if row.active and row.role in UI_VISIBLE_ROLES:
            if not row.ui_key:
                errors.append(f"{prefix}: role={row.role} requires ui_key")
            if not row.label:
                errors.append(f"{prefix}: role={row.role} requires label")
        if row.active and row.role == "auto":
            if not row.source:
                errors.append(f"{prefix}: role=auto requires source")
            if not row.mapping_key:
                errors.append(f"{prefix}: role=auto requires mapping_key")
        if row.active and row.role == "one_hot" and not row.one_hot_group:
            errors.append(f"{prefix}: role=one_hot requires one_hot_group")
        if row.active and row.role == "result" and row.ml_name not in catalog.targets():
            errors.append(f"{prefix}: role=result did not enter targets projection")

    _validate_model_input_projection(errors, catalog)
    return errors


def validate_registry_references(catalog, model_registry: dict) -> list[str]:
    """Return errors for MODEL_REGISTRY references missing from the catalog."""
    errors: list[str] = []
    catalog_names = {row.ml_name for row in catalog.active_rows if row.ml_name}
    for model_key, config in model_registry.items():
        for target in config.get("targets", ()):
            if target not in catalog_names:
                errors.append(f"{model_key}: target '{target}' is missing from catalog")
        for target, rules in config.get("target_rules", {}).items():
            if target not in catalog_names:
                errors.append(f"{model_key}: target rule '{target}' is missing from catalog")
            for rule_name in ("exclude", "allowed"):
                for feature_name in rules.get(rule_name, ()):
                    if feature_name not in catalog_names:
                        errors.append(
                            f"{model_key}: {rule_name} feature '{feature_name}' is missing from catalog"
                        )
    return errors


def _validate_unique(errors: list[str], field_name: str, values: Iterable[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    for value in sorted(duplicates):
        errors.append(f"duplicate {field_name}: {value}")


def _validate_model_input_projection(errors: list[str], catalog) -> None:
    for name in catalog.base_features():
        if name in SEASONAL_OUTPUT_NAMES:
            errors.append(f"seasonal output '{name}' cannot enter base feature projection")
