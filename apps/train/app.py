"""Trainer application bootstrap for the PySide6 rewrite."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.train_controller import TrainController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.shell import TrainShell
from core.data_definition.contract import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEFINITION_ROOT = PROJECT_ROOT / "config" / "data_definition"
DEFAULT_GENERATION_ROOT = DEFAULT_DEFINITION_ROOT / "generation_store"
DEFAULT_BOOTSTRAP_MANIFEST_PATH = DEFAULT_DEFINITION_ROOT / "manifest.json"


def create_shell(
    *,
    generation_root: str | Path | None = None,
    bootstrap_manifest_path: str | Path | None = None,
) -> TrainShell:
    """Compose the Trainer shell with the production execution adapter."""
    repository = DataDefinitionGenerationRepository(
        generation_root or DEFAULT_GENERATION_ROOT
    )
    try:
        repository.read_active()
    except FileNotFoundError:
        repository.publish(
            load_manifest(bootstrap_manifest_path or DEFAULT_BOOTSTRAP_MANIFEST_PATH)
        )
    data_definition_controller = DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    )
    controller = TrainController(execution_factory=QProcessTrainingRunner)
    return TrainShell(
        train_controller=controller,
        data_definition_controller=data_definition_controller,
        predict_composition=build_predict_workspace_composition(),
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
