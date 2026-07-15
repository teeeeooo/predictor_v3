"""Complete-row validation primitives for controlled definition commands."""

from __future__ import annotations

from core.data_definition.command_contract import mapping_template_for_relation
from core.data_definition.command_types import DataDefinitionCommandIssue
from core.data_definition.draft import DataDefinitionDraftRow
from core.predictor_schema.catalog_v2 import (
    ALLOWED_DATA_TYPES,
    ALLOWED_EDITORS,
    ALLOWED_VALUE_SOURCES,
)

_EDITOR_DATA_TYPES = {
    "text": frozenset({"string"}),
    "number": frozenset({"number"}),
    "dropdown": frozenset({"string", "boolean"}),
    "readonly": frozenset({"string", "number", "boolean"}),
    "status": frozenset({"status"}),
}
_BOOLEAN_FIELDS = frozenset(
    {"visible", "required", "readonly", "model_input_enabled", "active"}
)


def validate_complete_row(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    """Validate a complete candidate row against current controlled contracts."""
    issues: list[DataDefinitionCommandIssue] = []
    if row.data_type not in ALLOWED_DATA_TYPES:
        issues.append(_issue("data_type_invalid", "data_type", f"Unsupported data type: {row.data_type}"))
    if row.editor not in ALLOWED_EDITORS:
        issues.append(_issue("editor_invalid", "editor", f"Unsupported editor: {row.editor}"))
    elif row.data_type not in _EDITOR_DATA_TYPES.get(row.editor, frozenset()):
        issues.append(_issue(
            "editor_data_type_invalid",
            "editor",
            f"Editor '{row.editor}' does not support data type '{row.data_type}'.",
        ))
    if row.value_source not in ALLOWED_VALUE_SOURCES:
        issues.append(_issue(
            "value_source_invalid", "value_source", f"Unsupported value source: {row.value_source}"
        ))
    if row.visible and not row.label.strip():
        issues.append(_issue("label_required", "label", "Visible definitions require a label."))
    if row.value_source == "mapping_lookup":
        if not row.mapping_attribute.strip():
            issues.append(_issue(
                "mapping_attribute_required", "mapping_attribute", "Mapping attribute is required."
            ))
        if mapping_template_for_relation(
            row.mapping_entity,
            row.trigger_column,
            row.rule_id,
        ) is None:
            issues.append(_issue(
                "mapping_template_unsupported",
                "mapping_entity",
                "Mapping lookup relation is not a supported current template.",
            ))
        if row.role not in {"auto", "helper"} or row.editor != "readonly" or not row.readonly:
            issues.append(_issue(
                "mapping_shape_unsupported",
                "value_source",
                "Mapping lookup rows require an auto/helper role and readonly editor contract.",
            ))
    if row.model_input_enabled and not (row.ml_name.strip() or row.one_hot_group.strip()):
        issues.append(_issue(
            "model_input_name_required",
            "model_input_enabled",
            "Model input activation requires an ML name or one-hot group.",
        ))
    return tuple(issues)


def coerce_edit_field(field_name: str, value: object) -> tuple[object, str]:
    """Coerce one field without accepting an invalid boolean spelling."""
    if field_name not in _BOOLEAN_FIELDS:
        return ("" if value is None else str(value).strip()), ""
    if isinstance(value, bool):
        return value, ""
    text = "" if value is None else str(value).strip().casefold()
    if text in {"true", "1", "yes", "y"}:
        return True, ""
    if text in {"false", "0", "no", "n", ""}:
        return False, ""
    return value, f"{field_name} must be true or false."


def _issue(code: str, field_name: str, message: str) -> DataDefinitionCommandIssue:
    return DataDefinitionCommandIssue(code, field_name, message)
