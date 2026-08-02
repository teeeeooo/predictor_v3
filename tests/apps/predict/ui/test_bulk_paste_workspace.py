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


MAPPING = {
    "odu": {"ODU-A": {}, "ODU-B": {}},
    "fin_type": {"F&T": {}, "Blue": {}},
    "pi": {"7": {}, "9": {}},
    "row": {"1": {}, "2": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        },
        "ODU-B": {
            "Available_Fins": ["Blue"],
            "Available_Pis": ["9"],
            "Available_Rows": ["2"],
        },
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
        "ODU-B Blue 9 2": {"Cond Area": 6.5, "Cond Volume": 7.5},
    },
}


class _MappingRepository:
    mapping_file = ""

    def __init__(self) -> None:
        self.load_count = 0

    def load(self) -> dict:
        self.load_count += 1
        return MAPPING


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


def _workspace(rows: int = 1, mapping_repository=None) -> PredictWorkspace:  # noqa: ANN001
    _app()
    session = PredictSession()
    session.case_store.append_empty_rows(rows)
    workspace = PredictWorkspace(
        session=session,
        initial_empty_rows=0,
        mapping_repository=mapping_repository or _EmptyMappingRepository(),
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


def test_bulk_replaces_stale_row_options_using_its_single_mapping_snapshot():
    repository = _MappingRepository()
    workspace = _workspace(mapping_repository=repository)
    case_id = workspace.session.case_order[0]
    case = workspace.session.case_store.get_case(case_id)
    case.input_values["odu"] = "ODU-B"
    workspace.input_edit_controller.handle_cell_edited(case_id, "odu")
    assert workspace.input_edit_controller.dropdown_options_for_case(
        case_id, "fin_type"
    ) == ("Blue",)
    loads_before_paste = repository.load_count
    odu_col = next(
        index for index, column in enumerate(workspace.case_model.columns)
        if column.key == "odu"
    )
    workspace.case_table.selectionModel().setCurrentIndex(
        workspace.case_model.index(0, odu_col),
        QItemSelectionModel.ClearAndSelect,
    )

    assert workspace.case_table.paste_tsv_at_selection(
        "ODU-A\tF&T\t7\t1"
    ) > 0

    assert repository.load_count == loads_before_paste + 1
    expected = {"fin_type": ("F&T",), "pi": ("7",), "row": ("1",)}
    for key, options in expected.items():
        col = next(
            index for index, column in enumerate(workspace.case_model.columns)
            if column.key == key
        )
        assert workspace._dropdown_options_for_index(
            workspace.case_model.index(0, col)
        ) == options


def test_mapping_issues_reconcile_from_current_row_after_single_cell_edits():
    workspace = _workspace(mapping_repository=_MappingRepository())
    odu_col = next(
        index for index, column in enumerate(workspace.case_model.columns)
        if column.key == "odu"
    )
    workspace.case_table.selectionModel().setCurrentIndex(
        workspace.case_model.index(0, odu_col),
        QItemSelectionModel.ClearAndSelect,
    )
    assert workspace.case_table.paste_tsv_at_selection(
        "ODU-A\tBlue\t9\t2"
    ) > 0
    assert {
        issue.column_key for issue in workspace.bulk_paste_transaction.issues
    } >= {"fin_type", "pi", "row"}

    cooling_col = next(
        index for index, column in enumerate(workspace.case_model.columns)
        if column.key == "cooling_capa"
    )
    assert workspace.case_model.setData(
        workspace.case_model.index(0, cooling_col), "1000", Qt.EditRole
    )
    assert {
        issue.column_key for issue in workspace.bulk_paste_transaction.issues
    } >= {"fin_type", "pi", "row"}

    fin_col = next(
        index for index, column in enumerate(workspace.case_model.columns)
        if column.key == "fin_type"
    )
    assert workspace.case_model.setData(
        workspace.case_model.index(0, fin_col), "F&T", Qt.EditRole
    )
    assert workspace.bulk_paste_transaction.issues == ()
    assert workspace.input_edit_controller.dropdown_options_for_case(
        workspace.session.case_order[0], "pi"
    ) == ("7",)


def test_table_chronology_reauthorizes_bulk_after_later_edit_is_undone():
    workspace = _workspace(rows=2)
    assert workspace.case_table.paste_tsv_at_selection("1000") == 1
    heating_col = next(
        index for index, column in enumerate(workspace.case_model.columns)
        if column.key == "heating_capa"
    )
    workspace.case_table.selectionModel().setCurrentIndex(
        workspace.case_model.index(1, heating_col),
        QItemSelectionModel.ClearAndSelect,
    )
    assert workspace.case_table.replace_current_cell("2000")

    assert workspace.case_table.undo() == 1
    assert workspace.case_table.undo() > 0
    assert workspace.session.case_store.get_case_at(0).input_values.get(
        "cooling_capa", ""
    ) == ""
