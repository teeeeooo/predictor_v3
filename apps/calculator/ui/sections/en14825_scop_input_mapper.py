"""SCOP section input mapping helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from apps.calculator.ui.en14825 import ScopPointInput, ScopTableModel
from apps.calculator.ui.table_grid_model import parse_numeric_cell


@dataclass(frozen=True)
class ScopInputMapping:
    """Parsed SCOP point inputs and invalid text fields."""

    inputs: dict[str, ScopPointInput]
    invalid_fields: dict[str, str]


def build_scop_point_inputs(text_values: Mapping[str, str]) -> ScopInputMapping:
    """Parse SCOP table text values and build point input models."""
    parsed_values: dict[str, float | None] = {}
    invalid_fields: dict[str, str] = {}

    for field_key, raw_value in text_values.items():
        stripped = raw_value.strip()
        if not stripped:
            parsed_values[field_key] = None
            continue
        try:
            parsed_values[field_key] = parse_numeric_cell(raw_value)
        except ValueError:
            parsed_values[field_key] = None
            invalid_fields[field_key] = "숫자 입력 필요"

    inputs = {
        col: ScopPointInput(
            declared_capacity=parsed_values.get(f"declared_capacity_{col}"),
            declared_cop=parsed_values.get(f"declared_cop_{col}"),
            tested_capacity=parsed_values.get(f"tested_capacity_{col}"),
            tested_power=parsed_values.get(f"tested_power_{col}"),
        )
        for col in ScopTableModel.COL_KEYS
    }

    return ScopInputMapping(inputs=inputs, invalid_fields=invalid_fields)
