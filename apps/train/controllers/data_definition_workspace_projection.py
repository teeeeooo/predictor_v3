"""Qt-free task-state projection for the Data Definition workspace."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_impact_projection import DataDefinitionImpactProjection
from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
)
from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState


@dataclass(frozen=True)
class DataDefinitionWorkspaceProjection:
    state: str
    status_kind: str
    headline: str
    headline_detail: str
    surface_title: str
    surface_message: str
    review_label: str
    review_enabled: bool
    show_add_edit: bool
    show_reset: bool
    show_refresh: bool
    save_label: str
    show_saved_handoff: bool

def project_data_definition_workspace(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
    impact: DataDefinitionImpactProjection,
) -> DataDefinitionWorkspaceProjection:
    mode = _workspace_mode(state, inventory)
    if mode == "load_error":
        return _projection(
            mode,
            "error",
            "Definitions could not be loaded",
            "Refresh after the source issue is resolved.",
            "Load error",
            state.message,
            show_refresh=True,
        )
    if mode == "write_error":
        result = dict(state.save_result_rows)
        message = result.get("Message") or state.message
        return _projection(
            mode,
            "error",
            "Schema save failed",
            "The unsaved draft is retained.",
            "Retry the schema save",
            f"{message} Correct the write issue, then retry Save schema.",
            review_label="Review changes",
            review_enabled=True,
            show_reset=True,
            save_label="Retry Save",
        )
    if mode == "blocked":
        blocker_message = _actionable_blocker(state, impact)
        return _projection(
            mode,
            "error",
            "Save blocked",
            _blocked_headline_detail(impact),
            "Save blocked",
            blocker_message,
            review_label="Review blocker",
            review_enabled=True,
            show_reset=True,
        )
    if mode == "dirty":
        count = len(impact.definitions)
        change_text = f"{count} unsaved change" + ("" if count == 1 else "s")
        return _projection(
            mode,
            "warning",
            change_text,
            "Predict restart required" if impact.requires_restart else "Review before saving",
            "Review changes before saving",
            _dirty_message(impact),
            review_label="Review changes",
            review_enabled=True,
            show_reset=True,
        )
    if mode == "saved":
        result = dict(state.save_result_rows)
        latest = result.get("Message", "The latest schema write completed successfully.")
        return _projection(
            mode,
            "good",
            "Schema saved",
            "Restart Predict to use this change",
            "Schema saved",
            f"{latest} Restart Predict before using the saved schema.",
            show_add_edit=True,
            show_refresh=True,
            show_saved_handoff=bool(state.saved_mapping_handoffs),
        )
    if mode == "no_match":
        return _projection(
            mode,
            "neutral",
            "No matching definition",
            "The draft and filters are unchanged.",
            "No definition selected",
            "Clear the search and filters to return to the canonical inventory order.",
            show_add_edit=True,
            show_refresh=True,
        )
    if mode == "no_selection":
        return _projection(
            mode,
            "neutral",
            "No definition selected",
            "Select a definition or add a supported input.",
            "Choose the next step",
            "Select an inventory row to understand it, or use Add to create a supported definition.",
            show_add_edit=True,
            show_refresh=True,
        )
    return _projection(
        "clean",
        "good",
        "No unsaved changes",
        "Definitions are ready to browse.",
        "No unsaved changes.",
        "Find a definition, review its summary, then use Add or Edit when needed.",
        show_add_edit=True,
        show_refresh=True,
    )


def _projection(
    state: str,
    status_kind: str,
    headline: str,
    headline_detail: str,
    surface_title: str,
    surface_message: str,
    *,
    review_label: str = "Review changes",
    review_enabled: bool = False,
    show_add_edit: bool = False,
    show_reset: bool = False,
    show_refresh: bool = False,
    save_label: str = "Save schema",
    show_saved_handoff: bool = False,
) -> DataDefinitionWorkspaceProjection:
    return DataDefinitionWorkspaceProjection(
        state=state,
        status_kind=status_kind,
        headline=headline,
        headline_detail=headline_detail,
        surface_title=surface_title,
        surface_message=surface_message,
        review_label=review_label,
        review_enabled=review_enabled,
        show_add_edit=show_add_edit,
        show_reset=show_reset,
        show_refresh=show_refresh,
        save_label=save_label,
        show_saved_handoff=show_saved_handoff,
    )


def _workspace_mode(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> str:
    if state.status == "error" and not state.draft_rows:
        return "load_error"
    result_status = dict(state.save_result_rows).get("Status", "")
    if state.status == "error" and state.draft_changed and result_status == "error":
        return "write_error"
    if state.draft_changed and (
        not state.can_save_schema or "blocked" in (state.status, result_status)
    ):
        return "blocked"
    if state.draft_changed:
        return "dirty"
    if state.status == "saved":
        return "saved"
    if inventory.view_state == "no_match":
        return "no_match"
    if inventory.selected_identity is None:
        return "no_selection"
    return "clean"


def _dirty_message(impact: DataDefinitionImpactProjection) -> str:
    labels = ", ".join(item.label for item in impact.definitions[:3])
    if len(impact.definitions) > 3:
        labels += f" and {len(impact.definitions) - 3} more"
    runtime = (
        "Predict restart is required."
        if impact.requires_restart
        else "Predict restart is not required."
    )
    mapping = (
        "Mapping metadata changes will take effect after the schema is saved."
        if impact.mapping_impacts
        else "No Data Mapping structure changes."
    )
    compatibility = (
        "Retraining is required."
        if impact.requires_retrain
        else "The current model compatibility projection is unchanged."
    )
    return f"Affected: {labels or 'current draft'}. {runtime} {mapping} {compatibility}"


def _blocked_headline_detail(impact: DataDefinitionImpactProjection) -> str:
    if any(item.code == "ml_compatibility_projection_write_required" for item in impact.blockers):
        return "Model compatibility update required"
    return "Resolve the reported schema issue before saving"


def _actionable_blocker(
    state: DataDefinitionControllerState,
    impact: DataDefinitionImpactProjection,
) -> str:
    blocker = next((item for item in impact.blockers if item.severity == "error"), None)
    if blocker is None:
        return "Review the blocker evidence, correct the draft, or Reset Draft."
    label = _definition_label(state, blocker.related_row_identity)
    if blocker.code == "ml_compatibility_projection_write_required":
        return (
            f"{label} changes the active model compatibility contract. "
            "This project does not currently own a Feature Catalog writer. "
            "Reset Draft or review the blocker evidence."
        )
    prefix = f"{label}: " if label else ""
    return f"{prefix}{blocker.message} Correct the affected field or Reset Draft."


def _definition_label(
    state: DataDefinitionControllerState,
    identity: tuple[str, str] | None,
) -> str:
    if identity is None:
        return "The current draft"
    try:
        index = state.draft_row_identities.index(identity)
    except ValueError:
        return identity[1]
    values = {cell.field_name: cell.value for cell in state.draft_rows[index]}
    return values.get("label") or values.get("ml_name") or identity[1]
