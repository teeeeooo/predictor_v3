"""Qt-facing adapter for the Predict bulk-paste application transaction."""

from __future__ import annotations

from apps.predict.application.bulk_paste import (
    BulkPasteDestination,
    BulkPasteOutcome,
)


class PredictBulkPasteUiAdapter:
    """Bridge selection/model notifications and aggregate paste feedback."""

    def __init__(self, workspace) -> None:  # noqa: ANN001
        self._workspace = workspace

    def apply(
        self,
        text: str,
        top: int,
        left: int,
        bottom: int,
        right: int,
    ) -> int:
        """Apply toolbar/keyboard paste through one reset-bracketed transaction."""
        workspace = self._workspace
        if not workspace._can_mutate_rows():
            return 0
        if not (0 <= left < workspace.case_model.columnCount()):
            return 0
        column = workspace.case_model.columns[left]
        if not column.editable or not column.feature_identity:
            workspace.status_label.setText("편집 가능한 입력 셀을 선택해 주세요.")
            return 0
        selected_columns = sum(
            item.editable
            for item in workspace.case_model.columns[left:right + 1]
        )
        destination = BulkPasteDestination(
            start_row=top,
            start_feature_identity=column.feature_identity,
            selected_rows=bottom - top + 1,
            selected_columns=max(1, selected_columns),
        )
        workspace.model_group.begin_reset()
        outcome = workspace.bulk_paste_transaction.apply(text, destination)
        workspace.case_model.set_input_issues(outcome.issues)
        workspace.model_group.end_reset()
        workspace._reconcile_shared_case_selection()
        workspace._refresh_after_row_change()
        self._show_feedback(outcome)
        if outcome.applied and outcome.undo_id:
            undo_id = outcome.undo_id
            workspace.case_table.register_compound_undo(
                lambda: self.undo(undo_id)
            )
        return outcome.pasted_cells + outcome.derived_cells

    def undo(self, transaction_id: str) -> int:
        """Apply one compound paste undo through the same model boundary."""
        workspace = self._workspace
        if not workspace._can_mutate_rows():
            return 0
        workspace.model_group.begin_reset()
        outcome = workspace.bulk_paste_transaction.undo(transaction_id)
        workspace.case_model.set_input_issues(outcome.issues)
        workspace.model_group.end_reset()
        workspace._reconcile_shared_case_selection()
        workspace._refresh_after_row_change()
        if outcome.applied:
            workspace.status_label.setText(
                f"붙여넣기 실행 취소 완료: 추가 행 {outcome.expanded_rows}개 제거"
            )
        else:
            workspace.status_label.setText(outcome.message)
        return (
            outcome.pasted_cells + outcome.derived_cells + outcome.expanded_rows
            if outcome.applied else 0
        )

    def clear_history(self) -> None:
        """Release UI and canonical paste undo after a row/runtime context reset."""
        self._workspace.bulk_paste_transaction.clear_undo_history()
        self._workspace.case_table.clear_undo_history()

    def clear_issues_for_case(self, case_id: str) -> None:
        """Reproject issues after the ordinary single-cell owner changes a row."""
        issues = self._workspace.bulk_paste_transaction.clear_issues_for_case(case_id)
        self._workspace.case_model.set_input_issues(issues)

    def _show_feedback(self, outcome: BulkPasteOutcome) -> None:
        workspace = self._workspace
        if not outcome.applied:
            workspace.status_label.setText(outcome.message)
            return
        issue_rows = len({issue.case_id for issue in outcome.issues})
        message = (
            f"붙여넣기 완료: 입력 {outcome.pasted_cells}개, "
            f"행 {outcome.expanded_rows}개 확장"
        )
        if outcome.issues:
            message += f", 확인 필요 {issue_rows}행/{len(outcome.issues)}셀"
        if outcome.truncated_cells:
            message += f", 입력 범위 밖 {outcome.truncated_cells}개 제외"
        workspace.status_label.setText(message)


__all__ = ["PredictBulkPasteUiAdapter"]
