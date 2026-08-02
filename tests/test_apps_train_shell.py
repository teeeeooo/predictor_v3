"""Train shell visual foundation tests."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableView,
    QTextEdit,
)

from apps.predict.application.models import PredictionModelStatus
from apps.predict.application.workspace_state import (
    PredictWorkspaceState,
    WorkspaceSurface,
)
from apps.predict.application.bulk_paste import BulkPasteTransaction
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.services.prediction_service import PredictionService
from apps.predict.ui.shell import PredictShell
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingResourceStatus,
    TrainingResult,
)
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.shell import TrainShell
from apps.train.ui.train_model_panel import TrainModelPanel
from apps.train.application.model_management import (
    CandidateReview,
    ModelManagementSnapshot,
    TargetMetricReview,
)
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _train_shell(*, predict_composition=None) -> TrainShell:  # noqa: ANN001
    service = DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    return TrainShell(
        data_definition_controller=DataDefinitionController(service),
        predict_composition=predict_composition,
    )


class UnavailablePredictionService:
    def model_status(self):
        return PredictionModelStatus("unavailable", "missing")


def _unavailable_predict_composition():
    return build_predict_workspace_composition(
        prediction_service=UnavailablePredictionService()
    )


class FakeTrainController:
    def __init__(self, *, finish_immediately: bool = True) -> None:
        self.is_running = False
        self.finish_immediately = finish_immediately
        self.started_request = None
        self.cancel_called = False
        self.last_result = None

    def resource_status(self, data_path=None, model_output_path=None):  # noqa: ANN001
        data_status = "exists" if data_path and Path(data_path).is_file() else "missing"
        return TrainingResourceStatus(
            data_path=str(data_path or ""),
            model_path=str(model_output_path or ""),
            data_status=data_status,
            model_status="missing",
        )

    def start(
        self,
        request,
        *,
        status_callback=None,
        log_callback=None,
        progress_callback=None,
        finished_callback=None,
        failed_callback=None,
        cancelled_callback=None,
    ):
        self.started_request = request
        self.is_running = True
        if status_callback is not None:
            status_callback("fake training")
        if log_callback is not None:
            log_callback(TrainingLogEvent(request.run_id, "fake log"))
        if progress_callback is not None:
            progress_callback(
                TrainingProgress(
                    request.run_id,
                    completed=1,
                    total=3,
                    message="fake progress",
                    indeterminate=False,
                )
            )
        if not self.finish_immediately:
            return None
        self.is_running = False
        result = TrainingResult(
            run_id=request.run_id,
            status="complete",
            summary="fake summary",
            model_path=request.model_output_path,
            message="fake complete",
        )
        self.last_result = result
        if finished_callback is not None:
            finished_callback(result)
        return None

    def cancel(self) -> bool:
        self.cancel_called = True
        self.is_running = False
        return True


class LifecycleAwareFakeTrainController(FakeTrainController):
    def __init__(self) -> None:
        super().__init__()
        self.snapshot = ModelManagementSnapshot(
            "active",
            active_candidate_id="active-existing",
            active_revision=1,
            candidates=(_candidate_review("active-existing", active=True),),
        )

    def inspect_models(self):
        return self.snapshot

    def start(self, request, **callbacks):
        self.snapshot = ModelManagementSnapshot(
            "active",
            active_candidate_id="active-existing",
            active_revision=1,
            candidates=(
                _candidate_review("candidate-new"),
                _candidate_review("active-existing", active=True),
            ),
        )
        return super().start(request, **callbacks)


@pytest.fixture(autouse=True)
def _cleanup_qt_widgets():
    yield
    app = QApplication.instance()
    if app is None:
        return
    for widget in QApplication.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    app.processEvents()


def test_train_shell_tabs_and_predict_workspace_reuse():
    _app()
    shell = _train_shell()
    standalone = PredictShell()

    assert shell.tabs.count() == 4
    assert [shell.tabs.tabText(index) for index in range(4)] == [
        "Predict",
        "Train / Model",
        "Data Definition",
        "Data Mapping",
    ]
    assert isinstance(shell.tabs.widget(0), PredictWorkspace)
    assert isinstance(shell.tabs.widget(2), DataDefinitionPanel)
    assert isinstance(shell.tabs.widget(3), DataMappingPanel)
    for workspace in (standalone.workspace, shell.predict_workspace):
        assert isinstance(workspace.workspace_state, PredictWorkspaceState)
        assert isinstance(workspace.bulk_paste_transaction, BulkPasteTransaction)
        assert workspace.case_table._paste_handler == workspace.bulk_paste_ui.apply
        assert workspace.workspace_state.current_surface is WorkspaceSurface.INPUT
        assert workspace.surface_host.stack.count() == 2


def test_predict_shell_keeps_standalone_title_and_status_strip():
    _app()
    shell = PredictShell()
    workspace = shell.workspace

    assert workspace.findChild(QLabel, "PredictWorkspaceTitle") is not None
    assert workspace.status_strip.parent() is workspace


def test_train_embedded_predict_workspace_hides_duplicate_title_and_status_strip():
    _app()
    shell = _train_shell()
    workspace = shell.tabs.widget(0)

    assert isinstance(workspace, PredictWorkspace)
    assert workspace.findChild(QLabel, "PredictWorkspaceTitle") is None
    assert workspace.status_strip.parent() is None


def test_standalone_and_embedded_predict_share_no_model_execution_gate(monkeypatch):
    _app()
    monkeypatch.setattr(
        PredictionService,
        "model_status",
        lambda _self: pytest.fail("default local model service must not be consulted"),
    )
    standalone_shell = PredictShell(composition=_unavailable_predict_composition())
    embedded_shell = _train_shell(
        predict_composition=_unavailable_predict_composition()
    )
    standalone = standalone_shell.workspace
    embedded = embedded_shell.predict_workspace

    assert not standalone.command_bar.run_button.isEnabled()
    assert not embedded.command_bar.run_button.isEnabled()
    for workspace in (standalone, embedded):
        assert not workspace.prediction_controller.can_start_prediction
        assert all(
            "Train" not in button.text()
            for button in workspace.command_bar.findChildren(QPushButton)
        )

    predict_source = Path("apps/predict").resolve()
    assert "apps.train" not in (
        (predict_source / "ui" / "workspace.py").read_text(encoding="utf-8")
        + (predict_source / "app.py").read_text(encoding="utf-8")
    )


def test_train_model_panel_initial_state_with_and_without_data(tmp_path):
    _app()
    panel = TrainModelPanel(controller=FakeTrainController())

    assert panel.objectName() == "TrainModelPanel"
    log = panel.findChild(QTextEdit, "TrainingLog")
    assert log is not None
    assert panel.findChild(QProgressBar) is not None
    table = panel.summary_table
    assert table is not None
    assert table.model().rowCount() == 5
    assert table.model().headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Target"

    buttons = {button.text(): button for button in panel.findChildren(QPushButton)}
    panel.set_data_path(str(tmp_path / "missing.csv"))
    assert buttons["학습 데이터 선택"].isEnabled()
    assert not buttons["학습 실행"].isEnabled()
    assert not buttons["중지"].isEnabled()

    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))
    assert buttons["학습 실행"].isEnabled()
    assert {"학습 데이터 선택", "학습 실행", "중지"} <= set(buttons)
    assert {"새로고침", "고급 정보 보기", "이 모델 사용"} <= set(buttons)


def test_train_model_panel_start_updates_progress_log_and_summary(tmp_path):
    _app()
    controller = FakeTrainController()
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))

    panel.run_button.click()

    assert controller.started_request is not None
    assert controller.started_request.data_path == str(data_path)
    assert "fake log" in panel.log.toPlainText()
    assert "fake summary" in panel.log.toPlainText()
    assert panel.progress_bar.value() == 100
    model = panel.summary_table.model()
    assert model.data(model.index(0, 2)) == "완료"


def test_train_model_panel_cancel_button_calls_controller(tmp_path):
    _app()
    controller = FakeTrainController(finish_immediately=False)
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))

    panel.run_button.click()
    assert panel.cancel_button.isEnabled()
    panel.cancel_button.click()

    assert controller.cancel_called


def test_training_completion_refreshes_candidate_without_auto_active(tmp_path):
    _app()
    controller = LifecycleAwareFakeTrainController()
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))

    panel.run_button.click()

    assert panel.workflow_tabs.currentWidget() is panel.model_management_panel
    assert panel.active_model_label.text().endswith("active-existing")
    assert panel.model_management_panel.candidate_table.model().rowCount() == 2
    assert (
        panel.model_management_panel._snapshot.active_candidate_id
        == "active-existing"
    )


def test_train_ui_widgets_do_not_import_core_execution_foundations():
    sources = (
        Path("apps/train/ui/shell.py"),
        Path("apps/train/ui/train_model_panel.py"),
        Path("apps/train/ui/model_management_panel.py"),
        Path("apps/train/ui/data_mapping_panel.py"),
    )
    forbidden = (
        "from core.training",
        "from apps.train.services",
        "import optuna",
        "import sklearn",
        "import subprocess",
        ".fit(",
        "load_workbook",
    )

    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden)


def test_train_ui_uses_model_views_not_qtablewidget():
    sources = (
        Path("apps/train/ui/train_model_panel.py"),
        Path("apps/train/ui/model_management_panel.py"),
        Path("apps/train/ui/data_mapping_panel.py"),
    )

    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert "QTableWidget" not in text
        assert "QTableWidgetItem" not in text


def test_train_views_delegate_artifact_existence_checks():
    shell_source = Path("apps/train/ui/shell.py").read_text(encoding="utf-8")
    panel_source = Path("apps/train/ui/train_model_panel.py").read_text(encoding="utf-8")
    management_source = Path(
        "apps/train/ui/model_management_panel.py"
    ).read_text(encoding="utf-8")

    assert ".exists()" not in shell_source
    assert ".exists()" not in panel_source
    assert ".exists()" not in management_source
    assert "json" not in management_source
    assert "joblib" not in management_source


def test_train_shell_uses_public_data_mapping_navigation_only():
    shell_source = Path("apps/train/ui/shell.py").read_text(encoding="utf-8")

    assert "data_mapping_panel.open_requirement(request)" in shell_source
    assert "_selected_group_key" not in shell_source
    assert "row_table" not in shell_source
    assert "selectionModel" not in shell_source


def _candidate_review(
    candidate_id: str,
    *,
    active: bool = False,
) -> CandidateReview:
    return CandidateReview(
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
        created_at="2026-07-25T00:00:00+00:00",
        is_active=active,
        promotion_eligible=True,
        blocking_reasons=(),
        targets=(
            TargetMetricReview(
                "dynamic-target",
                "Dynamic Target",
                "complete",
                r2=0.8,
                mae=1.2,
                rmse=2.3,
                comparison="no_baseline",
            ),
        ),
        baseline_kind="no_baseline",
    )
