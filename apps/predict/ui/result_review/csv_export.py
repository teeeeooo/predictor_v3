"""Qt path selection for selected-row Result Review CSV export."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QWidget

from apps.predict.adapters.result_review import publish_result_review_csv

from .table_view import ResultReviewTableView


logger = logging.getLogger(__name__)
CSV_FILTER = "CSV files (*.csv);;All files (*)"
DEFAULT_FILENAME = "predict_result_review.csv"


def export_selected_rows_csv(
    parent: QWidget,
    table: ResultReviewTableView,
) -> str:
    """Choose a destination and publish the selected canonical full-row document."""
    model = table.model()
    if model is None or not hasattr(model, "full_row_document_for_rows"):
        return "CSV로 내보낼 결과 행을 선택하세요."
    document = model.full_row_document_for_rows(table.selected_row_indexes())
    if document is None:
        return "CSV로 내보낼 결과 행을 선택하세요."
    path, _selected_filter = QFileDialog.getSaveFileName(
        parent,
        "Result Review CSV 저장",
        DEFAULT_FILENAME,
        CSV_FILTER,
    )
    if not path:
        return "CSV 저장을 취소했습니다."
    try:
        publish_result_review_csv(path, document)
    except OSError:
        logger.exception("Result Review CSV publication failed")
        return "CSV 저장 중 문제가 발생했습니다. 파일 위치와 권한을 확인해 주세요."
    return f"결과 CSV 저장 완료: {Path(path).name}"
