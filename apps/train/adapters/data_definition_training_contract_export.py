"""CSV publication adapters for disposable Data Definition onboarding exports."""

from __future__ import annotations

import csv
from pathlib import Path

from apps.train.application.data_definition.training_contract_export import (
    TrainingContractExportDocument,
)

REFERENCE_HEADERS = (
    "generation_id",
    "definition_identity",
    "definition_kind",
    "ml_name",
    "label",
    "column_key",
    "role",
    "active",
    "raw_train_required",
    "training_header_order",
    "value_source",
    "mapping_entity",
    "mapping_attribute",
    "one_hot_group",
)


def publish_training_header_template(
    destination: str | Path,
    document: TrainingContractExportDocument,
) -> Path:
    """Write exactly one authoritative raw-training header row with no data rows."""
    path = Path(destination)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        csv.writer(stream).writerow(document.training_headers)
    return path


def publish_definition_reference(
    destination: str | Path,
    document: TrainingContractExportDocument,
) -> Path:
    """Write a review-only generation crosswalk for common spreadsheet tools."""
    path = Path(destination)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(REFERENCE_HEADERS)
        for row in document.reference_rows:
            writer.writerow(_reference_values(document.generation_id, row))
    return path


def _reference_values(generation_id, row) -> tuple[object, ...]:  # noqa: ANN001
    return (
        generation_id,
        row.definition_identity,
        row.definition_kind,
        row.ml_name,
        row.label,
        row.column_key,
        row.role,
        "Yes" if row.active else "No",
        "Yes" if row.raw_train_required else "No",
        row.training_header_order or "",
        row.value_source,
        row.mapping_entity,
        row.mapping_attribute,
        row.one_hot_group,
    )
