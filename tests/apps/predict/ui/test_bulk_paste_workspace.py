"""Qt adapter coverage for the Predict-owned bulk-paste transaction."""

import os

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from apps.predict.application.workspace_state import WorkspaceSurface
from apps.predict.state.predict_session import PredictSession
from apps.predict.ui.workspace import PredictWorkspace


class _EmptyMappingRepository:
    mapping_file = ""

    def load(self) -> dict:
        return {}


class _PasteShortcutEvent:
    accepted = False

    def matches(self, sequence) -> bool:  # noqa: ANN001
        return sequence == QKeySequence.Paste

    def accept(self) -> None:
        self.accepted = True


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


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


def _workspace(rows: int = 1) -> PredictWorkspace:
    _app()
    session = PredictSession()
    session.case_store.append_empty_rows(rows)
    workspace = PredictWorkspace(
        session=session,
        initial_empty_rows=0,
        mapping_repository=_EmptyMappingRepository(),
    )
    index = workspace.case_model.index(0, 0)
    workspace.case_table.selectionModel().setCurrentIndex(
        index, QItemSelectionModel.ClearAndSelect
    )
    return workspace


def test_overflow_paste_and_compound_undo_each_emit_one_bounded_model_reset():
    workspace = _workspace()
    input_reset = QSignalSpy(workspace.case_model.modelReset)
    result_reset = QSignalSpy(workspace.result_review_model.modelReset)

    changed = workspace.case_table.paste_tsv_at_selection(
        "1000\n2000\n3000\n4000\n"
    )

    assert changed == 4
    assert len(workspace.session.case_store) == 4
    assert input_reset.count() == 1
    assert result_reset.count() == 1
    assert "행 3개 확장" in workspace.status_label.text()

    assert workspace.case_table.undo() == 7
    assert len(workspace.session.case_store) == 1
    assert input_reset.count() == 2
    assert result_reset.count() == 2


def test_numeric_issue_is_projected_to_the_exact_cell_and_valid_row_survives():
    workspace = _workspace(rows=2)

    assert workspace.case_table.paste_tsv_at_selection("bad\n1200\n") == 2

    issue = workspace.case_model.input_issue(0, 0)
    assert issue is not None
    assert (issue.case_id, issue.column_key, issue.code) == (
        workspace.session.case_order[0],
        "cooling_capa",
        "invalid_numeric",
    )
    assert workspace.case_model.data(
        workspace.case_model.index(0, 0),
        Qt.ToolTipRole,
    ) == issue.message
    assert workspace.session.case_store.get_case_at(1).input_values["cooling_capa"] == "1200"
    assert "확인 필요 1행/1셀" in workspace.status_label.text()


def test_toolbar_and_keyboard_shortcut_share_the_same_transaction_entry(monkeypatch):
    workspace = _workspace()
    calls = []
    original = workspace.bulk_paste_transaction.apply

    def counted(text, destination):  # noqa: ANN001, ANN202
        calls.append((text, destination.start_feature_identity))
        return original(text, destination)

    monkeypatch.setattr(workspace.bulk_paste_transaction, "apply", counted)
    QApplication.clipboard().setText("1000")
    workspace.command_bar.paste_button.click()
    assert workspace.case_table.undo() > 0

    QApplication.clipboard().setText("2000")
    event = _PasteShortcutEvent()
    workspace.case_table.keyPressEvent(event)

    assert event.accepted
    assert [item[0] for item in calls] == ["1000", "2000"]
    assert workspace.session.case_store.get_case_at(0).input_values["cooling_capa"] == "2000"


def test_keyboard_paste_cannot_bypass_result_or_running_mutation_gates():
    workspace = _workspace()
    before = workspace.session.revision

    workspace.workspace_state.choose_surface(WorkspaceSurface.RESULT)
    assert workspace.case_table.paste_tsv_at_selection("1000") == 0
    assert workspace.session.revision == before

    workspace.workspace_state.choose_surface(WorkspaceSurface.INPUT)
    workspace.prediction_controller._is_running = True
    assert workspace.case_table.paste_tsv_at_selection("1000") == 0
    assert workspace.session.revision == before
