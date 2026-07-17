"""UI-facing before/after rows for Data Definition draft changes."""

from __future__ import annotations

from core.data_definition import DataDefinitionDraftRow, DataDefinitionSavePlan


def draft_change_rows(
    save_plan: DataDefinitionSavePlan,
) -> tuple[tuple[str, ...], ...]:
    if not save_plan.changed_fields:
        return (("info", "", "", "", "No draft changes."),)
    return tuple(
        (
            change.row_identity[0],
            change.row_identity[1],
            change.field_name,
            _change_value(change.field_name, change.before),
            _change_value(change.field_name, change.after),
        )
        for change in save_plan.changed_fields
    )


def _change_value(field_name: str, value: object) -> str:
    if field_name == "__row__" and isinstance(value, DataDefinitionDraftRow):
        return value.column_key or value.ml_name
    if isinstance(value, bool):
        return str(value).lower()
    return "" if value is None else str(value)
