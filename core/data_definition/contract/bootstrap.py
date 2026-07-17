"""Deterministic bootstrap from the repository's current distributed contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.data_definition.contract.identity import bootstrap_identity
from core.data_definition.contract.model import (
    ContractGeneration,
    DerivedDefinition,
    FeatureDefinition,
    MappingRequirementDefinition,
    ModelGroupDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    OrderingContract,
    TargetDefinition,
    UnifiedFeatureManifest,
)
from core.data_definition.derived_policy import load_current_derived_feature_policy
from core.data_definition.projection import MODE_MISSING_ALLOWED
from core.ml.feature_catalog import load_feature_catalog
from core.ml.registry import MODEL_REGISTRY
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2

_DERIVED_OPERANDS = {
    "Cool_Capa_per_EER": ("Cooling Capa", "Comp EER"),
    "Cool_Capa_per_CondArea": ("Cooling Capa", "Cond Area"),
    "Cool_Capa_per_EvapArea": ("Cooling Capa", "Evap Area"),
    "Cool_Capa_per_cc": ("Cooling Capa", "Comp cc"),
    "Heat_Capa_per_EER": ("Heating Capa", "Comp EER"),
    "Heat_Capa_per_CondArea": ("Heating Capa", "Cond Area"),
    "Heat_Capa_per_EvapArea": ("Heating Capa", "Evap Area"),
    "Heat_Capa_per_cc": ("Heating Capa", "Comp cc"),
}


def bootstrap_manifest(
    *,
    schema_path: str | Path | None = None,
    feature_catalog_path: str | Path | None = None,
) -> UnifiedFeatureManifest:
    """Build the canonical contract or fail on unsupported legacy divergence."""
    schema = load_predict_schema_catalog_v2(schema_path)
    catalog = load_feature_catalog(feature_catalog_path)
    features = tuple(_feature(row) for row in schema.rows)
    feature_by_key = {item.column_key: item for item in features}
    feature_by_ml = {item.ml_name: item for item in features if item.ml_name}
    derived = _derived_definitions()
    one_hot_groups = _one_hot_definitions(features)
    targets, model_groups = _target_definitions(features)
    requirements = _mapping_requirements(features, feature_by_key)
    ml_order = _ml_order(catalog.rows, feature_by_ml, derived)
    ordering = OrderingContract(
        predict=tuple(item.identity for item in sorted(features, key=lambda item: item.display_order)),
        ml=ml_order,
        derived=tuple(item.identity for item in derived),
        targets=tuple(item.identity for item in targets),
    )
    semantic_seed = json.dumps(
        {
            "features": [item.identity for item in features],
            "ml": ml_order,
            "derived": [item.identity for item in derived],
            "targets": [item.identity for item in targets],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    generation_id = "bootstrap-" + hashlib.sha256(semantic_seed.encode()).hexdigest()[:20]
    return UnifiedFeatureManifest(
        contract_version="unified_feature_contract.v1",
        generation=ContractGeneration(generation_id=generation_id),
        preprocessing_version="v1.0",
        features=features,
        derived=derived,
        one_hot_groups=one_hot_groups,
        targets=targets,
        model_groups=model_groups,
        mapping_requirements=requirements,
        ordering=ordering,
    )


def _feature(row) -> FeatureDefinition:  # noqa: ANN001
    return FeatureDefinition(
        identity=bootstrap_identity("feature", row.column_key),
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
        zero_fill_policy=("mode_missing_allowed" if row.ml_name in MODE_MISSING_ALLOWED else "disallow"),
    )


def _derived_definitions() -> tuple[DerivedDefinition, ...]:
    rows = load_current_derived_feature_policy()
    unknown = [row.ml_name for row in rows if row.ml_name not in _DERIVED_OPERANDS]
    if unknown:
        raise ValueError(f"unsupported derived definitions: {', '.join(unknown)}")
    return tuple(
        DerivedDefinition(
            identity=bootstrap_identity("derived", row.ml_name),
            ml_name=row.ml_name,
            operation="safe_ratio",
            numerator_ml_name=_DERIVED_OPERANDS[row.ml_name][0],
            denominator_ml_name=_DERIVED_OPERANDS[row.ml_name][1],
            zero_fill_policy=row.zero_fill_policy,
            active=row.active,
        )
        for row in rows
    )


def _one_hot_definitions(features: tuple[FeatureDefinition, ...]) -> tuple[OneHotGroupDefinition, ...]:
    selectors = {
        item.one_hot_group: item for item in features
        if item.active and item.role == "input" and item.value_source == "one_hot"
    }
    emitted: dict[str, list[FeatureDefinition]] = {}
    for item in features:
        if item.active and item.role == "one_hot_feature":
            emitted.setdefault(item.one_hot_group, []).append(item)
    if set(selectors) != set(emitted):
        raise ValueError("one-hot selectors and emitted groups do not match")
    return tuple(
        OneHotGroupDefinition(
            identity=bootstrap_identity("onehot_group", group_key),
            group_key=group_key,
            selector_feature_identity=selector.identity,
            category_source="mapping_backed",
            unknown_policy="warn_all_zero",
            missing_policy="all_zero",
            categories=tuple(
                OneHotCategoryDefinition(
                    identity=bootstrap_identity("onehot_category", f"{group_key}:{row.ml_name}"),
                    source_value=row.ml_name,
                    emitted_ml_name=row.ml_name,
                    order=index,
                )
                for index, row in enumerate(sorted(emitted[group_key], key=lambda item: item.display_order), 1)
            ),
        )
        for group_key, selector in sorted(selectors.items(), key=lambda item: item[1].display_order)
    )


def _target_definitions(features: tuple[FeatureDefinition, ...]) -> tuple[tuple[TargetDefinition, ...], tuple[ModelGroupDefinition, ...]]:
    result_by_ml = {item.ml_name: item for item in features if item.role == "result" and item.ml_name}
    target_to_group = {
        target: key for key, config in MODEL_REGISTRY.items() for target in config["targets"]
    }
    if set(target_to_group) != set(result_by_ml):
        raise ValueError("schema result targets and MODEL_REGISTRY targets do not match")
    targets = tuple(
        TargetDefinition(
            identity=bootstrap_identity("target", feature.ml_name),
            feature_identity=feature.identity,
            ml_name=feature.ml_name,
            model_group_identity=bootstrap_identity("model_group", target_to_group[feature.ml_name]),
            presentation_order=index,
        )
        for index, feature in enumerate(sorted(result_by_ml.values(), key=lambda item: item.display_order), 1)
    )
    target_id = {item.ml_name: item.identity for item in targets}
    groups = tuple(
        ModelGroupDefinition(
            identity=bootstrap_identity("model_group", key),
            registry_key=key,
            name=config["name"],
            target_identities=tuple(target_id[name] for name in config["targets"]),
            use_rfe=bool(config["use_rfe"]),
            target_rules=tuple(
                (name, tuple(rule.get("allowed", rule.get("exclude", ()))))
                for name, rule in config["target_rules"].items()
            ),
        )
        for key, config in MODEL_REGISTRY.items()
    )
    return targets, groups


def _mapping_requirements(features, feature_by_key) -> tuple[MappingRequirementDefinition, ...]:  # noqa: ANN001
    rows = []
    for item in features:
        if item.value_source != "mapping_lookup":
            continue
        trigger = feature_by_key.get(item.trigger_column)
        if trigger is None:
            raise ValueError(f"mapping requirement trigger missing: {item.trigger_column}")
        rows.append(MappingRequirementDefinition(
            identity=bootstrap_identity("mapping_requirement", item.column_key),
            feature_identity=item.identity,
            mapping_entity=item.mapping_entity,
            mapping_attribute=item.mapping_attribute,
            trigger_feature_identity=trigger.identity,
            rule_id=item.rule_id,
            data_type=item.data_type,
            required=item.required,
        ))
    return tuple(rows)


def _ml_order(catalog_rows, feature_by_ml, derived) -> tuple[str, ...]:  # noqa: ANN001
    derived_by_ml = {item.ml_name: item for item in derived}
    identities = []
    for row in catalog_rows:
        owner = derived_by_ml.get(row.ml_name) or feature_by_ml.get(row.ml_name)
        if owner is None:
            raise ValueError(f"ML catalog row has no canonical owner: {row.ml_name}")
        identities.append(owner.identity)
    if len(identities) != len(set(identities)):
        raise ValueError("ML catalog contains duplicate canonical owners")
    return tuple(identities)
