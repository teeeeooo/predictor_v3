"""Predict workspace unified case-table surface."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QFrame,
    QVBoxLayout,
    QWidget,
)

from core.ml.artifacts import MODEL_FILE

from apps.common.ui import style
from apps.predict.controllers.input_edit_controller import InputEditController
from apps.predict.controllers.prediction_controller import PredictionController
from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.command_bar import PredictCommandBar
from apps.predict.ui.tables.delegates import DropdownDelegate
from apps.predict.ui.status_widgets import StatusBadge, StatusStrip
from apps.predict.ui.tables.case_table_model import CaseTableModel
from apps.predict.ui.tables.case_table_view import CaseTableView


DEFAULT_INITIAL_ROWS = 3


class PredictWorkspace(QWidget):
    """Variable-size batch prediction workspace."""

    def __init__(
        self,
        parent: QWidget | None = None,
        session: PredictSession | None = None,
        initial_empty_rows: int = DEFAULT_INITIAL_ROWS,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PredictWorkspace")
        self.session = session or PredictSession()
        if len(self.session.case_store) == 0 and initial_empty_rows > 0:
            self.session.case_store.append_empty_rows(initial_empty_rows)
        self.mapping_repository = PredictMappingRepository()
        self.input_edit_controller = InputEditController(
            self.session,
            mapping_repository=self.mapping_repository,
        )
        self.prediction_controller = PredictionController(self.session)

        self.case_model = CaseTableModel(
            self.session,
            edit_callback=self._handle_input_cell_edited,
        )
        self.case_table = CaseTableView(self)
        self.case_table.setModel(self.case_model)
        self._configure_tables()

        title = QLabel("Predict")
        title.setObjectName("PredictWorkspaceTitle")
        title.setFont(style.qfont("font.window_title"))

        self.model_badge = StatusBadge("모델 상태", self._model_status_text(), self._model_status_kind())
        self.mapping_badge = StatusBadge(
            "mapping",
            self._mapping_status_text(),
            self._mapping_status_kind(),
        )
        self.preprocess_badge = StatusBadge("preprocess", "v1.0", "ready")
        self.schema_badge = StatusBadge("schema", "ready", "ready")
        status_strip = StatusStrip(
            (
                self.model_badge,
                self.mapping_badge,
                self.preprocess_badge,
                self.schema_badge,
            ),
            self,
        )

        self.command_bar = PredictCommandBar(self)
        self.command_bar.run_button.clicked.connect(self._run_prediction)
        self.command_bar.reset_button.clicked.connect(self._reset_rows)
        self.command_bar.add_row_button.clicked.connect(self._append_row)
        self.command_bar.delete_row_button.clicked.connect(
            self._delete_selected_or_last_row
        )
        self.command_bar.paste_button.clicked.connect(self._paste_from_clipboard)
        self.command_bar.copy_results_button.clicked.connect(self._copy_results_selection)
        self.command_bar.copy_results_button.setText("선택 복사")

        title_layout = QHBoxLayout()
        title_layout.addWidget(title)
        title_layout.addStretch(1)

        table_panel = self._build_table_panel("Unified Case Table", self.case_table)

        self.status_label = QLabel()
        self.status_label.setObjectName("PredictWorkspaceStatus")
        self.status_label.setFont(style.qfont("font.caption"))
        self.summary_label = QLabel()
        self.summary_label.setObjectName("PredictWorkspaceSummary")
        self.summary_label.setFont(style.qfont("font.caption"))
        self.result_badge = StatusBadge("결과", "대기", "neutral")
        self.bottom_status = self._build_bottom_status()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addLayout(title_layout)
        layout.addWidget(status_strip)
        layout.addWidget(self.command_bar)
        layout.addWidget(table_panel, 1)
        layout.addWidget(self.bottom_status)
        self._refresh()

    def _configure_tables(self) -> None:
        self.case_table.setAlternatingRowColors(True)
        self.case_table.setSortingEnabled(False)
        self.case_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.case_table.horizontalHeader().setStretchLastSection(False)
        self.case_table.verticalHeader().setDefaultSectionSize(34)
        self.case_table.setStyleSheet("")
        for column_index, column in enumerate(self.case_model.columns):
            width = max(56, min(column.width, 150))
            self.case_table.setColumnWidth(column_index, width)
        self._configure_dropdown_delegate()

    def _configure_dropdown_delegate(self) -> None:
        fallback_options = {
            "ref_type": ("R410A", "R32", "R290"),
            "exp_type": ("EEV", "Capi"),
        }
        items_by_column = {
            column_index: fallback_options.get(column.key, ())
            for column_index, column in enumerate(self.case_model.columns)
            if column.dropdown
        }
        if items_by_column:
            delegate = DropdownDelegate(items_by_column, self.case_table)
            self.case_table.setItemDelegate(delegate)
            self.case_table.dropdown_delegate = delegate

    def _build_table_panel(self, title: str, table: QWidget) -> QWidget:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        label = QLabel(title)
        label.setObjectName("PanelTitle")
        label.setFont(style.qfont("font.panel_title"))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(label)
        layout.addWidget(self._build_group_band())
        layout.addWidget(table)
        return panel

    def _build_group_band(self) -> QFrame:
        band = QFrame(self)
        band.setObjectName("ColumnGroupBand")
        layout = QHBoxLayout(band)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        groups = (
            "Input",
            "Auto-fill / Calculated",
            "Prediction Results",
            "Status / Warning",
        )
        for text in groups:
            label = QLabel(text, band)
            label.setObjectName("ColumnGroupBandLabel")
            label.setFont(style.qfont("font.caption"))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 1)
        return band

    def _build_bottom_status(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.md"))
        layout.addWidget(self.summary_label)
        layout.addWidget(self.result_badge)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        return panel

    def _append_row(self) -> None:
        row_index = len(self.session.case_store)
        self._begin_insert_rows(row_index, row_index)
        self.session.case_store.append_empty_rows(1)
        self._end_insert_rows()
        self._refresh_after_row_change()

    def _delete_selected_or_last_row(self) -> None:
        rows = self._selected_case_rows()
        if not rows and len(self.session.case_store) > 0:
            rows = [len(self.session.case_store) - 1]
        self._remove_row_indexes(rows)

    def _reset_rows(self) -> None:
        self._begin_reset_models()
        removed = self.session.case_store.remove_rows(self.session.case_order)
        self.session.remove_results_for_cases(removed)
        self.session.case_store.append_empty_rows(DEFAULT_INITIAL_ROWS)
        self._end_reset_models()
        self._refresh_after_row_change()

    def _refresh(self) -> None:
        self.case_model.refresh()
        self._refresh_after_row_change()

    def _refresh_after_row_change(self) -> None:
        counts = self.session.summary_counts()
        self.summary_label.setText(
            "전체 {total}건 | 실행 중 {running}건 | 예측 완료 {completed}건 | 오류 {errors}건 | 입력 확인 {invalid}건 | 변경됨 {dirty}건".format(
                **counts
            )
        )
        self._refresh_result_badge(counts)
        if not self.status_label.text():
            self.status_label.setText("대기 중")

    def _refresh_result_badge(self, counts: dict[str, int]) -> None:
        if counts["errors"]:
            self.result_badge.set_status(f"오류 {counts['errors']}건", "error")
        elif counts["invalid"]:
            self.result_badge.set_status(f"입력 확인 {counts['invalid']}건", "warning")
        elif counts["running"]:
            self.result_badge.set_status(f"실행 중 {counts['running']}건", "running")
        elif counts["completed"]:
            self.result_badge.set_status(f"완료 {counts['completed']}건", "ready")
        else:
            self.result_badge.set_status("대기", "neutral")

    def _run_prediction(self) -> None:
        self.command_bar.run_button.setEnabled(False)
        self.status_label.setText("예측 실행 중...")
        try:
            summary = self.prediction_controller.run_all(
                status_callback=self._set_status_text,
                result_callback=self._refresh_result_row,
            )
        except Exception as exc:
            self.status_label.setText(f"예측 실행 오류: {str(exc).splitlines()[0]}")
            return
        finally:
            self.command_bar.run_button.setEnabled(True)
        self._refresh_after_row_change()
        self.status_label.setText(
            "예측 완료: 전체 {total}건 | 완료 {complete}건 | 오류 {error}건 | 입력 확인 {invalid}건".format(
                total=summary.total,
                complete=summary.complete,
                error=summary.error,
                invalid=summary.invalid,
            )
        )

    def _set_status_text(self, message: str) -> None:
        self.status_label.setText(message)

    def _refresh_result_row(self, result: ResultRow) -> None:
        self.case_model.refresh_case_id(result.case_id)

    def _handle_input_cell_edited(self, case_id: str, changed_key: str) -> None:
        self.input_edit_controller.handle_cell_edited(case_id, changed_key)
        self.case_model.refresh_case_id(case_id)
        if not Path(self.mapping_repository.mapping_file).exists():
            self.status_label.setText("입력이 변경되었습니다. mapping 파일이 없어 autofill은 제한됩니다.")
        else:
            self.status_label.setText("입력이 변경되었습니다.")

    def _paste_from_clipboard(self) -> None:
        changed = self.case_table.paste_tsv_at_selection(QApplication.clipboard().text())
        self.status_label.setText(f"붙여넣기 완료: {changed}개 셀")
        self._refresh_after_row_change()

    def _copy_results_selection(self) -> None:
        text = self.case_table.copy_selection_tsv()
        QApplication.clipboard().setText(text)
        copied = "선택 셀 복사 완료" if text else "복사할 셀을 선택하세요"
        self.status_label.setText(copied)

    def _selected_case_rows(self) -> list[int]:
        return sorted(
            {index.row() for index in self.case_table.selectionModel().selectedIndexes()}
        )

    def _remove_row_indexes(self, rows: list[int]) -> None:
        valid_rows = sorted(
            {row for row in rows if 0 <= row < len(self.session.case_store)},
            reverse=True,
        )
        for group in self._contiguous_descending_groups(valid_rows):
            first_row = group[-1]
            last_row = group[0]
            case_ids = [self.session.case_order[row] for row in range(first_row, last_row + 1)]
            self._begin_remove_rows(first_row, last_row)
            removed = self.session.case_store.remove_rows(case_ids)
            self.session.remove_results_for_cases(removed)
            self._end_remove_rows()
        self._refresh_after_row_change()

    def _contiguous_descending_groups(self, rows: list[int]) -> list[list[int]]:
        groups: list[list[int]] = []
        for row in rows:
            if not groups or groups[-1][-1] - 1 != row:
                groups.append([row])
            else:
                groups[-1].append(row)
        return groups

    def _begin_insert_rows(self, first_row: int, last_row: int) -> None:
        self.case_model.begin_insert_rows(first_row, last_row)

    def _end_insert_rows(self) -> None:
        self.case_model.end_insert_rows()

    def _begin_remove_rows(self, first_row: int, last_row: int) -> None:
        self.case_model.begin_remove_rows(first_row, last_row)

    def _end_remove_rows(self) -> None:
        self.case_model.end_remove_rows()

    def _begin_reset_models(self) -> None:
        self.case_model.begin_reset_model()

    def _end_reset_models(self) -> None:
        self.case_model.end_reset_model()

    def _model_status_text(self) -> str:
        return "model.pkl loaded" if Path(MODEL_FILE).exists() else "model.pkl missing"

    def _model_status_kind(self) -> str:
        return "ready" if Path(MODEL_FILE).exists() else "missing"

    def _mapping_status_text(self) -> str:
        return "loaded" if Path(self.mapping_repository.mapping_file).exists() else "missing"

    def _mapping_status_kind(self) -> str:
        return "ready" if Path(self.mapping_repository.mapping_file).exists() else "missing"
