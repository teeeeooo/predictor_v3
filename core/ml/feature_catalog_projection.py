"""Projection helpers for the ML feature catalog."""

from __future__ import annotations

from collections.abc import Iterable


BASE_FEATURE_ROLES = frozenset({"input", "auto", "one_hot", "result", "hidden"})
RAW_TRAINING_HEADER_ROLES = frozenset({"input", "auto", "one_hot", "result"})
UI_VISIBLE_ROLES = frozenset({"input", "auto", "result"})
PREDICTOR_GROUP_ORDER = ("input", "auto", "result")

# Legacy deterministic export order for result-like names inside BASE_FEATURES.
# TARGETS order is owned by result row order in the catalog.
BASE_FEATURE_RESULT_EXPORT_ORDER = (
    "Ref Qty",
    "Cooling Power",
    "Heating Power",
    "Cooling Hz",
    "Heating Hz",
)


def active_rows(rows):
    """Return active catalog rows in catalog order."""
    return tuple(row for row in rows if row.active)


def base_features(rows) -> list[str]:
    """Return the legacy deterministic BASE_FEATURES export."""
    active = active_rows(rows)
    base_rows = [
        row.ml_name
        for row in active
        if row.role in BASE_FEATURE_ROLES - {"result"} and row.ml_name
    ]
    results_by_name = {row.ml_name: row for row in active if row.role == "result"}
    ordered_results = [
        name for name in BASE_FEATURE_RESULT_EXPORT_ORDER if name in results_by_name
    ]
    remaining_results = [
        row.ml_name
        for row in active
        if row.role == "result" and row.ml_name not in BASE_FEATURE_RESULT_EXPORT_ORDER
    ]
    return base_rows + ordered_results + remaining_results


def derived_features(rows) -> list[str]:
    """Return active derived feature names."""
    return [row.ml_name for row in active_rows(rows) if row.role == "derived" and row.ml_name]


def targets(rows) -> list[str]:
    """Return active target names in catalog result-row order."""
    return [row.ml_name for row in active_rows(rows) if row.role == "result" and row.ml_name]


def predictor_rows(rows) -> tuple:
    """Return active rows that can project to predictor schema columns."""
    rows_by_group = {
        role: [
            row
            for row in active_rows(rows)
            if row.role == role and row.ui_key
        ]
        for role in PREDICTOR_GROUP_ORDER
    }
    return tuple(
        row
        for role in PREDICTOR_GROUP_ORDER
        for row in rows_by_group[role]
    )


def predictor_columns_projection(
    rows,
    role_defaults: dict[str, dict],
    width_overrides: dict[str, int] | None = None,
) -> list[dict]:
    """Project catalog rows into predictor column metadata."""
    width_overrides = width_overrides or {}
    columns: list[dict] = []
    for row in predictor_rows(rows):
        metadata = {
            "key": row.ui_key,
            "header": row.label,
            "group": row.role,
            **role_defaults[row.role],
        }
        if row.ui_key in width_overrides:
            metadata["width"] = width_overrides[row.ui_key]
        if row.role in {"input", "auto"}:
            metadata["ml_feature"] = row.ml_name
        if row.role == "auto":
            metadata["source"] = row.source
            metadata["mapping_key"] = row.mapping_key
        if row.role == "result":
            metadata["readonly"] = True
            metadata["ml_target"] = row.ml_name
        columns.append(metadata)
    return columns


def one_hot_groups(rows) -> dict[str, tuple[str, ...]]:
    """Return one-hot group names mapped to ordered ML feature names."""
    grouped: dict[str, list[str]] = {}
    for row in active_rows(rows):
        if row.role != "one_hot":
            continue
        grouped.setdefault(row.one_hot_group, []).append(row.ml_name)
    return {group: tuple(names) for group, names in grouped.items()}


def one_hot_group(rows, group_name: str) -> tuple[str, ...]:
    """Return a named one-hot group with a clear missing-group error."""
    groups = one_hot_groups(rows)
    try:
        return groups[group_name]
    except KeyError as exc:
        raise ValueError(
            f"missing one-hot group '{group_name}' in feature catalog"
        ) from exc


def zero_fill_policies(rows) -> dict[str, str]:
    """Return active ML names mapped to zero-fill policy."""
    return {
        row.ml_name: row.zero_fill_policy
        for row in active_rows(rows)
        if row.ml_name
    }


def training_headers(rows) -> list[str]:
    """Return raw training data headers expected to match catalog ml_name values."""
    return [
        row.ml_name
        for row in active_rows(rows)
        if row.role in RAW_TRAINING_HEADER_ROLES and row.ml_name
    ]


def validate_training_headers(headers: Iterable[str], catalog) -> list[str]:
    """Return training header contract errors without supporting aliases."""
    observed = {str(header).strip() for header in headers if str(header).strip()}
    all_catalog_names = {row.ml_name for row in catalog.active_rows if row.ml_name}
    required = set(catalog.training_headers())

    errors: list[str] = []
    unknown = sorted(observed - all_catalog_names)
    missing = sorted(required - observed)
    if unknown:
        errors.append(f"unknown training header(s): {', '.join(unknown)}")
    if missing:
        errors.append(f"missing required training header(s): {', '.join(missing)}")
    return errors
