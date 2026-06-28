"""Qt-free unified case table display schema adapter."""

from dataclasses import dataclass

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_predict_column_schema,
)


@dataclass(frozen=True)
class UnifiedCaseColumn:
    """Display column descriptor for the unified Predict case table."""

    index: int
    key: str
    header: str
    group: str
    width: int
    editable: bool
    dropdown: bool
    core_key: bool
    virtual: bool
    read_only: bool
    copyable: bool
    source: str
    source_key: str
    mapping: str
    dropdown_target: str
    ml_feature: str
    ml_target: str
    bg_color: str

    @property
    def is_input(self) -> bool:
        """Return whether this column belongs to user input."""
        return self.group == GROUP_INPUT

    @property
    def is_auto(self) -> bool:
        """Return whether this column belongs to auto-filled/calculated data."""
        return self.group == GROUP_AUTO

    @property
    def is_result(self) -> bool:
        """Return whether this column belongs to prediction results."""
        return self.group == GROUP_RESULT

    @property
    def is_status(self) -> bool:
        """Return whether this column belongs to status/warning display."""
        return self.group == GROUP_STATUS


GROUP_INPUT = "input"
GROUP_AUTO = "auto"
GROUP_RESULT = "result"
GROUP_STATUS = "status"

STATUS_COLUMNS = (
    {
        "key": "status",
        "header": "Status",
        "width": 92,
        "source": "result_status",
        "source_key": "status",
    },
    {
        "key": "message",
        "header": "Warning / Error",
        "width": 150,
        "source": "result_message",
        "source_key": "message",
    },
)


def build_case_table_column_schema() -> tuple[UnifiedCaseColumn, ...]:
    """Return unified case-table columns in display order."""
    columns = [
        _from_predict_column(index, column)
        for index, column in enumerate(build_predict_column_schema())
    ]
    start = len(columns)
    columns.extend(
        _virtual_status_column(start + offset, metadata)
        for offset, metadata in enumerate(STATUS_COLUMNS)
    )
    return tuple(columns)


def input_columns() -> tuple[UnifiedCaseColumn, ...]:
    """Return editable input columns."""
    return _columns_by_group(GROUP_INPUT)


def auto_columns() -> tuple[UnifiedCaseColumn, ...]:
    """Return auto-fill/calculated columns."""
    return _columns_by_group(GROUP_AUTO)


def result_columns() -> tuple[UnifiedCaseColumn, ...]:
    """Return prediction result columns."""
    return _columns_by_group(GROUP_RESULT)


def status_columns() -> tuple[UnifiedCaseColumn, ...]:
    """Return app-side status/warning columns."""
    return _columns_by_group(GROUP_STATUS)


def dropdown_columns() -> tuple[UnifiedCaseColumn, ...]:
    """Return dropdown-capable input columns."""
    return tuple(column for column in input_columns() if column.dropdown)


def column_by_key(key: str) -> UnifiedCaseColumn:
    """Return one unified case-table column by key."""
    try:
        return _COLUMNS_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"unknown unified case table column key: {key}") from exc


def _columns_by_group(group: str) -> tuple[UnifiedCaseColumn, ...]:
    return tuple(column for column in _CASE_TABLE_COLUMNS if column.group == group)


def _from_predict_column(index: int, column: PredictColumn) -> UnifiedCaseColumn:
    source = _source_for_group(column.group)
    editable = column.group == GROUP_INPUT and column.editable
    read_only = not editable
    return UnifiedCaseColumn(
        index=index,
        key=column.key,
        header=column.header,
        group=column.group,
        width=column.width,
        editable=editable,
        dropdown=column.dropdown,
        core_key=True,
        virtual=False,
        read_only=read_only,
        copyable=True,
        source=source,
        source_key=column.key,
        mapping=column.mapping,
        dropdown_target=column.dropdown_target,
        ml_feature=column.ml_feature,
        ml_target=column.ml_target,
        bg_color=column.bg_color,
    )


def _virtual_status_column(
    index: int,
    metadata: dict[str, object],
) -> UnifiedCaseColumn:
    return UnifiedCaseColumn(
        index=index,
        key=str(metadata["key"]),
        header=str(metadata["header"]),
        group=GROUP_STATUS,
        width=int(metadata["width"]),
        editable=False,
        dropdown=False,
        core_key=False,
        virtual=True,
        read_only=True,
        copyable=True,
        source=str(metadata["source"]),
        source_key=str(metadata["source_key"]),
        mapping="",
        dropdown_target="",
        ml_feature="",
        ml_target="",
        bg_color="",
    )


def _source_for_group(group: str) -> str:
    if group == GROUP_INPUT:
        return "input_values"
    if group == GROUP_AUTO:
        return "autofill_values"
    if group == GROUP_RESULT:
        return "result_values"
    return ""


_CASE_TABLE_COLUMNS = build_case_table_column_schema()
_COLUMNS_BY_KEY = {column.key: column for column in _CASE_TABLE_COLUMNS}
