"""Toolkit-neutral models for row-per-case calculator batch surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class BatchColumnRole(str, Enum):
    INPUT = "input"
    RESULT = "result"
    STATUS = "status"


class BatchRowState(str, Enum):
    PENDING = "pending"
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class BatchColumnSpec:
    key: str
    label: str
    role: BatchColumnRole
    width_chars: int = 12


@dataclass(frozen=True)
class BatchProfileSpec:
    profile_key: str
    title: str
    columns: tuple[BatchColumnSpec, ...]
    default_rows: tuple[Mapping[str, str], ...]

    def __post_init__(self) -> None:
        keys = tuple(column.key for column in self.columns)
        if len(set(keys)) != len(keys):
            raise ValueError("batch column keys must be unique")
        if not any(column.role is BatchColumnRole.INPUT for column in self.columns):
            raise ValueError("batch profile requires at least one input column")

    def columns_for_role(self, role: BatchColumnRole) -> tuple[BatchColumnSpec, ...]:
        return tuple(column for column in self.columns if column.role is role)

    @property
    def input_keys(self) -> tuple[str, ...]:
        return tuple(column.key for column in self.columns_for_role(BatchColumnRole.INPUT))

    @property
    def result_keys(self) -> tuple[str, ...]:
        return tuple(column.key for column in self.columns_for_role(BatchColumnRole.RESULT))

    @property
    def status_keys(self) -> tuple[str, ...]:
        return tuple(column.key for column in self.columns_for_role(BatchColumnRole.STATUS))


class BatchTableModel:
    """Text storage for a batch table; calculator logic lives in handlers."""

    def __init__(self, spec: BatchProfileSpec) -> None:
        self.spec = spec
        self.rows: list[dict[str, str]] = []
        for values in spec.default_rows:
            self.add_row(values)

    def add_row(self, values: Mapping[str, str] | None = None) -> int:
        row = {column.key: "" for column in self.spec.columns}
        if values:
            unknown = set(values) - set(row)
            if unknown:
                raise KeyError(f"Unknown batch columns: {sorted(unknown)!r}")
            row.update({key: str(value) for key, value in values.items()})
        self.rows.append(row)
        return len(self.rows) - 1

    def remove_row(self, row_index: int) -> None:
        if len(self.rows) <= 1:
            return
        del self.rows[row_index]

    def row_values(self, row_index: int) -> dict[str, str]:
        return dict(self.rows[row_index])

    def input_values(self, row_index: int) -> dict[str, str]:
        row = self.rows[row_index]
        return {key: row.get(key, "") for key in self.spec.input_keys}

    def set_cell(self, row_index: int, column_key: str, value: str) -> None:
        if column_key not in self.rows[row_index]:
            raise KeyError(f"Unknown batch column: {column_key!r}")
        self.rows[row_index][column_key] = value

    def set_results(self, row_index: int, values: Mapping[str, str]) -> None:
        writable = set(self.spec.result_keys) | set(self.spec.status_keys)
        for key, value in values.items():
            if key not in writable:
                raise KeyError(f"Cannot write non-result batch column: {key!r}")
            self.rows[row_index][key] = value

    def clear_results(self) -> None:
        for row in self.rows:
            for key in (*self.spec.result_keys, *self.spec.status_keys):
                row[key] = ""
