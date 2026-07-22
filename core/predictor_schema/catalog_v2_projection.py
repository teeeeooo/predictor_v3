"""Projection helpers for the read-only Predict Schema Catalog v2 draft."""

from __future__ import annotations

from pathlib import Path

from core.predictor_schema.catalog_v2 import (
    PredictSchemaCatalogV2,
    PredictSchemaV2Row,
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)
from core.predictor_schema.presentation import presentation_metadata

CORE_PROJECTED_ROLES = frozenset({"input", "auto", "result"})


def load_projected_columns_v2(path: str | Path | None = None) -> list[dict]:
    """Load, validate, and project v2 draft rows into current COLUMNS-like dicts."""
    catalog = load_predict_schema_catalog_v2(path)
    errors = validate_predict_schema_catalog_v2(catalog)
    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"invalid predict schema v2 draft: {joined}")
    return project_schema_v2_columns(catalog)


def project_schema_v2_columns(catalog: PredictSchemaCatalogV2) -> list[dict]:
    """Project active v2 rows to current core predictor column metadata."""
    rows = [
        row
        for row in catalog.active_rows
        if row.visible and row.role in CORE_PROJECTED_ROLES
    ]
    return [_project_row(row) for row in sorted(rows, key=lambda row: row.display_order)]


def project_schema_v2_rows(rows: tuple[PredictSchemaV2Row, ...]) -> list[dict]:
    """Project an already validated immutable generation projection."""
    visible = (
        row for row in rows
        if row.active and row.visible and row.role in CORE_PROJECTED_ROLES
    )
    return [_project_row(row) for row in sorted(visible, key=lambda row: row.display_order)]


def one_hot_selector_groups(catalog: PredictSchemaCatalogV2) -> dict[str, str]:
    """Return selector column keys mapped to one-hot group names."""
    return {
        row.column_key: row.one_hot_group
        for row in catalog.active_rows
        if row.value_source == "one_hot" and row.role == "input" and row.one_hot_group
    }


def one_hot_feature_groups(catalog: PredictSchemaCatalogV2) -> dict[str, tuple[str, ...]]:
    """Return emitted one-hot feature names grouped by one-hot group."""
    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in catalog.active_rows:
        if row.role != "one_hot_feature" or not row.one_hot_group or not row.ml_name:
            continue
        grouped.setdefault(row.one_hot_group, []).append((row.display_order, row.ml_name))
    return {
        group: tuple(name for _, name in sorted(items))
        for group, items in grouped.items()
    }


def status_schema_rows(catalog: PredictSchemaCatalogV2) -> tuple[PredictSchemaV2Row, ...]:
    """Return status/message rows represented in v2 but excluded from core projection."""
    return tuple(
        sorted(
            (row for row in catalog.active_rows if row.role == "status"),
            key=lambda row: row.display_order,
        )
    )


def _project_row(row: PredictSchemaV2Row) -> dict:
    metadata = {
        "key": row.column_key,
        "header": row.label,
        "group": row.role,
        **presentation_metadata(row.column_key, row.role),
    }
    if row.editor == "dropdown":
        metadata["type"] = "dropdown"
        metadata["mapping"] = _legacy_dropdown_mapping(row)
    if row.role in {"input", "auto"} and row.model_input_enabled and row.ml_name:
        metadata["ml_feature"] = row.ml_name
    if row.role == "auto":
        metadata["source"] = _legacy_autofill_source(row)
        metadata["mapping_key"] = _legacy_mapping_key(row)
    if row.role == "result":
        metadata["readonly"] = True
        if row.value_source == "result" and row.ml_name:
            metadata["ml_target"] = row.ml_name
    return metadata


def _legacy_dropdown_mapping(row: PredictSchemaV2Row) -> str:
    """Return the current adapter compatibility mapping key for dropdown rows.

    This is intentionally not the v2 semantic `mapping_entity`. Current
    `DROPDOWN_TARGET = {k: k}` and dropdown adapters still expect the legacy
    dropdown column key as the mapping identifier.
    """
    return row.column_key


def _legacy_autofill_source(row: PredictSchemaV2Row) -> str:
    """Return the current autofill trigger column compatibility field."""
    return row.trigger_column


def _legacy_mapping_key(row: PredictSchemaV2Row) -> str:
    """Return the current autofill mapping attribute compatibility field."""
    return row.mapping_attribute
