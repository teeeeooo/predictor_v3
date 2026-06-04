import pytest

from ui_tk.batch_models import (
    BatchColumnRole,
    BatchColumnSpec,
    BatchProfileSpec,
    BatchTableModel,
)


def _spec() -> BatchProfileSpec:
    return BatchProfileSpec(
        profile_key="demo",
        title="Demo",
        columns=(
            BatchColumnSpec("case", "Case", BatchColumnRole.INPUT),
            BatchColumnSpec("input", "Input", BatchColumnRole.INPUT),
            BatchColumnSpec("result", "Result", BatchColumnRole.RESULT),
            BatchColumnSpec("status", "Status", BatchColumnRole.STATUS),
        ),
        default_rows=({"case": "Case 1", "input": "10"},),
    )


def test_profile_spec_groups_columns_by_role():
    spec = _spec()

    assert spec.input_keys == ("case", "input")
    assert spec.result_keys == ("result",)
    assert spec.status_keys == ("status",)


def test_profile_spec_rejects_duplicate_column_keys():
    with pytest.raises(ValueError, match="unique"):
        BatchProfileSpec(
            profile_key="bad",
            title="Bad",
            columns=(
                BatchColumnSpec("x", "X", BatchColumnRole.INPUT),
                BatchColumnSpec("x", "X2", BatchColumnRole.RESULT),
            ),
            default_rows=(),
        )


def test_table_model_keeps_result_columns_write_only_for_results():
    model = BatchTableModel(_spec())

    model.set_results(0, {"result": "42", "status": "OK"})

    assert model.row_values(0)["result"] == "42"
    assert model.row_values(0)["status"] == "OK"
    with pytest.raises(KeyError):
        model.set_results(0, {"input": "11"})


def test_table_model_clear_results_preserves_inputs():
    model = BatchTableModel(_spec())
    model.set_results(0, {"result": "42", "status": "OK"})

    model.clear_results()

    assert model.row_values(0)["case"] == "Case 1"
    assert model.row_values(0)["input"] == "10"
    assert model.row_values(0)["result"] == ""
    assert model.row_values(0)["status"] == ""


def test_table_model_remove_row_keeps_one_row_minimum():
    model = BatchTableModel(_spec())
    model.add_row({"case": "Case 2", "input": "20"})

    model.remove_row(1)

    assert len(model.rows) == 1
    assert model.row_values(0)["case"] == "Case 1"

    model.remove_row(0)

    assert len(model.rows) == 1
