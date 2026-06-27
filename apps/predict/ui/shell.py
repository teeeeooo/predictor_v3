"""Minimal Predict shell."""

from PySide6.QtWidgets import QMainWindow

from apps.predict.ui.workspace import PredictWorkspace


class PredictShell(QMainWindow):
    """Minimal shell for the PySide6 Predict window."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("HVAC V3 Predictor")
        self.resize(1200, 760)
        self.workspace = PredictWorkspace(self)
        self.setCentralWidget(self.workspace)
