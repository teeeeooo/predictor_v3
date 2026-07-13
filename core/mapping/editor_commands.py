"""Pure edit commands for mapping editor drafts."""

from __future__ import annotations

from dataclasses import replace

from core.mapping.condenser_identity import canonical_condenser_pi
from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorRow,
)


def set_draft_cell(
    draft: MappingEditorDraft,
    group_key: str,
    row_index: int,
    column: str,
    value: object,
) -> MappingEditorDraft:
    """Return a draft with one cell value changed."""
    group = _group_or_none(draft, group_key)
    if group is None or column not in group.columns or not 0 <= row_index < len(group.rows):
        return draft
    row = group.rows[row_index]
    values = dict(row.values)
    _set_cell_value(group, values, column, value)
    source_key = str(value).strip() if column == group.columns[0] else row.source_key
    return _replace_group(
        draft,
        replace(
            group,
            rows=_replace_row(
                group.rows,
                row_index,
                replace(row, values=values, source_key=source_key),
            ),
        ),
    )


def add_draft_row(draft: MappingEditorDraft, group_key: str) -> MappingEditorDraft:
    """Return a draft with one blank row appended to a group."""
    group = _group_or_none(draft, group_key)
    if group is None:
        return draft
    blank = MappingEditorRow(values={column: "" for column in group.columns})
    return _replace_group(draft, replace(group, rows=(*group.rows, blank)))


def duplicate_draft_row(
    draft: MappingEditorDraft,
    group_key: str,
    row_index: int,
) -> MappingEditorDraft:
    """Return a draft with one row duplicated after the source row."""
    group = _group_or_none(draft, group_key)
    if group is None or not 0 <= row_index < len(group.rows):
        return draft
    row = group.rows[row_index]
    duplicate = replace(row, values=dict(row.values))
    rows = (*group.rows[: row_index + 1], duplicate, *group.rows[row_index + 1 :])
    return _replace_group(draft, replace(group, rows=rows))


def delete_draft_row(
    draft: MappingEditorDraft,
    group_key: str,
    row_index: int,
) -> MappingEditorDraft:
    """Return a draft with one row removed from a group."""
    group = _group_or_none(draft, group_key)
    if group is None or not 0 <= row_index < len(group.rows):
        return draft
    rows = (*group.rows[:row_index], *group.rows[row_index + 1 :])
    return _replace_group(draft, replace(group, rows=rows))


def _group_or_none(draft: MappingEditorDraft, group_key: str) -> MappingEditorGroup | None:
    return draft.group(group_key)


def _set_cell_value(
    group: MappingEditorGroup,
    values: dict[str, object],
    column: str,
    value: object,
) -> None:
    if group.group_key != "odu_cond_specs":
        values[column] = value
        return
    if column == "Fin Type":
        values[column] = value
        values["Pi"] = canonical_condenser_pi(value, values.get("Pi"))
        return
    if column == "Pi":
        values[column] = canonical_condenser_pi(values.get("Fin Type"), value)
        return
    values[column] = value


def _replace_group(
    draft: MappingEditorDraft,
    replacement: MappingEditorGroup,
) -> MappingEditorDraft:
    return replace(
        draft,
        groups=tuple(
            replacement if group.group_key == replacement.group_key else group
            for group in draft.groups
        ),
    )


def _replace_row(
    rows: tuple[MappingEditorRow, ...],
    row_index: int,
    replacement: MappingEditorRow,
) -> tuple[MappingEditorRow, ...]:
    return (*rows[:row_index], replacement, *rows[row_index + 1 :])
