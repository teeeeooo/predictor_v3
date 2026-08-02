"""Final-combination staging for a Predict bulk-paste transaction."""

from __future__ import annotations

from typing import Any, Callable, Sequence

from apps.predict.application.bulk_paste_contract import (
    BulkPasteDestination,
    StagedBulkPasteIssue,
)
from apps.predict.state.input_transaction import StagedCaseInput
from core.mapping.autofill import build_autofill_updates


BaseOptionResolver = Callable[[str, object], tuple[str, ...]]


class BulkPasteStager:
    """Stage raw input, existing mapping policy, derived values, and issues."""

    def __init__(
        self,
        session,
        columns: Sequence[object],
        base_option_resolver: BaseOptionResolver,
    ) -> None:  # noqa: ANN001
        self._session = session
        self._columns = tuple(columns)
        self._columns_by_key = {column.key: column for column in self._columns}
        self.input_columns = tuple(
            column for column in self._columns
            if column.is_input and column.editable
        )
        self.input_index_by_identity = {
            column.feature_identity: index
            for index, column in enumerate(self.input_columns)
        }
        self._base_option_resolver = base_option_resolver

    def parse_and_expand(
        self, text: str, destination: BulkPasteDestination
    ) -> list[list[str]]:
        """Parse the complete TSV payload before any canonical mutation."""
        grid = _parse_tsv(text)
        if not grid:
            return []
        return _expand_grid(grid, destination)

    def stage(
        self,
        grid: list[list[str]],
        *,
        start_row: int,
        start_column: int,
        mapping_data: object,
    ) -> tuple[
        tuple[StagedCaseInput, ...],
        tuple[StagedBulkPasteIssue, ...],
        int,
        int,
        int,
    ]:
        """Return complete row states resolved from each final raw combination."""
        staged_rows = []
        issues = []
        pasted_cells = derived_cells = truncated_cells = 0
        mapping = mapping_data if isinstance(mapping_data, dict) else {}
        for offset, raw_row in enumerate(grid):
            row_index = start_row + offset
            existing = (
                self._session.case_store.get_case_at(row_index)
                if row_index < len(self._session.case_store)
                else None
            )
            before_inputs = dict(existing.input_values) if existing else {}
            before_autofill = dict(existing.autofill_values) if existing else {}
            inputs = dict(before_inputs)
            autofill = dict(before_autofill)
            dirty = set(existing.dirty_fields) if existing else set()
            destination_columns = self.input_columns[start_column:]
            explicit_columns = destination_columns[:len(raw_row)]
            explicit_keys = {column.key for column in explicit_columns}
            truncated_cells += max(0, len(raw_row) - len(destination_columns))
            for column, value in zip(explicit_columns, raw_row):
                if str(inputs.get(column.key, "")) != value:
                    pasted_cells += 1
                    dirty.add(column.key)
                inputs[column.key] = value

            row_options: dict[str, tuple[str, ...]] = {}
            for key in _resolution_order(explicit_columns):
                resolution = build_autofill_updates(
                    {**autofill, **inputs}, key, mapping
                )
                row_options.update(resolution.dropdown_options)
                for update in resolution.updates:
                    target = self._columns_by_key.get(update.key)
                    if target is None:
                        continue
                    if target.is_auto:
                        autofill[update.key] = update.value
                    elif target.is_input and update.key not in explicit_keys:
                        if inputs.get(update.key, "") != update.value:
                            dirty.add(update.key)
                        inputs[update.key] = update.value

            final_values = {**autofill, **inputs}
            for key in ("odu", "fin_type"):
                row_options.update(
                    build_autofill_updates(final_values, key, mapping).dropdown_options
                )
            issues.extend(
                self._validate_final_row(row_index, inputs, row_options, mapping_data)
            )
            derived_cells += sum(
                before_inputs.get(key, "") != value
                for key, value in inputs.items()
                if key not in explicit_keys
            )
            derived_cells += sum(
                before_autofill.get(key, "") != value
                for key, value in autofill.items()
            )
            staged_rows.append(StagedCaseInput(row_index, inputs, autofill, dirty))
        return tuple(staged_rows), tuple(issues), pasted_cells, derived_cells, truncated_cells

    def _validate_final_row(
        self,
        row_index: int,
        inputs: dict[str, Any],
        row_options: dict[str, tuple[str, ...]],
        mapping_data: object,
    ) -> list[StagedBulkPasteIssue]:
        issues = []
        for column in self.input_columns:
            value = inputs.get(column.key, "")
            text = "" if value is None else str(value).strip()
            if text and column.ml_feature:
                try:
                    float(value)
                except (TypeError, ValueError):
                    issues.append(StagedBulkPasteIssue(
                        row_index, column.key, "invalid_numeric",
                        f"{column.header}: 숫자로 입력해 주세요.",
                    ))
            if not text or not column.dropdown:
                continue
            options = (
                row_options[column.key]
                if column.key in row_options
                else self._base_option_resolver(column.key, mapping_data)
            )
            if options and text not in options:
                issues.append(StagedBulkPasteIssue(
                    row_index, column.key, "invalid_mapping_combination",
                    f"{column.header}: 현재 입력 조합에서 사용할 수 없는 값입니다.",
                ))
        return issues


def _parse_tsv(text: str) -> list[list[str]]:
    if not isinstance(text, str):
        raise TypeError("TSV input must be a string")
    if text == "":
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    rows = normalized.split("\n")
    if rows and rows[-1] == "":
        rows.pop()
    return [row.split("\t") for row in rows]


def _expand_grid(
    grid: list[list[str]], destination: BulkPasteDestination
) -> list[list[str]]:
    selected_rows = max(1, destination.selected_rows)
    selected_columns = max(1, destination.selected_columns)
    if len(grid) == 1 and len(grid[0]) == 1:
        return [list(grid[0]) * selected_columns for _ in range(selected_rows)]
    if len(grid) == 1 and len(grid[0]) == selected_columns and selected_rows > 1:
        return [list(grid[0]) for _ in range(selected_rows)]
    return grid


def _resolution_order(columns: Sequence[object]) -> tuple[str, ...]:
    keys = [column.key for column in columns]
    priority = ("idu", "odu", "fin_type", "pi", "row", "compressor")
    return tuple(
        [key for key in priority if key in keys]
        + [key for key in keys if key not in priority]
    )


__all__ = ["BaseOptionResolver", "BulkPasteStager"]
