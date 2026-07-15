"""Focused detail projection for the Data Definition inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState

if TYPE_CHECKING:
    from apps.train.controllers.data_definition_presentation import DataDefinitionInventoryRow


@dataclass(frozen=True)
class DataDefinitionDetailState:
    """Focused detail projection for one selected inventory row."""

    state: str
    title: str
    message: str
    identity: tuple[str, str] | None
    rows: tuple[tuple[str, str], ...]


def project_detail(
    state: DataDefinitionControllerState,
    row: DataDefinitionInventoryRow | None,
    view_state: str,
) -> DataDefinitionDetailState:
    """Project selected draft-cell metadata into user-facing detail rows."""
    if row is None:
        message = {
            "load_error": state.message,
            "empty": "No definitions are available.",
            "no_match": "Clear or change the search and filters to select a definition.",
        }.get(view_state, "Select a definition to see its details.")
        return DataDefinitionDetailState("no_selection", "No definition selected", message, None, ())
    values = {cell.field_name: cell.value for cell in row.cells}
    changed_fields = tuple(cell.field_name for cell in row.cells if cell.changed)
    editable = any(cell.editable for cell in row.cells)
    edit_reason = (
        "Schema-backed fields can be edited in Advanced Diagnostics > Raw Draft."
        if editable
        else next((cell.reason for cell in row.cells if cell.reason), "Direct editing is blocked.")
    )
    rows = (
        ("Label", row.label),
        ("Internal key", row.internal_key),
        ("Definition category", row.category),
        ("Source kind", values.get("source_kind", row.identity[0])),
        ("Role / type / editor", _joined(values, "role", "data_type", "editor")),
        ("Visible / required / readonly", _flags(values)),
        ("Value source", row.source_type),
        ("Mapping entity", values.get("mapping_entity") or "—"),
        ("Mapping attribute", values.get("mapping_attribute") or "—"),
        ("Trigger", values.get("trigger_column") or "—"),
        ("Model input", row.model_input),
        ("ML name", row.ml_name or "—"),
        ("ML compatibility", _ml_compatibility(state, row, changed_fields)),
        ("Active", values.get("active") or "false"),
        ("Direct edit", "Allowed" if editable else "Blocked"),
        ("Direct edit policy", edit_reason),
        ("Changed fields", ", ".join(changed_fields) or "None"),
        ("Restart / retrain impact", state.impact_summary),
        ("Save blockers", _blocker_summary(state, changed_fields)),
        ("Display order", values.get("display_order") or "—"),
        ("Rule ID", values.get("rule_id") or "—"),
        ("One-hot group", values.get("one_hot_group") or "—"),
        ("Raw notes", values.get("notes") or "—"),
    )
    return DataDefinitionDetailState("selected", row.label, row.internal_key, row.identity, rows)


def _blocker_summary(
    state: DataDefinitionControllerState,
    changed_fields: tuple[str, ...],
) -> str:
    errors = tuple(row[3] for row in state.save_blocker_rows if row and row[0] == "error")
    if not errors:
        return "None"
    if changed_fields:
        return " | ".join(errors)
    return "Current draft is blocked by changes to another definition."


def _ml_compatibility(
    state: DataDefinitionControllerState,
    row: DataDefinitionInventoryRow,
    changed_fields: tuple[str, ...],
) -> str:
    blocker_codes = {item[1] for item in state.save_blocker_rows if len(item) > 1}
    if changed_fields and "ml_compatibility_projection_write_required" in blocker_codes:
        return "Blocked — compatibility projection writer required"
    if "feature_projection_parity_mismatch" in blocker_codes:
        return "Mismatch"
    if row.model_input == "Enabled" or row.ml_name:
        return "Compatible with current projection"
    return "Not a model input"


def _joined(values: dict[str, str], *fields: str) -> str:
    return " / ".join(values.get(field) or "—" for field in fields)


def _flags(values: dict[str, str]) -> str:
    return " / ".join(
        f"{field}: {values.get(field) or 'false'}"
        for field in ("visible", "required", "readonly")
    )
