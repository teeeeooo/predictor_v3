"""Trainer application bootstrap for the PySide6 rewrite."""

import os
import sys
from collections.abc import Mapping
from pathlib import Path

from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.adapters.one_hot_vocabulary import (
    load_persisted_mapping_vocabulary_snapshots,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.train_controller import TrainController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.shell import TrainShell
from core.data_definition.contract import load_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEFINITION_ROOT = PROJECT_ROOT / "config" / "data_definition"
DEFAULT_BOOTSTRAP_MANIFEST_PATH = DEFAULT_DEFINITION_ROOT / "manifest.json"


def default_generation_root(
    *,
    platform_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Return the per-user runtime root without mixing state into source config."""
    resolved_platform = platform_name or os.name
    resolved_environment = environment if environment is not None else os.environ
    resolved_home = home or Path.home()
    if resolved_platform == "nt":
        fallback = resolved_home / "AppData" / "Local"
        base = Path(resolved_environment.get("LOCALAPPDATA", fallback))
    else:
        fallback = resolved_home / ".local" / "state"
        base = Path(resolved_environment.get("XDG_STATE_HOME", fallback))
    return base / "predictor_v3" / "data_definition"


def create_shell(
    *,
    generation_root: str | Path | None = None,
    bootstrap_manifest_path: str | Path | None = None,
) -> TrainShell:
    """Compose the Trainer shell with the production execution adapter."""
    root = generation_root if generation_root is not None else default_generation_root()
    repository = DataDefinitionGenerationRepository(root)
    try:
        active = repository.read_active()
    except FileNotFoundError:
        repository.publish(
            load_manifest(bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH)
        )
        active = repository.read_active()
    process_registry_snapshot = model_registry_snapshot(active.manifest)
    data_definition_controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=load_persisted_mapping_vocabulary_snapshots(),
    ))
    controller = TrainController(
        execution_factory=QProcessTrainingRunner,
        registry_provider=lambda: process_registry_snapshot,
    )
    return TrainShell(
        train_controller=controller,
        data_definition_controller=data_definition_controller,
        predict_composition=build_predict_workspace_composition(
            one_hot_snapshot=active.projections.one_hot_runtime
        ),
    )


def main() -> int:
    """Run the Trainer application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = create_shell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
