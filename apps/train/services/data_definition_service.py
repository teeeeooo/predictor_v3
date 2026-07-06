"""Data Definition service for Train/Admin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionReport,
    DataDefinitionSavePlan,
    build_data_definition_draft,
    build_data_definition_report,
    build_data_definition_save_plan,
    field_editability,
)
from core.data_definition.draft import replace_draft_row

BOOLEAN_DRAFT_FIELDS = frozenset(
    {"visible", "required", "readonly", "model_input_enabled", "active"}
)


@dataclass(frozen=True)
class DataDefinitionDraftEditResult:
    """Service result for one in-memory draft edit."""

    draft: DataDefinitionDraft
    accepted: bool
    message: str


class DataDefinitionService:
    """Load and mutate in-memory Data Definition state."""

    def __init__(self, *, schema_path: str | Path | None = None) -> None:
        self._schema_path = Path(schema_path) if schema_path is not None else None

    def load_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Return the current read-only Data Definition report."""
        return build_data_definition_report(
            schema_path=self._schema_path,
            training_data_path=training_data_path,
        )

    def refresh_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Reload the report for refresh actions."""
        return self.load_report(training_data_path=training_data_path)

    def load_draft(self) -> DataDefinitionDraft:
        """Return an in-memory editable draft loaded from the schema owner path."""
        return build_data_definition_draft(schema_path=self._schema_path)

    def refresh_draft(self) -> DataDefinitionDraft:
        """Discard in-memory edits and reload the draft."""
        return self.load_draft()

    def edit_draft_cell(
        self,
        draft: DataDefinitionDraft,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> DataDefinitionDraftEditResult:
        """Return a new draft after applying one UI-originated cell edit."""
        row = next((item for item in draft.rows if item.identity == row_identity), None)
        if row is None:
            return DataDefinitionDraftEditResult(
                draft,
                False,
                f"Draft row not found: {row_identity}",
            )
        editability = field_editability(row, field_name)
        if not editability.editable:
            return DataDefinitionDraftEditResult(draft, False, editability.reason)
        coerced, error = _coerce_draft_value(field_name, value)
        if error:
            return DataDefinitionDraftEditResult(draft, False, error)
        updated = replace_draft_row(draft, row_identity, **{field_name: coerced})
        return DataDefinitionDraftEditResult(updated, True, "Draft cell updated.")

    def preview_save_plan(
        self,
        draft: DataDefinitionDraft,
        *,
        current_report: DataDefinitionReport | None = None,
    ) -> DataDefinitionSavePlan:
        """Build the current draft save-plan preview without writing files."""
        report = current_report or self.load_report()
        return build_data_definition_save_plan(draft, current_report=report)


def _coerce_draft_value(field_name: str, value: object) -> tuple[object, str]:
    if field_name not in BOOLEAN_DRAFT_FIELDS:
        return "" if value is None else str(value), ""
    if isinstance(value, bool):
        return value, ""
    text = "" if value is None else str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True, ""
    if text in {"false", "0", "no", "n", ""}:
        return False, ""
    return value, f"{field_name} must be true or false."
