"""Whole-candidate validation for the canonical Unified Feature contract."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.projections import ContractProjections, generate_projections
from core.ml.feature_catalog import FeatureCatalog
from core.ml.feature_catalog_validation import validate_feature_catalog
from core.predictor_schema.catalog_v2 import PredictSchemaCatalogV2, validate_predict_schema_catalog_v2


@dataclass(frozen=True)
class ContractValidationIssue:
    code: str
    message: str


def validate_contract(manifest: UnifiedFeatureManifest) -> tuple[ContractValidationIssue, ...]:
    """Validate all owners together; any issue blocks publication."""
    issues: list[ContractValidationIssue] = []
    identities = _all_identities(manifest)
    _duplicates(issues, "stable_identity_duplicate", identities)
    _duplicates(issues, "predict_key_collision", [item.column_key for item in manifest.features if item.active])
    _duplicates(issues, "ml_name_collision", [
        item.ml_name for item in (*manifest.features, *manifest.derived) if item.active and item.ml_name
    ])
    feature_ids = {item.identity for item in manifest.features}
    derived_ids = {item.identity for item in manifest.derived}
    target_ids = {item.identity for item in manifest.targets}
    _validate_order(issues, "predict", manifest.ordering.predict, feature_ids)
    ml_expected = {
        item.identity for item in manifest.features
        if item.active and item.ml_name and (
            item.model_input_enabled or item.role == "result"
        )
    } | {item.identity for item in manifest.derived if item.active}
    _validate_order(issues, "ml", manifest.ordering.ml, ml_expected)
    _validate_order(issues, "derived", manifest.ordering.derived, derived_ids)
    _validate_order(issues, "targets", manifest.ordering.targets, target_ids)
    _validate_derived(issues, manifest)
    _validate_one_hot(issues, manifest)
    _validate_targets(issues, manifest)
    _validate_mapping(issues, manifest)
    if issues:
        return tuple(issues)
    try:
        projections = generate_projections(manifest)
    except (KeyError, ValueError) as exc:
        return (ContractValidationIssue("projection_generation_failed", str(exc)),)
    issues.extend(_projection_issues(manifest, projections))
    return tuple(issues)


def require_valid_contract(manifest: UnifiedFeatureManifest) -> ContractProjections:
    issues = validate_contract(manifest)
    if issues:
        raise ValueError("; ".join(f"{item.code}: {item.message}" for item in issues))
    return generate_projections(manifest)


def _all_identities(manifest: UnifiedFeatureManifest) -> list[str]:
    return [item.identity for item in manifest.features] + [item.identity for item in manifest.derived] + [
        item.identity for item in manifest.one_hot_groups
    ] + [item.identity for group in manifest.one_hot_groups for item in group.categories] + [
        item.identity for item in manifest.targets
    ] + [item.identity for item in manifest.model_groups] + [
        item.identity for item in manifest.mapping_requirements
    ]


def _duplicates(issues, code: str, values) -> None:  # noqa: ANN001
    seen = set()
    for value in values:
        if value in seen:
            issues.append(ContractValidationIssue(code, f"duplicate value: {value}"))
        seen.add(value)


def _validate_order(issues, name: str, order, expected: set[str]) -> None:  # noqa: ANN001
    if len(order) != len(set(order)):
        issues.append(ContractValidationIssue(f"{name}_order_duplicate", f"{name} order contains duplicates"))
    if set(order) != expected:
        issues.append(ContractValidationIssue(f"{name}_order_incomplete", f"{name} order does not exactly cover its objects"))


def _validate_derived(issues, manifest) -> None:  # noqa: ANN001
    known = {item.ml_name for item in (*manifest.features, *manifest.derived) if item.ml_name}
    dependencies = {
        item.ml_name: (item.numerator_ml_name, item.denominator_ml_name)
        for item in manifest.derived if item.active
    }
    for name, refs in dependencies.items():
        for ref in refs:
            if ref not in known:
                issues.append(ContractValidationIssue("derived_dependency_missing", f"{name} references {ref}"))
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            issues.append(ContractValidationIssue("derived_dependency_cycle", f"cycle at {name}"))
            return
        if name in visited:
            return
        visiting.add(name)
        for ref in dependencies.get(name, ()):
            if ref in dependencies:
                visit(ref)
        visiting.remove(name)
        visited.add(name)

    for name in dependencies:
        visit(name)


def _validate_one_hot(issues, manifest) -> None:  # noqa: ANN001
    feature_by_id = {item.identity: item for item in manifest.features}
    emitted = {item.ml_name: item for item in manifest.features if item.role == "one_hot_feature"}
    for group in manifest.one_hot_groups:
        selector = feature_by_id.get(group.selector_feature_identity)
        if selector is None or selector.value_source != "one_hot" or selector.one_hot_group != group.group_key:
            issues.append(ContractValidationIssue("one_hot_selector_invalid", group.group_key))
        names = [item.emitted_ml_name for item in group.categories if item.active]
        _duplicates(issues, "one_hot_category_emitted_duplicate", names)
        for name in names:
            row = emitted.get(name)
            if row is None or row.one_hot_group != group.group_key:
                issues.append(ContractValidationIssue("one_hot_emitted_invalid", f"{group.group_key}: {name}"))


def _validate_targets(issues, manifest) -> None:  # noqa: ANN001
    features = {item.identity: item for item in manifest.features}
    groups = {item.identity: item for item in manifest.model_groups}
    for target in manifest.targets:
        feature = features.get(target.feature_identity)
        group = groups.get(target.model_group_identity)
        if feature is None or feature.role != "result" or feature.ml_name != target.ml_name:
            issues.append(ContractValidationIssue("target_feature_invalid", target.ml_name))
        if group is None or target.identity not in group.target_identities:
            issues.append(ContractValidationIssue("target_model_group_invalid", target.ml_name))


def _validate_mapping(issues, manifest) -> None:  # noqa: ANN001
    features = {item.identity: item for item in manifest.features}
    declarations: dict[tuple[str, str], tuple[str, bool]] = {}
    for requirement in manifest.mapping_requirements:
        feature = features.get(requirement.feature_identity)
        trigger = features.get(requirement.trigger_feature_identity)
        if feature is None or trigger is None or feature.value_source != "mapping_lookup":
            issues.append(ContractValidationIssue("mapping_requirement_relation_invalid", requirement.identity))
            continue
        key = (requirement.mapping_entity, requirement.mapping_attribute)
        shape = (requirement.data_type, requirement.required)
        if key in declarations and declarations[key] != shape:
            issues.append(ContractValidationIssue("mapping_requirement_type_conflict", f"{key}"))
        declarations[key] = shape


def _projection_issues(manifest, projections) -> list[ContractValidationIssue]:  # noqa: ANN001
    issues = []
    if projections.generation_id != manifest.generation.generation_id:
        issues.append(ContractValidationIssue("projection_generation_mismatch", projections.generation_id))
    for message in validate_predict_schema_catalog_v2(PredictSchemaCatalogV2(rows=projections.predict)):
        issues.append(ContractValidationIssue("predict_projection_invalid", message))
    for message in validate_feature_catalog(FeatureCatalog(rows=projections.ml)):
        issues.append(ContractValidationIssue("ml_projection_invalid", message))
    return issues
