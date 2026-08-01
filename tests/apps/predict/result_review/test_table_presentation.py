"""Shared PySide Result Review model/view behavior."""

import os

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication

from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ui.result_review import ResultReviewTableModel, ResultReviewTableView


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

    assert view.textElideMode() == Qt.ElideRight
    assert [line.split("\t")[0] for line in text.splitlines()[1:]] == ["1", "2"]
    assert text.splitlines()[0].split("\t")[:10] == [
        "Case", "상태", "냉방능력", "난방능력", "사양 요약",
        "EER", "COP", "냉방 주파수", "난방 주파수", "냉매량",
    ]
    assert view.copy_selected_rows_to_clipboard()
    assert QApplication.clipboard().text() == text


def test_composition_exposes_same_projection_seam_for_shared_shell_consumers():
    composition = build_predict_workspace_composition(initial_empty_rows=1)

    assert composition.result_review_projection.session is composition.session
    assert ResultReviewTableModel(composition.result_review_projection).rowCount() == 1
