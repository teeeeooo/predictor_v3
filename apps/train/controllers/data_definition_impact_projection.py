"""Concise UI-facing impact projection for Data Definition workflows."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_detail_projection import (
    DataDefinitionFocusedBlockerItem,
    project_blockers,
)
from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState
from apps.train.controllers.data_definition_impact_text import (
    change_text,
    mapping_text,
    result_text,
    runtime_text,
    save_text,
)

_MAPPING_FIELDS = frozenset(
    {"mapping_entity", "mapping_attribute", "trigger_column", "rule_id", "value_source"}
)


@dataclass(frozen=True)
class ImpactFieldChange:
    """One concise before/after field mutation."""

    field_name: str
    before: str
    after: str


@dataclass(frozen=True)
class ImpactDefinitionChange:
    """One affected definition in deterministic draft order."""

    identity: tuple[str, str]
    action: str
    label: str
    fields: tuple[ImpactFieldChange, ...]


@dataclass(frozen=True)
class DataDefinitionImpactProjection:
    """Single non-mutating impact preview for the default workspace."""

    status: str
    definitions: tuple[ImpactDefinitionChange, ...]
    schema_write_status: str
    save_enabled: bool
    blockers: tuple[DataDefinitionFocusedBlockerItem, ...]
    warnings: tuple[str, ...]
    requires_restart: bool
    requires_retrain: bool
    ml_fingerprint_changed: bool
    training_header_evidence: str
    model_activation_evidence: str
    mapping_impacts: tuple[tuple[str, ...], ...]
    save_result_status: str
    save_result_rows: tuple[tuple[str, str], ...]
    change_text: str
    save_text: str
    runtime_text: str
    mapping_text: str
    result_text: str


def project_data_definition_impact(
    state: DataDefinitionControllerState,
    selected_identity: tuple[str, str] | None = None,
) -> DataDefinitionImpactProjection:
    """Project existing authoritative evidence without mutating application state."""
    definitions = _definition_changes(state)
    schema_status = next(
        (row[1] for row in state.save_plan_rows if row and row[0] == "schema_csv"),
        "unavailable",
    )
    blockers = project_blockers(state, selected_identity) if selected_identity else ()
    warnings = tuple(
        item.message
        for item in state.blocker_items
        if item.severity == "warning"
    )
    blocker_codes = {item.code for item in state.blocker_items if item.severity == "error"}
    ml_changed = "ml_compatibility_projection_write_required" in blocker_codes
    mapping_impacts = _mapping_impacts(state, definitions)
    result = dict(state.save_result_rows)
    result_status = result.get("Status", "not_attempted")
    status = (
        "clean"
        if not state.draft_changed
        else "blocked"
        if not state.can_save_schema
        or result_status == "blocked"
        else "dirty"
    )
    training = _readiness(state, "training_headers")
    activation = _readiness(state, "model_activation")
    return DataDefinitionImpactProjection(
        status=status,
        definitions=definitions,
        schema_write_status=schema_status,
        save_enabled=state.save_action_enabled,
        blockers=blockers,
        warnings=warnings,
        requires_restart=state.requires_restart,
        requires_retrain=state.requires_retrain,
        ml_fingerprint_changed=ml_changed,
        training_header_evidence=training,
        model_activation_evidence=activation,
        mapping_impacts=mapping_impacts,
        save_result_status=result_status,
        save_result_rows=state.save_result_rows,
        change_text=change_text(definitions),
        save_text=save_text(status, schema_status, state.save_action_enabled, blockers, warnings),
        runtime_text=runtime_text(state, ml_changed, training, activation),
        mapping_text=mapping_text(mapping_impacts),
        result_text=result_text(result),
    )


def _definition_changes(
    state: DataDefinitionControllerState,
) -> tuple[ImpactDefinitionChange, ...]:
    grouped: dict[tuple[str, str], list[ImpactFieldChange]] = {}
    actions: dict[tuple[str, str], str] = {}
    for source, key, field_name, before, after in state.draft_change_rows:
        if not field_name or source not in {"schema_row", "derived_policy", "feature_projection"}:
            continue
        identity = (source, key)
        if field_name == "__row__":
            actions[identity] = "Add" if not before else "Remove"
            grouped.setdefault(identity, [])
        else:
            actions.setdefault(identity, "Edit")
            grouped.setdefault(identity, []).append(
                ImpactFieldChange(field_name, before, after)
            )
    current_values = _current_values(state)
    draft_order = {identity: index for index, identity in enumerate(state.draft_row_identities)}
    ordered = sorted(
        grouped,
        key=lambda identity: (draft_order.get(identity, len(draft_order)), identity),
    )
    return tuple(
        ImpactDefinitionChange(
            identity=identity,
            action=actions[identity],
            label=(
                current_values.get(identity, {}).get("label")
                or current_values.get(identity, {}).get("ml_name")
                or identity[1]
            ),
            fields=tuple(grouped[identity]),
        )
        for identity in ordered
    )


def _current_values(
    state: DataDefinitionControllerState,
) -> dict[tuple[str, str], dict[str, str]]:
    return {
        identity: {cell.field_name: cell.value for cell in cells}
        for identity, cells in zip(
            state.draft_row_identities,
            state.draft_rows,
            strict=True,
        )
    }


def _mapping_impacts(
    state: DataDefinitionControllerState,
    definitions: tuple[ImpactDefinitionChange, ...],
) -> tuple[tuple[str, ...], ...]:
    requirement_keys = {row[0] for row in state.mapping_requirement_rows}
    values = _current_values(state)
    affected = {
        item.identity[1]
        for item in definitions
        if item.identity[1] in requirement_keys
        or any(field.field_name in _MAPPING_FIELDS for field in item.fields)
    }
    current = tuple(
        (
            "Required",
            *row,
            "required"
            if values.get(("schema_row", row[0]), {}).get("required") == "true"
            else "optional",
            "Data Mapping owns concrete values",
        )
        for row in state.mapping_requirement_rows
        if row[0] in affected
    )
    current_keys = {row[1] for row in current}
    removed = tuple(
        (
            "Removed or incomplete", item.identity[1], "", "", "", "", "", "unknown",
            "Data Mapping values unchanged",
        )
        for item in definitions
        if item.identity[1] in affected and item.identity[1] not in current_keys
    )
    return (*current, *removed)


def _readiness(state: DataDefinitionControllerState, name: str) -> str:
    row = next((item for item in state.readiness_rows if item[0] == name), None)
    if row is None:
        return "unavailable — no owner evidence"
    return f"{row[1]} — {row[2]}"
