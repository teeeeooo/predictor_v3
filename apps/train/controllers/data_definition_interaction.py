"""Qt-free action presentation for the Data Definition workspace."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
)
from apps.train.controllers.data_definition_state_builder import (
    DataDefinitionControllerState,
)


@dataclass(frozen=True)
class DefinitionActionPresentation:
    """Enabled state and user-facing explanation for one workspace action."""

    enabled: bool
    reason: str


@dataclass(frozen=True)
class DataDefinitionInteractionPresentation:
    """Action states derived only from existing controller projections."""

    save: DefinitionActionPresentation
    edit: DefinitionActionPresentation
    review_blockers: DefinitionActionPresentation
    status_text: str


def project_data_definition_interaction(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> DataDefinitionInteractionPresentation:
    """Explain action availability without reimplementing validation rules."""
    save_result = dict(state.save_result_rows).get("Status", "")
    if inventory.save_enabled:
        save_reason = (
            "Retry Save schema; the unsaved draft was retained."
            if save_result == "error"
            else "Save schema changes."
        )
    elif not state.draft_changed:
        save_reason = "No unsaved schema changes."
    else:
        save_reason = "Resolve the compatibility blockers before saving the schema."

    identity = inventory.selected_identity
    edit_enabled = bool(identity and identity[0] == "schema_row")
    if edit_enabled:
        edit_reason = "Edit the selected Definition."
    elif identity is None:
        edit_reason = "Select a schema-backed Definition first."
    else:
        edit_reason = "This Definition is read-only in the controlled editor."

    has_blockers = bool(
        state.draft_changed
        and any(item.severity == "error" for item in state.blocker_items)
    )
    return DataDefinitionInteractionPresentation(
        save=DefinitionActionPresentation(inventory.save_enabled, save_reason),
        edit=DefinitionActionPresentation(edit_enabled, edit_reason),
        review_blockers=DefinitionActionPresentation(
            has_blockers,
            "Review the blocker summary for the selected Definition."
            if has_blockers
            else "No compatibility blockers to review.",
        ),
        status_text=_status_text(state, inventory),
    )


def _status_text(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> str:
    if inventory.status_key == "load_error":
        return f"Load error: {state.message}"
    if inventory.status_key == "saved":
        return "Saved: Schema saved. Restart required before Predict uses the change."
    if inventory.status_key == "write_error":
        return "Write error: Unsaved changes retained. Retry Save schema."
    if inventory.status_key == "blocked":
        return "Blocked: Review compatibility blockers before Save schema."
    if inventory.status_key == "dirty":
        return "Unsaved changes: Review impact, then Save schema."
    return "Clean: Definitions loaded."
