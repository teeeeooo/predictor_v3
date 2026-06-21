"""Headless two-row matrix models for calculator batch surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

CellAddress = tuple[int, int]


class MatrixPhysicalRowType(str, Enum):
    CAPACITY = "capacity"
    POWER = "power"


class MatrixCellKind(str, Enum):
    CASE = "case"
    ROW_TYPE = "row_type"
    INPUT = "input"
    RESULT = "result"
    BLANK_READ_ONLY = "blank_read_only"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class MatrixMeasurementPointSpec:
    key: str
    label: str
    input_keys_by_row_type: Mapping[MatrixPhysicalRowType, str | None]
    width_chars: int = 12

    def input_key_for(self, row_type: MatrixPhysicalRowType) -> str | None:
        return self.input_keys_by_row_type.get(row_type)


@dataclass(frozen=True)
class MatrixCellDescriptor:
    kind: MatrixCellKind
    logical_case_index: int
    physical_row_type: MatrixPhysicalRowType
    column_key: str
    input_key: str | None = None
    result_key: str | None = None

    @property
    def editable(self) -> bool:
        return self.kind is MatrixCellKind.INPUT and self.input_key is not None

    @property
    def read_only(self) -> bool:
        return self.kind in {
            MatrixCellKind.CASE,
            MatrixCellKind.ROW_TYPE,
            MatrixCellKind.RESULT,
            MatrixCellKind.BLANK_READ_ONLY,
            MatrixCellKind.NOT_APPLICABLE,
        }

    @property
    def blank_read_only(self) -> bool:
        return self.kind is MatrixCellKind.BLANK_READ_ONLY

    @property
    def not_applicable(self) -> bool:
        return self.kind is MatrixCellKind.NOT_APPLICABLE


@dataclass(frozen=True)
class BatchMatrixSpec:
    profile_key: str
    title: str
    physical_rows: tuple[MatrixPhysicalRowType, ...]
    row_type_labels: Mapping[MatrixPhysicalRowType, str]
    measurement_points: tuple[MatrixMeasurementPointSpec, ...]
    result_metrics: tuple[tuple[str, str, int], ...]
    default_cases: tuple[Mapping[str, str], ...] = ()

    @property
    def column_count(self) -> int:
        return 2 + len(self.measurement_points) + len(self.result_metrics)

    @property
    def measurement_start_column(self) -> int:
        return 2

    @property
    def result_start_column(self) -> int:
        return self.measurement_start_column + len(self.measurement_points)

    @property
    def input_keys(self) -> tuple[str, ...]:
        keys: list[str] = []
        for point in self.measurement_points:
            for row_type in self.physical_rows:
                key = point.input_key_for(row_type)
                if key is not None and key not in keys:
                    keys.append(key)
        return tuple(keys)

    @property
    def result_keys(self) -> tuple[str, ...]:
        return tuple(key for key, _label, _width in self.result_metrics)

    def physical_row_count(self, logical_case_count: int) -> int:
        return max(0, logical_case_count) * len(self.physical_rows)

    def logical_case_index_from_physical_row(self, row: int) -> int:
        self._check_nonnegative_row(row)
        return row // len(self.physical_rows)

    def row_type_from_physical_row(self, row: int) -> MatrixPhysicalRowType:
        self._check_nonnegative_row(row)
        return self.physical_rows[row % len(self.physical_rows)]

    def resolve_cell(self, position: CellAddress) -> MatrixCellDescriptor:
        row, column = position
        self._check_nonnegative_row(row)
        if column < 0 or column >= self.column_count:
            raise IndexError(f"matrix column out of range: {column}")
        logical_case = self.logical_case_index_from_physical_row(row)
        row_type = self.row_type_from_physical_row(row)
        first_row_type = self.physical_rows[0]
        if column == 0:
            if row_type is first_row_type:
                return MatrixCellDescriptor(
                    MatrixCellKind.CASE, logical_case, row_type, "case"
                )
            return MatrixCellDescriptor(
                MatrixCellKind.BLANK_READ_ONLY, logical_case, row_type, "case"
            )
        if column == 1:
            return MatrixCellDescriptor(
                MatrixCellKind.ROW_TYPE, logical_case, row_type, "row_type"
            )
        if column < self.result_start_column:
            point = self.measurement_points[column - self.measurement_start_column]
            input_key = point.input_key_for(row_type)
            if input_key is None:
                return MatrixCellDescriptor(
                    MatrixCellKind.NOT_APPLICABLE, logical_case, row_type, point.key
                )
            return MatrixCellDescriptor(
                MatrixCellKind.INPUT,
                logical_case,
                row_type,
                point.key,
                input_key=input_key,
            )
        metric_key, _metric_label, _width = self.result_metrics[
            column - self.result_start_column
        ]
        if row_type is first_row_type:
            return MatrixCellDescriptor(
                MatrixCellKind.RESULT,
                logical_case,
                row_type,
                metric_key,
                result_key=metric_key,
            )
        return MatrixCellDescriptor(
            MatrixCellKind.BLANK_READ_ONLY, logical_case, row_type, metric_key
        )

    def resolve_input_key(self, position: CellAddress) -> str | None:
        return self.resolve_cell(position).input_key

    def is_editable(self, position: CellAddress) -> bool:
        return self.resolve_cell(position).editable

    def is_read_only(self, position: CellAddress) -> bool:
        return self.resolve_cell(position).read_only

    def is_blank_read_only(self, position: CellAddress) -> bool:
        return self.resolve_cell(position).blank_read_only

    def is_not_applicable(self, position: CellAddress) -> bool:
        return self.resolve_cell(position).not_applicable

    def display_text(
        self,
        position: CellAddress,
        case_data: Mapping[str, str],
        result_data: Mapping[str, str] | None = None,
    ) -> str:
        cell = self.resolve_cell(position)
        if cell.kind is MatrixCellKind.CASE:
            return str(cell.logical_case_index + 1)
        if cell.kind is MatrixCellKind.ROW_TYPE:
            row_type = self.row_type_from_physical_row(position[0])
            return self.row_type_labels[row_type]
        if cell.kind is MatrixCellKind.INPUT and cell.input_key is not None:
            return str(case_data.get(cell.input_key, ""))
        if cell.kind is MatrixCellKind.RESULT and cell.result_key is not None:
            return str((result_data or {}).get(cell.result_key, ""))
        return ""

    def editable_targets(
        self, values: Mapping[CellAddress, str]
    ) -> dict[CellAddress, str]:
        return {
            position: value
            for position, value in values.items()
            if self.is_editable(position)
        }

    def snapshot_cases(
        self, cases: tuple[Mapping[str, str], ...] | list[Mapping[str, str]]
    ) -> tuple[dict[str, str], ...]:
        known = set(self.input_keys) | set(self.result_keys)
        return tuple(
            {key: str(value) for key, value in case.items() if key in known}
            for case in cases
        )

    def restore_cases(
        self, snapshot: tuple[Mapping[str, str], ...] | list[Mapping[str, str]]
    ) -> list[dict[str, str]]:
        return [dict(case) for case in self.snapshot_cases(snapshot)]

    @staticmethod
    def _check_nonnegative_row(row: int) -> None:
        if row < 0:
            raise IndexError(f"matrix row out of range: {row}")


DECLARED_CAPACITY = "declared_capacity"
FULL_CAPACITY = "full_capacity"
FULL_POWER = "full_power"
HALF_CAPACITY = "half_capacity"
HALF_POWER = "half_power"
CSPF = "cspf"
CSEC = "csec"


HONG_KONG_CSPF_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="hong_kong_cspf",
    title="Hong Kong CSPF Batch Matrix",
    physical_rows=(
        MatrixPhysicalRowType.CAPACITY,
        MatrixPhysicalRowType.POWER,
    ),
    row_type_labels=MappingProxyType(
        {
            MatrixPhysicalRowType.CAPACITY: "Capacity",
            MatrixPhysicalRowType.POWER: "Power",
        }
    ),
    measurement_points=(
        MatrixMeasurementPointSpec(
            "declared",
            "Declared",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: DECLARED_CAPACITY,
                    MatrixPhysicalRowType.POWER: None,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_full",
            "35 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: FULL_CAPACITY,
                    MatrixPhysicalRowType.POWER: FULL_POWER,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_half",
            "35 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: HALF_CAPACITY,
                    MatrixPhysicalRowType.POWER: HALF_POWER,
                }
            ),
        ),
    ),
    result_metrics=((CSPF, "CSPF", 9), (CSEC, "CSEC", 10)),
    default_cases=(
        {},
        {},
        {},
        {},
        {},
    ),
)
