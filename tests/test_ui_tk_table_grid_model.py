"""Pure contract tests for the table/grid input model."""

import importlib
import sys

import pytest

from apps.calculator.ui.table_grid_model import (
    GridCellState,
    GridColumn,
    GridRow,
    TableGridModel,
    parse_numeric_cell,
)


def _model() -> TableGridModel:
    return TableGridModel(
        rows=(GridRow("full", "Full"), GridRow("half", "Half")),
        columns=(GridColumn("capacity", "Capacity"), GridColumn("power", "Power")),
    )


def test_model_module_does_not_import_ui_toolkits():
    qt_binding = "Py" + "Qt5"
    for name in list(sys.modules):
        if (
            name == "tkinter"
            or name.startswith("tkinter.")
            or name.startswith(qt_binding)
            or name == "apps.calculator.ui.table_grid_model"
        ):
            del sys.modules[name]

    importlib.import_module("apps.calculator.ui.table_grid_model")

    assert not any(
        name == "tkinter" or name.startswith("tkinter.") for name in sys.modules
    )
    assert not any(name.startswith(qt_binding) for name in sys.modules)


def test_schema_initializes_empty_missing_cells():
    model = _model()

    assert model.get_cell("full", "capacity") == ""
    assert model.cell_state("full", "capacity") is GridCellState.MISSING
    assert model.invalid_cells() == (
        ("full", "capacity"),
        ("full", "power"),
        ("half", "capacity"),
        ("half", "power"),
    )


def test_set_cell_reports_only_actual_changes():
    model = _model()

    assert model.set_cell("full", "capacity", "3,600") is True
    assert model.set_cell("full", "capacity", "3,600") is False
    assert model.get_cell("full", "capacity") == "3,600"
    assert model.cell_state("full", "capacity") is GridCellState.VALID


def test_unknown_cell_address_raises_keyerror():
    model = _model()

    with pytest.raises(KeyError):
        model.get_cell("missing", "capacity")
    with pytest.raises(KeyError):
        model.set_cell("full", "missing", "1")


@pytest.mark.parametrize(
    ("text", "value"),
    [(" 3,600 ", 3600.0), ("-1.5", -1.5), ("1e2", 100.0)],
)
def test_parse_numeric_cell_supports_trim_commas_and_numeric_text(text, value):
    assert parse_numeric_cell(text) == value


@pytest.mark.parametrize("text", ["", "  ", "bad", "NaN", "inf"])
def test_parse_numeric_cell_rejects_missing_or_invalid_text(text):
    with pytest.raises(ValueError):
        parse_numeric_cell(text)


def test_invalid_and_missing_states_are_distinct():
    model = _model()

    model.set_cell("full", "capacity", "bad")

    assert model.cell_state("full", "capacity") is GridCellState.INVALID
    assert model.cell_state("full", "power") is GridCellState.MISSING


def test_text_and_numeric_table_snapshots():
    model = _model()
    model.set_cells(
        {
            ("full", "capacity"): "3,600",
            ("full", "power"): "900",
            ("half", "capacity"): "1,700",
            ("half", "power"): "380",
        }
    )

    assert model.as_text_table() == {
        "full": {"capacity": "3,600", "power": "900"},
        "half": {"capacity": "1,700", "power": "380"},
    }
    assert model.as_numeric_table() == {
        "full": {"capacity": 3600.0, "power": 900.0},
        "half": {"capacity": 1700.0, "power": 380.0},
    }


def test_numeric_snapshot_fails_fast_on_invalid_or_missing_cell():
    with pytest.raises(ValueError, match="invalid cells"):
        _model().as_numeric_table()
