"""Qt-free variable-size case storage."""

from collections.abc import Callable, Iterable

from apps.predict.state.case_row import CaseRow


class CaseStore:
    """Own ordered prediction cases without assuming a fixed row count."""

    def __init__(self, mutation_callback: Callable[[], None] | None = None) -> None:
        self._cases_by_id: dict[str, CaseRow] = {}
        self._case_order: list[str] = []
        self._next_case_number = 1
        self._mutation_callback = mutation_callback or (lambda: None)

    def bind_mutation_callback(self, callback: Callable[[], None]) -> None:
        self._mutation_callback = callback
        for case in self._cases_by_id.values():
            case.bind_mutation_callback(callback)

    @property
    def case_order(self) -> tuple[str, ...]:
        """Return case ids in UI row order."""
        return tuple(self._case_order)

    def __len__(self) -> int:
        return len(self._case_order)

    def append_empty_rows(self, count: int = 1) -> list[CaseRow]:
        """Append empty case rows and return the created rows."""
        if count < 0:
            raise ValueError("count must be non-negative")
        rows = [self._append_case() for _ in range(count)]
        if rows:
            self._mutation_callback()
        return rows

    def insert_empty_rows(self, index: int, count: int = 1) -> list[CaseRow]:
        """Insert empty case rows at index and return the created rows."""
        if count < 0:
            raise ValueError("count must be non-negative")
        insert_at = max(0, min(index, len(self._case_order)))
        rows = [self._create_case() for _ in range(count)]
        for offset, row in enumerate(rows):
            self._cases_by_id[row.case_id] = row
            self._case_order.insert(insert_at + offset, row.case_id)
        if rows:
            self._mutation_callback()
        return rows

    def remove_rows(self, case_ids: Iterable[str]) -> list[str]:
        """Remove cases by id and return ids that were removed."""
        requested = set(case_ids)
        removed: list[str] = []
        kept_order: list[str] = []
        for case_id in self._case_order:
            if case_id in requested:
                self._cases_by_id.pop(case_id, None)
                removed.append(case_id)
            else:
                kept_order.append(case_id)
        self._case_order = kept_order
        if removed:
            self._mutation_callback()
        return removed

    def remove_row_indexes(self, indexes: Iterable[int]) -> list[str]:
        """Remove cases by current row indexes."""
        ids = [
            self._case_order[index]
            for index in sorted(set(indexes))
            if 0 <= index < len(self._case_order)
        ]
        return self.remove_rows(ids)

    def update_cell_value(self, case_id: str, key: str, value: object) -> None:
        """Update one editable cell through the store."""
        self.get_case(case_id).set_input_value(key, value)

    def get_case(self, case_id: str) -> CaseRow:
        """Return a case by id."""
        try:
            return self._cases_by_id[case_id]
        except KeyError as exc:
            raise KeyError(f"unknown case_id: {case_id}") from exc

    def get_case_at(self, row_index: int) -> CaseRow:
        """Return a case by current row index."""
        return self.get_case(self._case_order[row_index])

    def _append_case(self) -> CaseRow:
        row = self._create_case()
        self._cases_by_id[row.case_id] = row
        self._case_order.append(row.case_id)
        return row

    def _create_case(self) -> CaseRow:
        case_id = f"case-{self._next_case_number:04d}"
        self._next_case_number += 1
        return CaseRow(case_id=case_id, _mutation_callback=self._mutation_callback)
