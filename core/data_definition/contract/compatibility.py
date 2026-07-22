"""Versioned Derived compatibility decoding without mutating history."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition.contract.model import (
    DerivedDefinition,
    LegacyDerivedDefinition,
    LegacyOneHotCategoryDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    LegacyModelGroupDefinition,
    LegacyTargetDefinition,
    ModelGroupDefinition,
    TargetDefinition,
    UnifiedFeatureManifest,
)

CURRENT_CONTRACT_VERSION = "unified_feature_contract.v4"
TARGET_LEGACY_CONTRACT_VERSION = "unified_feature_contract.v3"
ONE_HOT_LEGACY_CONTRACT_VERSION = "unified_feature_contract.v2"
LEGACY_CONTRACT_VERSION = "unified_feature_contract.v1"
SUPPORTED_CONTRACT_VERSIONS = frozenset({
    LEGACY_CONTRACT_VERSION,
    ONE_HOT_LEGACY_CONTRACT_VERSION,
    TARGET_LEGACY_CONTRACT_VERSION,
    CURRENT_CONTRACT_VERSION,
})


def current_derived_definitions(
    manifest: UnifiedFeatureManifest,
) -> tuple[DerivedDefinition, ...]:
    """Return identity operands, rejecting missing or ambiguous legacy names."""
    if manifest.contract_version in {
        CURRENT_CONTRACT_VERSION,
        TARGET_LEGACY_CONTRACT_VERSION,
        ONE_HOT_LEGACY_CONTRACT_VERSION,
    }:
        return tuple(_require_current(item) for item in manifest.derived)
    if manifest.contract_version != LEGACY_CONTRACT_VERSION:
        raise ValueError(f"unsupported contract_version: {manifest.contract_version!r}")
    by_name: dict[str, list[str]] = {}
    for item in (*manifest.features, *manifest.derived):
        if item.ml_name:
            by_name.setdefault(item.ml_name, []).append(item.identity)
    resolved: list[DerivedDefinition] = []
    for item in manifest.derived:
        if not isinstance(item, LegacyDerivedDefinition):
            raise ValueError("v1 manifest contains a non-legacy Derived DTO")
        numerator = _resolve_legacy_name(item, "numerator", item.numerator_ml_name, by_name)
        denominator = _resolve_legacy_name(
            item, "denominator", item.denominator_ml_name, by_name
        )
        resolved.append(DerivedDefinition(
            identity=item.identity,
            ml_name=item.ml_name,
            operation=item.operation,
            numerator_identity=numerator,
            denominator_identity=denominator,
            zero_denominator_policy="constant",
            zero_value=float(item.zero_value),
            zero_fill_policy=item.zero_fill_policy,
            active=item.active,
        ))
    return tuple(resolved)


def migrate_manifest(manifest: UnifiedFeatureManifest) -> UnifiedFeatureManifest:
    """Return an in-memory v4 candidate; never writes the source generation."""
    if manifest.contract_version == CURRENT_CONTRACT_VERSION:
        current_derived_definitions(manifest)
        current_one_hot_definitions(manifest)
        current_target_definitions(manifest)
        return manifest
    return replace(
        manifest,
        contract_version=CURRENT_CONTRACT_VERSION,
        derived=current_derived_definitions(manifest),
        one_hot_groups=current_one_hot_definitions(manifest),
        targets=current_target_definitions(manifest),
        model_groups=current_model_group_definitions(manifest),
    )


def current_one_hot_definitions(
    manifest: UnifiedFeatureManifest,
) -> tuple[OneHotGroupDefinition, ...]:
    """Resolve legacy emitted names to exactly one stable Feature identity."""
    if manifest.contract_version in {CURRENT_CONTRACT_VERSION, TARGET_LEGACY_CONTRACT_VERSION}:
        groups = []
        for group in manifest.one_hot_groups:
            categories = tuple(_require_current_category(item) for item in group.categories)
            groups.append(replace(group, categories=categories))
        return tuple(groups)
    if manifest.contract_version not in {
        LEGACY_CONTRACT_VERSION,
        ONE_HOT_LEGACY_CONTRACT_VERSION,
    }:
        raise ValueError(f"unsupported contract_version: {manifest.contract_version!r}")
    by_name: dict[str, list[str]] = {}
    feature_by_id = {item.identity: item for item in manifest.features}
    for item in manifest.features:
        if item.ml_name:
            by_name.setdefault(item.ml_name, []).append(item.identity)
    groups = []
    for group in manifest.one_hot_groups:
        selector = feature_by_id.get(group.selector_feature_identity)
        source_binding = getattr(group, "source_binding", "") or (
            selector.mapping_entity if selector is not None else ""
        )
        categories = []
        for item in group.categories:
            if isinstance(item, OneHotCategoryDefinition):
                categories.append(item)
                continue
            if not isinstance(item, LegacyOneHotCategoryDefinition):
                raise ValueError("legacy manifest contains an unsupported One-hot category DTO")
            matches = by_name.get(item.emitted_ml_name, ())
            if len(matches) != 1:
                reason = "missing" if not matches else "ambiguous"
                raise ValueError(
                    f"legacy One-hot category {group.group_key}/{item.source_value!r} "
                    f"emitted Feature {item.emitted_ml_name!r} is {reason}; "
                    "resolve it to exactly one Feature identity"
                )
            categories.append(OneHotCategoryDefinition(
                identity=item.identity,
                source_value=item.source_value,
                emitted_feature_identity=matches[0],
                emitted_ml_name=item.emitted_ml_name,
                order=item.order,
                active=item.active,
            ))
        groups.append(OneHotGroupDefinition(
            identity=group.identity,
            group_key=group.group_key,
            selector_feature_identity=group.selector_feature_identity,
            category_source=group.category_source,
            unknown_policy=group.unknown_policy,
            missing_policy=group.missing_policy,
            categories=tuple(categories),
            source_binding=source_binding,
            active=getattr(group, "active", True),
        ))
    return tuple(groups)


def operand_ml_name(
    manifest: UnifiedFeatureManifest,
    identity: str,
) -> str:
    owners = [
        item.ml_name
        for item in (*manifest.features, *current_derived_definitions(manifest))
        if item.identity == identity
    ]
    if len(owners) != 1 or not owners[0]:
        raise ValueError(f"Derived operand identity must resolve exactly once: {identity}")
    return owners[0]


def current_model_group_definitions(
    manifest: UnifiedFeatureManifest,
) -> tuple[ModelGroupDefinition, ...]:
    """Normalize historical duplicated group membership to read-only metadata."""
    if all(isinstance(item, ModelGroupDefinition) for item in manifest.model_groups):
        groups = tuple(manifest.model_groups)
        if not all(isinstance(item, ModelGroupDefinition) for item in groups):
            raise ValueError("v4 manifest contains a legacy Model Group DTO")
        return groups
    groups = []
    for item in manifest.model_groups:
        if not isinstance(item, LegacyModelGroupDefinition):
            raise ValueError("legacy manifest contains a non-legacy Model Group DTO")
        groups.append(ModelGroupDefinition(
            identity=item.identity,
            registry_key=item.registry_key,
            name=item.name,
            use_rfe=item.use_rfe,
        ))
    return tuple(groups)


def current_target_definitions(
    manifest: UnifiedFeatureManifest,
) -> tuple[TargetDefinition, ...]:
    """Resolve legacy ML-name policy references to stable input-owner identities."""
    if all(isinstance(item, TargetDefinition) for item in manifest.targets):
        targets = tuple(manifest.targets)
        if not all(isinstance(item, TargetDefinition) for item in targets):
            raise ValueError("v4 manifest contains a legacy Target DTO")
        return targets

    owner_by_name: dict[str, list[str]] = {}
    result_names = {
        item.ml_name for item in manifest.features if item.role == "result" and item.ml_name
    }
    for item in (*manifest.features, *current_derived_definitions(manifest)):
        if item.ml_name and getattr(item, "active", True) and getattr(item, "role", "") != "result":
            owner_by_name.setdefault(item.ml_name, []).append(item.identity)
    # FeatureDefinition carries role; DerivedDefinition does not and is therefore eligible.
    for item in manifest.features:
        if item.role == "result" and item.ml_name:
            owner_by_name.pop(item.ml_name, None)

    rule_by_target: dict[str, tuple[str, tuple[str, ...]]] = {}
    registry_order_by_target: dict[str, int] = {}
    for group in manifest.model_groups:
        if not isinstance(group, LegacyModelGroupDefinition):
            raise ValueError("legacy manifest contains a non-legacy Model Group DTO")
        for name, mode, values in group.target_rules:
            if name in rule_by_target:
                raise ValueError(f"legacy Target policy is ambiguous: {name}")
            rule_by_target[name] = (mode, values)
        for index, identity in enumerate(group.target_identities, 1):
            registry_order_by_target[identity] = index

    resolved = []
    for item in manifest.targets:
        if not isinstance(item, LegacyTargetDefinition):
            raise ValueError("legacy manifest contains a non-legacy Target DTO")
        try:
            mode, names = rule_by_target[item.ml_name]
        except KeyError as exc:
            raise ValueError(f"legacy Target policy is missing: {item.ml_name}") from exc
        identities = []
        noops = []
        for name in names:
            matches = owner_by_name.get(name, ())
            if len(matches) == 1:
                identities.append(matches[0])
            elif not matches and name in result_names and mode == "exclude":
                noops.append(next(
                    feature.identity for feature in manifest.features
                    if feature.role == "result" and feature.ml_name == name
                ))
            else:
                reason = "missing" if not matches else "ambiguous"
                raise ValueError(
                    f"legacy Target {item.ml_name} policy reference {name!r} is {reason}; "
                    "resolve it to exactly one active training input owner"
                )
        resolved.append(TargetDefinition(
            identity=item.identity,
            feature_identity=item.feature_identity,
            ml_name=item.ml_name,
            model_group_identity=item.model_group_identity,
            presentation_order=item.presentation_order,
            policy_mode=mode,
            policy_owner_identities=tuple(identities),
            registry_order=registry_order_by_target.get(item.identity, item.presentation_order),
            active=item.active,
            legacy_noop_result_identities=tuple(noops),
        ))
    return tuple(resolved)


def _resolve_legacy_name(item, role: str, name: str, by_name) -> str:  # noqa: ANN001
    matches = by_name.get(name, ())
    if len(matches) != 1:
        reason = "missing" if not matches else "ambiguous"
        raise ValueError(
            f"legacy Derived {item.ml_name} {role} {name!r} is {reason}; "
            "resolve it to exactly one Feature or Derived identity"
        )
    return matches[0]


def _require_current(item) -> DerivedDefinition:  # noqa: ANN001
    if not isinstance(item, DerivedDefinition):
        raise ValueError("v2 manifest contains a legacy Derived DTO")
    return item


def _require_current_category(item) -> OneHotCategoryDefinition:  # noqa: ANN001
    if not isinstance(item, OneHotCategoryDefinition):
        raise ValueError("v3 manifest contains a legacy One-hot category DTO")
    return item
