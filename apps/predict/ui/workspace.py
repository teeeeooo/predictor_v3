"""Predict workspace split-table skeleton."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from apps.predict.controllers.prediction_controller import PredictionController
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables.input_table_model import InputTableModel
from apps.predict.ui.tables.input_table_view import InputTableView
from apps.predict.ui.tables.result_table_model import ResultTableModel
from apps.predict.ui.tables.result_table_view import ResultTableView
from apps.predict.ui.tables.table_sync import TableSelectionScrollSync


DEFAULT_INITIAL_ROWS = 3


class PredictWorkspace(QWidget):
    """Variable-size batch prediction workspace skeleton."""

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
        self.prediction_controller = PredictionController(self.session)

        self.input_model = InputTableModel(self.session)
        self.result_model = ResultTableModel(self.session)
        self.input_table = InputTableView(self)
        self.result_table = ResultTableView(self)
        self.input_table.setModel(self.input_model)
        self.result_table.setModel(self.result_model)
        self._configure_tables()
        self.table_sync = TableSelectionScrollSync(self.input_table, self.result_table)

        title = QLabel("Predict workspace")
        title.setObjectName("PredictWorkspaceTitle")

        self.run_button = QPushButton("예측 실행")
        self.reset_button = QPushButton("초기화")
        self.add_row_button = QPushButton("행 추가")
        self.delete_row_button = QPushButton("행 삭제")

        self.run_button.clicked.connect(self._run_prediction)
        self.reset_button.clicked.connect(self._reset_rows)
        self.add_row_button.clicked.connect(self._append_row)
        self.delete_row_button.clicked.connect(self._delete_selected_or_last_row)

        command_layout = QHBoxLayout()
        command_layout.addWidget(title)
        command_layout.addStretch(1)
        command_layout.addWidget(self.run_button)
        command_layout.addWidget(self.reset_button)
        command_layout.addWidget(self.add_row_button)
        command_layout.addWidget(self.delete_row_button)

        input_panel = self._build_table_panel("Input Cases", self.input_table)
        result_panel = self._build_table_panel("Prediction Results", self.result_table)
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(input_panel)
        splitter.addWidget(result_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.status_label = QLabel()
        self.status_label.setObjectName("PredictWorkspaceStatus")

        layout = QVBoxLayout(self)
        layout.addLayout(command_layout)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.status_label)
        self._refresh()

    def _configure_tables(self) -> None:
        for table in (self.input_table, self.result_table):
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(False)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)

    def _build_table_panel(self, title: str, table: QWidget) -> QWidget:
        panel = QWidget(self)
        label = QLabel(title)
        label.setObjectName(f"{title.replace(' ', '')}Title")
        layout = QVBoxLayout(panel)
        layout.addWidget(label)
        layout.addWidget(table)
        return panel

    def _append_row(self) -> None:
        row_index = len(self.session.case_store)
        self._begin_insert_rows(row_index, row_index)
        self.session.case_store.append_empty_rows(1)
        self._end_insert_rows()
        self._refresh_after_row_change()

    def _delete_selected_or_last_row(self) -> None:
        rows = self._selected_input_rows()
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
        self.input_model.refresh()
        self.result_model.refresh()
        self._refresh_after_row_change()

    def _refresh_after_row_change(self) -> None:
        self.table_sync.sync_row_heights()
        counts = self.session.summary_counts()
        self.status_label.setText(
            "전체 {total}건 | 실행 중 {running}건 | 예측 완료 {completed}건 | 오류 {errors}건 | 입력 확인 {invalid}건 | 변경됨 {dirty}건".format(
                **counts
            )
        )

    def _run_prediction(self) -> None:
        self.run_button.setEnabled(False)
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
            self.run_button.setEnabled(True)
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
        self.result_model.refresh_case_id(result.case_id)

    def _selected_input_rows(self) -> list[int]:
        return sorted(
            {index.row() for index in self.input_table.selectionModel().selectedRows()}
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
        self.input_model.begin_insert_rows(first_row, last_row)
        self.result_model.begin_insert_rows(first_row, last_row)

    def _end_insert_rows(self) -> None:
        self.result_model.end_insert_rows()
        self.input_model.end_insert_rows()

    def _begin_remove_rows(self, first_row: int, last_row: int) -> None:
        self.input_model.begin_remove_rows(first_row, last_row)
        self.result_model.begin_remove_rows(first_row, last_row)

    def _end_remove_rows(self) -> None:
        self.result_model.end_remove_rows()
        self.input_model.end_remove_rows()

    def _begin_reset_models(self) -> None:
        self.input_model.begin_reset_model()
        self.result_model.begin_reset_model()

    def _end_reset_models(self) -> None:
        self.result_model.end_reset_model()
        self.input_model.end_reset_model()
