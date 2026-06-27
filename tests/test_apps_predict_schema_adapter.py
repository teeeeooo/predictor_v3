"""Predict app schema adapter contract tests."""

import subprocess
import sys

from apps.predict.schema.column_schema_adapter import (
    build_input_column_schema,
    build_predict_column_schema,
    build_result_column_schema,
    column_by_key,
    dropdown_columns,
)
from core.predictor_schema.columns import (
    AUTO_COLS,
    COLUMNS,
    DROPDOWN_COLS,
    INPUT_COLS,
    RESULT_COLS,
)


def test_predict_column_schema_preserves_core_order_and_headers():
    schema = build_predict_column_schema()

    assert len(schema) == len(COLUMNS)
    assert [column.key for column in schema] == [column["key"] for column in COLUMNS]
    assert [column.header for column in schema] == [column["header"] for column in COLUMNS]


def test_predict_column_schema_groups_match_core_owner():
    input_schema = build_input_column_schema()
    result_schema = build_result_column_schema()

    assert [column.key for column in input_schema] == INPUT_COLS + AUTO_COLS
    assert [column.key for column in result_schema] == RESULT_COLS
    assert all(column.editable for column in input_schema if column.group == "input")
    assert all(not column.editable for column in input_schema if column.group == "auto")
    assert all(not column.editable for column in result_schema)


def test_predict_column_schema_dropdown_metadata():
    dropdown_schema = dropdown_columns()

    assert [column.key for column in dropdown_schema] == DROPDOWN_COLS
    assert all(column.dropdown for column in dropdown_schema)
    assert column_by_key("idu").mapping == "idu"
    assert column_by_key("idu").dropdown_target == "idu"


def test_predict_column_schema_exposes_ml_feature_and_target_metadata():
    assert column_by_key("cooling_capa").ml_feature == "Cooling Capa"
    assert column_by_key("id_volume").ml_feature == "ID Volume"
    assert column_by_key("cooling_power").ml_target == "Cooling Power"
    assert column_by_key("ref_qty").ml_target == "Ref Qty"


def test_predict_schema_adapter_is_qt_free():
    code = (
        "import sys; "
        "from apps.predict.schema.column_schema_adapter import build_predict_column_schema; "
        "assert build_predict_column_schema(); "
        "assert 'PySide6' not in sys.modules; "
        "qt_binding = 'Py' + 'Qt5'; "
        "assert qt_binding not in sys.modules"
    )
    subprocess.run([sys.executable, "-B", "-c", code], check=True)
