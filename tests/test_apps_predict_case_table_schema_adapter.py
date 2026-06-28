"""Unified Predict case table schema adapter tests."""

import subprocess
import sys

from apps.predict.schema.case_table_schema_adapter import (
    auto_columns,
    build_case_table_column_schema,
    column_by_key,
    dropdown_columns,
    input_columns,
    result_columns,
    status_columns,
)
from core.predictor_schema.columns import (
    AUTO_COLS,
    COLUMNS,
    DROPDOWN_COLS,
    INPUT_COLS,
    RESULT_COLS,
)


def test_case_table_schema_preserves_core_order_before_virtual_status_columns():
    schema = build_case_table_column_schema()
    core_keys = [column["key"] for column in COLUMNS]

    assert [column.key for column in schema[: len(core_keys)]] == core_keys
    assert [column.key for column in schema[-2:]] == ["status", "message"]
    assert [column.index for column in schema] == list(range(len(schema)))


def test_case_table_schema_groups_match_core_owner():
    assert [column.key for column in input_columns()] == INPUT_COLS
    assert [column.key for column in auto_columns()] == AUTO_COLS
    assert [column.key for column in result_columns()] == RESULT_COLS
    assert [column.key for column in status_columns()] == ["status", "message"]


def test_status_columns_are_virtual_app_side_columns():
    core_keys = {column["key"] for column in COLUMNS}

    for column in status_columns():
        assert column.key not in core_keys
        assert not column.core_key
        assert column.virtual
        assert column.read_only
        assert column.copyable


def test_only_input_columns_are_editable():
    schema = build_case_table_column_schema()

    assert all(column.editable for column in input_columns())
    assert all(not column.editable for column in auto_columns())
    assert all(not column.editable for column in result_columns())
    assert all(not column.editable for column in status_columns())
    assert all(column.read_only == (not column.editable) for column in schema)


def test_result_and_status_columns_are_read_only_but_copyable():
    readonly_columns = result_columns() + status_columns()

    assert all(column.read_only for column in readonly_columns)
    assert all(column.copyable for column in readonly_columns)


def test_dropdown_columns_follow_core_dropdown_order():
    dropdown_schema = dropdown_columns()

    assert [column.key for column in dropdown_schema] == DROPDOWN_COLS
    assert all(column.dropdown for column in dropdown_schema)
    assert column_by_key("odu").dropdown_target == "odu"


def test_case_table_schema_adapter_is_qt_free():
    code = (
        "import sys; "
        "from apps.predict.schema.case_table_schema_adapter "
        "import build_case_table_column_schema; "
        "assert build_case_table_column_schema(); "
        "assert 'PySide6' not in sys.modules; "
        "qt_binding = 'Py' + 'Qt5'; "
        "assert qt_binding not in sys.modules"
    )
    subprocess.run([sys.executable, "-B", "-c", code], check=True)
