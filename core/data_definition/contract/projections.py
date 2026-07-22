"""Generated compatibility and runtime projections for one manifest generation."""

from __future__ import annotations

import csv
import heapq
import io
from dataclasses import dataclass, replace

from core.data_definition.contract.model import (
    DerivedDefinition,
    LegacyDerivedDefinition,
    LegacyOneHotGroupDefinition,
    OneHotGroupDefinition,
    UnifiedFeatureManifest,
)
from core.data_definition.contract.compatibility import current_derived_definitions
from core.data_definition.one_hot.runtime import (
    OneHotRuntimeSnapshot,
    one_hot_runtime_snapshot,
)
from core.data_definition.model import MappingRequirement, ProjectedFeatureRow
from core.ml.feature_catalog import REQUIRED_HEADERS as ML_HEADERS
from core.predictor_schema.catalog_v2 import PredictSchemaV2Row, REQUIRED_HEADERS


@dataclass(frozen=True)
class ContractProjections:
    generation_id: str
    predict: tuple[PredictSchemaV2Row, ...]
    ml: tuple[ProjectedFeatureRow, ...]
    derived: tuple[DerivedDefinition | LegacyDerivedDefinition, ...]
    one_hot: tuple[OneHotGroupDefinition | LegacyOneHotGroupDefinition, ...]
    one_hot_runtime: OneHotRuntimeSnapshot
    target_registry: tuple[tuple[str, dict[str, object]], ...]
    mapping_requirements: tuple[MappingRequirement, ...]


def generate_projections(manifest: UnifiedFeatureManifest) -> ContractProjections:
    """Generate every consumer projection without reading another owner."""
    features = {item.identity: item for item in manifest.features}
    ordered_predict = tuple(features[identity] for identity in manifest.ordering.predict)
    predict = tuple(
        PredictSchemaV2Row(
            line_number=index,
            display_order=item.display_order,
            column_key=item.column_key,
            label=item.label,
            role=item.role,
            editor=item.editor,
            data_type=item.data_type,
            visible=item.visible,
            required=item.required,
            readonly=item.readonly,
            value_source=item.value_source,
            mapping_entity=item.mapping_entity,
            mapping_attribute=item.mapping_attribute,
            trigger_column=item.trigger_column,
            rule_id=item.rule_id,
            model_input_enabled=item.model_input_enabled,
            ml_name=item.ml_name,
            one_hot_group=item.one_hot_group,
            active=item.active,
            notes=item.notes,
        )
        for index, item in enumerate(ordered_predict, 2)
    )
    ml_owners = {item.identity: item for item in (*manifest.features, *manifest.derived)}
    ml = tuple(
        _ml_row(ml_owners[identity], index)
        for index, identity in enumerate(manifest.ordering.ml, 1)
    )
    targets_by_id = {item.identity: item for item in manifest.targets}
    target_position = {
        identity: index for index, identity in enumerate(manifest.ordering.targets)
    }
    ordered_groups = sorted(
        manifest.model_groups,
        key=lambda group: min(
            (target_position[identity] for identity in group.target_identities),
            default=len(target_position),
        ),
    )
    registry = tuple(
        (
            group.registry_key,
            {
                "name": group.name,
                "targets": [
                    targets_by_id[item].ml_name
                    for item in sorted(
                        group.target_identities,
                        key=target_position.__getitem__,
                    )
                ],
                "use_rfe": group.use_rfe,
                "target_rules": {
                    name: {policy: list(values)} for name, policy, values in group.target_rules
                },
            },
        )
        for group in ordered_groups
    )
    feature_by_id = {item.identity: item for item in manifest.features}
    requirements = tuple(
        MappingRequirement(
            column_key=feature_by_id[item.feature_identity].column_key,
            ml_name=feature_by_id[item.feature_identity].ml_name,
            mapping_entity=item.mapping_entity,
            mapping_attribute=item.mapping_attribute,
            trigger_column=feature_by_id[item.trigger_feature_identity].column_key,
            rule_id=item.rule_id,
            data_type=item.data_type,
            required=item.required,
            model_input_enabled=feature_by_id[item.feature_identity].model_input_enabled,
        )
        for item in manifest.mapping_requirements
    )
    return ContractProjections(
        generation_id=manifest.generation.generation_id,
        predict=predict,
        ml=ml,
        derived=tuple(
            item for item in _topological_derived(manifest) if item.active
        ),
        one_hot=tuple(
            replace(
                group,
                categories=tuple(sorted(group.categories, key=lambda item: item.order)),
            )
            for group in manifest.one_hot_groups
        ),
        one_hot_runtime=one_hot_runtime_snapshot(manifest),
        target_registry=registry,
        mapping_requirements=requirements,
    )


def topological_derived_identities(
    manifest: UnifiedFeatureManifest,
) -> tuple[str, ...]:
    """Return deterministic dependency order using canonical order as tie-break."""
    return tuple(item.identity for item in _topological_derived(manifest))


def _topological_derived(
    manifest: UnifiedFeatureManifest,
) -> tuple[DerivedDefinition | LegacyDerivedDefinition, ...]:
    current = current_derived_definitions(manifest)
    derived_by_id = {item.identity: item for item in current}
    priority = {
        identity: index for index, identity in enumerate(manifest.ordering.derived)
    }
    dependencies: dict[str, set[str]] = {}
    dependents: dict[str, set[str]] = {identity: set() for identity in derived_by_id}
    for identity, item in derived_by_id.items():
        refs = {
            ref
            for ref in (item.numerator_identity, item.denominator_identity)
            if ref in derived_by_id
        }
        dependencies[identity] = refs
        for ref in refs:
            dependents[ref].add(identity)
    ready = [
        (priority.get(identity, len(priority)), identity)
        for identity, refs in dependencies.items()
        if not refs
    ]
    heapq.heapify(ready)
    ordered: list[DerivedDefinition] = []
    while ready:
        _position, identity = heapq.heappop(ready)
        ordered.append(derived_by_id[identity])
        for dependent in sorted(dependents[identity]):
            dependencies[dependent].discard(identity)
            if not dependencies[dependent]:
                heapq.heappush(
                    ready,
                    (priority.get(dependent, len(priority)), dependent),
                )
    if len(ordered) != len(derived_by_id):
        raise ValueError("derived dependency graph contains a cycle")
    if manifest.contract_version.endswith(".v1"):
        legacy_by_id = {item.identity: item for item in manifest.derived}
        return tuple(legacy_by_id[item.identity] for item in ordered)
    return tuple(ordered)


def predict_csv_text(projection: ContractProjections) -> str:
    return _csv_text(REQUIRED_HEADERS, (_predict_payload(row) for row in projection.predict))


def ml_csv_text(projection: ContractProjections) -> str:
    return _csv_text(ML_HEADERS, (_ml_payload(row) for row in projection.ml))


def _ml_row(owner, index: int) -> ProjectedFeatureRow:  # noqa: ANN001
    if isinstance(owner, (DerivedDefinition, LegacyDerivedDefinition)):
        return ProjectedFeatureRow(
            order=index * 10,
            ml_name=owner.ml_name,
            role="derived",
            zero_fill_policy=owner.zero_fill_policy,
            active=owner.active,
        )
    role = "one_hot" if owner.role == "one_hot_feature" else owner.role
    return ProjectedFeatureRow(
        order=index * 10,
        ml_name=owner.ml_name,
        role=role,
        ui_key="" if role == "one_hot" else owner.column_key,
        label=owner.label,
        source=owner.trigger_column if role == "auto" else "",
        mapping_key=owner.mapping_attribute if role == "auto" else "",
        one_hot_group=owner.one_hot_group if role == "one_hot" else "",
        zero_fill_policy=owner.zero_fill_policy,
        active=owner.active,
    )


def _predict_payload(row: PredictSchemaV2Row) -> dict[str, str]:
    return {
        field: _csv_value(getattr(row, field))
        for field in REQUIRED_HEADERS
    }


def _ml_payload(row: ProjectedFeatureRow) -> dict[str, str]:
    return {
        "order": str(row.order),
        "ml_name": row.ml_name,
        "role": row.role,
        "ui_key": row.ui_key,
        "label": row.label,
        "source": row.source,
        "mapping_key": row.mapping_key,
        "one_hot_group": row.one_hot_group,
        "zero_fill_policy": row.zero_fill_policy,
        "active": _csv_value(row.active),
        "notes": "",
    }


def _csv_text(headers, rows) -> str:  # noqa: ANN001
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _csv_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
