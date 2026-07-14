"""Presentation helpers for Data Mapping Manager tables."""

from __future__ import annotations

from apps.train.controllers.data_mapping_controller import DataMappingControllerState

ENTITY_HEADERS = ("Group", "Label", "Rows", "Active", "Notes")
GROUP_HEADERS = ("Group", "Rows")
ATTRIBUTE_HEADERS = ("Field", "Label", "Type", "Required", "Notes")
VALIDATION_HEADERS = ("Level", "Group", "Row", "Field", "Message")


def entity_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for the entity list table."""
    return tuple(
        (
            entity.entity_key,
            entity.label,
            str(entity.row_count),
            _bool_text(entity.active),
            entity.notes,
        )
        for entity in state.entities
    )


def group_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return concise user-facing rows for group navigation."""
    return tuple((entity.label, str(entity.row_count)) for entity in state.entities)


def attribute_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for the selected entity attribute table."""
    return tuple(
        (
            attribute.attribute_key,
            attribute.label,
            attribute.data_type,
            _bool_text(attribute.required),
            attribute.notes,
        )
        for attribute in state.attributes
    )


def value_headers(state: DataMappingControllerState) -> tuple[str, ...]:
    """Return table headers for row data values."""
    return state.value_headers


def value_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for selected entity row data."""
    return tuple(row.values for row in state.values)


def validation_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for validation summary."""
    if not state.validation_rows:
        return (("info", "", "", "", "Mapping draft projection OK."),)
    return tuple(
        (
            row.severity,
            row.entity_key,
            row.row_key,
            row.attribute_key,
            row.message,
        )
        for row in state.validation_rows
    )


def status_summary(state: DataMappingControllerState) -> str:
    """Return concise resource, group, issue, dirty, and Save state text."""
    entity = next(
        (item for item in state.entities if item.entity_key == state.selected_group_key),
        None,
    )
    group_text = f"{entity.label} · {entity.row_count} rows" if entity else "No group"
    actions = {action.key: action for action in state.actions}
    save_action = actions.get("save_mapping_json")
    resource_text = {
        "exists": "Available",
        "available": "Provider available",
        "missing": "Missing",
        "load-error": "Load error",
    }.get(state.resource_status, state.resource_status)
    return (
        f"Resource: {resource_text}  |  Group: {group_text}  |  "
        f"Issues: {len(state.validation_rows)}  |  "
        f"Draft: {'Unsaved' if state.dirty else 'Saved'}  |  "
        f"Save: {'Available' if save_action and save_action.enabled else 'Blocked'}"
    )


def status_kind(state: DataMappingControllerState) -> str:
    """Map controller status to a semantic visual style."""
    return {
        "ready": "ready",
        "warning": "warning",
    }.get(state.status, "error")


def workspace_state_copy(state: DataMappingControllerState) -> tuple[str, str]:
    """Return title/message for non-populated primary workspace states."""
    entity = next(
        (item for item in state.entities if item.entity_key == state.selected_group_key),
        None,
    )
    if state.status == "missing":
        return (
            "Mapping resource unavailable",
            "The configured mapping file was not found. Restore it, then use Reload.",
        )
    if state.resource_status == "load-error":
        return (
            "Mapping data could not be loaded",
            "Review the issue details, correct the source, then use Reload.",
        )
    if entity is not None and not state.values:
        return (
            f"{entity.label} has no rows",
            "This group is available but empty. Use Add to create its first row.",
        )
    if entity is None:
        return (
            "No mapping groups available",
            "No editable mapping groups were projected. Review the source, then Reload.",
        )
    return "", ""


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
