"""Side-effect-free command and Save impact projection."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.command_types import (
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
)
from core.data_definition.contract import (
    UnifiedFeatureManifest,
    candidate_manifest_from_draft,
    scoped_fingerprints,
    validate_contract,
)
from core.data_definition.save_contract import DataDefinitionSavePlan
from core.data_definition.dependency_policy import feature_dependencies
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.derived.commands import derived_downstream_identities
from core.data_definition.contract.compatibility import current_derived_definitions


@dataclass(frozen=True)
class FeatureImpactEvidence:
    feature_identity: str
    feature_display_name: str
    reference_identity: str
    dependency_owner: str
    dependency_code: str
    predict_key_change: tuple[str, str] | None = None
    ml_name_change: tuple[str, str] | None = None
    automatically_updated: bool = False
    blocked: bool = False
    resolution: str = ""
    message: str = ""


@dataclass(frozen=True)
class FeatureImpactPreview:
    action: str
    command_accepted: bool
    predict_projection_changed: bool
    ordered_ml_projection_changed: bool
    mapping_requirements_changed: bool
    model_compatibility_changed: bool
    requires_retraining: bool
    save_allowed: bool
    affected_identities: tuple[tuple[str, str], ...]
    evidence: tuple[FeatureImpactEvidence, ...]
    blockers: tuple[DataDefinitionCommandIssue, ...]
    candidate_generation_id: str
    candidate_fingerprint: str
    derived_semantics_changed: bool
    derived_semantics_fingerprint: str
    execution_order_before: tuple[str, ...]
    execution_order_after: tuple[str, ...]
    downstream_identities: tuple[str, ...]
    summary: str


def build_feature_impact_preview(
    base: UnifiedFeatureManifest | None,
    result: DataDefinitionCommandResult,
    save_plan: DataDefinitionSavePlan,
    *,
    source_draft: DataDefinitionDraft | None = None,
) -> FeatureImpactPreview:
    """Compare the exact hypothetical command draft with its canonical base."""
    if not result.accepted:
        return FeatureImpactPreview(
            result.action,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            result.affected_identities,
            _impact_evidence(source_draft, result),
            result.issues,
            "",
            "",
            False,
            "",
            (),
            (),
            (),
            result.message,
        )
    predict_changed = False
    ml_changed = False
    mapping_changed = False
    compatibility_changed = save_plan.requires_retrain
    validation_issues: tuple[DataDefinitionCommandIssue, ...] = ()
    candidate_generation_id = ""
    candidate_fingerprint = ""
    derived_semantics_changed = False
    derived_semantics_fingerprint = ""
    execution_before: tuple[str, ...] = ()
    execution_after: tuple[str, ...] = ()
    if base is not None:
        try:
            candidate = candidate_manifest_from_draft(result.draft, base)
            candidate_generation_id = candidate.generation.generation_id
            contract_issues = validate_contract(candidate)
            if contract_issues:
                validation_issues = tuple(
                    DataDefinitionCommandIssue(
                        item.code,
                        "contract",
                        item.message,
                        "Resolve the affected canonical dependency before Save.",
                    )
                    for item in contract_issues
                )
            before = scoped_fingerprints(base)
            after = scoped_fingerprints(candidate)
            candidate_fingerprint = after.combined
            predict_changed = before.predict != after.predict
            ml_changed = before.ordered_ml != after.ordered_ml
            mapping_changed = before.mapping_requirements != after.mapping_requirements
            compatibility_changed = before.model_compatibility != after.model_compatibility
            derived_semantics_changed = before.derived_semantics != after.derived_semantics
            derived_semantics_fingerprint = after.derived_semantics
            execution_before = tuple(
                item.ml_name for item in current_derived_definitions(base) if item.active
            )
            execution_after = tuple(
                item.ml_name for item in current_derived_definitions(candidate) if item.active
            )
        except (KeyError, ValueError) as exc:
            validation_issues = (DataDefinitionCommandIssue(
                "canonical_candidate_invalid",
                "contract",
                str(exc),
                "Resolve the affected canonical dependency before Save.",
            ),)
    blockers = (*result.issues, *validation_issues, *_save_blockers(save_plan, compatibility_changed))
    save_allowed = not blockers
    retraining = bool(compatibility_changed or save_plan.requires_retrain)
    changed = []
    if predict_changed:
        changed.append("Predict projection")
    if ml_changed:
        changed.append("ordered ML projection")
    if mapping_changed:
        changed.append("Mapping requirements")
    if derived_semantics_changed:
        changed.append("Derived semantics")
    summary = ", ".join(changed) if changed else "presentation-only or no projection change"
    if retraining:
        summary += "; retraining or model migration required"
    if blockers:
        summary += "; Save blocked"
    return FeatureImpactPreview(
        result.action,
        True,
        predict_changed,
        ml_changed,
        mapping_changed,
        compatibility_changed,
        retraining,
        save_allowed,
        result.affected_identities or ((result.identity,) if result.identity else ()),
        _impact_evidence(source_draft, result),
        tuple(blockers),
        candidate_generation_id,
        candidate_fingerprint,
        derived_semantics_changed,
        derived_semantics_fingerprint,
        execution_before,
        execution_after,
        _downstream(source_draft, result),
        summary,
    )


def _impact_evidence(
    source_draft: DataDefinitionDraft | None,
    result: DataDefinitionCommandResult,
) -> tuple[FeatureImpactEvidence, ...]:
    if source_draft is None:
        return ()
    identity = result.identity or (
        result.affected_identities[0] if result.affected_identities else None
    )
    source = next((row for row in source_draft.rows if row.identity == identity), None)
    current = next((row for row in result.draft.rows if row.identity == identity), None)
    feature = current or source
    if feature is None:
        return ()
    key_change = None
    ml_change = None
    if source is not None and current is not None:
        if source.column_key != current.column_key:
            key_change = (source.column_key, current.column_key)
        if source.ml_name != current.ml_name:
            ml_change = (source.ml_name, current.ml_name)
    blocked_codes = {item.code for item in result.issues}
    evidence = [FeatureImpactEvidence(
        feature.stable_identity or feature.identity[1],
        feature.label or feature.column_key or feature.ml_name,
        feature.stable_identity or feature.identity[1],
        "Data Definition",
        "feature_transition",
        key_change,
        ml_change,
        message=f"{result.action} affects this Feature.",
    )]
    if feature.source_kind == "derived_policy":
        owners = {
            row.stable_identity: row for row in source_draft.rows if row.stable_identity
        }
        for role, reference in (
            ("numerator", feature.numerator_identity),
            ("denominator", feature.denominator_identity),
        ):
            operand = owners.get(reference)
            evidence.append(FeatureImpactEvidence(
                feature.stable_identity,
                feature.ml_name,
                reference,
                "Derived operand",
                role,
                message=(
                    f"{role.title()} uses "
                    f"{(operand.label or operand.ml_name) if operand else reference}."
                ),
            ))
        return tuple(evidence)
    if source is None:
        return tuple(evidence)
    affected = set(result.affected_identities)
    for dependency in feature_dependencies(source_draft, source):
        evidence.append(FeatureImpactEvidence(
            source.stable_identity or source.identity[1],
            source.label or source.column_key or source.ml_name,
            dependency.affected_identity,
            dependency.owner,
            dependency.code,
            key_change,
            ml_change,
            dependency.code == "feature_trigger_reference"
            and ("schema_row", dependency.affected_identity) in affected,
            dependency.code in blocked_codes,
            dependency.resolution,
            dependency.message,
        ))
    return tuple(evidence)


def _downstream(
    draft: DataDefinitionDraft | None,
    result: DataDefinitionCommandResult,
) -> tuple[str, ...]:
    if draft is None:
        return ()
    identity = result.identity or (
        result.affected_identities[0] if result.affected_identities else None
    )
    row = next((item for item in draft.rows if item.identity == identity), None)
    if row is None or row.source_kind != "derived_policy":
        return ()
    return derived_downstream_identities(draft, row.stable_identity)


def _save_blockers(
    plan: DataDefinitionSavePlan,
    compatibility_changed: bool,
) -> tuple[DataDefinitionCommandIssue, ...]:
    ignored = {"candidate_feature_projection_mismatch"} if not compatibility_changed else set()
    blockers = tuple(
        DataDefinitionCommandIssue(
            item.code,
            item.field_name or item.target,
            item.message,
            "Resolve this Save guard or complete the required migration before publication.",
        )
        for item in plan.blocked_reasons
        if item.severity == "error" and item.code not in ignored
    )
    if compatibility_changed and not any(
        item.code in {
            "ml_compatibility_projection_write_required",
            "model_compatibility_migration_required",
        }
        for item in blockers
    ):
        blockers = (*blockers, DataDefinitionCommandIssue(
            "model_compatibility_migration_required",
            "model_artifact",
            "Ordered ML/model compatibility changed; publication remains blocked.",
            "Complete retraining or consumer migration before publication.",
        ))
    return blockers
