"""Minimal Predict shell."""

from PySide6.QtWidgets import QMainWindow

from apps.common.ui.style import app_stylesheet
from apps.common.ui.window_policy import apply_initial_window_layout
from apps.predict.composition import PredictWorkspaceComposition
from apps.predict.ui.workspace import PredictWorkspace
from collections.abc import Callable


class PredictShell(QMainWindow):
    """Minimal shell for the PySide6 Predict window."""

    def __init__(
        self,
        parent: QMainWindow | None = None,
        *,
        composition: PredictWorkspaceComposition | None = None,
        generation_refresh: Callable[[], bool] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("HVAC Performance Predictor")
        self.setStyleSheet(app_stylesheet())
        self.workspace = PredictWorkspace(
            self, composition=composition, generation_refresh=generation_refresh
        )
        self.setCentralWidget(self.workspace)
        apply_initial_window_layout(self, (1200, 760))
