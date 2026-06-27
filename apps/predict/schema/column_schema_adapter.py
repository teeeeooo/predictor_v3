"""Qt-free predictor column schema adapter."""

from dataclasses import dataclass
from typing import Any

from core.predictor_schema.columns import (
    AUTO_COLS,
    COLUMNS,
    DROPDOWN_COLS,
    DROPDOWN_TARGET,
    INPUT_COLS,
    RESULT_COLS,
)


@dataclass(frozen=True)
class PredictColumn:
    """Predict table column descriptor derived from core schema metadata."""

    index: int
    key: str
    header: str
    group: str
    width: int
    editable: bool
    dropdown: bool
    mapping: str
    dropdown_target: str
    ml_feature: str
    ml_target: str
    source: str
    mapping_key: str
    bg_color: str

    @property
    def is_input(self) -> bool:
        """Return whether this column belongs to user input."""
        return self.group == "input"

    @property
    def is_auto(self) -> bool:
        """Return whether this column belongs to auto-filled inputs."""
        return self.group == "auto"

    @property
    def is_result(self) -> bool:
        """Return whether this column belongs to prediction results."""
        return self.group == "result"


def build_predict_column_schema() -> tuple[PredictColumn, ...]:
    """Return every predictor column descriptor in core schema order."""
    return tuple(
        _column_from_metadata(index, metadata)
        for index, metadata in enumerate(COLUMNS)
    )


def build_input_column_schema() -> tuple[PredictColumn, ...]:
    """Return user-input and auto-filled columns for the input table."""
    return tuple(column for column in build_predict_column_schema() if column.key in _INPUT_KEYS)


def build_result_column_schema() -> tuple[PredictColumn, ...]:
    """Return result columns for the result table."""
    return tuple(column for column in build_predict_column_schema() if column.key in _RESULT_KEYS)


def dropdown_columns() -> tuple[PredictColumn, ...]:
    """Return dropdown-capable input columns."""
    return tuple(column for column in build_input_column_schema() if column.dropdown)


def column_by_key(key: str) -> PredictColumn:
    """Return one column descriptor by schema key."""
    try:
        return _COLUMNS_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"unknown predictor column key: {key}") from exc


def _column_from_metadata(index: int, metadata: dict[str, Any]) -> PredictColumn:
    key = str(metadata["key"])
    group = str(metadata.get("group", ""))
    readonly = bool(metadata.get("readonly", False))
    dropdown = metadata.get("type") == "dropdown" or key in DROPDOWN_COLS
    editable = group == "input" and not readonly
    return PredictColumn(
        index=index,
        key=key,
        header=str(metadata.get("header", key)),
        group=group,
        width=int(metadata.get("width", 100)),
        editable=editable,
        dropdown=dropdown,
        mapping=str(metadata.get("mapping", "")),
        dropdown_target=str(DROPDOWN_TARGET.get(key, "")),
        ml_feature=str(metadata.get("ml_feature", "")),
        ml_target=str(metadata.get("ml_target", "")),
        source=str(metadata.get("source", "")),
        mapping_key=str(metadata.get("mapping_key", "")),
        bg_color=str(metadata.get("bg_color", "")),
    )


_INPUT_KEYS = frozenset(INPUT_COLS) | frozenset(AUTO_COLS)
_RESULT_KEYS = frozenset(RESULT_COLS)
_COLUMNS_BY_KEY = {column.key: column for column in build_predict_column_schema()}
