"""Project Data Definition rows to current Feature Catalog compatibility rows."""

from __future__ import annotations

from pathlib import Path

from core.data_definition.derived_policy import load_current_derived_feature_policy
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.model import (
    DataDefinitionRow,
    DerivedFeatureDefinition,
    MappingRequirement,
    ProjectedFeatureRow,
)
from core.ml.catalog_fingerprint import current_catalog_fingerprint
from core.ml.feature_catalog import FeatureCatalog, FeatureCatalogRow
from core.predictor_schema.catalog_v2 import (
    PredictSchemaCatalogV2,
    PredictSchemaV2Row,
    load_predict_schema_catalog_v2,
)

MODE_MISSING_ALLOWED = frozenset(
    {"Cooling Capa", "Heating Capa", "Cooling Power", "Heating Power"}
)

# Current compatibility order for `config/ml/features.csv` parity only.
FEATURE_PROJECTION_COMPATIBILITY_ORDER = ("input", "auto", "one_hot", "result", "derived")


def load_data_definition_rows(
    path: str | Path | None = None,
) -> tuple[DataDefinitionRow, ...]:
    """Load active schema rows as Data Definition rows."""
    catalog = load_predict_schema_catalog_v2(path)
    return data_definition_rows_from_catalog(catalog)


def data_definition_rows_from_catalog(
    catalog: PredictSchemaCatalogV2,
) -> tuple[DataDefinitionRow, ...]:
    """Return active schema rows normalized for Data Definition validation."""
    return tuple(_definition_row(row) for row in catalog.active_rows)


def project_feature_catalog_from_schema(
    schema_path: str | Path | None = None,
    derived_policy: tuple[DerivedFeatureDefinition, ...] | None = None,
) -> tuple[ProjectedFeatureRow, ...]:
    """Project schema rows plus derived policy to Feature Catalog-compatible rows."""
    catalog = load_predict_schema_catalog_v2(schema_path)
    return project_feature_catalog_from_catalog(catalog, derived_policy)


def project_feature_catalog_from_catalog(
    catalog: PredictSchemaCatalogV2,
    derived_policy: tuple[DerivedFeatureDefinition, ...] | None = None,
) -> tuple[ProjectedFeatureRow, ...]:
    """Project an already loaded schema catalog to compatibility rows."""
    policy = derived_policy or load_current_derived_feature_policy()
    rows: list[ProjectedFeatureRow] = []
    active_rows = tuple(row for row in catalog.active_rows if row.active)
    for role in FEATURE_PROJECTION_COMPATIBILITY_ORDER:
        rows.extend(_project_rows_for_role(role, active_rows, policy))
    return _renumber(rows)


def project_feature_catalog_from_draft(
    draft: DataDefinitionDraft,
    derived_policy: tuple[DerivedFeatureDefinition, ...] | None = None,
) -> tuple[ProjectedFeatureRow, ...]:
    """Project schema-backed draft rows to ML compatibility rows."""
    schema_rows = tuple(
        _schema_row_from_draft(row, line_number=index)
        for index, row in enumerate(
            (item for item in draft.rows if item.source_kind == "schema_row"),
            start=2,
        )
    )
    return project_feature_catalog_from_catalog(
        PredictSchemaCatalogV2(rows=schema_rows),
        derived_policy,
    )


def projected_feature_catalog_fingerprint(
    rows: tuple[ProjectedFeatureRow, ...],
) -> str:
    """Return the existing ML compatibility fingerprint for projected rows."""
    # ProjectedFeatureRow intentionally exposes every field consumed by the
    # catalog fingerprint owner, so the compatibility DTO needs no second copy.
    return current_catalog_fingerprint(FeatureCatalog(rows=rows))  # type: ignore[arg-type]


def projected_row_from_catalog_row(row: FeatureCatalogRow) -> ProjectedFeatureRow:
    """Normalize current Feature Catalog rows for parity comparison."""
    return ProjectedFeatureRow(
        order=row.order,
        ml_name=row.ml_name,
        role=row.role,
        ui_key=row.ui_key,
        label=row.label,
        source=row.source,
        mapping_key=row.mapping_key,
        one_hot_group=row.one_hot_group,
        zero_fill_policy=row.zero_fill_policy,
        active=row.active,
    )


def extract_mapping_requirements(
    rows: tuple[DataDefinitionRow, ...],
) -> tuple[MappingRequirement, ...]:
    """Return active mapping lookup requirements without reading mapping values."""
    requirements = [
        MappingRequirement(
            column_key=row.column_key,
            ml_name=row.ml_name,
            mapping_entity=row.mapping_entity,
            mapping_attribute=row.mapping_attribute,
            trigger_column=row.trigger_column,
            rule_id=row.rule_id,
        )
        for row in rows
        if row.value_source == "mapping_lookup"
        and row.mapping_entity
        and row.mapping_attribute
        and row.trigger_column
    ]
    return tuple(requirements)


def _project_rows_for_role(
    role: str,
    rows: tuple[PredictSchemaV2Row, ...],
    policy: tuple[DerivedFeatureDefinition, ...],
) -> list[ProjectedFeatureRow]:
    if role == "input":
        return _project_input_rows(rows)
    if role == "auto":
        return _project_auto_rows(rows)
    if role == "one_hot":
        return _project_one_hot_rows(rows)
    if role == "result":
        return _project_result_rows(rows)
    if role == "derived":
        return _project_derived_rows(policy)
    raise ValueError(f"unsupported feature projection role '{role}'")


def _project_input_rows(rows: tuple[PredictSchemaV2Row, ...]) -> list[ProjectedFeatureRow]:
    return [
        _feature_row(row, role="input", ui_key=row.column_key, label=row.label)
        for row in rows
        if row.role == "input"
        and row.model_input_enabled
        and row.value_source == "manual"
        and row.ml_name
    ]


def _project_auto_rows(rows: tuple[PredictSchemaV2Row, ...]) -> list[ProjectedFeatureRow]:
    return [
        _feature_row(
            row,
            role="auto",
            ui_key=row.column_key,
            label=row.label,
            source=row.trigger_column,
            mapping_key=row.mapping_attribute,
        )
        for row in rows
        if row.role == "auto" and row.model_input_enabled and row.ml_name
    ]


def _project_one_hot_rows(rows: tuple[PredictSchemaV2Row, ...]) -> list[ProjectedFeatureRow]:
    return [
        _feature_row(
            row,
            role="one_hot",
            label=row.label,
            one_hot_group=row.one_hot_group,
        )
        for row in rows
        if row.role == "one_hot_feature" and row.model_input_enabled and row.ml_name
    ]


def _project_result_rows(rows: tuple[PredictSchemaV2Row, ...]) -> list[ProjectedFeatureRow]:
    return [
        _feature_row(row, role="result", ui_key=row.column_key, label=row.label)
        for row in rows
        if row.role == "result" and row.value_source == "result" and row.ml_name
    ]


def _project_derived_rows(
    policy: tuple[DerivedFeatureDefinition, ...],
) -> list[ProjectedFeatureRow]:
    return [
        ProjectedFeatureRow(
            order=0,
            ml_name=row.ml_name,
            role="derived",
            zero_fill_policy=row.zero_fill_policy,
            active=row.active,
        )
        for row in policy
    ]


def _feature_row(
    row: PredictSchemaV2Row,
    *,
    role: str,
    ui_key: str = "",
    label: str = "",
    source: str = "",
    mapping_key: str = "",
    one_hot_group: str = "",
) -> ProjectedFeatureRow:
    return ProjectedFeatureRow(
        order=0,
        ml_name=row.ml_name,
        role=role,
        ui_key=ui_key,
        label=label,
        source=source,
        mapping_key=mapping_key,
        one_hot_group=one_hot_group,
        zero_fill_policy=_zero_fill_policy(row.ml_name),
        active=row.active,
    )


def _renumber(rows: list[ProjectedFeatureRow]) -> tuple[ProjectedFeatureRow, ...]:
    return tuple(
        ProjectedFeatureRow(
            order=index * 10,
            ml_name=row.ml_name,
            role=row.role,
            ui_key=row.ui_key,
            label=row.label,
            source=row.source,
            mapping_key=row.mapping_key,
            one_hot_group=row.one_hot_group,
            zero_fill_policy=row.zero_fill_policy,
            active=row.active,
        )
        for index, row in enumerate(rows, start=1)
    )


def _zero_fill_policy(ml_name: str) -> str:
    return "mode_missing_allowed" if ml_name in MODE_MISSING_ALLOWED else "disallow"


def _definition_row(row: PredictSchemaV2Row) -> DataDefinitionRow:
    return DataDefinitionRow(
        column_key=row.column_key,
        label=row.label,
        role=row.role,
        value_source=row.value_source,
        mapping_entity=row.mapping_entity,
        mapping_attribute=row.mapping_attribute,
        trigger_column=row.trigger_column,
        rule_id=row.rule_id,
        model_input_enabled=row.model_input_enabled,
        ml_name=row.ml_name,
        one_hot_group=row.one_hot_group,
        display_order=row.display_order,
    )


def _schema_row_from_draft(
    row: DataDefinitionDraftRow,
    *,
    line_number: int,
) -> PredictSchemaV2Row:
    return PredictSchemaV2Row(
        line_number=line_number,
        display_order=row.display_order,
        column_key=row.column_key,
        label=row.label,
        role=row.role,
        editor=row.editor,
        data_type=row.data_type,
        visible=row.visible,
        required=row.required,
        readonly=row.readonly,
        value_source=row.value_source,
        mapping_entity=row.mapping_entity,
        mapping_attribute=row.mapping_attribute,
        trigger_column=row.trigger_column,
        rule_id=row.rule_id,
        model_input_enabled=row.model_input_enabled,
        ml_name=row.ml_name,
        one_hot_group=row.one_hot_group,
        active=row.active,
        notes=row.notes,
    )
