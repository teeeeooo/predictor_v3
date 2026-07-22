"""Production TrainShell object graph and runtime-generation ownership."""

from __future__ import annotations

from pathlib import Path

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.common.runtime_generation.paths import default_generation_root
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
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.controllers.train_controller import TrainController
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
) -> TrainShell:
    root = generation_root if generation_root is not None else default_generation_root()
    repository = DataDefinitionGenerationRepository(root)
    try:
        active = repository.read_active()
    except FileNotFoundError:
        repository.publish(load_manifest(bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH))
        active = repository.read_active()

    predict_composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        model_file=MODEL_FILE,
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
        active, predict_composition, model_file=MODEL_FILE
    )
    train_participant = TrainRuntimeParticipant(active)
    mapping_participant = MappingRuntimeParticipant(active, mapping_service)
    coordinator = RuntimeGenerationCoordinator(repository, (
        definition_participant,
        predict_participant,
        train_participant,
        mapping_participant,
    ))
    train_controller = TrainController(
        execution_factory=QProcessTrainingRunner,
        registry_provider=lambda: train_participant.registry_snapshot,
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
