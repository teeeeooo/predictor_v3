"""Qt-free production composition for headless experiments."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps.common.model_lifecycle import (
    ModelLifecycleRepository,
    default_model_lifecycle_root,
)
from apps.common.runtime_generation.paths import default_generation_root
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.adapters.subprocess_training_runner import SubprocessTrainingRunner
from apps.train.application.experiments.service import ExperimentApplicationService
from apps.train.application.experiments.records import current_revision
from apps.train.application.experiments.store import ExperimentStore
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.composition.training_results import build_candidate_publisher
from core.data_definition.contract import load_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from core.data_definition.derived.evaluator import evaluation_snapshot

from .runtime import DEFAULT_BOOTSTRAP_MANIFEST_PATH

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def build_headless_experiment_service(
    *,
    generation_root: str | Path | None = None,
    bootstrap_manifest_path: str | Path | None = None,
    lifecycle_root: str | Path | None = None,
    campaign_id: str = "",
    extra_training_args: tuple[str, ...] = (),
    project_root: str | Path = PROJECT_ROOT,
) -> ExperimentApplicationService:
    generation_repository = DataDefinitionGenerationRepository(
        generation_root or default_generation_root()
    )
    bootstrap = load_manifest(
        bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH
    )

    def runtime_available() -> bool:
        return bool(generation_repository.active_generation_id(optional=True))

    def runtime_snapshot():  # noqa: ANN202
        if runtime_available():
            return generation_repository.read_active()
        return SimpleNamespace(manifest=bootstrap)

    def initialize_runtime() -> None:
        if not runtime_available():
            generation_repository.publish(bootstrap)

    lifecycle_repository = ModelLifecycleRepository(
        lifecycle_root or default_model_lifecycle_root()
    )
    store = ExperimentStore(lifecycle_repository.root)

    def execution_factory() -> SubprocessTrainingRunner:
        return SubprocessTrainingRunner(
            extra_args=extra_training_args,
            cancellation_requested=(
                (lambda: store.read_control(campaign_id) == "cancel")
                if campaign_id
                else None
            ),
        )

    lifecycle = TrainingLifecycleService(
        execution_factory=execution_factory,
        registry_provider=lambda: model_registry_snapshot(
            runtime_snapshot().manifest
        ),
        repository=lifecycle_repository,
        publisher=build_candidate_publisher(lifecycle_repository),
    )
    return ExperimentApplicationService(
        lifecycle,
        lifecycle_root=lifecycle_repository.root,
        revision_provider=lambda: current_revision(project_root),
        derived_snapshot_provider=lambda: evaluation_snapshot(
            runtime_snapshot().manifest
        ),
        runtime_initializer=initialize_runtime,
        runtime_available=runtime_available,
    )
