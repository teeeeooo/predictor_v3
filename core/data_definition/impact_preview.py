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
    blockers: tuple[DataDefinitionCommandIssue, ...]
    summary: str


def build_feature_impact_preview(
    base: UnifiedFeatureManifest | None,
    result: DataDefinitionCommandResult,
    save_plan: DataDefinitionSavePlan,
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
            result.issues,
            result.message,
        )
    predict_changed = False
    ml_changed = False
    mapping_changed = False
    compatibility_changed = save_plan.requires_retrain
    validation_issues: tuple[DataDefinitionCommandIssue, ...] = ()
    if base is not None:
        try:
            candidate = candidate_manifest_from_draft(result.draft, base)
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
            predict_changed = before.predict != after.predict
            ml_changed = before.ordered_ml != after.ordered_ml
            mapping_changed = before.mapping_requirements != after.mapping_requirements
            compatibility_changed = before.model_compatibility != after.model_compatibility
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
        tuple(blockers),
        summary,
    )


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
