"""Minimal Trainer shell."""

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.common.ui.window_policy import apply_initial_window_layout
from apps.predict.composition import PredictWorkspaceComposition
from apps.predict.ui.status_widgets import model_status_badge_state
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.application.data_mapping import (
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.controllers.train_controller import TrainController
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.train_model_panel import TrainModelPanel


class TrainShell(QMainWindow):
    """Minimal shell for the PySide6 Trainer window."""

    tab_names = (
        "Predict",
        "Train / Model",
        "Data Definition",
        "Data Mapping",
    )

    def __init__(
        self,
        parent: QMainWindow | None = None,
        *,
        train_controller: TrainController | None = None,
        data_definition_controller: DataDefinitionController | None = None,
        data_mapping_controller: DataMappingController | None = None,
        predict_composition: PredictWorkspaceComposition | None = None,
    ) -> None:
        super().__init__(parent)
        self.train_controller = train_controller or TrainController()
        self.data_mapping_controller = data_mapping_controller or DataMappingController()
        self.data_definition_controller = data_definition_controller or DataDefinitionController()
        self.setWindowTitle("HVAC Training Studio")
        self.setStyleSheet(style.app_stylesheet())

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        self.status_badges: dict[str, QLabel] = {}
        layout.addWidget(self._build_status_strip())
        tabs = QTabWidget(self)
        self.predict_workspace = PredictWorkspace(
            tabs,
            show_title=False,
            show_status_strip=False,
            composition=predict_composition,
        )
        self.train_model_panel = TrainModelPanel(
            tabs,
            controller=self.train_controller,
            on_model_status_changed=self.refresh_status_strip,
        )
        tabs.addTab(
            self.predict_workspace,
            self.tab_names[0],
        )
        tabs.addTab(self.train_model_panel, self.tab_names[1])
        self.data_definition_panel = DataDefinitionPanel(
            tabs,
            controller=self.data_definition_controller,
            on_open_data_mapping=self.open_data_mapping,
        )
        tabs.addTab(self.data_definition_panel, self.tab_names[2])
        self.data_mapping_panel = DataMappingPanel(
            tabs,
            controller=self.data_mapping_controller,
        )
        tabs.addTab(
            self.data_mapping_panel,
            self.tab_names[3],
        )
        layout.addWidget(tabs, 1)
        self.setCentralWidget(central)
        self.tabs = tabs
        apply_initial_window_layout(self, (1280, 820))

    def open_data_mapping(
        self,
        request: DataMappingNavigationRequest,
    ) -> DataMappingNavigationResult:
        """Orchestrate tab selection and public Data Mapping navigation."""
        self.tabs.setCurrentWidget(self.data_mapping_panel)
        return self.data_mapping_panel.open_requirement(request)

    def _build_status_strip(self) -> QFrame:
        strip = QFrame(self)
        strip.setObjectName("Panel")
        strip.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        for key, label, value, kind in self._status_values():
            badge = _badge(label, value, kind)
            self.status_badges[key] = badge
            layout.addWidget(badge)
        layout.addStretch(1)
        return strip

    def refresh_status_strip(self) -> None:
        """Refresh Trainer and embedded Predict resource status badges."""
        for key, label, value, kind in self._status_values():
            badge = self.status_badges.get(key)
            if badge is not None:
                _set_badge(badge, label, value, kind)
        model_text, model_kind = model_status_badge_state(
            self.predict_workspace.prediction_controller.model_status()
        )
        self.predict_workspace.model_badge.set_status(model_text, model_kind)

    def _status_values(self) -> tuple[tuple[str, str, str, str], ...]:
        training = self.train_controller.resource_status()
        model_exists = training.model_status == "exists"
        train_data_exists = training.data_status == "exists"
        mapping_exists = self.data_mapping_controller.resource_status() == "exists"
        return (
            (
                "model",
                "모델 상태",
                "model.pkl 로드됨" if model_exists else "model.pkl 없음",
                "ready" if model_exists else "missing",
            ),
            ("preprocess", "전처리", "v1.0", "ready"),
            (
                "train_data",
                "학습 데이터",
                "확인됨" if train_data_exists else "없음",
                "ready" if train_data_exists else "missing",
            ),
            (
                "mapping",
                "데이터 매핑",
                "로드됨" if mapping_exists else "없음",
                "ready" if mapping_exists else "missing",
            ),
        )


def _badge(label: str, value: str, kind: str) -> QLabel:
    badge = QLabel()
    badge.setObjectName("StatusBadge")
    badge.setTextFormat(Qt.RichText)
    _set_badge(badge, label, value, kind)
    return badge


def _set_badge(badge: QLabel, label: str, value: str, kind: str) -> None:
    resolved = style.status_style(kind)
    badge.setText(
        f"<span style='color:{resolved.foreground};'>●</span> "
        f"<span style='color:{style.color('text.default')};'>{escape(label)}: {escape(value)}</span>"
    )
    badge.setStyleSheet(style.status_badge_stylesheet(kind))
