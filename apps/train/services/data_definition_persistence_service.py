"""Application transaction for publishing a Data Definition draft generation."""

from __future__ import annotations

from apps.train.application.data_definition import (
    DataDefinitionGenerationRepositoryPort,
)
from core.data_definition.contract import (
    candidate_manifest_from_draft,
    require_valid_contract,
    scoped_fingerprints,
)
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.save_contract import (
    DataDefinitionSaveBlocker,
    DataDefinitionSavePlan,
)
from core.data_definition.schema_writer import DataDefinitionSchemaSaveResult

_CANONICAL_PROJECTION_BLOCKERS = frozenset({"candidate_feature_projection_mismatch"})


class DataDefinitionPersistenceService:
    """Validate and publish a complete candidate while preserving legacy guards."""

    def __init__(self, repository: DataDefinitionGenerationRepositoryPort) -> None:
        self._repository = repository

    @property
    def active_schema_path(self):  # noqa: ANN201
        return self._repository.read_active().path / "projections" / "schema.csv"

    @property
    def active_feature_catalog_path(self):  # noqa: ANN201
        return self._repository.read_active().path / "projections" / "features.csv"

    def save(
        self,
        draft: DataDefinitionDraft,
        save_plan: DataDefinitionSavePlan,
    ) -> DataDefinitionSchemaSaveResult:
        if not draft.is_changed:
            return DataDefinitionSchemaSaveResult(
                False,
                self.active_schema_path,
                0,
                (),
                "Draft is unchanged; generation publication skipped.",
                status="noop",
            )
        active = self._repository.read_active()
        protected_blockers = tuple(
            item for item in save_plan.blocked_reasons
            if item.severity == "error"
            and item.code not in _CANONICAL_PROJECTION_BLOCKERS
        )
        if protected_blockers:
            return DataDefinitionSchemaSaveResult(
                False,
                self.active_schema_path,
                0,
                protected_blockers,
                "Canonical generation save guard blocked publication.",
                status="blocked",
            )
        try:
            candidate = candidate_manifest_from_draft(draft, active.manifest)
            require_valid_contract(candidate)
        except (KeyError, ValueError) as exc:
            return self._blocked(
                "canonical_candidate_invalid",
                f"Canonical generation candidate is invalid: {exc}",
            )
        blockers = self._effective_blockers(save_plan, active.manifest, candidate)
        if blockers:
            return DataDefinitionSchemaSaveResult(
                False,
                self.active_schema_path,
                0,
                blockers,
                "Canonical generation save guard blocked publication.",
                status="blocked",
            )
        try:
            published = self._repository.publish(candidate)
        except (OSError, ValueError, FileExistsError) as exc:
            return DataDefinitionSchemaSaveResult(
                False,
                self.active_schema_path,
                0,
                (),
                f"Generation publication failed: {exc}",
                status="error",
            )
        return DataDefinitionSchemaSaveResult(
            True,
            published.generation_path / "projections" / "schema.csv",
            len(candidate.features),
            (),
            f"Data Definition generation {published.generation_id} published.",
            status="written",
        )

    @staticmethod
    def _effective_blockers(save_plan, active, candidate):  # noqa: ANN001
        before = scoped_fingerprints(active)
        after = scoped_fingerprints(candidate)
        model_compatible = before.model_compatibility == after.model_compatibility
        return tuple(
            item for item in save_plan.blocked_reasons
            if item.severity == "error" and not (
                model_compatible and item.code in _CANONICAL_PROJECTION_BLOCKERS
            )
        )

    def _blocked(self, code: str, message: str) -> DataDefinitionSchemaSaveResult:
        blocker = DataDefinitionSaveBlocker(code, "error", message, "generation_bundle")
        return DataDefinitionSchemaSaveResult(
            False,
            self.active_schema_path,
            0,
            (blocker,),
            message,
            status="blocked",
        )
