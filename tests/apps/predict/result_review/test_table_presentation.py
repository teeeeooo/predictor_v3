"""Shared PySide Result Review model/view behavior."""

import os

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView, QHeaderView

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ui.result_review import ResultReviewTableModel, ResultReviewTableView


RESULT_WIDTHS = (64, 100, 100, 100, 360, 72, 72, 112, 112, 90)


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_model_is_exact_readonly_projection_and_summary_tooltip_is_full_text():
    _app()
    composition = build_predict_workspace_composition(initial_empty_rows=1)
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    case.input_values.update(
        {
            "idu": "A very long indoor unit value",
            "evap_index": "A very long evaporator value",
        }
    )
    model = ResultReviewTableModel(composition.result_review_projection)
    summary = model.index(0, 4)

    assert model.rowCount() == 1
    assert model.columnCount() == 10
    assert [model.headerData(i, Qt.Horizontal) for i in range(10)] == [
        "Case", "상태", "냉방능력", "난방능력", "사양 요약",
        "EER", "COP", "냉방 주파수", "난방 주파수", "냉매량",
    ]
    assert model.flags(summary) == Qt.ItemIsEnabled | Qt.ItemIsSelectable
    assert model.data(summary, Qt.DisplayRole) == model.data(summary, Qt.ToolTipRole)
    assert "A very long indoor unit value" in model.data(summary, Qt.ToolTipRole)


def test_view_elides_only_visually_and_copies_selected_full_rows_with_headers():
    _app()
    composition = build_predict_workspace_composition(initial_empty_rows=2)
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    case.input_values.update(
        {
            "idu": "A very long indoor unit value retained in full",
            "evap_index": "A very long evaporator value retained in full",
        }
    )
    model = ResultReviewTableModel(composition.result_review_projection)
    view = ResultReviewTableView()
    view.setModel(model)
    selection = view.selectionModel()
    selection.select(
        model.index(1, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )
    selection.select(
        model.index(0, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )

    text = view.copy_selected_rows_tsv()
    copied_rows = [line.split("\t") for line in text.splitlines()]
    full_summary = model.data(model.index(0, 4), Qt.DisplayRole)

    assert not view.wordWrap()
    assert view.textElideMode() == Qt.ElideRight
    assert view.selectionBehavior() == QAbstractItemView.SelectRows
    assert view.selectionMode() == QAbstractItemView.ExtendedSelection
    assert view.verticalHeader().sectionResizeMode(0) == QHeaderView.Interactive
    assert [line.split("\t")[0] for line in text.splitlines()[1:]] == ["1", "2"]
    assert text.splitlines()[0].split("\t")[:10] == [
        "Case", "상태", "냉방능력", "난방능력", "사양 요약",
        "EER", "COP", "냉방 주파수", "난방 주파수", "냉매량",
    ]
    assert copied_rows[1][4] == full_summary
    assert "retained in full" in copied_rows[1][4]
    assert view.copy_selected_rows_to_clipboard()
    assert QApplication.clipboard().text() == text


def test_composition_exposes_same_projection_seam_for_shared_shell_consumers():
    composition = build_predict_workspace_composition(initial_empty_rows=1)

    assert composition.result_review_projection.session is composition.session
    assert ResultReviewTableModel(composition.result_review_projection).rowCount() == 1


def test_narrow_view_pins_only_case_and_status_with_shared_native_interactions():
    app = _app()
    composition = build_predict_workspace_composition(initial_empty_rows=20)
    model = ResultReviewTableModel(composition.result_review_projection)
    view = ResultReviewTableView()
    view.setModel(model)
    view.verticalHeader().setDefaultSectionSize(34)
    view.pinned_anchor_view.verticalHeader().setDefaultSectionSize(34)
    for column, width in enumerate(RESULT_WIDTHS):
        view.setColumnWidth(column, width)
    view.resize(620, 260)
    view.show()
    app.processEvents()

    anchor = view.pinned_anchor_view
    assert view.pinned_columns_active
    assert anchor.isVisible()
    assert view.isColumnHidden(0) and view.isColumnHidden(1)
    assert not anchor.isColumnHidden(0) and not anchor.isColumnHidden(1)
    assert all(anchor.isColumnHidden(column) for column in range(2, 10))
    assert anchor.model() is model
    assert anchor.selectionModel() is view.selectionModel()

    anchored_status = anchor.visualRect(model.index(2, 1))
    QTest.mouseClick(anchor.viewport(), Qt.LeftButton, pos=anchored_status.center())
    app.processEvents()
    assert view.selectionModel().currentIndex().row() == 2
    assert [index.row() for index in view.selectionModel().selectedRows()] == [2]
    expected_copy = view.copy_selected_rows_tsv()
    assert expected_copy.splitlines()[1].split("\t")[0] == "3"
    QApplication.clipboard().clear()
    QTest.keyClick(anchor, Qt.Key_C, Qt.ControlModifier)
    assert QApplication.clipboard().text() == expected_copy

    view.horizontalScrollBar().setValue(view.horizontalScrollBar().maximum())
    assert view.horizontalScrollBar().value() > 0
    assert anchor.horizontalScrollBar().value() == 0
    assert anchor.visualRect(model.index(2, 0)).isValid()

    view.verticalScrollBar().setValue(view.verticalScrollBar().maximum())
    app.processEvents()
    assert anchor.verticalScrollBar().value() == view.verticalScrollBar().value()
    anchor.verticalScrollBar().setValue(3)
    app.processEvents()
    assert view.verticalScrollBar().value() == 3
    assert anchor.visualRect(model.index(3, 0)).top() == view.visualRect(
        model.index(3, 2)
    ).top()

    anchor.setColumnWidth(1, 128)
    app.processEvents()
    assert anchor.columnWidth(1) == 128
    assert anchor.rowHeight(3) == view.rowHeight(3)
    view.resize(sum(RESULT_WIDTHS) + 200, 260)
    app.processEvents()
    assert not view.pinned_columns_active
    assert view.columnWidth(1) == 128


def test_wide_view_uses_original_single_surface_without_blank_anchor_region():
    app = _app()
    composition = build_predict_workspace_composition(initial_empty_rows=3)
    model = ResultReviewTableModel(composition.result_review_projection)
    view = ResultReviewTableView()
    view.setModel(model)
    for column, width in enumerate(RESULT_WIDTHS):
        view.setColumnWidth(column, width)
    view.resize(sum(RESULT_WIDTHS) + 160, 260)
    view.show()
    app.processEvents()

    assert not view.pinned_columns_active
    assert not view.pinned_anchor_view.isVisible()
    assert all(not view.isColumnHidden(column) for column in range(10))
    assert view.horizontalScrollBar().maximum() == 0
    assert view.visualRect(model.index(0, 0)).left() == 0
