"""Cross-owner One-hot, Target, and Mapping relation validation."""

from __future__ import annotations

from core.data_definition.contract.compatibility import current_one_hot_definitions
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
        if (
            selector is None
            or selector.active != group.active
            or selector.role != "input"
            or selector.editor != "dropdown"
            or selector.data_type != "string"
            or selector.readonly
            or not selector.visible
            or selector.value_source != "one_hot"
            or bool(selector.ml_name)
            or selector.one_hot_group != group.group_key
        ):
            issues.append(ContractValidationIssue(
                "one_hot_selector_invalid", group.group_key
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


def _validate_targets(issues, manifest) -> None:  # noqa: ANN001
    features = {item.identity: item for item in manifest.features}
    groups = {item.identity: item for item in manifest.model_groups}
    targets = {item.identity: item for item in manifest.targets}
    _duplicates(issues, "target_presentation_order_duplicate", [
        item.presentation_order for item in manifest.targets
    ])
    presentation = tuple(
        item.identity for item in sorted(
            manifest.targets,
            key=lambda item: (item.presentation_order, item.identity),
        )
    )
    if presentation != manifest.ordering.targets:
        issues.append(ContractValidationIssue(
            "target_presentation_order_mismatch",
            "target presentation_order does not match canonical target ordering",
        ))
    memberships: dict[str, list[str]] = {}
    for group in manifest.model_groups:
        _duplicates(issues, "model_group_target_duplicate", group.target_identities)
        group_target_names = []
        for identity in group.target_identities:
            target = targets.get(identity)
            if target is None:
                issues.append(ContractValidationIssue(
                    "model_group_target_orphan", f"{group.registry_key}: {identity}"
                ))
                continue
            memberships.setdefault(identity, []).append(group.identity)
            group_target_names.append(target.ml_name)
        rule_targets = [name for name, _policy, _values in group.target_rules]
        _duplicates(issues, "model_group_target_rule_duplicate", rule_targets)
        if set(rule_targets) != set(group_target_names):
            issues.append(ContractValidationIssue(
                "model_group_target_rule_incomplete", group.registry_key
            ))
    for target in manifest.targets:
        feature = features.get(target.feature_identity)
        group = groups.get(target.model_group_identity)
        if (
            feature is None
            or feature.role != "result"
            or feature.ml_name != target.ml_name
        ):
            issues.append(ContractValidationIssue(
                "target_feature_invalid", target.ml_name
            ))
        if (
            group is None
            or memberships.get(target.identity) != [target.model_group_identity]
        ):
            issues.append(ContractValidationIssue(
                "target_model_group_invalid", target.ml_name
            ))


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
