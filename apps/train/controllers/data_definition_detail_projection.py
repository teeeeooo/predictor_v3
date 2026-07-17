"""Focused detail projection for the Data Definition inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from apps.train.controllers.data_definition_state_builder import (
    DataDefinitionBlockerItem,
    DataDefinitionControllerState,
)

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


BlockerRelevance = Literal[
    "direct",
    "other_definition",
    "selection_unavailable",
    "global",
]


@dataclass(frozen=True)
class DataDefinitionFocusedBlockerItem:
    """One deduplicated blocker classified for the selected definition."""

    severity: str
    code: str
    target: str
    message: str
    related_row_identity: tuple[str, str] | None
    related_field: str
    source: str
    relevance: BlockerRelevance
    related_definition_name: str


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
        "Supported schema-backed fields can be changed through Edit."
        if editable
        else next((cell.reason for cell in row.cells if cell.reason), "Direct editing is blocked.")
    )
    rows = (
        ("Label", row.label),
        ("Internal key", row.internal_key),
        ("Definition category", row.category),
        ("Definition origin", _friendly_value(values.get("source_kind", row.identity[0]))),
        ("Role / type / editor", _friendly_joined(values, "role", "data_type", "editor")),
        ("Visible / required / readonly", _flags(values)),
        ("Value source", row.source_type),
        ("Mapping group", _friendly_value(values.get("mapping_entity")) or "—"),
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
        ("Save blockers", _blocker_summary(state, row.identity)),
        ("Display order", values.get("display_order") or "—"),
        ("Rule ID", values.get("rule_id") or "—"),
        ("One-hot group", values.get("one_hot_group") or "—"),
        ("Notes", values.get("notes") or "—"),
    )
    return DataDefinitionDetailState("selected", row.label, row.internal_key, row.identity, rows)


def _blocker_summary(
    state: DataDefinitionControllerState,
    selected_identity: tuple[str, str],
) -> str:
    blockers = project_blockers(state, selected_identity)
    if not blockers:
        return "None"
    direct = tuple(item for item in blockers if item.relevance == "direct")
    other = tuple(item for item in blockers if item.relevance == "other_definition")
    global_items = tuple(item for item in blockers if item.relevance == "global")
    sections: list[str] = []
    if direct:
        sections.append(_blocker_section("Direct blockers", direct))
    else:
        sections.append("No direct blocker for this definition.")
    if other:
        sections.append(_blocker_section("Draft blockers from other definitions", other))
    if global_items:
        sections.append(_blocker_section("Global draft blockers", global_items))
    return "\n\n".join(sections)


def project_blockers(
    state: DataDefinitionControllerState,
    selected_identity: tuple[str, str] | None,
) -> tuple[DataDefinitionFocusedBlockerItem, ...]:
    """Collect every blocker and classify only its selection relevance."""
    selected_identity = _resolve_identity(state, selected_identity)
    plan_items = tuple(
        item
        for item in state.blocker_items
        if item.severity == "error" and item.source == "save_plan"
    )
    plan_keys = {_blocker_key(item) for item in plan_items}
    result_items = tuple(
        item
        for item in state.blocker_items
        if item.severity == "error"
        and item.source == "last_save_result"
        and _blocker_key(item) not in plan_keys
    )
    classified = tuple(
        _focused_blocker(state, item, selected_identity)
        for item in (*plan_items, *result_items)
    )
    return tuple(
        item
        for relevance in (
            "direct",
            "other_definition",
            "selection_unavailable",
            "global",
        )
        for item in classified
        if item.relevance == relevance
    )


def _resolve_identity(
    state: DataDefinitionControllerState,
    identity: tuple[str, str] | None,
) -> tuple[str, str] | None:
    if identity is None or identity in state.draft_row_identities:
        return identity
    for candidate, cells in zip(state.draft_row_identities, state.draft_rows, strict=True):
        values = {cell.field_name: cell.value for cell in cells}
        if identity[0] == candidate[0] and identity[1] in {
            values.get("column_key", ""), values.get("ml_name", ""),
        }:
            return candidate
    return identity


def _blocker_key(item: DataDefinitionBlockerItem) -> tuple[object, ...]:
    return (
        item.code,
        item.target,
        item.related_row_identity,
        item.related_field,
        " ".join(item.message.split()).casefold(),
    )


def _focused_blocker(
    state: DataDefinitionControllerState,
    item: DataDefinitionBlockerItem,
    selected_identity: tuple[str, str] | None,
) -> DataDefinitionFocusedBlockerItem:
    relevance: BlockerRelevance = (
        "global"
        if item.related_row_identity is None
        else "selection_unavailable"
        if selected_identity is None
        else "direct"
        if item.related_row_identity == selected_identity
        else "other_definition"
    )
    return DataDefinitionFocusedBlockerItem(
        severity=item.severity,
        code=item.code,
        target=item.target,
        message=item.message,
        related_row_identity=item.related_row_identity,
        related_field=item.related_field,
        source=item.source,
        relevance=relevance,
        related_definition_name=_definition_name(state, item.related_row_identity),
    )


def _blocker_section(
    title: str,
    items: tuple[DataDefinitionFocusedBlockerItem, ...],
) -> str:
    return "\n".join((title, *(_blocker_line(item) for item in items)))


def _blocker_line(item: DataDefinitionFocusedBlockerItem) -> str:
    definition = (
        f"{item.related_definition_name} — "
        if item.relevance in {"other_definition", "selection_unavailable"}
        and item.related_row_identity
        else ""
    )
    context = " / ".join(
        part for part in (item.related_field, item.target) if part
    )
    context_text = f" [{context}]" if context else ""
    return f"- {definition}{item.code}{context_text}: {item.message}"


def _definition_name(
    state: DataDefinitionControllerState,
    identity: tuple[str, str] | None,
) -> str:
    if identity is None:
        return ""
    try:
        index = state.draft_row_identities.index(identity)
    except ValueError:
        return identity[1]
    values = {cell.field_name: cell.value for cell in state.draft_rows[index]}
    return values.get("column_key") or values.get("label") or identity[1]


def _friendly_value(value: str | None) -> str:
    return (value or "").replace("_", " ").strip().title()


def _friendly_joined(values: dict[str, str], *keys: str) -> str:
    return " / ".join(_friendly_value(values.get(key)) or "—" for key in keys)


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
    if row.model_input == "Used" or row.ml_name:
        return "Compatible with current projection"
    return "Not a model input"


def _joined(values: dict[str, str], *fields: str) -> str:
    return " / ".join(values.get(field) or "—" for field in fields)


def _flags(values: dict[str, str]) -> str:
    return " / ".join(
        f"{field}: {values.get(field) or 'false'}"
        for field in ("visible", "required", "readonly")
    )
