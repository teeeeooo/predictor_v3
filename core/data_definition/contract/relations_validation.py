"""Cross-owner One-hot, Target, and Mapping relation validation."""

from __future__ import annotations

from core.data_definition.contract.compatibility import (
    current_model_group_definitions,
    current_one_hot_definitions,
    current_target_definitions,
)
from core.data_definition.contract.model import LegacyModelGroupDefinition
from core.data_definition.target_registry.defaults import VALIDATED_GROUP_BY_KEY
from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.validation_types import ContractValidationIssue

_ALLOWED_CATEGORY_SOURCES = frozenset({"static", "mapping_backed", "external"})
_ALLOWED_UNKNOWN_POLICIES = frozenset({"warn_all_zero"})
_ALLOWED_MISSING_POLICIES = frozenset({"all_zero"})


def validate_relations(
    issues: list[ContractValidationIssue],
    manifest: UnifiedFeatureManifest,
) -> None:
    """Append cross-contract relation issues without generating projections."""
    _validate_one_hot(issues, manifest)
    _validate_targets(issues, manifest)
    _validate_mapping(issues, manifest)


def _validate_one_hot(issues, manifest) -> None:  # noqa: ANN001
    feature_by_id = {item.identity: item for item in manifest.features}
    try:
        groups = current_one_hot_definitions(manifest)
    except ValueError as exc:
        issues.append(ContractValidationIssue("one_hot_legacy_relation_invalid", str(exc)))
        return
    emitted = {
        item.identity: item
        for item in manifest.features
        if item.role == "one_hot_feature"
    }
    _duplicates(issues, "one_hot_group_key_duplicate", [
        group.group_key for group in groups
    ])
    _duplicates(issues, "one_hot_selector_duplicate", [
        group.selector_feature_identity for group in groups if group.active
    ])
    emitted_memberships: dict[str, int] = {}
    for group in groups:
        selector = feature_by_id.get(group.selector_feature_identity)
        restore = group.selector_restore
        if restore is not None and (
            not restore.active
            or restore.role != "input"
            or restore.data_type != "string"
            or bool(restore.ml_name)
            or restore.value_source == "one_hot"
            or bool(restore.one_hot_group)
        ):
            issues.append(ContractValidationIssue(
                "one_hot_selector_restore_invalid", group.group_key
            ))
        if restore is not None and (
            selector is None or restore.identity != group.selector_feature_identity
        ):
            issues.append(ContractValidationIssue(
                "one_hot_selector_restore_missing", group.group_key
            ))
        elif restore is not None and not group.active:
            if not _selector_matches_restore(selector, restore):
                issues.append(ContractValidationIssue(
                    "one_hot_inactive_selector_mutated", group.group_key
                ))
        elif not _valid_runtime_selector(selector, group):
            issues.append(ContractValidationIssue(
                "one_hot_selector_invalid", group.group_key
            ))
        if (
            restore is None
            and selector is not None
            and selector.rule_id == f"one_hot:{group.identity}"
        ):
            issues.append(ContractValidationIssue(
                "one_hot_selector_restore_missing", group.group_key
            ))
        if group.category_source not in _ALLOWED_CATEGORY_SOURCES:
            issues.append(ContractValidationIssue(
                "one_hot_category_source_invalid", group.group_key
            ))
        if group.category_source in {"mapping_backed", "external"} and not group.source_binding:
            issues.append(ContractValidationIssue(
                "one_hot_source_binding_invalid", group.group_key
            ))
        if group.category_source == "static" and group.source_binding:
            issues.append(ContractValidationIssue(
                "one_hot_source_binding_invalid", group.group_key
            ))
        if (
            (group.active or restore is None)
            and group.category_source == "mapping_backed"
            and selector is not None
            and selector.mapping_entity != group.source_binding
        ):
            issues.append(ContractValidationIssue(
                "one_hot_selector_mapping_binding_mismatch", group.group_key
            ))
        if group.unknown_policy not in _ALLOWED_UNKNOWN_POLICIES:
            issues.append(ContractValidationIssue(
                "one_hot_unknown_policy_invalid", group.group_key
            ))
        if group.missing_policy not in _ALLOWED_MISSING_POLICIES:
            issues.append(ContractValidationIssue(
                "one_hot_missing_policy_invalid", group.group_key
            ))
        active_categories = [item for item in group.categories if item.active]
        if group.active and not active_categories:
            issues.append(ContractValidationIssue(
                "one_hot_active_category_required", group.group_key
            ))
        _duplicates(issues, "one_hot_category_emitted_duplicate", [
            item.emitted_feature_identity for item in group.categories
        ])
        _duplicates(issues, "one_hot_category_emitted_duplicate", [
            item.emitted_ml_name for item in group.categories
        ])
        _duplicates(issues, "one_hot_category_source_duplicate", [
            item.source_value for item in group.categories
        ])
        _duplicates(issues, "one_hot_category_order_duplicate", [
            item.order for item in group.categories
        ])
        if tuple(group.categories) != tuple(
            sorted(group.categories, key=lambda item: item.order)
        ):
            issues.append(ContractValidationIssue(
                "one_hot_category_storage_order_mismatch", group.group_key
            ))
        if tuple(item.order for item in group.categories) != tuple(
            range(1, len(group.categories) + 1)
        ):
            issues.append(ContractValidationIssue(
                "one_hot_category_order_invalid", group.group_key
            ))
        group_feature_ids = {
            item.emitted_feature_identity for item in group.categories
        }
        projected_group_order = tuple(
            identity for identity in manifest.ordering.ml
            if identity in group_feature_ids
        )
        expected_group_order = tuple(
            item.emitted_feature_identity
            for item in sorted(group.categories, key=lambda category: category.order)
            if group.active and item.active
        )
        if projected_group_order != expected_group_order:
            issues.append(ContractValidationIssue(
                "one_hot_ml_order_mismatch", group.group_key
            ))
        if group.category_source == "external":
            _duplicates(issues, "one_hot_provider_category_duplicate", [
                item.provider_category_identity for item in group.categories
                if item.provider_category_identity
            ])
        for category in group.categories:
            if (
                not category.emitted_ml_name
                or not category.source_value
                or not category.emitted_feature_identity
                or category.order < 1
            ):
                issues.append(ContractValidationIssue(
                    "one_hot_category_invalid",
                    f"{group.group_key}: {category.identity}",
                ))
            if group.category_source == "external" and not category.provider_category_identity:
                issues.append(ContractValidationIssue(
                    "one_hot_provider_category_invalid",
                    f"{group.group_key}: {category.identity}",
                ))
            row = emitted.get(category.emitted_feature_identity)
            expected_active = group.active and category.active
            if (
                row is None
                or row.role != "one_hot_feature"
                or row.editor != "readonly"
                or row.data_type != "number"
                or row.visible
                or not row.readonly
                or row.value_source != "one_hot"
                or not row.model_input_enabled
                or row.one_hot_group != group.group_key
                or row.active != expected_active
                or row.ml_name != category.emitted_ml_name
            ):
                issues.append(ContractValidationIssue(
                    "one_hot_emitted_invalid",
                    f"{group.group_key}: {category.emitted_feature_identity}",
                ))
            emitted_memberships[category.emitted_feature_identity] = (
                emitted_memberships.get(category.emitted_feature_identity, 0) + 1
            )
    for identity in emitted:
        if emitted_memberships.get(identity, 0) != 1:
            issues.append(ContractValidationIssue(
                "one_hot_emitted_membership_invalid",
                f"{identity} must belong to exactly one category",
            ))


def _valid_runtime_selector(selector, group) -> bool:  # noqa: ANN001
    return bool(
        selector is not None
        and selector.active == group.active
        and selector.role == "input"
        and selector.editor == "dropdown"
        and selector.data_type == "string"
        and not selector.readonly
        and selector.visible
        and selector.value_source == "one_hot"
        and not selector.ml_name
        and selector.one_hot_group == group.group_key
    )


def _selector_matches_restore(selector, restore) -> bool:  # noqa: ANN001
    if selector is None:
        return False
    return all(
        getattr(selector, field) == getattr(restore, field)
        for field in (
            "identity",
            "display_order",
            "column_key",
            "label",
            "role",
            "editor",
            "data_type",
            "visible",
            "required",
            "readonly",
            "value_source",
            "mapping_entity",
            "mapping_attribute",
            "trigger_column",
            "rule_id",
            "model_input_enabled",
            "ml_name",
            "one_hot_group",
            "active",
            "notes",
            "zero_fill_policy",
        )
    )


def _validate_targets(issues, manifest) -> None:  # noqa: ANN001
    features = {item.identity: item for item in manifest.features}
    try:
        definitions = current_target_definitions(manifest)
        group_definitions = current_model_group_definitions(manifest)
    except ValueError as exc:
        issues.append(ContractValidationIssue("target_legacy_relation_invalid", str(exc)))
        return
    groups = {item.identity: item for item in group_definitions}
    targets = {item.identity: item for item in definitions}
    _duplicates(issues, "target_identity_duplicate", [item.identity for item in definitions])
    _duplicates(issues, "target_result_feature_duplicate", [item.feature_identity for item in definitions])
    _duplicates(issues, "target_active_ml_name_duplicate", [
        item.ml_name for item in definitions if item.active
    ])
    _duplicates(issues, "target_presentation_order_duplicate", [
        item.presentation_order for item in definitions
    ])
    presentation = tuple(
        item.identity for item in sorted(
            definitions,
            key=lambda item: (item.presentation_order, item.identity),
        )
    )
    if presentation != manifest.ordering.targets:
        issues.append(ContractValidationIssue(
            "target_presentation_order_mismatch",
            "target presentation_order does not match canonical target ordering",
        ))
    _duplicates(issues, "model_group_registry_key_duplicate", [
        item.registry_key for item in group_definitions
    ])
    if set(item.registry_key for item in group_definitions) != set(VALIDATED_GROUP_BY_KEY):
        issues.append(ContractValidationIssue(
            "model_group_catalog_invalid", "exactly the three validated model groups are required"
        ))
    for group in group_definitions:
        supported = VALIDATED_GROUP_BY_KEY.get(group.registry_key)
        if supported is None or group.name != supported.name or group.use_rfe != supported.use_rfe:
            issues.append(ContractValidationIssue(
                "model_group_metadata_mutation", group.registry_key
            ))
        members = [item.registry_order for item in definitions if item.model_group_identity == group.identity]
        _duplicates(issues, "target_registry_order_duplicate", members)
        if sorted(members) != list(range(1, len(members) + 1)):
            issues.append(ContractValidationIssue("target_registry_order_invalid", group.registry_key))
    eligible_owners = {
        item.identity: item
        for item in (*manifest.features, *manifest.derived)
        if item.active and item.ml_name and getattr(item, "role", "") != "result"
    }
    result_feature_ids = {
        item.identity for item in manifest.features if item.role == "result" and item.ml_name
    }
    target_feature_ids = {item.feature_identity for item in definitions}
    for orphan in sorted(result_feature_ids - target_feature_ids):
        issues.append(ContractValidationIssue("target_result_orphan", orphan))
    for target in definitions:
        feature = features.get(target.feature_identity)
        group = groups.get(target.model_group_identity)
        if (
            feature is None
            or feature.role != "result"
            or feature.editor != "readonly"
            or feature.data_type != "number"
            or not feature.readonly
            or feature.value_source != "result"
            or feature.model_input_enabled
            or feature.ml_name != target.ml_name
            or feature.active != target.active
        ):
            issues.append(ContractValidationIssue(
                "target_feature_invalid", target.ml_name
            ))
        if (
            group is None
        ):
            issues.append(ContractValidationIssue(
                "target_model_group_invalid", target.ml_name
            ))
        if target.policy_mode not in {"allowed", "exclude"}:
            issues.append(ContractValidationIssue("target_policy_mode_invalid", target.ml_name))
        _duplicates(issues, "target_policy_owner_duplicate", target.policy_owner_identities)
        for identity in target.policy_owner_identities:
            if identity in result_feature_ids or identity not in eligible_owners:
                issues.append(ContractValidationIssue(
                    "target_policy_owner_invalid", f"{target.ml_name}: {identity}"
                ))
        if target.policy_mode == "allowed" and not target.policy_owner_identities:
            issues.append(ContractValidationIssue("target_policy_allowed_empty", target.ml_name))
        available_ids = set(eligible_owners)
        resolved_ids = set(target.policy_owner_identities)
        policy_result = (
            available_ids & resolved_ids
            if target.policy_mode == "allowed"
            else available_ids - resolved_ids
        )
        if target.policy_mode in {"allowed", "exclude"} and not policy_result:
            issues.append(ContractValidationIssue("target_policy_result_empty", target.ml_name))
        if target.legacy_noop_result_identities and target.policy_mode != "exclude":
            issues.append(ContractValidationIssue("target_policy_legacy_noop_invalid", target.ml_name))
        if any(identity not in result_feature_ids for identity in target.legacy_noop_result_identities):
            issues.append(ContractValidationIssue("target_policy_legacy_noop_invalid", target.ml_name))

    # Historical manifests must also prove their duplicated relation was internally exact.
    for group in manifest.model_groups:
        if not isinstance(group, LegacyModelGroupDefinition):
            continue
        _duplicates(issues, "model_group_target_duplicate", group.target_identities)
        associated = tuple(
            item.identity for item in definitions if item.model_group_identity == group.identity
        )
        if set(group.target_identities) != set(associated):
            issues.append(ContractValidationIssue("model_group_target_projection_mismatch", group.registry_key))


def _validate_mapping(issues, manifest) -> None:  # noqa: ANN001
    features = {item.identity: item for item in manifest.features}
    feature_by_key = {item.column_key: item for item in manifest.features}
    declarations: dict[tuple[str, str], tuple[str, bool]] = {}
    requirements_by_feature: dict[str, int] = {}
    relation_keys = []
    for requirement in manifest.mapping_requirements:
        feature = features.get(requirement.feature_identity)
        trigger = features.get(requirement.trigger_feature_identity)
        if (
            feature is None
            or trigger is None
            or feature.value_source != "mapping_lookup"
        ):
            issues.append(ContractValidationIssue(
                "mapping_requirement_relation_invalid",
                requirement.identity,
            ))
            continue
        requirements_by_feature[requirement.feature_identity] = (
            requirements_by_feature.get(requirement.feature_identity, 0) + 1
        )
        relation_keys.append((
            requirement.mapping_entity,
            requirement.mapping_attribute,
            requirement.rule_id,
            requirement.trigger_feature_identity,
        ))
        expected_trigger = feature_by_key.get(feature.trigger_column)
        if (
            requirement.mapping_entity != feature.mapping_entity
            or requirement.mapping_attribute != feature.mapping_attribute
            or requirement.rule_id != feature.rule_id
            or requirement.data_type != feature.data_type
            or requirement.required != feature.required
            or expected_trigger is None
            or requirement.trigger_feature_identity != expected_trigger.identity
        ):
            issues.append(ContractValidationIssue(
                "mapping_requirement_feature_mismatch", requirement.identity
            ))
        key = (requirement.mapping_entity, requirement.mapping_attribute)
        shape = (requirement.data_type, requirement.required)
        if key in declarations and declarations[key] != shape:
            issues.append(ContractValidationIssue(
                "mapping_requirement_type_conflict", f"{key}"
            ))
        declarations[key] = shape
    _duplicates(issues, "mapping_requirement_relation_duplicate", relation_keys)
    for feature in manifest.features:
        count = requirements_by_feature.get(feature.identity, 0)
        if feature.value_source == "mapping_lookup" and count != 1:
            issues.append(ContractValidationIssue(
                "mapping_requirement_coverage_invalid",
                f"{feature.column_key} requires exactly one mapping requirement",
            ))


def _duplicates(issues, code: str, values) -> None:  # noqa: ANN001
    seen = set()
    for value in values:
        if value in seen:
            issues.append(ContractValidationIssue(code, f"duplicate value: {value}"))
        seen.add(value)
