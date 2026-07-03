"""Projection helpers for the read-only Predict Schema Catalog v2 draft."""

from __future__ import annotations

from pathlib import Path

from core.predictor_schema.catalog_v2 import (
    PredictSchemaCatalogV2,
    PredictSchemaV2Row,
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)

ROLE_PRESENTATION_DEFAULTS = {
    "input": {"width": 90, "bg_color": "#FFFFFF"},
    "auto": {"width": 90, "bg_color": "#F2F2F2"},
    "result": {"width": 100, "bg_color": "#E6F3E6"},
}

WIDTH_OVERRIDES = {
    "idu": 120,
    "evap_index": 100,
    "odu": 120,
    "fin_type": 80,
    "pi": 60,
    "row": 60,
    "compressor": 120,
    "ref_type": 80,
    "exp_type": 80,
    "comp_eer": 80,
    "comp_cc": 80,
    "ref_qty": 80,
    "cspf": 110,
    "hspf2": 110,
}

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
        **ROLE_PRESENTATION_DEFAULTS[row.role],
    }
    if row.column_key in WIDTH_OVERRIDES:
        metadata["width"] = WIDTH_OVERRIDES[row.column_key]
    if row.editor == "dropdown":
        metadata["type"] = "dropdown"
        metadata["mapping"] = row.column_key
    if row.role in {"input", "auto"} and row.model_input_enabled and row.ml_name:
        metadata["ml_feature"] = row.ml_name
    if row.role == "auto":
        metadata["source"] = row.trigger_column
        metadata["mapping_key"] = row.mapping_attribute
    if row.role == "result":
        metadata["readonly"] = True
        if row.value_source == "result" and row.ml_name:
            metadata["ml_target"] = row.ml_name
    return metadata
