"""Minimal Trainer shell placeholder."""

from apps.predict.ui.workspace import PredictWorkspace


class TrainShell:
    """Placeholder shell for the future PySide6 Trainer window."""

    tab_names = ("Predict", "Train / Model", "Data Mapping")

    def __init__(self) -> None:
        self.predict_workspace = PredictWorkspace()
