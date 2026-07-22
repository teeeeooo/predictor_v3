"""Dependency evidence and blockers for basic Feature mutation commands."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.compatibility import (
    current_derived_definitions,
    current_target_definitions,
)
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.predictor_schema.columns import FIXED_INDEX_COLUMN_KEYS


@dataclass(frozen=True)
class FeatureDependency:
    code: str
    owner: str
    affected_identity: str
    message: str
    blocks_rename: bool = False
    blocks_remove: bool = False
    blocks_disable: bool = False
    resolution: str = ""


def feature_dependencies(
    draft: DataDefinitionDraft,
    row: DataDefinitionDraftRow,
) -> tuple[FeatureDependency, ...]:
    """Return current canonical references without reading external values."""
    manifest = draft.base_manifest
    if not isinstance(manifest, UnifiedFeatureManifest):
        return ()
    dependencies: list[FeatureDependency] = []
    dependencies.extend(_derived_dependencies(manifest, row))
    dependencies.extend(_one_hot_dependencies(manifest, row))
    dependencies.extend(_mapping_dependencies(manifest, row))
    dependencies.extend(_target_dependencies(manifest, row))
    dependencies.extend(_model_dependencies(manifest, row))
    dependencies.extend(_fixed_consumer_dependencies(manifest, row))
    dependencies.extend(_draft_reference_dependencies(draft, row))
    return _unique_dependencies(dependencies)


def is_supported_basic_feature(row: DataDefinitionDraftRow) -> bool:
    """Return whether 4C+4D owns authoring for this Feature shape."""
    if row.source_kind != "schema_row":
        return False
    if row.role in {"result", "status", "one_hot_feature"}:
        return False
    if row.value_source in {"formula", "result", "status", "one_hot", "rule_options"}:
        return False
    return row.role in {"input", "auto", "helper", "hidden"}


def _derived_dependencies(manifest, row):  # noqa: ANN001
    return [
        FeatureDependency(
            "derived_expression_reference",
            "Derived",
            item.identity,
            f"Derived Feature '{item.ml_name}' references this stable Feature identity.",
            False,
            True,
            item.active,
            "Remove, disable, or retarget the dependent Derived definition first.",
        )
        for item in current_derived_definitions(manifest)
        if row.stable_identity in {item.numerator_identity, item.denominator_identity}
    ]


def _one_hot_dependencies(manifest, row):  # noqa: ANN001
    dependencies = []
    for group in manifest.one_hot_groups:
        if group.selector_feature_identity == row.stable_identity:
            dependencies.append(FeatureDependency(
                "one_hot_selector_reference",
                "One-hot",
                group.identity,
                f"One-hot group '{group.group_key}' uses this Feature as its selector.",
                True,
                True,
                True,
                "Manage the selector/group together in Phase 4F.",
            ))
        for category in group.categories:
            if row.ml_name and category.emitted_ml_name == row.ml_name:
                dependencies.append(FeatureDependency(
                    "one_hot_emitted_reference",
                    "One-hot",
                    category.identity,
                    f"One-hot category '{category.source_value}' emits this ML name.",
                    True,
                    True,
                    True,
                    "Manage emitted Features with their group in Phase 4F.",
                ))
    return dependencies


def _mapping_dependencies(manifest, row):  # noqa: ANN001
    dependencies = []
    for requirement in manifest.mapping_requirements:
        if requirement.feature_identity == row.stable_identity:
            dependencies.append(FeatureDependency(
                "mapping_requirement_owner",
                "Data Mapping requirement",
                requirement.identity,
                "This Feature owns a canonical Mapping requirement.",
                False,
                False,
                False,
                "The requirement follows stable identity; concrete mapping values are unchanged.",
            ))
        if requirement.trigger_feature_identity == row.stable_identity:
            dependencies.append(FeatureDependency(
                "mapping_trigger_reference",
                "Data Mapping requirement",
                requirement.identity,
                "Another Mapping requirement uses this Feature as its trigger.",
                False,
                True,
                True,
                "Remove or retarget the dependent Mapping-backed Feature first.",
            ))
    return dependencies


def _target_dependencies(manifest, row):  # noqa: ANN001
    return [
        FeatureDependency(
            "target_feature_reference",
            "Result/Target",
            item.identity,
            f"Target '{item.ml_name}' references this Feature.",
            True,
            True,
            True,
            "Migrate the Target and registry contract in Phase 4G.",
        )
        for item in manifest.targets
        if item.feature_identity == row.stable_identity or (
            row.ml_name and item.ml_name == row.ml_name
        )
    ]


def _model_dependencies(manifest, row):  # noqa: ANN001
    if not row.ml_name:
        return []
    dependencies = []
    if row.stable_identity in manifest.ordering.ml:
        dependencies.append(FeatureDependency(
            "ordered_ml_projection",
            "ML contract",
            row.stable_identity,
            f"'{row.ml_name}' is part of the ordered training/inference projection.",
            False,
            True,
            False,
            "Keep the current name or complete an explicit model migration/retraining workflow.",
        ))
    for target in current_target_definitions(manifest):
        if row.stable_identity in target.policy_owner_identities:
            dependencies.append(FeatureDependency(
                "target_policy_owner_reference",
                "Target policy",
                target.identity,
                f"Target '{target.ml_name}' policy references '{row.ml_name}' by stable identity.",
                False,
                True,
                True,
                "Remove or retarget the Target policy reference first.",
            ))
    return dependencies


def _fixed_consumer_dependencies(_manifest, row):  # noqa: ANN001
    if row.column_key not in FIXED_INDEX_COLUMN_KEYS:
        return []
    return [FeatureDependency(
        "protected_predict_consumer",
        "core.predictor_schema.columns",
        row.stable_identity or row.identity[1],
        f"Predict import-time indexes require fixed column key '{row.column_key}'.",
        True,
        True,
        False,
        "Migrate the fixed-index Predict consumer to a generation provider before changing this key.",
    )]


def _draft_reference_dependencies(draft, row):  # noqa: ANN001
    return [
        FeatureDependency(
            "feature_trigger_reference",
            "Data Definition",
            item.stable_identity,
            f"Feature '{item.label}' references Predict key '{row.column_key}' as its trigger.",
            False,
            True,
            True,
            "Remove or retarget the dependent Feature first; Rename updates this reference atomically.",
        )
        for item in draft.rows
        if item.identity != row.identity and item.trigger_column == row.column_key
    ]


def _unique_dependencies(items):  # noqa: ANN001
    seen = set()
    result = []
    for item in items:
        key = (item.code, item.affected_identity)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return tuple(result)
