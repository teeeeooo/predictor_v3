"""Whole-candidate validation for the canonical Unified Feature contract."""

from __future__ import annotations

import math

from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.projections import (
    ContractProjections,
    generate_projections,
    topological_derived_identities,
)
from core.data_definition.contract.relations_validation import validate_relations
from core.data_definition.contract.compatibility import current_derived_definitions
from core.data_definition.contract.validation_types import ContractValidationIssue
from core.data_definition.derived_operand_policy import derived_operand_eligibility
from core.ml.feature_catalog import FeatureCatalog
from core.ml.feature_catalog_validation import validate_feature_catalog
from core.predictor_schema.catalog_v2 import (
    MAX_DISPLAY_ORDER,
    MIN_DISPLAY_ORDER,
    PredictSchemaCatalogV2,
    validate_predict_schema_catalog_v2,
)
from core.data_definition.contract.compatibility import current_target_definitions
from core.data_definition.target_registry.defaults import VALIDATED_MODEL_GROUPS

def validate_contract(manifest: UnifiedFeatureManifest) -> tuple[ContractValidationIssue, ...]:
    """Validate all owners together; any issue blocks publication."""
    issues: list[ContractValidationIssue] = []
    identities = _all_identities(manifest)
    _duplicates(issues, "stable_identity_duplicate", identities)
    _duplicates(issues, "predict_key_collision", [
        item.column_key for item in manifest.features
    ])
    _duplicates(issues, "ml_name_collision", [
        item.ml_name
        for item in (*manifest.features, *manifest.derived)
        if item.ml_name
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
    _validate_storage_order(issues, manifest)
    _validate_derived(issues, manifest)
    validate_relations(issues, manifest)
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
    return (
        [item.identity for item in manifest.features]
        + [item.identity for item in manifest.derived]
        + [item.identity for item in manifest.one_hot_groups]
        + [
            item.identity
            for group in manifest.one_hot_groups
            for item in group.categories
        ]
        + [item.identity for item in manifest.targets]
        + [item.identity for item in manifest.model_groups]
        + [item.identity for item in manifest.mapping_requirements]
    )


def _duplicates(issues, code: str, values) -> None:  # noqa: ANN001
    seen = set()
    for value in values:
        if value in seen:
            issues.append(ContractValidationIssue(code, f"duplicate value: {value}"))
        seen.add(value)


def _validate_order(issues, name: str, order, expected: set[str]) -> None:  # noqa: ANN001
    if len(order) != len(set(order)):
        issues.append(ContractValidationIssue(
            f"{name}_order_duplicate",
            f"{name} order contains duplicates",
        ))
    if set(order) != expected:
        issues.append(ContractValidationIssue(
            f"{name}_order_incomplete",
            f"{name} order does not exactly cover its objects",
        ))


def _validate_derived(issues, manifest) -> None:  # noqa: ANN001
    try:
        definitions = current_derived_definitions(manifest)
    except ValueError as exc:
        issues.append(ContractValidationIssue("derived_legacy_reference_invalid", str(exc)))
        return
    derived_by_id = {item.identity: item for item in definitions}
    target_feature_ids = {item.feature_identity for item in manifest.targets}
    dependencies: dict[str, tuple[str, str]] = {}
    for item in definitions:
        if item.operation != "safe_ratio":
            issues.append(ContractValidationIssue(
                "derived_operation_invalid", f"{item.ml_name}: {item.operation}"
            ))
        if item.zero_denominator_policy != "constant":
            issues.append(ContractValidationIssue(
                "derived_zero_policy_invalid", item.ml_name
            ))
        if (
            isinstance(item.zero_value, bool)
            or not isinstance(item.zero_value, (int, float))
            or not math.isfinite(float(item.zero_value))
        ):
            issues.append(ContractValidationIssue(
                "derived_zero_value_invalid", f"{item.ml_name}: finite numeric required"
            ))
        refs = (item.numerator_identity, item.denominator_identity)
        dependencies[item.identity] = refs
        if item.identity in refs:
            issues.append(ContractValidationIssue(
                "derived_self_reference", item.ml_name
            ))
        for ref in refs:
            eligibility = derived_operand_eligibility(
                manifest.features,
                definitions,
                ref,
                target_feature_identities=target_feature_ids,
                consumer_identity=item.identity,
                consumer_active=item.active,
            )
            if not eligibility.eligible:
                issues.append(ContractValidationIssue(
                    eligibility.code,
                    f"{item.ml_name}: {eligibility.reason} ({ref})",
                ))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            issues.append(ContractValidationIssue(
                "derived_dependency_cycle", f"cycle at {derived_by_id[identity].ml_name}"
            ))
            return
        if identity in visited:
            return
        visiting.add(identity)
        for ref in dependencies.get(identity, ()):
            if ref in derived_by_id:
                visit(ref)
        visiting.remove(identity)
        visited.add(identity)

    for identity in dependencies:
        visit(identity)
    try:
        topological = topological_derived_identities(manifest)
    except (KeyError, ValueError):
        return
    if topological != manifest.ordering.derived:
        issues.append(ContractValidationIssue(
            "derived_order_not_topological",
            "derived canonical order does not satisfy its dependency DAG",
        ))


def _validate_storage_order(issues, manifest) -> None:  # noqa: ANN001
    _duplicates(issues, "predict_display_order_duplicate", [
        item.display_order for item in manifest.features
    ])
    for item in manifest.features:
        if (
            type(item.display_order) is not int
            or not MIN_DISPLAY_ORDER <= item.display_order <= MAX_DISPLAY_ORDER
        ):
            issues.append(ContractValidationIssue(
                "predict_display_order_invalid",
                f"{item.identity}: display_order must be between "
                f"{MIN_DISPLAY_ORDER} and {MAX_DISPLAY_ORDER}",
            ))
    if tuple(item.identity for item in manifest.features) != manifest.ordering.predict:
        issues.append(ContractValidationIssue(
            "predict_storage_order_mismatch",
            "Feature storage order does not match canonical Predict order",
        ))
    display_order = tuple(
        item.identity for item in sorted(
            manifest.features,
            key=lambda item: (item.display_order, item.identity),
        )
    )
    if display_order != manifest.ordering.predict:
        issues.append(ContractValidationIssue(
            "predict_display_order_mismatch",
            "Feature display_order contradicts canonical Predict order",
        ))
    if tuple(item.identity for item in manifest.derived) != manifest.ordering.derived:
        issues.append(ContractValidationIssue(
            "derived_storage_order_mismatch",
            "Derived storage order does not match canonical Derived order",
        ))
    if tuple(item.identity for item in manifest.targets) != manifest.ordering.targets:
        issues.append(ContractValidationIssue(
            "target_storage_order_mismatch",
            "Target storage order does not match canonical target order",
        ))


def _projection_issues(manifest, projections) -> list[ContractValidationIssue]:  # noqa: ANN001
    issues = []
    if projections.generation_id != manifest.generation.generation_id:
        issues.append(ContractValidationIssue(
            "projection_generation_mismatch",
            projections.generation_id,
        ))
    feature_by_id = {item.identity: item for item in manifest.features}
    ml_by_id = {item.identity: item for item in (*manifest.features, *manifest.derived)}
    target_by_id = {item.identity: item for item in manifest.targets}
    if tuple(item.column_key for item in projections.predict) != tuple(
        feature_by_id[identity].column_key for identity in manifest.ordering.predict
    ):
        issues.append(ContractValidationIssue(
            "predict_projection_order_mismatch", "Predict projection order is not canonical"
        ))
    if tuple(item.ml_name for item in projections.ml) != tuple(
        ml_by_id[identity].ml_name for identity in manifest.ordering.ml
    ):
        issues.append(ContractValidationIssue(
            "ml_projection_order_mismatch", "ML projection order is not canonical"
        ))
    if tuple(item.identity for item in projections.derived) != tuple(
        identity
        for identity in manifest.ordering.derived
        if next(item for item in manifest.derived if item.identity == identity).active
    ):
        issues.append(ContractValidationIssue(
            "derived_projection_order_mismatch", "Derived projection order is not canonical"
        ))
    projected_targets = tuple(
        name
        for _group, payload in projections.target_registry
        for name in payload["targets"]
    )
    targets = current_target_definitions(manifest)
    if manifest.contract_version.endswith(".v4"):
        group_by_key = {item.registry_key: item.identity for item in manifest.model_groups}
        canonical_targets = tuple(
            target.ml_name
            for supported in VALIDATED_MODEL_GROUPS
            for target in sorted(
                (item for item in targets if item.active and item.model_group_identity == group_by_key[supported.registry_key]),
                key=lambda item: (item.registry_order, item.identity),
            )
        )
    else:
        canonical_targets = tuple(
            target_by_id[identity].ml_name for identity in manifest.ordering.targets
            if target_by_id[identity].active
        )
    if projected_targets != canonical_targets:
        issues.append(ContractValidationIssue(
            "target_projection_order_mismatch",
            "Target registry projection does not preserve registry iteration order",
        ))
    for message in validate_predict_schema_catalog_v2(
        PredictSchemaCatalogV2(rows=projections.predict)
    ):
        issues.append(ContractValidationIssue("predict_projection_invalid", message))
    for message in validate_feature_catalog(FeatureCatalog(rows=projections.ml)):
        issues.append(ContractValidationIssue("ml_projection_invalid", message))
    return issues
