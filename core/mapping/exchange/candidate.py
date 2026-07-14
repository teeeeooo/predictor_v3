"""Typed full-replacement candidate builder for parsed exchange sections."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from core.mapping.condenser_identity import condenser_requires_pi
from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorRow,
)
from core.mapping.exchange.identity import (
    exchange_row_identity,
    normalize_exchange_identity_values,
)
from core.mapping.exchange.parser import MappingExchangeSection, import_issue
from core.mapping.entity_model import MappingValidationError
from core.mapping.value_policy import coerce_mapping_value, mapping_column_data_type


def build_mapping_exchange_candidate(
    current_draft: MappingEditorDraft,
    sections: dict[str, MappingExchangeSection],
) -> tuple[MappingEditorDraft | None, tuple[MappingValidationError, ...]]:
    """Build typed rows while preserving only matching-row hidden payload."""
    blockers: list[MappingValidationError] = []
    replacement_groups: list[MappingEditorGroup] = []
    for current_group in current_draft.groups:
        section = sections.get(current_group.group_key)
        if section is None:
            blockers.append(
                import_issue(
                    "import_current_group_missing",
                    f"Current projection has no import section for '{current_group.group_key}'.",
                    group=current_group.group_key,
                )
            )
            continue
        existing_rows = _existing_rows_by_identity(current_group, blockers)
        imported_rows: list[MappingEditorRow] = []
        seen: set[tuple[str, ...]] = set()
        indexes = {column: section.header.index(column) for column in current_group.columns}
        for row_number, record in enumerate(section.rows):
            values: dict[str, Any] = {}
            for column in current_group.columns:
                values[column] = _canonicalize_value(
                    current_group,
                    column,
                    record[indexes[column]],
                    blockers,
                    row_number,
                )
            identity = normalize_exchange_identity_values(current_group, values)
            if identity is None:
                blockers.append(
                    import_issue(
                        "import_identity_missing",
                        f"Group '{current_group.label}' row {row_number + 1} is missing its identity value.",
                        group=current_group.group_key,
                        field=current_group.columns[0] if current_group.columns else "identity",
                        row_index=row_number,
                    )
                )
                continue
            if identity in seen:
                code = (
                    "import_duplicate_cond_specs_identity"
                    if current_group.group_key == "odu_cond_specs"
                    else "import_duplicate_key"
                )
                blockers.append(
                    import_issue(
                        code,
                        f"Group '{current_group.label}' contains duplicate identity at row {row_number + 1}.",
                        group=current_group.group_key,
                        field=current_group.columns[0] if current_group.columns else "identity",
                        row_index=row_number,
                    )
                )
            seen.add(identity)
            _validate_required_values(current_group, values, blockers, row_number)
            hidden = _matching_hidden_values(current_group, existing_rows.get(identity))
            hidden.update(values)
            imported_rows.append(
                MappingEditorRow(
                    values=hidden,
                    source_key=" ".join(identity),
                    unresolved=False,
                    notes="",
                )
            )
        replacement_groups.append(replace(current_group, rows=tuple(imported_rows)))
    if blockers:
        return None, tuple(blockers)
    return replace(current_draft, groups=tuple(replacement_groups)), ()


def _existing_rows_by_identity(
    group: MappingEditorGroup,
    blockers: list[MappingValidationError],
) -> dict[tuple[str, ...], MappingEditorRow]:
    rows: dict[tuple[str, ...], MappingEditorRow] = {}
    for row in group.rows:
        identity = exchange_row_identity(group, row)
        if identity is None:
            continue
        if identity in rows:
            blockers.append(
                import_issue(
                    "import_current_identity_ambiguous",
                    f"Current draft group '{group.label}' has duplicate identity {' '.join(identity)}; import is blocked to protect hidden payload.",
                    group=group.group_key,
                )
            )
            continue
        rows[identity] = row
    return rows


def _canonicalize_value(
    group: MappingEditorGroup,
    column: str,
    raw: str,
    blockers: list[MappingValidationError],
    row_number: int,
) -> Any:
    try:
        return coerce_mapping_value(raw, mapping_column_data_type(group, column))
    except ValueError:
        data_type = mapping_column_data_type(group, column)
        blockers.append(
            import_issue(
                f"import_invalid_{data_type}",
                f"Group '{group.label}' row {row_number + 1} column '{column}' has an invalid {data_type} value.",
                group=group.group_key,
                field=column,
                row_index=row_number,
            )
        )
        return raw


def _validate_required_values(
    group: MappingEditorGroup,
    values: dict[str, Any],
    blockers: list[MappingValidationError],
    row_number: int,
) -> None:
    required = list(group.required_columns)
    if group.group_key == "odu_cond_specs":
        required.extend(("ODU", "Fin Type", "Row", "Cond Area", "Cond Volume"))
        if condenser_requires_pi(values.get("Fin Type", "")):
            required.append("Pi")
    for column in dict.fromkeys(required):
        if str(values.get(column, "")).strip():
            continue
        blockers.append(
            import_issue(
                "import_required_value_missing",
                f"Group '{group.label}' row {row_number + 1} is missing required value '{column}'.",
                group=group.group_key,
                field=column,
                row_index=row_number,
            )
        )


def _matching_hidden_values(
    group: MappingEditorGroup,
    existing: MappingEditorRow | None,
) -> dict[str, Any]:
    if existing is None:
        return {}
    return {
        key: value
        for key, value in existing.values.items()
        if key not in group.columns
    }
