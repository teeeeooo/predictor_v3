"""Atomic canonical input-state mutation for Predict bulk transactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from apps.predict.state.case_row import CaseRow
from apps.predict.state.result_state_boundary import copy_result


@dataclass(frozen=True)
class StagedCaseInput:
    """One final row state prepared outside the canonical session."""

    row_index: int
    input_values: dict[str, Any]
    autofill_values: dict[str, Any]
    dirty_fields: set[str]


@dataclass(frozen=True)
class InputTransactionCommit:
    """Canonical commit evidence and the sealed compound-undo identity."""

    transaction_id: str
    affected_case_ids: tuple[str, ...]
    added_case_ids: tuple[str, ...]


@dataclass
class _SessionSnapshot:
    case_order: tuple[str, ...]
    cases: dict[str, tuple[dict, dict, set, int]]
    next_case_number: int
    results: dict
    allowed_executions: dict
    revision: int


@dataclass
class _UndoState:
    before: _SessionSnapshot
    committed_case_order: tuple[str, ...]
    committed_values: dict[str, tuple[dict, dict]]
    expected_revision: int
    affected_existing_ids: tuple[str, ...]
    added_case_ids: tuple[str, ...]


class PredictInputTransactionAuthority:
    """Apply staged inputs atomically and issue one fail-closed undo command."""

    def __init__(self, session) -> None:  # noqa: ANN001
        self._session = session
        self._undo_states: dict[str, _UndoState] = {}

    def commit(
        self,
        staged_rows: tuple[StagedCaseInput, ...],
        *,
        expected_revision: int,
    ) -> InputTransactionCommit:
        """Commit complete row states or restore the exact pre-commit session."""
        if self._session.revision != expected_revision:
            raise ValueError("Predict session changed after bulk paste staging")
        self._validate_staged_rows(staged_rows)
        before = self._snapshot()
        try:
            required_rows = max(
                (row.row_index + 1 for row in staged_rows),
                default=len(before.case_order),
            )
            append_count = max(0, required_rows - len(before.case_order))
            added = self._session.case_store.append_empty_rows(append_count)
            added_ids = tuple(row.case_id for row in added)
            affected: list[str] = []
            for staged in staged_rows:
                case = self._session.case_store.get_case_at(staged.row_index)
                if self._apply_case_state(case, staged):
                    affected.append(case.case_id)

            for case_id in affected:
                self._session._allowed_executions.pop(case_id, None)
                self._session._mark_case_result_stale(case_id, "input_changed")
            if affected or added_ids:
                self._session._revision = before.revision + 1
            self._session._validate_canonical_state()
        except Exception:
            self._restore_exact(before)
            raise

        transaction_id = f"bulk-input-{uuid4().hex}"
        affected_ids = tuple(dict.fromkeys(affected))
        affected_existing = tuple(
            case_id for case_id in affected_ids if case_id in before.cases
        )
        committed_values = {
            case_id: (
                dict(self._session.case_store.get_case(case_id).input_values),
                dict(self._session.case_store.get_case(case_id).autofill_values),
            )
            for case_id in self._session.case_order
        }
        self._undo_states[transaction_id] = _UndoState(
            before=before,
            committed_case_order=self._session.case_order,
            committed_values=committed_values,
            expected_revision=self._session.revision,
            affected_existing_ids=affected_existing,
            added_case_ids=added_ids,
        )
        return InputTransactionCommit(transaction_id, affected_ids, added_ids)

    def undo(self, transaction_id: str) -> InputTransactionCommit:
        """Undo input shape/state without reviving pre-transaction results."""
        state = self._undo_states.get(transaction_id)
        if state is None:
            raise ValueError("bulk paste undo command is unavailable")
        self._validate_undo_target(state)
        current = self._snapshot()
        try:
            if state.added_case_ids:
                self._session.case_store.remove_rows(state.added_case_ids)
            restored: list[str] = []
            for case_id in state.affected_existing_ids:
                case = self._session.case_store.get_case(case_id)
                inputs, autofill, dirty, _old_revision = state.before.cases[case_id]
                changed = (
                    case.input_values != inputs
                    or case.autofill_values != autofill
                    or case.dirty_fields != dirty
                )
                case.input_values = dict(inputs)
                case.autofill_values = dict(autofill)
                case.dirty_fields = set(dirty)
                if changed:
                    case.input_revision += 1
                    restored.append(case_id)
            for case_id in restored:
                self._session._allowed_executions.pop(case_id, None)
                self._session._mark_case_result_stale(case_id, "input_changed")
            self._session._revision = current.revision + 1
            self._session._validate_canonical_state()
        except Exception:
            self._restore_exact(current)
            raise
        del self._undo_states[transaction_id]
        return InputTransactionCommit(
            transaction_id,
            tuple(restored),
            state.added_case_ids,
        )

    def discard(self, transaction_id: str) -> None:
        """Release an undo command when its UI history is invalidated."""
        self._undo_states.pop(transaction_id, None)

    def reauthorize(self, transaction_id: str) -> None:
        """Seal a new revision only after UI chronology restored exact inputs."""
        state = self._undo_states.get(transaction_id)
        if state is None:
            raise ValueError("bulk paste undo command is unavailable")
        self._validate_committed_values(state)
        state.expected_revision = self._session.revision

    def _apply_case_state(self, case: CaseRow, staged: StagedCaseInput) -> bool:
        value_changed = (
            case.input_values != staged.input_values
            or case.autofill_values != staged.autofill_values
        )
        dirty_changed = case.dirty_fields != staged.dirty_fields
        if not value_changed and not dirty_changed:
            return False
        case.input_values = dict(staged.input_values)
        case.autofill_values = dict(staged.autofill_values)
        case.dirty_fields = set(staged.dirty_fields)
        if value_changed:
            case.input_revision += 1
        return value_changed

    def _snapshot(self) -> _SessionSnapshot:
        store = self._session.case_store
        return _SessionSnapshot(
            case_order=store.case_order,
            cases={
                case_id: (
                    dict(case.input_values),
                    dict(case.autofill_values),
                    set(case.dirty_fields),
                    case.input_revision,
                )
                for case_id in store.case_order
                for case in (store.get_case(case_id),)
            },
            next_case_number=store._next_case_number,
            results={
                case_id: copy_result(result)
                for case_id, result in self._session._results_by_case_id.items()
            },
            allowed_executions=dict(self._session._allowed_executions),
            revision=self._session.revision,
        )

    def _restore_exact(self, snapshot: _SessionSnapshot) -> None:
        store = self._session.case_store
        store._case_order = list(snapshot.case_order)
        store._cases_by_id = {
            case_id: CaseRow(
                case_id=case_id,
                input_values=dict(values[0]),
                autofill_values=dict(values[1]),
                dirty_fields=set(values[2]),
                input_revision=values[3],
                _mutation_callback=self._session._touch,
            )
            for case_id, values in snapshot.cases.items()
        }
        store._next_case_number = snapshot.next_case_number
        self._session._results_by_case_id = {
            case_id: copy_result(result)
            for case_id, result in snapshot.results.items()
        }
        self._session._allowed_executions = dict(snapshot.allowed_executions)
        self._session._revision = snapshot.revision

    def _validate_staged_rows(
        self, staged_rows: tuple[StagedCaseInput, ...]
    ) -> None:
        indexes = tuple(row.row_index for row in staged_rows)
        if any(index < 0 for index in indexes) or len(indexes) != len(set(indexes)):
            raise ValueError("bulk paste staged row indexes are invalid")
        if indexes and indexes != tuple(range(min(indexes), max(indexes) + 1)):
            raise ValueError("bulk paste staged rows must be contiguous")

    def _validate_undo_target(self, state: _UndoState) -> None:
        if self._session.revision != state.expected_revision:
            raise ValueError("Predict session changed after bulk paste")
        self._validate_committed_values(state)

    def _validate_committed_values(self, state: _UndoState) -> None:
        if self._session.case_order != state.committed_case_order:
            raise ValueError("Predict row shape changed after bulk paste")
        for case_id, expected in state.committed_values.items():
            case = self._session.case_store.get_case(case_id)
            actual = (case.input_values, case.autofill_values)
            if any(
                _without_empty_values(actual_values)
                != _without_empty_values(expected_values)
                for actual_values, expected_values in zip(actual, expected)
            ):
                raise ValueError("Predict inputs changed after bulk paste")


def _without_empty_values(values: dict) -> dict:
    """Normalize the table owner's equivalent blank/missing cell states."""
    return {
        key: value for key, value in values.items()
        if value is not None and value != ""
    }


__all__ = [
    "InputTransactionCommit",
    "PredictInputTransactionAuthority",
    "StagedCaseInput",
]
