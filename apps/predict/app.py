"""Predict application bootstrap for the PySide6 rewrite."""

import sys

from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.application.runtime_generation import StandalonePredictGenerationGuard
from apps.predict.ui.shell import PredictShell
from apps.common.runtime_generation.paths import default_generation_root
from apps.common.model_lifecycle import (
    ActiveModelResolver,
    LegacyModelMigrationService,
    ModelLifecycleRepository,
    default_model_lifecycle_root,
)
from apps.common.runtime_generation.repository import DataDefinitionGenerationRepository
from apps.predict.application.runtime_generation_participant import PredictRuntimeParticipant
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from core.data_definition.contract import load_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from core.ml.artifacts import MODEL_FILE
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOOTSTRAP_MANIFEST_PATH = PROJECT_ROOT / "config" / "data_definition" / "manifest.json"


def create_shell(
    *, generation_root: str | Path | None = None,
    bootstrap_manifest_path: str | Path | None = None,
    lifecycle_root: str | Path | None = None,
) -> PredictShell:
    """Create the minimal Predict shell."""
    repository = DataDefinitionGenerationRepository(
        generation_root or default_generation_root()
    )
    try:
        active = repository.read_active()
    except FileNotFoundError:
        repository.publish(load_manifest(bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH))
        active = repository.read_active()
    lifecycle_repository = ModelLifecycleRepository(
        lifecycle_root or default_model_lifecycle_root()
    )
    registry_provider = lambda: model_registry_snapshot(active.manifest)
    migration = LegacyModelMigrationService(
        lifecycle_repository, registry_provider
    ).migrate_if_needed(MODEL_FILE)
    resolution = ActiveModelResolver(lifecycle_repository).resolve()
    resolved_model_path = (
        resolution.model_path
        if resolution.status == "resolved"
        else str(lifecycle_repository.root / ".missing-active-model.pkl")
    )
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        model_file=resolved_model_path,
    )
    participant = PredictRuntimeParticipant(
        active, composition, model_file=resolved_model_path
    )
    guard = StandalonePredictGenerationGuard(repository, participant)
    shell = PredictShell(composition=composition)

    def refresh_generation() -> bool:
        ready = guard.ensure_current()
        if shell.workspace.generation_id != participant.active_generation_id:
            shell.workspace.apply_runtime_composition(participant.composition)
        return ready

    shell.workspace.configure_generation_refresh(
        refresh_generation,
        lambda: ". ".join(
            item for item in (guard.status, guard.recommended_action) if item
        ),
    )
    refresh_generation()
    shell.workspace.show_generation_status()
    shell.generation_guard = guard
    shell.model_resolution = resolution
    shell.legacy_migration = migration
    return shell


def main() -> int:
    """Run the Predict application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = create_shell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
