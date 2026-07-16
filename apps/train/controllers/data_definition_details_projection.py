"""Normalized read-only Details projection for Data Definition rows."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
)
from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState
from apps.train.controllers.data_definition_summary_projection import (
    DataDefinitionSummaryProjection,
    DefinitionSummaryFact,
    project_data_definition_summary,
)


@dataclass(frozen=True)
class DataDefinitionDetailsProjection:
    """Immutable snapshot consumed by the read-only Details dialog."""

    state: str
    identity: tuple[str, str] | None
    title: str
    internal_key: str
    status: str
    description: str
    facts: tuple[DefinitionSummaryFact, ...]
    technical_details: tuple[tuple[str, str], ...]
    edit_enabled: bool
    edit_reason: str


def project_data_definition_details(
    state: DataDefinitionControllerState,
    inventory: DataDefinitionInventoryProjection,
) -> DataDefinitionDetailsProjection:
    """Combine existing summary and detail evidence without widget interpretation."""
    summary = project_data_definition_summary(state, inventory)
    technical_details = _technical_details(summary, inventory.detail.rows)
    return DataDefinitionDetailsProjection(
        state=summary.state,
        identity=inventory.selected_identity,
        title=summary.title,
        internal_key=summary.internal_key,
        status=summary.status,
        description=summary.description,
        facts=summary.facts,
        technical_details=technical_details,
        edit_enabled=summary.edit_enabled,
        edit_reason=summary.edit_reason,
    )


def _technical_details(
    summary: DataDefinitionSummaryProjection,
    rows: tuple[tuple[str, str], ...],
) -> tuple[tuple[str, str], ...]:
    """Keep technical evidence deterministic and remove Summary-owned duplicates."""
    summary_labels = {fact.label for fact in summary.facts}
    summary_labels.update({"Label", "Internal key", "Definition category", "Active"})
    return tuple(
        (label, value)
        for label, value in rows
        if label not in summary_labels
    )
