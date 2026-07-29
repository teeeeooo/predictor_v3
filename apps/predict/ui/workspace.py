"""Predict workspace unified case-table surface."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QFrame,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.predict.application.prediction_usecase import PredictionRunSummary
from apps.predict.composition import (
    PredictWorkspaceComposition,
    build_predict_workspace_composition,
)
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.command_bar import PredictCommandBar
from apps.predict.ui.tables.delegates import DropdownDelegate
from apps.predict.ui.status_widgets import (
    StatusBadge,
    StatusStrip,
    mapping_status_badge_state,
    model_status_badge_state,
    prediction_summary_text,
)
from apps.predict.ui.tables.case_table_model import CaseTableModel
from apps.predict.ui.tables.case_table_view import CaseTableView
from apps.predict.ui.tables.group_header import TableLinkedGroupHeader
from apps.predict.ui.runtime_generation import apply_runtime_composition
from apps.predict.ui.model_lifecycle_ui import PredictModelLifecycleUi


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from apps.predict.mapping.mapping_repository import PredictMappingRepository
    from apps.predict.state.predict_session import PredictSession


DEFAULT_INITIAL_ROWS = 3


class PredictWorkspace(QWidget):
    """Variable-size batch prediction workspace."""

    def __init__(
        self,
        parent: QWidget | None = None,
        session: PredictSession | None = None,
        initial_empty_rows: int = DEFAULT_INITIAL_ROWS,
        mapping_repository: PredictMappingRepository | None = None,
        show_title: bool = True,
        show_status_strip: bool = True,
        composition: PredictWorkspaceComposition | None = None,
        generation_refresh: Callable[[], bool] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PredictWorkspace")
        if composition is not None and (session is not None or mapping_repository is not None):
            raise ValueError(
                "composition cannot be combined with session or mapping_repository"
            )
        resolved = composition or build_predict_workspace_composition(
            session=session,
            initial_empty_rows=initial_empty_rows,
            mapping_repository=mapping_repository,
        )
        self.session = resolved.session
        self.table_edit_controller = resolved.table_edit_controller
        self.mapping_repository = resolved.mapping_repository
        self.input_edit_controller = resolved.input_edit_controller
        self.prediction_controller = resolved.prediction_controller
        self.dropdown_option_adapter = resolved.dropdown_option_adapter
        self.generation_id = resolved.generation_id
        self._generation_refresh = generation_refresh
        self._generation_status_provider: Callable[[], str] | None = None

        self.case_model = CaseTableModel(
            self.session,
            columns=resolved.columns,
            edit_callback=self._handle_input_cell_edited,
        )
        self.case_table = CaseTableView(self)
        self.case_table.setModel(self.case_model)
        self._configure_tables()

        model_text, model_kind = model_status_badge_state(
            self.prediction_controller.model_status()
        )
        mapping_text, mapping_kind = mapping_status_badge_state(
            self.dropdown_option_adapter.mapping_status()
        )
        self.model_badge = StatusBadge("모델 상태", model_text, model_kind)
        self.mapping_badge = StatusBadge(
            "데이터 매핑",
            mapping_text,
            mapping_kind,
        )
        self.preprocess_badge = StatusBadge("전처리", "v1.0", "ready")
        self.schema_badge = StatusBadge("입력 스키마", "준비됨", "ready")
        self.status_strip = StatusStrip(
            (self.model_badge, self.mapping_badge, self.preprocess_badge, self.schema_badge),
            self,
        )

        self.command_bar = PredictCommandBar(self)
        self.command_bar.run_button.clicked.connect(self._run_prediction)
        self.command_bar.cancel_button.clicked.connect(self._cancel_prediction)
        self.command_bar.reset_button.clicked.connect(self._reset_rows)
        self.command_bar.add_row_button.clicked.connect(self._append_row)
        self.command_bar.delete_row_button.clicked.connect(
            self._delete_selected_or_last_row
        )
        self.command_bar.paste_button.clicked.connect(self._paste_from_clipboard)
        self.command_bar.copy_results_button.clicked.connect(self._copy_results_selection)
        self.command_bar.refresh_button.clicked.connect(self._refresh_generation)
        self.command_bar.copy_results_button.setText("선택 복사")

        table_panel = self._build_table_panel("예측 케이스", self.case_table)

        self.status_label = QLabel()
        self.status_label.setObjectName("PredictWorkspaceStatus")
        self.status_label.setFont(style.qfont("font.caption"))
        self.summary_label = QLabel()
        self.summary_label.setObjectName("PredictWorkspaceSummary")
        self.summary_label.setFont(style.qfont("font.caption"))
        self.result_badge = StatusBadge("결과", "대기", "neutral")
        self.bottom_status = self._build_bottom_status()
        self.model_lifecycle_ui = PredictModelLifecycleUi(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        if show_title:
            self.title_label = QLabel("HVAC Performance Predictor")
            self.title_label.setObjectName("PredictWorkspaceTitle")
            self.title_label.setFont(style.qfont("font.window_title"))
            title_layout = QHBoxLayout()
            title_layout.addWidget(self.title_label)
            title_layout.addStretch(1)
            layout.addLayout(title_layout)
        else:
            self.title_label = None
        if show_status_strip:
            layout.addWidget(self.status_strip)
        else:
            self.status_strip.setParent(None)
        layout.addWidget(self.command_bar)
        layout.addWidget(table_panel, 1)
        layout.addWidget(self.bottom_status)
        self._refresh()
        self.model_lifecycle_ui.refresh()

    def apply_runtime_composition(
        self, composition: PredictWorkspaceComposition
    ) -> None:
        """Swap one already-prepared Predict runtime while retaining case state."""
        apply_runtime_composition(self, composition)

    def configure_generation_refresh(
        self,
        refresh: Callable[[], bool],
        status_provider: Callable[[], str],
    ) -> None:
        self._generation_refresh = refresh
        self._generation_status_provider = status_provider

    def show_generation_status(self) -> None:
        if self._generation_status_provider is not None:
            self.status_label.setText(self._generation_status_provider())

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
        items_by_column = {
            column_index: self.dropdown_option_adapter.base_options_for_key(column.key)
            for column_index, column in enumerate(self.case_model.columns)
            if column.dropdown
        }
        if items_by_column:
            delegate = DropdownDelegate(
                items_by_column,
                self.case_table,
                option_provider=self._dropdown_options_for_index,
            )
            self.case_table.setItemDelegate(delegate)
            self.case_table.dropdown_delegate = delegate

    def _dropdown_options_for_index(self, index) -> tuple[str, ...]:  # noqa: ANN001
        if not index.isValid():
            return ()
        column = self.case_model.columns[index.column()]
        if not column.dropdown:
            return ()
        case_id = self.session.case_order[index.row()]
        row_options = self.input_edit_controller.dropdown_options_for_case(
            case_id,
            column.key,
        )
        return self.dropdown_option_adapter.options_for_key(column.key, row_options)

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
        self.group_header = TableLinkedGroupHeader(
            self.case_table,
            self.case_model.columns,
            panel,
        )
        layout.addWidget(self.group_header)
        layout.addWidget(table)
        return panel

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
        if not self._can_mutate_rows():
            return
        inserted = self.table_edit_controller.append_row_span(1)
        if inserted is None:
            return
        first_row, last_row = inserted
        self._begin_insert_rows(first_row, last_row)
        self.table_edit_controller.append_empty_rows(1)
        self._end_insert_rows()
        self._refresh_after_row_change()

    def _delete_selected_or_last_row(self) -> None:
        if not self._can_mutate_rows():
            return
        rows = self._selected_case_rows()
        if not rows and len(self.session.case_store) > 0:
            rows = [len(self.session.case_store) - 1]
        self._remove_row_indexes(rows)

    def _reset_rows(self) -> None:
        if not self._can_mutate_rows():
            return
        self._begin_reset_models()
        self.table_edit_controller.reset_rows(DEFAULT_INITIAL_ROWS)
        self._end_reset_models()
        self.case_table.clear_undo_history()
        self._refresh_idle_session_projection()

    def _refresh(self) -> None:
        self.case_model.refresh()
        self._refresh_after_row_change()

    def _refresh_after_row_change(self) -> None:
        counts = self.session.summary_counts()
        self.summary_label.setText(
            "전체 {total}건 | 실행 중 {running}건 | 예측 완료 {completed}건 | 경고 {warnings}건 | 오류 {errors}건 | 입력 확인 {invalid}건 | 취소 {cancelled}건 | 변경됨 {dirty}건".format(
                **counts
            )
        )
        self._refresh_result_badge(counts)
        if not self.status_label.text():
            self.status_label.setText("대기 중")

    def _refresh_idle_session_projection(self) -> None:
        """Project one fully reset Predict session as idle."""
        self._set_running_state(False)
        self._refresh_after_row_change()
        self.status_label.setText("대기 중")

    def _refresh_result_badge(self, counts: dict[str, int]) -> None:
        if counts["running"]:
            self.result_badge.set_status(f"실행 중 {counts['running']}건", "running")
        elif counts["errors"]:
            self.result_badge.set_status(f"오류 {counts['errors']}건", "error")
        elif counts["invalid"]:
            self.result_badge.set_status(f"입력 확인 {counts['invalid']}건", "warning")
        elif counts["cancelled"]:
            self.result_badge.set_status(f"취소 {counts['cancelled']}건", "warning")
        elif counts["warnings"]:
            self.result_badge.set_status(f"경고 {counts['warnings']}건", "warning")
        elif counts["completed"]:
            self.result_badge.set_status(f"완료 {counts['completed']}건", "ready")
        else:
            self.result_badge.set_status("대기", "neutral")

    def _run_prediction(self) -> None:
        if self.prediction_controller.is_running:
            self.status_label.setText("예측이 이미 실행 중입니다.")
            return
        self.model_lifecycle_ui.refresh()
        if self._generation_refresh is not None and not self._generation_refresh():
            self.show_generation_status()
            return
        self._set_running_state(True)
        self.status_label.setText("예측 실행 중...")
        try:
            self.prediction_controller.start_all(
                result_callback=self._refresh_result_row,
                progress_callback=self._handle_prediction_progress,
                finished_callback=self._handle_prediction_finished,
            )
        except Exception:
            logger.exception("Predict start failed")
            self._set_running_state(False)
            self.status_label.setText(
                "예측 실행 중 문제가 발생했습니다. 잠시 후 다시 실행해 주세요."
            )
            return

    def _refresh_generation(self) -> None:
        if self._generation_refresh is None:
            self.status_label.setText("Up to date")
            return
        if self._generation_refresh():
            self.show_generation_status()
        else:
            self.show_generation_status()
        self.model_lifecycle_ui.refresh()

    def _cancel_prediction(self) -> None:
        self.prediction_controller.cancel()
        self.command_bar.cancel_button.setEnabled(False)
        self.status_label.setText("예측 취소 요청 중...")

    def _handle_prediction_progress(self, progress) -> None:  # noqa: ANN001
        percent = (
            int((progress.completed / progress.total) * 100) if progress.total else 0
        )
        self.status_label.setText(
            f"예측 진행: {progress.completed}/{progress.total} ({percent}%)"
        )

    def _handle_prediction_finished(self, summary: PredictionRunSummary) -> None:
        self._set_running_state(False)
        self._refresh_after_row_change()
        self.status_label.setText(prediction_summary_text(summary))

    def _refresh_result_row(self, result: ResultRow) -> None:
        self.case_model.refresh_case_id(result.case_id)
        self._refresh_after_row_change()

    def _handle_input_cell_edited(self, case_id: str, changed_key: str) -> None:
        self.input_edit_controller.handle_cell_edited(case_id, changed_key)
        self.case_model.refresh_case_id(case_id)
        mapping_status = self.dropdown_option_adapter.mapping_status().status
        if mapping_status == "missing":
            self.status_label.setText("입력이 변경되었습니다. mapping 파일이 없어 autofill은 제한됩니다.")
        elif mapping_status == "invalid":
            self.status_label.setText(
                "입력이 변경되었습니다. mapping 데이터가 유효하지 않아 autofill은 제한됩니다."
            )
        else:
            self.status_label.setText("입력이 변경되었습니다.")

    def _paste_from_clipboard(self) -> None:
        if not self._can_mutate_rows():
            return
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
        for group in self.table_edit_controller.removal_groups_for_indexes(rows):
            self._begin_remove_rows(group.first_row, group.last_row)
            self.table_edit_controller.remove_case_ids(group.case_ids)
            self._end_remove_rows()
        self._refresh_after_row_change()

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

    def _set_running_state(self, running: bool) -> None:
        self.command_bar.set_running(running)

    def _can_mutate_rows(self) -> bool:
        if self.prediction_controller.is_running:
            self.status_label.setText("예측 실행 중에는 행 변경을 할 수 없습니다.")
            return False
        return True
