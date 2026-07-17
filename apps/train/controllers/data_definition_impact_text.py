"""User-facing text formatting for Data Definition impact evidence."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.train.controllers.data_definition_impact_projection import ImpactDefinitionChange
    from apps.train.controllers.data_definition_detail_projection import (
        DataDefinitionFocusedBlockerItem,
    )
    from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState


def change_text(definitions: tuple[ImpactDefinitionChange, ...]) -> str:
    if not definitions:
        return "No unsaved definition changes."
    lines = [f"{len(definitions)} affected definition(s)"]
    for item in definitions:
        fields = ", ".join(
            f"{field.field_name}: {field.before or '—'} → {field.after or '—'}"
            for field in item.fields
        )
        lines.append(f"• {item.action} {item.label} ({item.column_key})" + (f" — {fields}" if fields else ""))
    return "\n".join(lines)


def save_text(
    status: str,
    schema_status: str,
    enabled: bool,
    blockers: tuple[DataDefinitionFocusedBlockerItem, ...],
    warnings: tuple[str, ...],
) -> str:
    visible_status = {
        "clean": "Clean",
        "dirty": "Unsaved changes",
        "blocked": "Blocked",
    }.get(status, status.title())
    lines = [
        f"{visible_status}  |  Schema write: {schema_status.replace('_', ' ')}  |  "
        f"Save schema: {'available' if enabled else 'unavailable'}"
    ]
    lines.extend(_blocker_text(item) for item in blockers)
    lines.extend(f"• warning: {warning}" for warning in warnings)
    return "\n".join(lines)


def _blocker_text(item: DataDefinitionFocusedBlockerItem) -> str:
    context: list[str] = []
    if (
        item.relevance in {"other_definition", "selection_unavailable"}
        and item.related_row_identity is not None
    ):
        context.append(f"definition: {item.related_definition_name}")
    if item.related_field:
        context.append(f"field: {item.related_field}")
    if item.target and item.target != item.related_field:
        context.append(f"target: {item.target}")
    context_text = f" [{'; '.join(context)}]" if context else ""
    relevance = item.relevance.replace("_", " ").title()
    return f"• {relevance}{context_text} — {item.message} ({item.code})"


def runtime_text(
    state: DataDefinitionControllerState,
    ml_changed: bool,
    training: str,
    activation: str,
) -> str:
    return "\n".join((
        f"Predict restart: {'required' if state.requires_restart else 'not required'}",
        f"Schema shape/metadata: {'changed' if state.draft_changed else 'unchanged'}",
        f"ML compatibility fingerprint: {'changed' if ml_changed else 'unchanged'}",
        f"Retrain: {'required' if state.requires_retrain else 'not required'}",
        f"Training headers: {training}",
        f"Model activation: {activation}",
    ))


def mapping_text(rows: tuple[tuple[str, ...], ...]) -> str:
    if not rows:
        return "No Mapping Requirement impact. Concrete values remain unchanged."
    lines = [
        f"• {row[1]}: {row[4]} in {row[3]} ({row[7]}; trigger {row[5]}, rule {row[6] or 'simple lookup'})"
        for row in rows
    ]
    lines.append(
        "Concrete values remain Data Mapping-owned. Save schema before opening coverage."
    )
    return "\n".join(lines)


def result_text(result: dict[str, str]) -> str:
    if result.get("Status") in {None, "No save attempted."}:
        return "No save attempted."
    lines = [
        f"Status: {result.get('Status', 'unavailable')} — {result.get('Message', '')}",
        f"Rows written: {result.get('Rows written', '0')}",
        f"Schema path: {result.get('Path') or '—'}",
        f"Backup path: {result.get('Backup') or '—'}",
    ]
    if result.get("Issues") not in {None, "", "none"}:
        lines.append(f"Issues: {result['Issues']}")
    if result.get("Status") == "written":
        lines.append("Restart Predict before using the saved schema.")
    if result.get("Status") == "error":
        lines.append("The dirty draft is retained; retry Save after the write issue clears.")
    return "\n".join(lines)
