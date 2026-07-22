"""Canonical compatibility and One-hot source impact enrichment."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionRestartImpact,
    DataDefinitionSaveBlocker,
    DataDefinitionSavePlan,
)
from core.data_definition.contract import candidate_manifest_from_draft, scoped_fingerprints
from core.data_definition.one_hot.drift import one_hot_drift_evidence
from core.data_definition.one_hot.model import VocabularySnapshot


class DataDefinitionSaveImpactService:
    """Enrich legacy save evidence using canonical generation semantics."""

    def __init__(
        self,
        *,
        canonical_persistence: bool,
        vocabulary_snapshots: tuple[VocabularySnapshot, ...],
    ) -> None:
        self._canonical_persistence = canonical_persistence
        self._vocabulary_snapshots = tuple(vocabulary_snapshots)

    def apply(
        self,
        draft: DataDefinitionDraft,
        plan: DataDefinitionSavePlan,
    ) -> DataDefinitionSavePlan:
        return self._source_impact(draft, self._canonical_impact(draft, plan))

    def _canonical_impact(
        self,
        draft: DataDefinitionDraft,
        plan: DataDefinitionSavePlan,
    ) -> DataDefinitionSavePlan:
        if not self._canonical_persistence or not draft.is_changed or draft.base_manifest is None:
            return plan
        try:
            candidate = candidate_manifest_from_draft(draft, draft.base_manifest)
            changed = (
                scoped_fingerprints(draft.base_manifest).model_compatibility
                != scoped_fingerprints(candidate).model_compatibility
            )
        except (KeyError, ValueError):
            return plan
        if not changed:
            blockers = plan.blocked_reasons
            blocked = any(
                item.severity == "error" and item.target in {"schema_csv", ""}
                for item in blockers
                if item.code not in {
                    "candidate_feature_projection_mismatch",
                    "ml_compatibility_projection_write_required",
                }
            )
            return replace(
                plan,
                can_save_schema=draft.is_changed and not blocked,
                blocked_reasons=blockers,
            )
        blockers = plan.blocked_reasons
        if not any(item.code == "model_compatibility_migration_required" for item in blockers):
            blockers = (*blockers, DataDefinitionSaveBlocker(
                "model_compatibility_migration_required",
                "error",
                "Ordered ML/model compatibility changed; complete retraining or consumer migration before publication.",
                "model_artifact",
            ))
        return replace(
            plan,
            can_save_schema=False,
            requires_retrain=True,
            blocked_reasons=blockers,
            restart_impact=DataDefinitionRestartImpact(
                plan.requires_restart,
                True,
                "Schema restart and model retrain are required before activation."
                if plan.requires_restart
                else "Model retraining or consumer migration is required before publication.",
            ),
        )

    def _source_impact(
        self,
        draft: DataDefinitionDraft,
        plan: DataDefinitionSavePlan,
    ) -> DataDefinitionSavePlan:
        evidence = one_hot_drift_evidence(
            tuple(draft.one_hot_groups), self._vocabulary_snapshots
        )
        additions = tuple(DataDefinitionSaveBlocker(
            item.code,
            "error" if item.blocking else "warning",
            f"One-hot source '{item.source_binding}' drift for "
            f"'{item.source_value or '<unavailable>'}'. {item.resolution}",
            "one_hot_runtime",
        ) for item in evidence)
        existing = {(item.code, item.message) for item in plan.blocked_reasons}
        additions = tuple(
            item for item in additions if (item.code, item.message) not in existing
        )
        return replace(
            plan,
            can_save_schema=plan.can_save_schema and not any(
                item.severity == "error" for item in additions
            ),
            blocked_reasons=(*plan.blocked_reasons, *additions),
        )
