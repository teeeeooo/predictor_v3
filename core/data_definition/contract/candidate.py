"""Project an immutable Data Definition draft onto a canonical base manifest."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition.contract.identity import bootstrap_identity
from core.data_definition.contract.model import (
    DerivedDefinition,
    FeatureDefinition,
    MappingRequirementDefinition,
    OrderingContract,
    UnifiedFeatureManifest,
)
from core.data_definition.contract.compatibility import migrate_manifest
from core.data_definition.contract.fingerprints import semantic_generation_id
from core.data_definition.contract.projections import topological_derived_identities
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.projection import project_feature_catalog_from_draft


def candidate_manifest_from_draft(
    draft: DataDefinitionDraft,
    base: UnifiedFeatureManifest,
) -> UnifiedFeatureManifest:
    """Return a new immutable generation candidate without mutating either input."""
    base = migrate_manifest(base)
    base_by_identity = {item.identity: item for item in base.features}
    base_by_key = {item.column_key: item for item in base.features}
    schema_rows = tuple(item for item in draft.rows if item.source_kind == "schema_row")
    rows_by_identity = {item.identity: item for item in schema_rows}
    ordered_rows = tuple(
        rows_by_identity[identity]
        for identity in draft.predict_order
        if identity in rows_by_identity
    )
    ordered_rows += tuple(item for item in schema_rows if item not in ordered_rows)
    features = tuple(
        _feature_from_draft(
            row,
            (
                base_by_identity.get(row.stable_identity)
                if row.stable_identity
                else base_by_key.get(row.column_key)
            ),
            base.generation.generation_id,
        )
        for row in ordered_rows
    )
    feature_by_key = {item.column_key: item for item in features}
    feature_by_ml = {item.ml_name: item for item in features if item.ml_name}
    derived = _derived_from_draft(draft)
    derived_by_ml = {item.ml_name: item for item in derived}
    projected_ml = project_feature_catalog_from_draft(draft)
    projected_ids = tuple(
        owner.identity
        for item in projected_ml
        if (owner := derived_by_ml.get(item.ml_name) or feature_by_ml.get(item.ml_name))
        is not None
    )
    eligible_ids = {
        item.identity
        for item in features
        if item.active and item.ml_name and (item.model_input_enabled or item.role == "result")
    } | {item.identity for item in derived if item.active}
    fallback_ids = tuple(item for item in projected_ids if item in eligible_ids) + tuple(
        item.identity for item in derived if item.active and item.identity not in projected_ids
    )
    requested_ml_order = tuple(identity[1] for identity in draft.ml_order)
    ml_order = tuple(item for item in requested_ml_order if item in eligible_ids) + tuple(
        item for item in fallback_ids if item not in requested_ml_order
    )
    requirements = tuple(
        _mapping_requirement(item, feature_by_key, base)
        for item in features if item.value_source == "mapping_lookup"
    )
    candidate = replace(
        base,
        generation=replace(
            base.generation,
            generation_id="candidate-pending",
            parent_generation_id=base.generation.generation_id,
            source="data_definition_save",
        ),
        features=features,
        derived=derived,
        one_hot_groups=tuple(draft.one_hot_groups),
        mapping_requirements=requirements,
        ordering=OrderingContract(
            predict=tuple(item.identity for item in features),
            ml=ml_order,
            derived=tuple(item.identity for item in derived),
            targets=base.ordering.targets,
        ),
    )
    derived_order = topological_derived_identities(candidate)
    derived_by_id = {item.identity: item for item in derived}
    candidate = replace(
        candidate,
        derived=tuple(derived_by_id[identity] for identity in derived_order),
        ordering=replace(candidate.ordering, derived=derived_order),
    )
    generation_id = semantic_generation_id(candidate, prefix="generation")
    return replace(candidate, generation=replace(candidate.generation, generation_id=generation_id))


def _derived_from_draft(draft: DataDefinitionDraft) -> tuple[DerivedDefinition, ...]:
    return tuple(
        DerivedDefinition(
            identity=row.stable_identity,
            ml_name=row.ml_name,
            operation=row.operation,
            numerator_identity=row.numerator_identity,
            denominator_identity=row.denominator_identity,
            zero_denominator_policy=row.zero_denominator_policy,
            zero_value=float(row.zero_value),
            zero_fill_policy="disallow",
            active=row.active,
        )
        for row in draft.rows
        if row.source_kind == "derived_policy"
    )


def _feature_from_draft(row, existing, parent_generation_id: str) -> FeatureDefinition:  # noqa: ANN001
    identity = (
        existing.identity
        if existing is not None
        else row.stable_identity
        or bootstrap_identity("feature", f"generation-add:{parent_generation_id}:{row.column_key}")
    )
    zero_fill = existing.zero_fill_policy if existing is not None else "disallow"
    return FeatureDefinition(
        identity=identity,
        display_order=row.display_order,
        column_key=row.column_key,
        label=row.label,
        role=row.role,
        editor=row.editor,
        data_type=row.data_type,
        visible=row.visible,
        required=row.required,
        readonly=row.readonly,
        value_source=row.value_source,
        mapping_entity=row.mapping_entity,
        mapping_attribute=row.mapping_attribute,
        trigger_column=row.trigger_column,
        rule_id=row.rule_id,
        model_input_enabled=row.model_input_enabled,
        ml_name=row.ml_name,
        one_hot_group=row.one_hot_group,
        active=row.active,
        notes=row.notes,
        zero_fill_policy=zero_fill,
    )


def _mapping_requirement(feature, feature_by_key, base) -> MappingRequirementDefinition:  # noqa: ANN001
    existing_by_feature = {
        item.feature_identity: item for item in base.mapping_requirements
    }
    existing = existing_by_feature.get(feature.identity)
    trigger = feature_by_key.get(feature.trigger_column)
    if trigger is None:
        raise ValueError(f"mapping requirement trigger missing: {feature.trigger_column}")
    return MappingRequirementDefinition(
        identity=(
            existing.identity if existing is not None else bootstrap_identity(
                "mapping_requirement", f"feature:{feature.identity}"
            )
        ),
        feature_identity=feature.identity,
        mapping_entity=feature.mapping_entity,
        mapping_attribute=feature.mapping_attribute,
        trigger_feature_identity=trigger.identity,
        rule_id=feature.rule_id,
        data_type=feature.data_type,
        required=feature.required,
    )
