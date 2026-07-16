"""Qt-free selected-definition summary for the task-oriented workspace."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
    DataDefinitionInventoryRow,
)
from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState


@dataclass(frozen=True)
class DefinitionSummaryFact:
    """One practical selected-definition answer."""

    label: str
    value: str


@dataclass(frozen=True)
class DataDefinitionSummaryProjection:
    """User-facing summary plus preserved lower-priority technical evidence."""

    state: str
    title: str
    internal_key: str
    status: str
    description: str
    facts: tuple[DefinitionSummaryFact, ...]
    technical_details: tuple[tuple[str, str], ...]
    edit_enabled: bool
    edit_reason: str


def project_data_definition_summary(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> DataDefinitionSummaryProjection:
    """Explain the selected row without interpreting policy in a widget."""
    row = next(
        (item for item in inventory.rows if item.identity == inventory.selected_identity),
        None,
    )
    if row is None:
        return _empty_summary(state, inventory)

    values = {cell.field_name: cell.value for cell in row.cells}
    required = _as_bool(values.get("required", "false"))
    editable = row.identity[0] == "schema_row"
    mapping = _mapping_summary(values)
    change_summary = {
        "Changed": "Unsaved change",
        "Blocked": "Change blocked",
        "Read-only": "Read-only",
        "Inactive": "Inactive",
    }.get(row.lifecycle_state, "No pending change")
    return DataDefinitionSummaryProjection(
        state="selected",
        title=row.label,
        internal_key=row.internal_key,
        status=row.lifecycle_state,
        description=_description(row, values),
        facts=(
            DefinitionSummaryFact("Kind", row.kind),
            DefinitionSummaryFact("Data Type", row.data_type),
            DefinitionSummaryFact("Value source", _value_source_summary(row.source_type)),
            DefinitionSummaryFact("Used in Predict", _yes_no(row.predict_visibility == "Used")),
            DefinitionSummaryFact("Model input", _yes_no(row.model_input == "Used")),
            DefinitionSummaryFact("Required", _yes_no(required)),
            DefinitionSummaryFact("Data Mapping", mapping),
            DefinitionSummaryFact("Editing", "Available" if editable else "Read-only"),
            DefinitionSummaryFact("Current change", change_summary),
        ),
        technical_details=inventory.detail.rows,
        edit_enabled=editable,
        edit_reason=(
            "Edit the selected Definition through the supported controlled fields."
            if editable
            else "This Definition is read-only in the controlled editor."
        ),
    )


def _empty_summary(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> DataDefinitionSummaryProjection:
    message = {
        "load_error": state.message,
        "empty": "No definitions are available. Refresh after the source issue is resolved.",
        "no_match": "Clear the search and filters to select a definition.",
    }.get(inventory.view_state, "Select a definition to understand its purpose and usage.")
    return DataDefinitionSummaryProjection(
        state="no_selection",
        title="No definition selected",
        internal_key="",
        status="",
        description=message,
        facts=(),
        technical_details=(),
        edit_enabled=False,
        edit_reason="Select a schema-backed Definition first.",
    )


def _description(row: DataDefinitionInventoryRow, values: dict[str, str]) -> str:
    data_type = values.get("data_type", "").strip().casefold()
    value_type = "numeric" if data_type == "number" else "text"
    if row.kind == "Mapping-backed Input":
        attribute = values.get("mapping_attribute") or "configured attribute"
        entity = _friendly(values.get("mapping_entity")) or "Data Mapping"
        return (
            f"{value_type.title()} input that uses the {attribute} value from "
            f"Data Mapping group {entity}."
        )
    if row.kind == "Mapping Attribute":
        attribute = values.get("mapping_attribute") or row.label
        return (
            f"{value_type.title()} Data Mapping attribute {attribute}; concrete values "
            "are managed in Data Mapping."
        )
    if row.kind == "One-hot Feature":
        return "Generated one-hot model feature derived from its schema selector."
    if row.kind == "Status":
        return "Status information shown by Predict; it is not an active model input."
    if row.kind == "Prediction Result":
        return "Calculated Predict result produced from the current schema and model workflow."
    if row.kind == "Derived":
        return "Derived model feature maintained by the current compatibility contract."
    if row.source_type == "Manual":
        usage = "Predict and the active model" if row.model_input == "Used" else "Predict"
        return f"Manual {value_type} input used by {usage}."
    return f"{row.kind} supplied from {row.source_type}."


def _mapping_summary(values: dict[str, str]) -> str:
    entity = _friendly(values.get("mapping_entity"))
    attribute = values.get("mapping_attribute", "").strip()
    if not entity and not attribute:
        return "None"
    return " / ".join(part for part in (entity, attribute) if part)


def _value_source_summary(source: str) -> str:
    return {
        "Manual": "Manual input",
        "Mapping": "Data Mapping",
        "Derived": "Derived",
        "One-hot": "One-hot projection",
        "Status": "Runtime status",
    }.get(source, source)


def _friendly(value: str | None) -> str:
    return (value or "").replace("_", " ").strip().title()


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _as_bool(value: str) -> bool:
    return value.strip().casefold() == "true"
