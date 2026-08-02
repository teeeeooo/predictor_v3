"""Qt-free Predict-owned bulk-paste transaction orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from apps.predict.application.bulk_paste_contract import (
    BulkPasteDestination,
    BulkPasteIssue,
    BulkPasteOutcome,
)
from apps.predict.application.bulk_paste_staging import (
    BaseOptionResolver,
    BulkPasteStager,
)
from apps.predict.state.predict_session import PredictSession


@dataclass(frozen=True)
class _UndoProjection:
    previous_issues: tuple[BulkPasteIssue, ...]
    pasted_cells: int
    derived_cells: int


class BulkPasteTransaction:
    """Parse, stage, resolve, validate, commit, and undo one Predict paste."""

    def __init__(
        self,
        session: PredictSession,
        columns: Sequence[object],
        mapping_loader: Callable[[], object],
        base_option_resolver: BaseOptionResolver,
    ) -> None:
        self._session = session
        self._stager = BulkPasteStager(
            session, columns, base_option_resolver
        )
        self._mapping_loader = mapping_loader
        self._issues: tuple[BulkPasteIssue, ...] = ()
        self._undo: dict[str, _UndoProjection] = {}

    @property
    def issues(self) -> tuple[BulkPasteIssue, ...]:
        """Return issues for the latest committed/undone input state."""
        return self._issues

    def apply(self, text: str, destination: BulkPasteDestination) -> BulkPasteOutcome:
        """Apply a complete TSV payload as one atomic canonical mutation."""
        try:
            grid = self._stager.parse_and_expand(text, destination)
            if not grid:
                return BulkPasteOutcome(
                    False, issues=self._issues,
                    message="붙여넣을 TSV 값이 없습니다.",
                )
            start_column = self._stager.input_index_by_identity.get(
                destination.start_feature_identity
            )
            if start_column is None or destination.start_row < 0:
                return BulkPasteOutcome(
                    False, issues=self._issues,
                    message="편집 가능한 입력 셀을 선택해 주세요.",
                )
            mapping_data = self._mapping_loader()
            staged, pending_issues, pasted_cells, derived_cells, truncated = (
                self._stager.stage(
                    grid,
                    start_row=destination.start_row,
                    start_column=start_column,
                    mapping_data=mapping_data,
                )
            )
            previous_issues = self._issues
            commit = self._session.commit_input_transaction(
                staged, expected_revision=self._session.revision
            )
        except Exception as exc:
            return BulkPasteOutcome(
                False,
                issues=self._issues,
                message=f"붙여넣기를 적용하지 못했습니다: {type(exc).__name__}: {exc}",
            )

        staged_case_ids = {
            self._session.case_order[row.row_index] for row in staged
        }
        staged_issues = tuple(
            BulkPasteIssue(
                self._session.case_order[item.row_index],
                item.column_key,
                item.code,
                item.message,
            )
            for item in pending_issues
        )
        issues = tuple(
            issue for issue in previous_issues
            if issue.case_id not in staged_case_ids
        ) + staged_issues
        self._issues = issues
        undo_id = commit.transaction_id if (
            commit.affected_case_ids or commit.added_case_ids
        ) else ""
        if undo_id:
            self._undo[undo_id] = _UndoProjection(
                previous_issues, pasted_cells, derived_cells
            )
            if len(self._undo) > 64:
                oldest = next(iter(self._undo))
                self.discard_undo(oldest)
        else:
            self._session.discard_input_transaction(commit.transaction_id)
        return BulkPasteOutcome(
            True,
            pasted_cells=pasted_cells,
            derived_cells=derived_cells,
            expanded_rows=len(commit.added_case_ids),
            affected_case_ids=commit.affected_case_ids,
            issues=issues,
            undo_id=undo_id,
            truncated_cells=truncated,
        )

    def undo(self, transaction_id: str) -> BulkPasteOutcome:
        """Undo one committed paste while retaining fail-closed result history."""
        projection = self._undo.get(transaction_id)
        if projection is None:
            return BulkPasteOutcome(
                False, issues=self._issues,
                message="되돌릴 붙여넣기 작업이 없습니다.",
            )
        try:
            commit = self._session.undo_input_transaction(transaction_id)
        except Exception as exc:
            return BulkPasteOutcome(
                False,
                issues=self._issues,
                message=f"붙여넣기 실행 취소를 적용하지 못했습니다: {type(exc).__name__}: {exc}",
            )
        del self._undo[transaction_id]
        self._issues = projection.previous_issues
        return BulkPasteOutcome(
            True,
            pasted_cells=projection.pasted_cells,
            derived_cells=projection.derived_cells,
            expanded_rows=len(commit.added_case_ids),
            affected_case_ids=commit.affected_case_ids,
            issues=self._issues,
        )

    def discard_undo(self, transaction_id: str) -> None:
        """Release canonical and projection undo state together."""
        self._undo.pop(transaction_id, None)
        self._session.discard_input_transaction(transaction_id)

    def clear_undo_history(self) -> None:
        """Release every sealed paste command after a row/runtime context change."""
        for transaction_id in tuple(self._undo):
            self.discard_undo(transaction_id)

    def clear_issues_for_case(self, case_id: str) -> tuple[BulkPasteIssue, ...]:
        """Drop paste-time issues when the single-cell owner edits that row."""
        self._issues = tuple(
            issue for issue in self._issues if issue.case_id != case_id
        )
        return self._issues


__all__ = [
    "BulkPasteDestination",
    "BulkPasteIssue",
    "BulkPasteOutcome",
    "BulkPasteTransaction",
]
