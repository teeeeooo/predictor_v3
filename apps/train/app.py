"""Trainer application bootstrap for the PySide6 rewrite."""

import sys

from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.controllers.train_controller import TrainController
from apps.train.ui.shell import TrainShell


def create_shell() -> TrainShell:
    """Compose the Trainer shell with the production execution adapter."""
    controller = TrainController(execution_factory=QProcessTrainingRunner)
    return TrainShell(
        train_controller=controller,
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
