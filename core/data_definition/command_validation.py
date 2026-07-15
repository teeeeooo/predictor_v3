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
_MAPPING_FIELDS = (
    "mapping_entity",
    "mapping_attribute",
    "trigger_column",
    "rule_id",
)
_MANUAL_DROPDOWN_RELATIONS = frozenset({
    ("", ""),
    ("idu", ""),
    ("evap_index", ""),
    ("odu", "odu_cond_clear_filter"),
    ("compressor", ""),
})
_RULE_OPTION_RELATIONS = frozenset({
    ("odu_cascade", "Available_Fins", "odu", "odu_cond_filter"),
    ("odu_cascade", "Available_Pis", "odu", "odu_cond_filter"),
    ("odu_cascade", "Available_Rows", "odu", "odu_cond_filter"),
})
_ONE_HOT_SELECTOR_RELATIONS = frozenset({
    ("ref_type", "one_hot_refrigerant", "refrigerant"),
    ("exp_type", "one_hot_expansion_device", "expansion_device"),
})


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
    issues.extend(_validate_role_contract(row))
    return tuple(issues)


def _validate_role_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    validators = {
        "input": _validate_input_contract,
        "auto": _validate_mapping_role_contract,
        "helper": _validate_mapping_role_contract,
        "result": _validate_result_contract,
        "status": _validate_status_contract,
        "one_hot_feature": _validate_one_hot_feature_contract,
        "hidden": _validate_hidden_contract,
    }
    validator = validators.get(row.role)
    if validator is None:
        return (_issue(
            "role_unsupported",
            "role",
            f"Role '{row.role}' is not supported by the current Data Definition contract.",
        ),)
    return validator(row)


def _validate_input_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if row.value_source not in {"manual", "rule_options", "one_hot"}:
        issues.append(_role_source_issue(row, "manual, rule-options, or one-hot"))
        return tuple(issues)
    if row.readonly:
        issues.append(_shape_issue("input_readonly_invalid", "readonly", "Input rows must remain editable."))
    if row.value_source == "manual":
        issues.extend(_validate_manual_input(row))
    elif row.value_source == "rule_options":
        issues.extend(_validate_rule_options_input(row))
    else:
        issues.extend(_validate_one_hot_selector(row))
    return tuple(issues)


def _validate_manual_input(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if row.editor not in {"text", "number", "dropdown"}:
        issues.append(_shape_issue(
            "manual_editor_invalid", "editor", "Manual inputs require a text, number, or dropdown editor."
        ))
    if row.editor in {"text", "number"}:
        issues.extend(_metadata_must_be_blank(row, _MAPPING_FIELDS))
    elif (row.mapping_entity, row.rule_id) not in _MANUAL_DROPDOWN_RELATIONS:
        issues.append(_shape_issue(
            "manual_dropdown_relation_unsupported",
            "mapping_entity",
            "Manual dropdown metadata must match a current supported option source.",
        ))
    issues.extend(_metadata_must_be_blank(row, ("mapping_attribute", "trigger_column", "one_hot_group")))
    return tuple(issues)


def _validate_rule_options_input(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    relation = (
        row.mapping_entity,
        row.mapping_attribute,
        row.trigger_column,
        row.rule_id,
    )
    issues: list[DataDefinitionCommandIssue] = []
    if row.editor != "dropdown" or row.data_type != "string":
        issues.append(_shape_issue(
            "rule_options_shape_invalid",
            "editor",
            "Rule-options inputs require an editable string dropdown.",
        ))
    if relation not in _RULE_OPTION_RELATIONS:
        issues.append(_shape_issue(
            "rule_options_relation_unsupported",
            "mapping_entity",
            "Rule-options metadata must match a current supported option relation.",
        ))
    if row.model_input_enabled or row.ml_name or row.one_hot_group:
        issues.append(_shape_issue(
            "rule_options_model_metadata_invalid",
            "model_input_enabled",
            "Rule-options inputs do not own model-input or one-hot metadata.",
        ))
    return tuple(issues)


def _validate_one_hot_selector(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    relation = (row.mapping_entity, row.rule_id, row.one_hot_group)
    issues: list[DataDefinitionCommandIssue] = []
    if row.editor != "dropdown" or row.data_type != "string":
        issues.append(_shape_issue(
            "one_hot_selector_shape_invalid",
            "editor",
            "One-hot selectors require an editable string dropdown.",
        ))
    if relation not in _ONE_HOT_SELECTOR_RELATIONS:
        issues.append(_shape_issue(
            "one_hot_selector_relation_unsupported",
            "one_hot_group",
            "One-hot selector metadata must match a current supported group relation.",
        ))
    if not row.model_input_enabled or row.ml_name:
        issues.append(_shape_issue(
            "one_hot_selector_model_metadata_invalid",
            "model_input_enabled",
            "One-hot selectors require model input enabled and a blank direct ML name.",
        ))
    issues.extend(_metadata_must_be_blank(row, ("mapping_attribute", "trigger_column")))
    return tuple(issues)


def _validate_mapping_role_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if row.value_source != "mapping_lookup":
        issues.append(_role_source_issue(row, "mapping lookup"))
    if row.editor != "readonly" or not row.readonly:
        issues.append(_shape_issue(
            "mapping_role_readonly_required",
            "editor",
            "Auto/helper mapping rows require a readonly editor and readonly=true.",
        ))
    if row.data_type not in {"string", "number"}:
        issues.append(_shape_issue(
            "mapping_role_data_type_invalid",
            "data_type",
            "Auto/helper mapping rows support current string or number values.",
        ))
    if row.one_hot_group:
        issues.append(_shape_issue(
            "mapping_role_one_hot_invalid",
            "one_hot_group",
            "Auto/helper mapping rows cannot own one-hot metadata.",
        ))
    if row.role == "helper" and (row.visible or row.model_input_enabled or row.ml_name):
        issues.append(_shape_issue(
            "helper_projection_invalid",
            "model_input_enabled",
            "Helper rows must remain hidden and projection-neutral.",
        ))
    return tuple(issues)


def _validate_result_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if row.value_source not in {"result", "formula"}:
        issues.append(_role_source_issue(row, "result or formula"))
    if row.editor != "readonly" or row.data_type != "number" or not row.readonly:
        issues.append(_shape_issue(
            "result_shape_invalid",
            "editor",
            "Result rows require a readonly numeric shape.",
        ))
    issues.extend(_metadata_must_be_blank(
        row,
        ("mapping_entity", "mapping_attribute", "trigger_column", "one_hot_group"),
    ))
    if row.value_source == "result" and (not row.ml_name or row.rule_id):
        issues.append(_shape_issue(
            "result_metadata_invalid",
            "ml_name",
            "ML result rows require an ML name and no formula rule.",
        ))
    if row.value_source == "formula" and (row.rule_id != "rule_result" or row.ml_name):
        issues.append(_shape_issue(
            "formula_metadata_invalid",
            "rule_id",
            "Formula result rows require the current rule_result relation and no ML name.",
        ))
    if row.model_input_enabled:
        issues.append(_shape_issue(
            "result_model_input_invalid", "model_input_enabled", "Result rows are not model inputs."
        ))
    return tuple(issues)


def _validate_status_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if (row.value_source, row.editor, row.data_type, row.readonly) != (
        "status", "status", "status", True,
    ):
        issues.append(_shape_issue(
            "status_shape_invalid",
            "value_source",
            "Status rows require the status source/editor/type and readonly=true.",
        ))
    if row.model_input_enabled or row.ml_name or row.one_hot_group:
        issues.append(_shape_issue(
            "status_model_metadata_invalid",
            "model_input_enabled",
            "Status rows cannot own model-input or one-hot metadata.",
        ))
    issues.extend(_metadata_must_be_blank(row, _MAPPING_FIELDS))
    return tuple(issues)


def _validate_one_hot_feature_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    issues: list[DataDefinitionCommandIssue] = []
    if (
        row.value_source != "one_hot"
        or row.editor != "readonly"
        or row.data_type != "number"
        or not row.readonly
        or row.visible
    ):
        issues.append(_shape_issue(
            "one_hot_feature_shape_invalid",
            "value_source",
            "One-hot feature rows require a hidden readonly numeric one-hot shape.",
        ))
    if not row.model_input_enabled or not row.ml_name or not row.one_hot_group:
        issues.append(_shape_issue(
            "one_hot_feature_metadata_required",
            "one_hot_group",
            "One-hot feature rows require model input, ML name, and one-hot group metadata.",
        ))
    issues.extend(_metadata_must_be_blank(row, _MAPPING_FIELDS))
    return tuple(issues)


def _validate_hidden_contract(
    row: DataDefinitionDraftRow,
) -> tuple[DataDefinitionCommandIssue, ...]:
    if row.editor == "readonly" and row.readonly and not row.visible:
        return ()
    return (_shape_issue(
        "hidden_shape_invalid",
        "editor",
        "Hidden rows must remain non-visible and readonly.",
    ),)


def _metadata_must_be_blank(
    row: DataDefinitionDraftRow,
    fields: tuple[str, ...],
) -> tuple[DataDefinitionCommandIssue, ...]:
    return tuple(
        _shape_issue(
            "source_metadata_not_allowed",
            field_name,
            f"{row.role}/{row.value_source} does not own {field_name} metadata.",
        )
        for field_name in fields
        if str(getattr(row, field_name)).strip()
    )


def _role_source_issue(
    row: DataDefinitionDraftRow,
    expected: str,
) -> DataDefinitionCommandIssue:
    return _shape_issue(
        "role_value_source_unsupported",
        "value_source",
        f"Role '{row.role}' requires {expected}; source '{row.value_source}' is unsupported.",
    )


def _shape_issue(code: str, field_name: str, message: str) -> DataDefinitionCommandIssue:
    return _issue(code, field_name, message)


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
