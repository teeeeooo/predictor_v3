"""Production TrainShell object graph and runtime-generation ownership."""

from __future__ import annotations

from pathlib import Path

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.common.runtime_generation.paths import default_generation_root
from apps.common.model_lifecycle import (
    ActiveModelResolver,
    LegacyModelMigrationService,
    ModelLifecycleRepository,
    default_model_lifecycle_root,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.promotion import ModelPromotionService
from apps.train.application.confirmation import (
    FinalDecisionApplicationService,
    RecommendationPromotionAuthorization,
    TrustedUserAuthorityIssuer,
)
from apps.train.adapters.data_definition_generation_repository import DataDefinitionGenerationRepository
from apps.train.adapters.one_hot_vocabulary import load_persisted_mapping_vocabulary_snapshots
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.application.runtime_generation import (
    DefinitionRuntimeParticipant,
    MappingRuntimeParticipant,
    PredictRuntimeParticipant,
    RuntimeGenerationCoordinator,
    TrainRuntimeParticipant,
)
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.controllers.train_controller import TrainController
from apps.train.composition.training_results import build_candidate_publisher
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.services.data_mapping_service import DataMappingService
from apps.train.ui.shell import TrainShell
from core.data_definition.contract import load_manifest
from core.ml.artifacts import MODEL_FILE

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DEFINITION_ROOT = PROJECT_ROOT / "config" / "data_definition"
DEFAULT_BOOTSTRAP_MANIFEST_PATH = DEFAULT_DEFINITION_ROOT / "manifest.json"


def create_shell(
    *,
    generation_root: str | Path | None = None,
    bootstrap_manifest_path: str | Path | None = None,
    lifecycle_root: str | Path | None = None,
) -> TrainShell:
    root = generation_root if generation_root is not None else default_generation_root()
    repository = DataDefinitionGenerationRepository(root)
    try:
        active = repository.read_active()
    except FileNotFoundError:
        repository.publish(load_manifest(bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH))
        active = repository.read_active()

    train_participant = TrainRuntimeParticipant(active)
    lifecycle_repository = ModelLifecycleRepository(
        lifecycle_root or default_model_lifecycle_root()
    )
    registry_provider = lambda: train_participant.registry_snapshot
    LegacyModelMigrationService(
        lifecycle_repository, registry_provider
    ).migrate_if_needed(MODEL_FILE)
    resolution = ActiveModelResolver(lifecycle_repository).resolve()
    resolved_model_path = (
        resolution.model_path
        if resolution.status == "resolved"
        else str(lifecycle_repository.root / ".missing-active-model.pkl")
    )

    predict_composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        model_file=resolved_model_path,
        lifecycle_repository=lifecycle_repository,
        model_resolution=resolution,
    )
    mapping_service = DataMappingService()
    definition_controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=load_persisted_mapping_vocabulary_snapshots(),
    ))
    definition_participant = DefinitionRuntimeParticipant(
        active, definition_controller
    )
    predict_participant = PredictRuntimeParticipant(
        active, predict_composition, model_file=resolved_model_path
    )
    mapping_participant = MappingRuntimeParticipant(active, mapping_service)
    coordinator = RuntimeGenerationCoordinator(repository, (
        definition_participant,
        predict_participant,
        train_participant,
        mapping_participant,
    ))
    training_lifecycle = TrainingLifecycleService(
        execution_factory=QProcessTrainingRunner,
        registry_provider=registry_provider,
        repository=lifecycle_repository,
        publisher=build_candidate_publisher(lifecycle_repository),
    )
    experiment_service = ExperimentApplicationService(
        training_lifecycle,
        lifecycle_root=lifecycle_repository.root,
        derived_snapshot_provider=lambda: (
            train_participant.derived_evaluation_snapshot
        ),
    )
    closeout_store = LifecycleCloseoutStore(lifecycle_repository.root)
    closeout_authorization = RecommendationPromotionAuthorization(
        lifecycle_repository.root
    )
    authority_issuer = TrustedUserAuthorityIssuer()
    final_decisions = FinalDecisionApplicationService(
        lifecycle_repository,
        ModelPromotionService(
            lifecycle_repository,
            registry_provider,
            authorization_review=closeout_authorization.review,
        ),
        closeout_store=closeout_store,
        authority_issuer=authority_issuer,
    )
    train_controller = TrainController(
        lifecycle_service=training_lifecycle,
        lifecycle_repository=lifecycle_repository,
        registry_provider=registry_provider,
        experiment_service=experiment_service,
        closeout_store=closeout_store,
        final_decision_service=final_decisions,
        user_authority_issuer=authority_issuer,
    )
    return TrainShell(
        train_controller=train_controller,
        data_definition_controller=definition_controller,
        data_mapping_controller=DataMappingController(mapping_service),
        predict_composition=predict_composition,
        generation_coordinator=coordinator,
        definition_participant=definition_participant,
        predict_participant=predict_participant,
        train_participant=train_participant,
        mapping_participant=mapping_participant,
    )
