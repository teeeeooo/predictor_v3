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

from apps.predict.state.predict_session import PredictSession
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
        session: PredictSession | None = None,
        parent: QWidget | None = None,
        initial_empty_rows: int = DEFAULT_INITIAL_ROWS,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PredictWorkspace")
        self.session = session or PredictSession()
        if len(self.session.case_store) == 0 and initial_empty_rows > 0:
            self.session.case_store.append_empty_rows(initial_empty_rows)

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
        self.run_button.setEnabled(False)
        self.reset_button = QPushButton("초기화")
        self.add_row_button = QPushButton("행 추가")
        self.delete_row_button = QPushButton("행 삭제")

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
        self.session.case_store.append_empty_rows(1)
        self._refresh()

    def _delete_selected_or_last_row(self) -> None:
        selected = self.input_table.selectionModel().selectedRows()
        if selected:
            removed = self.session.case_store.remove_row_indexes(
                index.row() for index in selected
            )
        elif len(self.session.case_store) > 0:
            removed = self.session.case_store.remove_row_indexes(
                [len(self.session.case_store) - 1]
            )
        else:
            removed = []
        self.session.remove_results_for_cases(removed)
        self._refresh()

    def _reset_rows(self) -> None:
        removed = self.session.case_store.remove_rows(self.session.case_order)
        self.session.remove_results_for_cases(removed)
        self.session.case_store.append_empty_rows(DEFAULT_INITIAL_ROWS)
        self._refresh()

    def _refresh(self) -> None:
        self.input_model.refresh()
        self.result_model.refresh()
        self.table_sync.sync_row_heights()
        counts = self.session.summary_counts()
        self.status_label.setText(
            "전체 {total}건 | 예측 완료 {completed}건 | 오류 {errors}건 | 변경됨 {dirty}건".format(
                **counts
            )
        )
