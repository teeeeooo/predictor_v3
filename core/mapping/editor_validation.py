"""Validate user-facing mapping editor drafts."""

from __future__ import annotations

from typing import Any

from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorValidationResult,
)
from core.mapping.editor_projection import (
    COMPRESSOR_GROUP,
    EVAP_INDEX_GROUP,
    EXPANSION_GROUP,
    IDU_GROUP,
    ODU_COND_SPECS_GROUP,
    ODU_GROUP,
    REFRIGERANT_GROUP,
)
from core.mapping.entity_model import MappingValidationError

NUMERIC_COLUMNS_BY_GROUP = {
    IDU_GROUP: ("ID Volume",),
    EVAP_INDEX_GROUP: ("Evap Area", "Evap Volume"),
    ODU_GROUP: ("OD Volume",),
    COMPRESSOR_GROUP: ("Comp EER", "Comp cc"),
    ODU_COND_SPECS_GROUP: ("Cond Area", "Cond Volume"),
}


def validate_mapping_editor_draft(
    draft: MappingEditorDraft,
) -> MappingEditorValidationResult:
    """Return user-facing draft validation issues and save enable state."""
    issues: list[MappingValidationError] = []
    for group in draft.groups:
        issues.extend(_validate_group_keys(group))
        issues.extend(_validate_group_numbers(group))
    issues.extend(_validate_required_option_group(draft, REFRIGERANT_GROUP, "Refrigerant"))
    issues.extend(_validate_required_option_group(draft, EXPANSION_GROUP, "Expansion"))
    issues.extend(_validate_odu_cond_specs(draft))
    return MappingEditorValidationResult(issues=tuple(issues))


def _validate_group_keys(group: MappingEditorGroup) -> list[MappingValidationError]:
    if not group.columns:
        return []
    key_column = group.columns[0]
    seen: dict[str, int] = {}
    issues: list[MappingValidationError] = []
    for index, row in enumerate(group.rows, start=1):
        key = _clean(row.value_for(key_column))
        if not key:
            issues.append(
                _issue("blank_key", group, index, key_column, "Required key is blank.")
            )
            continue
        if key in seen:
            issues.append(
                _issue(
                    "duplicate_key",
                    group,
                    index,
                    key_column,
                    f"Duplicate key '{key}'.",
                    row_key=key,
                )
            )
        seen[key] = index
    return issues


def _validate_group_numbers(group: MappingEditorGroup) -> list[MappingValidationError]:
    issues: list[MappingValidationError] = []
    for column in NUMERIC_COLUMNS_BY_GROUP.get(group.group_key, ()):
        for index, row in enumerate(group.rows, start=1):
            value = row.value_for(column)
            if _clean(value) and not _is_number(value):
                issues.append(
                    _issue(
                        "invalid_number",
                        group,
                        index,
                        column,
                        f"{column} must be numeric.",
                        row_key=row.source_key,
                    )
                )
    return issues


def _validate_required_option_group(
    draft: MappingEditorDraft,
    group_key: str,
    label: str,
) -> list[MappingValidationError]:
    group = draft.group(group_key)
    if group is not None and group.rows:
        return []
    return [
        MappingValidationError(
            code="required_section_missing",
            message=f"{label} options are required.",
            entity_key=label,
            attribute_key=label,
        )
    ]


def _validate_odu_cond_specs(draft: MappingEditorDraft) -> list[MappingValidationError]:
    group = draft.group(ODU_COND_SPECS_GROUP)
    if group is None:
        return []
    odu_values = _group_keys(draft.group(ODU_GROUP))
    seen: set[tuple[str, str, str, str]] = set()
    issues: list[MappingValidationError] = []
    for index, row in enumerate(group.rows, start=1):
        if row.unresolved:
            issues.append(
                _issue(
                    "unresolved_cond_specs",
                    group,
                    index,
                    "ODU",
                    "Runtime cond_specs row is not matched by ODU cascade options.",
                    row_key=row.source_key,
                )
            )
            continue
        odu = _clean(row.value_for("ODU"))
        fin = _clean(row.value_for("Fin Type"))
        pi = _clean(row.value_for("Pi"))
        row_value = _clean(row.value_for("Row"))
        if odu and odu not in odu_values:
            issues.append(
                _issue(
                    "referenced_row_missing",
                    group,
                    index,
                    "ODU",
                    f"ODU '{odu}' is not present in the ODU group.",
                    row_key=row.source_key,
                )
            )
        for column, value in (("Fin Type", fin), ("Pi", pi), ("Row", row_value)):
            if not value:
                issues.append(
                    _issue(
                        "required_field_missing",
                        group,
                        index,
                        column,
                        f"{column} is required.",
                        row_key=row.source_key,
                    )
                )
        composite = (odu, fin, pi, row_value)
        if all(composite):
            if composite in seen:
                issues.append(
                    _issue(
                        "duplicate_cond_specs_key",
                        group,
                        index,
                        "ODU",
                        "Duplicate ODU + Fin Type + Pi + Row combination.",
                        row_key=row.source_key,
                    )
                )
            seen.add(composite)
        for column in ("Cond Area", "Cond Volume"):
            value = row.value_for(column)
            if not _clean(value):
                issues.append(
                    _issue(
                        "required_field_missing",
                        group,
                        index,
                        column,
                        f"{column} is required.",
                        row_key=row.source_key,
                    )
                )
            elif not _is_number(value):
                issues.append(
                    _issue(
                        "invalid_number",
                        group,
                        index,
                        column,
                        f"{column} must be numeric.",
                        row_key=row.source_key,
                    )
                )
    return issues


def _group_keys(group: MappingEditorGroup | None) -> set[str]:
    if group is None or not group.columns:
        return set()
    key_column = group.columns[0]
    return {_clean(row.value_for(key_column)) for row in group.rows if _clean(row.value_for(key_column))}


def _issue(
    code: str,
    group: MappingEditorGroup,
    row_number: int,
    field: str,
    message: str,
    *,
    row_key: str = "",
) -> MappingValidationError:
    return MappingValidationError(
        code=code,
        message=message,
        entity_key=group.label,
        attribute_key=field,
        row_key=row_key or str(row_number),
        field=field,
    )


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        float(str(value).strip())
    except (TypeError, ValueError):
        return False
    return True
