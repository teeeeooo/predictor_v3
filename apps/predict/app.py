"""Predict application bootstrap for the PySide6 rewrite."""

import sys

from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ui.shell import PredictShell


def create_shell() -> PredictShell:
    """Create the minimal Predict shell."""
    return PredictShell(composition=build_predict_workspace_composition())


def main() -> int:
    """Run the Predict application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = create_shell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
