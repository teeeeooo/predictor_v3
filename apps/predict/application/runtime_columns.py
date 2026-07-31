"""Immutable identity-bearing column contract for one Predict generation."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.contract import FeatureDefinition
from core.predictor_schema.catalog_v2 import PredictSchemaV2Row


@dataclass(frozen=True)
class PredictRuntimeColumnDescriptor:
    """Canonical identity plus mutable metadata for one generation Feature."""

    feature_identity: str
    display_order: int
    key: str
    label: str
    role: str
    editor: str
    data_type: str
    visible: bool
    required: bool
    readonly: bool
    value_source: str
    mapping_entity: str
    mapping_attribute: str
    trigger_column: str
    rule_id: str
    model_input_enabled: bool
    ml_name: str
    one_hot_group: str
    active: bool
    notes: str

    @property
    def classification(self) -> str:
        """Return the Predict presentation class without changing Feature role."""
        if self.role in {"input", "auto", "result"}:
            return self.role
        return "excluded"


def build_runtime_column_descriptors(
    features: tuple[FeatureDefinition, ...],
    predict_order: tuple[str, ...],
    projection: tuple[PredictSchemaV2Row, ...],
) -> tuple[PredictRuntimeColumnDescriptor, ...]:
    """Bind identity from the canonical manifest and verify its public projection."""
    identities = tuple(item.identity for item in features)
    if any(not identity for identity in identities):
        raise ValueError("predict runtime Feature identity is missing")
    if len(set(identities)) != len(identities):
        raise ValueError("predict runtime Feature identity is duplicated")
    if len(set(predict_order)) != len(predict_order):
        raise ValueError("predict runtime ordering contains duplicate Feature identity")
    if set(predict_order) != set(identities):
        raise ValueError("predict runtime ordering has an incomplete Feature identity set")

    feature_by_identity = {item.identity: item for item in features}
    descriptors = tuple(
        _column_descriptor(feature_by_identity[identity])
        for identity in predict_order
    )
    if len(projection) != len(descriptors):
        raise ValueError("predict runtime generated projection is incomplete")
    for descriptor, row in zip(descriptors, projection, strict=True):
        if _descriptor_projection_values(descriptor) != _projection_values(row):
            raise ValueError(
                "predict runtime generated projection does not match canonical "
                f"Feature identity {descriptor.feature_identity}"
            )
    return descriptors


def _column_descriptor(
    feature: FeatureDefinition,
) -> PredictRuntimeColumnDescriptor:
    return PredictRuntimeColumnDescriptor(
        feature_identity=feature.identity,
        display_order=feature.display_order,
        key=feature.column_key,
        label=feature.label,
        role=feature.role,
        editor=feature.editor,
        data_type=feature.data_type,
        visible=feature.visible,
        required=feature.required,
        readonly=feature.readonly,
        value_source=feature.value_source,
        mapping_entity=feature.mapping_entity,
        mapping_attribute=feature.mapping_attribute,
        trigger_column=feature.trigger_column,
        rule_id=feature.rule_id,
        model_input_enabled=feature.model_input_enabled,
        ml_name=feature.ml_name,
        one_hot_group=feature.one_hot_group,
        active=feature.active,
        notes=feature.notes,
    )


def _descriptor_projection_values(
    descriptor: PredictRuntimeColumnDescriptor,
) -> tuple[object, ...]:
    return (
        descriptor.display_order,
        descriptor.key,
        descriptor.label,
        descriptor.role,
        descriptor.editor,
        descriptor.data_type,
        descriptor.visible,
        descriptor.required,
        descriptor.readonly,
        descriptor.value_source,
        descriptor.mapping_entity,
        descriptor.mapping_attribute,
        descriptor.trigger_column,
        descriptor.rule_id,
        descriptor.model_input_enabled,
        descriptor.ml_name,
        descriptor.one_hot_group,
        descriptor.active,
        descriptor.notes,
    )


def _projection_values(row: PredictSchemaV2Row) -> tuple[object, ...]:
    return (
        row.display_order,
        row.column_key,
        row.label,
        row.role,
        row.editor,
        row.data_type,
        row.visible,
        row.required,
        row.readonly,
        row.value_source,
        row.mapping_entity,
        row.mapping_attribute,
        row.trigger_column,
        row.rule_id,
        row.model_input_enabled,
        row.ml_name,
        row.one_hot_group,
        row.active,
        row.notes,
    )
