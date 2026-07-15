"""Pure inventory and detail presentation for Train Data Definition."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_detail_projection import (
    DataDefinitionDetailState,
    project_detail,
)
from apps.train.controllers.data_definition_state_builder import (
    DataDefinitionControllerState,
    DataDefinitionDraftCellState,
)


@dataclass(frozen=True)
class DataDefinitionInventoryRow:
    """One stable, user-facing definition inventory row."""

    identity: tuple[str, str]
    label: str
    internal_key: str
    category: str
    data_type: str
    source_type: str
    relationship: str
    predict_visibility: str
    model_input: str
    lifecycle_state: str
    ml_name: str
    cells: tuple[DataDefinitionDraftCellState, ...]


@dataclass(frozen=True)
class DataDefinitionInventoryProjection:
    """Filtered inventory, selection, detail, and status presentation state."""

    rows: tuple[DataDefinitionInventoryRow, ...]
    selected_identity: tuple[str, str] | None
    detail: DataDefinitionDetailState
    categories: tuple[str, ...]
    source_types: tuple[str, ...]
    lifecycle_states: tuple[str, ...]
    resolved_category: str
    resolved_source_type: str
    resolved_lifecycle_state: str
    view_state: str
    view_message: str
    status_key: str
    status_label: str
    save_enabled: bool


def project_data_definition_inventory(
    state: DataDefinitionControllerState,
    *,
    search: str = "",
    category: str = "",
    source_type: str = "",
    lifecycle_state: str = "",
    selected_identity: tuple[str, str] | None = None,
) -> DataDefinitionInventoryProjection:
    """Project controller state without mutating draft or application state."""
    canonical_rows = tuple(
        _inventory_row(identity, cells, state)
        for identity, cells in zip(
            state.draft_row_identities,
            state.draft_rows,
            strict=True,
        )
    )
    categories = tuple(sorted({row.category for row in canonical_rows}))
    source_types = tuple(sorted({row.source_type for row in canonical_rows}))
    lifecycle_states = tuple(sorted({row.lifecycle_state for row in canonical_rows}))
    resolved_category = _resolved_filter(category, categories)
    resolved_source_type = _resolved_filter(source_type, source_types)
    resolved_lifecycle_state = _resolved_filter(lifecycle_state, lifecycle_states)
    normalized_search = search.strip().casefold()
    visible_rows = tuple(
        row
        for row in canonical_rows
        if _matches(
            row,
            normalized_search,
            resolved_category,
            resolved_source_type,
            resolved_lifecycle_state,
        )
    )
    visible_identities = {row.identity for row in visible_rows}
    resolved_identity = (
        selected_identity
        if selected_identity in visible_identities
        else (visible_rows[0].identity if visible_rows else None)
    )
    selected = next(
        (row for row in visible_rows if row.identity == resolved_identity),
        None,
    )
    view_state, view_message = _view_state(state, canonical_rows, visible_rows)
    status_key, status_label = _application_status(state)
    return DataDefinitionInventoryProjection(
        rows=visible_rows,
        selected_identity=resolved_identity,
        detail=project_detail(state, selected, view_state),
        categories=categories,
        source_types=source_types,
        lifecycle_states=lifecycle_states,
        resolved_category=resolved_category,
        resolved_source_type=resolved_source_type,
        resolved_lifecycle_state=resolved_lifecycle_state,
        view_state=view_state,
        view_message=view_message,
        status_key=status_key,
        status_label=status_label,
        save_enabled=state.save_action_enabled,
    )


def _inventory_row(
    identity: tuple[str, str],
    cells: tuple[DataDefinitionDraftCellState, ...],
    state: DataDefinitionControllerState,
) -> DataDefinitionInventoryRow:
    values = {cell.field_name: cell.value for cell in cells}
    changed_fields = tuple(cell.field_name for cell in cells if cell.changed)
    direct_editable = any(cell.editable for cell in cells)
    active = _as_bool(values.get("active", "false"))
    lifecycle_state = (
        "Inactive"
        if not active
        else "Blocked"
        if not direct_editable or (changed_fields and state.draft_changed and not state.save_action_enabled)
        else "Active"
    )
    source_kind = values.get("source_kind", identity[0])
    internal_key = values.get("column_key") or values.get("ml_name") or identity[1]
    label = values.get("label") or values.get("ml_name") or internal_key
    value_source = values.get("value_source", "")
    return DataDefinitionInventoryRow(
        identity=identity,
        label=label,
        internal_key=internal_key,
        category=_category(values, source_kind),
        data_type=values.get("data_type") or ("Derived" if source_kind == "derived_policy" else "—"),
        source_type=_source_type(value_source, source_kind),
        relationship=_relationship(values),
        predict_visibility="Visible" if _as_bool(values.get("visible", "false")) else "Hidden",
        model_input=(
            "Enabled" if _as_bool(values.get("model_input_enabled", "false")) else "Disabled"
        ),
        lifecycle_state=lifecycle_state,
        ml_name=values.get("ml_name", ""),
        cells=cells,
    )


def _matches(
    row: DataDefinitionInventoryRow,
    search: str,
    category: str,
    source_type: str,
    lifecycle_state: str,
) -> bool:
    searchable = " ".join((row.label, row.internal_key, row.ml_name)).casefold()
    return (
        (not search or search in searchable)
        and (not category or row.category == category)
        and (not source_type or row.source_type == source_type)
        and (not lifecycle_state or row.lifecycle_state == lifecycle_state)
    )


def _resolved_filter(selected: str, available: tuple[str, ...]) -> str:
    return selected if selected in available else ""


def _view_state(
    state: DataDefinitionControllerState,
    canonical_rows: tuple[DataDefinitionInventoryRow, ...],
    visible_rows: tuple[DataDefinitionInventoryRow, ...],
) -> tuple[str, str]:
    if not canonical_rows and state.status == "error":
        return "load_error", state.message
    if not canonical_rows:
        return "empty", "No definitions are available in the current draft."
    if not visible_rows:
        return "no_match", "No definitions match the current search and filters."
    return "populated", f"{len(visible_rows)} of {len(canonical_rows)} definitions shown."


def _application_status(state: DataDefinitionControllerState) -> tuple[str, str]:
    if state.status == "error" and not state.draft_rows:
        return "load_error", "Load error"
    if state.status == "saved":
        return "saved", "Saved"
    if state.status == "error":
        return "write_error", "Write error"
    if state.status == "blocked":
        return "blocked", "Blocked"
    if state.draft_changed and not state.can_save_schema:
        return "blocked", "Blocked"
    if state.draft_changed:
        return "dirty", "Unsaved changes"
    return "clean", "Clean"


def _category(values: dict[str, str], source_kind: str) -> str:
    if source_kind == "derived_policy":
        return "Derived Policy"
    role = values.get("role", "")
    if role == "result":
        return "Prediction Result"
    if role == "status":
        return "Status"
    if role == "one_hot_feature":
        return "One-hot Feature"
    if values.get("value_source") == "mapping_lookup":
        return "Mapping-backed Input"
    if role == "input":
        return "Predict Input"
    return "Schema Definition"


def _source_type(value_source: str, source_kind: str) -> str:
    if source_kind == "derived_policy":
        return "Derived Policy"
    return value_source.replace("_", " ").title() if value_source else "Unspecified"


def _relationship(values: dict[str, str]) -> str:
    parts = [value for value in (values.get("mapping_entity"), values.get("mapping_attribute")) if value]
    relationship = " / ".join(parts)
    trigger = values.get("trigger_column", "")
    if trigger:
        relationship = f"{relationship} (trigger: {trigger})" if relationship else f"Trigger: {trigger}"
    if not relationship and values.get("one_hot_group"):
        relationship = f"One-hot: {values['one_hot_group']}"
    return relationship or "—"


def _as_bool(value: str) -> bool:
    return value.strip().casefold() == "true"
