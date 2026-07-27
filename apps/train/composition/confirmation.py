"""Production composition for shared Phase 5H application services."""

from __future__ import annotations

from pathlib import Path

from apps.common.model_lifecycle import (
    ModelLifecycleRepository,
    default_model_lifecycle_root,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.promotion import ModelPromotionService
from apps.common.runtime_generation.paths import default_generation_root
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.confirmation import (
    ConfirmationApplicationService,
    FinalDecisionApplicationService,
    LifecycleRetentionApplicationService,
    RecommendationPromotionAuthorization,
    SnapshotFreezeService,
    TrainingLifecycleConfirmationExecutor,
)
from apps.train.application.experiments.records import current_revision
from apps.train.composition.experiments import (
    PROJECT_ROOT,
    build_headless_experiment_service,
)
from core.data_definition.target_registry.runtime import model_registry_snapshot


def build_headless_confirmation_services(
    *,
    lifecycle_root: str | Path | None = None,
    generation_root: str | Path | None = None,
) -> dict[str, object]:
    lifecycle_repository = ModelLifecycleRepository(
        lifecycle_root or default_model_lifecycle_root()
    )
    generation_repository = DataDefinitionGenerationRepository(
        generation_root or default_generation_root()
    )
    closeout = LifecycleCloseoutStore(lifecycle_repository.root)
    experiments = build_headless_experiment_service(
        lifecycle_root=lifecycle_repository.root,
        generation_root=generation_repository.root,
    )
    authorization = RecommendationPromotionAuthorization(
        lifecycle_repository.root
    )
    promotion = ModelPromotionService(
        lifecycle_repository,
        lambda: model_registry_snapshot(
            generation_repository.read_active().manifest
        ),
        authorization_review=authorization.review,
    )
    execution = TrainingLifecycleConfirmationExecutor(
        experiments,
        lifecycle_repository,
        closeout_store=closeout,
    )
    snapshots = SnapshotFreezeService(
        lifecycle_repository,
        generation_repository,
        closeout_store=closeout,
    )
    confirmations = ConfirmationApplicationService(
        lifecycle_repository,
        generation_repository,
        promotion,
        execution,
        closeout_store=closeout,
        build_identity_provider=lambda: current_revision(PROJECT_ROOT),
    )
    decisions = FinalDecisionApplicationService(
        lifecycle_repository,
        promotion,
        closeout_store=closeout,
    )
    retention = LifecycleRetentionApplicationService(
        lifecycle_repository,
        closeout_store=closeout,
    )
    return {
        "repository": lifecycle_repository,
        "generation_repository": generation_repository,
        "closeout_store": closeout,
        "snapshots": snapshots,
        "confirmations": confirmations,
        "decisions": decisions,
        "retention": retention,
    }
