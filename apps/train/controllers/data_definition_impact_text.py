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
        lines.append(f"• {item.action} {item.label} ({item.identity[1]})" + (f" — {fields}" if fields else ""))
    return "\n".join(lines)


def save_text(
    status: str,
    schema_status: str,
    enabled: bool,
    blockers: tuple[DataDefinitionFocusedBlockerItem, ...],
    warnings: tuple[str, ...],
) -> str:
    lines = [
        f"Draft: {status}  |  schema.csv: {schema_status}  |  Save: {'enabled' if enabled else 'disabled'}"
    ]
    lines.extend(
        f"• {item.relevance}: {item.code} [{item.related_field or item.target}] — {item.message}"
        for item in blockers
    )
    lines.extend(f"• warning: {warning}" for warning in warnings)
    return "\n".join(lines)


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
        return "No Mapping Requirement impact. Coverage and navigation are deferred to Slice 3D."
    lines = [
        f"• {row[1]}: {row[4]} in {row[3]} ({row[7]}; trigger {row[5]}, rule {row[6] or 'simple lookup'})"
        for row in rows
    ]
    lines.append("Concrete values remain Data Mapping-owned; coverage and navigation are deferred to Slice 3D.")
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
