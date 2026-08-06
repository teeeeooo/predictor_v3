"""Read-only onboarding projection for one saved Data Definition generation."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.application.data_definition.ports import GenerationSnapshot
from core.data_definition.target_registry.runtime import model_registry_snapshot


@dataclass(frozen=True)
class TrainingContractReferenceRow:
    definition_identity: str
    definition_kind: str
    ml_name: str
    label: str
    column_key: str
    role: str
    active: bool
    raw_train_required: bool
    training_header_order: int | None
    value_source: str = ""
    mapping_entity: str = ""
    mapping_attribute: str = ""
    one_hot_group: str = ""


@dataclass(frozen=True)
class TrainingContractExportDocument:
    generation_id: str
    training_headers: tuple[str, ...]
    reference_rows: tuple[TrainingContractReferenceRow, ...]


@dataclass(frozen=True)
class TrainingContractExportContext:
    document: TrainingContractExportDocument
    draft_dirty: bool


def build_training_contract_export(
    snapshot: GenerationSnapshot,
) -> TrainingContractExportDocument:
    """Project disposable onboarding data from one immutable generation snapshot."""
    registry = model_registry_snapshot(snapshot.manifest)
    header_positions = {
        ml_name: index
        for index, ml_name in enumerate(registry.training_headers, start=1)
    }
    rows = tuple(
        _feature_reference(item, header_positions)
        for item in snapshot.manifest.features
    ) + tuple(
        _derived_reference(item, header_positions)
        for item in snapshot.manifest.derived
    )
    return TrainingContractExportDocument(
        generation_id=registry.generation_id,
        training_headers=registry.training_headers,
        reference_rows=rows,
    )


def _feature_reference(item, header_positions) -> TrainingContractReferenceRow:  # noqa: ANN001
    order = header_positions.get(item.ml_name)
    return TrainingContractReferenceRow(
        definition_identity=item.identity,
        definition_kind="Feature",
        ml_name=item.ml_name,
        label=item.label,
        column_key=item.column_key,
        role=item.role,
        active=item.active,
        raw_train_required=order is not None,
        training_header_order=order,
        value_source=item.value_source,
        mapping_entity=item.mapping_entity,
        mapping_attribute=item.mapping_attribute,
        one_hot_group=item.one_hot_group,
    )


def _derived_reference(item, header_positions) -> TrainingContractReferenceRow:  # noqa: ANN001
    order = header_positions.get(item.ml_name)
    return TrainingContractReferenceRow(
        definition_identity=item.identity,
        definition_kind="Derived",
        ml_name=item.ml_name,
        label="",
        column_key="",
        role="derived",
        active=item.active,
        raw_train_required=order is not None,
        training_header_order=order,
    )
