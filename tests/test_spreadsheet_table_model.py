import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from PyQt5.QtCore import Qt  # noqa: E402

from ui.spreadsheet_table import (  # noqa: E402
    AHRI_HSPF2_COLUMNS,
    AHRI_HSPF2_ROW_LABELS,
    AHRI_SEER2_COLUMNS,
    AHRI_SEER2_ROW_LABELS,
    EN14825_SCOP_COLUMNS,
    EN14825_SCOP_ROW_LABELS,
    EN14825_SEER_COLUMNS,
    EN14825_SEER_ROW_LABELS,
    SpreadsheetTableModel,
    format_tsv,
    make_ahri_hspf2_table_model,
    make_ahri_seer2_table_model,
    make_en14825_scop_table_model,
    make_en14825_seer_table_model,
    parse_tsv,
    points_from_grid,
)


AHRI_SEER2_COLUMNS = ["A_Full", "B_Full", "B_Low", "E_Int", "F_Low"]
DEFAULT_ROWS = ["능력 [Btu/h]", "전력 [W]"]


def _make_model(rows=DEFAULT_ROWS, cols=AHRI_SEER2_COLUMNS):
    return SpreadsheetTableModel(row_labels=rows, column_labels=cols)


# ---------- pure-Python helper tests ----------


def test_parse_tsv_handles_crlf_and_trailing_newline():
    tsv = "1\t2\t3\r\n4\t5\t6\r\n"
    assert parse_tsv(tsv) == [["1", "2", "3"], ["4", "5", "6"]]


def test_parse_tsv_returns_empty_for_empty_string():
    assert parse_tsv("") == []


def test_parse_tsv_rejects_non_string():
    with pytest.raises(TypeError, match="must be a string"):
        parse_tsv(123)  # type: ignore[arg-type]


def test_format_tsv_emits_trailing_newline():
    assert format_tsv([["1", "2"], ["3", "4"]]) == "1\t2\n3\t4\n"


def test_format_tsv_empty_grid_returns_empty_string():
    assert format_tsv([]) == ""


def test_points_from_grid_rejects_row_width_mismatch():
    with pytest.raises(ValueError, match="grid row width"):
        points_from_grid(
            AHRI_SEER2_COLUMNS,
            [["36000", "30000"], ["3000", "2200"]],
        )


# ---------- model: shape ----------


def test_table_shape_uses_row_and_column_labels():
    model = _make_model()
    assert model.rowCount() == 2
    assert model.columnCount() == 5
    assert model.row_labels == DEFAULT_ROWS
    assert model.column_labels == AHRI_SEER2_COLUMNS
    assert model.headerData(0, Qt.Horizontal) == "A_Full"
    assert model.headerData(4, Qt.Horizontal) == "F_Low"
    assert model.headerData(0, Qt.Vertical) == "능력 [Btu/h]"
    assert model.headerData(1, Qt.Vertical) == "전력 [W]"


def test_constructor_rejects_empty_labels():
    with pytest.raises(ValueError, match="row_labels"):
        SpreadsheetTableModel(row_labels=[], column_labels=AHRI_SEER2_COLUMNS)
    with pytest.raises(ValueError, match="column_labels"):
        SpreadsheetTableModel(row_labels=DEFAULT_ROWS, column_labels=[])


# ---------- model: set/get single cell ----------


def test_set_and_get_single_cell():
    model = _make_model()
    model.set_cell(0, 0, "36000")
    assert model.get_cell(0, 0) == "36000"
    # data() returns the same string for DisplayRole / EditRole.
    idx = model.index(0, 0)
    assert model.data(idx, Qt.DisplayRole) == "36000"
    assert model.data(idx, Qt.EditRole) == "36000"


def test_set_cell_coerces_none_to_empty_string():
    model = _make_model()
    model.set_cell(1, 2, None)
    assert model.get_cell(1, 2) == ""


def test_set_cell_rejects_out_of_bounds():
    model = _make_model()
    with pytest.raises(IndexError):
        model.set_cell(5, 0, "x")
    with pytest.raises(IndexError):
        model.set_cell(0, 10, "x")


# ---------- model: TSV paste ----------


def test_paste_2x3_tsv_at_origin_writes_rectangle():
    model = _make_model()
    tsv = "36000\t30000\t18000\n3000\t2200\t1200\n"
    written = model.paste_tsv(top_row=0, top_col=0, tsv=tsv)

    assert written == 6
    assert model.get_cell(0, 0) == "36000"
    assert model.get_cell(0, 1) == "30000"
    assert model.get_cell(0, 2) == "18000"
    assert model.get_cell(1, 0) == "3000"
    assert model.get_cell(1, 1) == "2200"
    assert model.get_cell(1, 2) == "1200"
    # Cells outside the paste rectangle stay empty.
    assert model.get_cell(0, 3) == ""
    assert model.get_cell(1, 4) == ""


def test_paste_at_offset_anchors_to_top_left():
    model = _make_model()
    written = model.paste_tsv(top_row=0, top_col=2, tsv="10\t20\n30\t40\n")
    assert written == 4
    assert model.get_cell(0, 2) == "10"
    assert model.get_cell(0, 3) == "20"
    assert model.get_cell(1, 2) == "30"
    assert model.get_cell(1, 3) == "40"


def test_paste_silently_drops_out_of_bounds_cells():
    model = _make_model()
    # The second row of the TSV would fall on row index 2, which does
    # not exist. The first row writes, the second is dropped.
    written = model.paste_tsv(top_row=1, top_col=3, tsv="a\tb\nc\td\n")
    assert written == 2
    assert model.get_cell(1, 3) == "a"
    assert model.get_cell(1, 4) == "b"


# ---------- model: TSV copy ----------


def test_copy_selected_rectangle_returns_tsv():
    model = _make_model()
    model.paste_tsv(0, 0, "36000\t30000\t18000\n3000\t2200\t1200\n")

    tsv = model.selected_to_tsv(
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    )
    assert tsv == "36000\t30000\t18000\n3000\t2200\t1200\n"


def test_copy_expands_non_rectangular_selection_to_bounding_rect():
    model = _make_model()
    model.set_cell(0, 0, "X")
    model.set_cell(1, 2, "Y")
    # Selection skips intermediate cells, but the helper still emits
    # the full bounding rectangle.
    tsv = model.selected_to_tsv([(0, 0), (1, 2)])
    assert tsv == "X\t\t\n\t\tY\n"


# ---------- model: clear ----------


def test_clear_helper_empties_selected_cells_only():
    model = _make_model()
    model.paste_tsv(0, 0, "1\t2\t3\n4\t5\t6\n")

    cleared = model.clear_cells([(0, 1), (1, 1)])
    assert cleared == 2
    assert model.get_cell(0, 0) == "1"
    assert model.get_cell(0, 1) == ""
    assert model.get_cell(0, 2) == "3"
    assert model.get_cell(1, 0) == "4"
    assert model.get_cell(1, 1) == ""
    assert model.get_cell(1, 2) == "6"


def test_clear_helper_returns_zero_when_selection_is_already_empty():
    model = _make_model()
    cleared = model.clear_cells([(0, 0), (0, 1)])
    assert cleared == 0


# ---------- model: undo ----------


def test_undo_restores_state_before_paste():
    model = _make_model()
    model.set_cell(0, 0, "seed")
    assert model.undo()  # undo the seed itself
    assert model.get_cell(0, 0) == ""

    # Re-seed; then snapshot the state and paste over it.
    model.set_cell(0, 0, "seed")
    before_paste = model.to_grid()
    model.paste_tsv(0, 0, "10\t20\n30\t40\n")
    assert model.get_cell(0, 0) == "10"

    assert model.undo()
    assert model.to_grid() == before_paste


def test_undo_restores_state_before_clear():
    model = _make_model()
    model.paste_tsv(0, 0, "1\t2\n3\t4\n")
    before_clear = model.to_grid()
    model.clear_cells([(0, 0), (1, 0)])
    assert model.get_cell(0, 0) == ""

    assert model.undo()
    assert model.to_grid() == before_clear


def test_undo_returns_false_when_stack_is_empty():
    model = _make_model()
    assert model.can_undo() is False
    assert model.undo() is False


def test_reset_undo_clears_stack():
    model = _make_model()
    model.set_cell(0, 0, "x")
    assert model.can_undo()
    model.reset_undo()
    assert model.can_undo() is False


# ---------- model: invalid numeric ----------


def test_invalid_numeric_value_is_stored_as_is():
    model = _make_model()
    model.set_cell(0, 0, "abc")
    assert model.get_cell(0, 0) == "abc"


def test_invalid_numeric_value_is_flagged():
    model = _make_model()
    model.set_cell(0, 0, "abc")
    model.set_cell(0, 1, "12.5")
    model.set_cell(0, 2, "")

    assert model.is_cell_invalid(0, 0) is True
    assert model.is_cell_invalid(0, 1) is False
    # Empty cells are not invalid; they just have no value yet.
    assert model.is_cell_invalid(0, 2) is False


# ---------- model: point dict conversion ----------


def test_as_point_dict_converts_capacity_power_rows():
    model = SpreadsheetTableModel(
        row_labels=DEFAULT_ROWS,
        column_labels=["A_Full", "B_Full"],
    )
    model.paste_tsv(0, 0, "36000\t30000\n3000\t2200\n")

    points = model.as_point_dict(capacity_row=0, power_row=1)
    assert points == {
        "A_Full": (36000.0, 3000.0),
        "B_Full": (30000.0, 2200.0),
    }


def test_as_point_dict_rejects_non_numeric_capacity():
    model = SpreadsheetTableModel(
        row_labels=DEFAULT_ROWS,
        column_labels=["A_Full"],
    )
    model.set_cell(0, 0, "abc")
    model.set_cell(1, 0, "1000")

    with pytest.raises(ValueError, match="non-numeric capacity or power"):
        model.as_point_dict()


def test_as_point_dict_rejects_empty_power():
    model = SpreadsheetTableModel(
        row_labels=DEFAULT_ROWS,
        column_labels=["A_Full"],
    )
    model.set_cell(0, 0, "36000")
    # Row 1 stays empty.
    with pytest.raises(ValueError, match="non-numeric capacity or power"):
        model.as_point_dict()


# ---------- AHRI SEER2 factory ----------


def test_ahri_seer2_factory_uses_locked_column_and_row_labels():
    model = make_ahri_seer2_table_model()

    assert model.column_labels == list(AHRI_SEER2_COLUMNS)
    assert model.row_labels == list(AHRI_SEER2_ROW_LABELS)
    assert model.rowCount() == 2
    assert model.columnCount() == 5


# ---------- AHRI HSPF2 factory ----------


def test_ahri_hspf2_columns_and_rows_match_design_doc():
    assert AHRI_HSPF2_COLUMNS == (
        "H01",
        "H11",
        "H12",
        "H1N",
        "H22",
        "H2Int",
        "H32",
    )
    assert AHRI_HSPF2_ROW_LABELS == ("능력 [Btu/h]", "전력 [W]")


def test_ahri_hspf2_factory_uses_locked_column_and_row_labels():
    model = make_ahri_hspf2_table_model()

    assert model.column_labels == list(AHRI_HSPF2_COLUMNS)
    assert model.row_labels == list(AHRI_HSPF2_ROW_LABELS)
    assert model.rowCount() == 2
    assert model.columnCount() == 7


def test_ahri_hspf2_as_point_dict_returns_calculator_test_point_shape():
    model = make_ahri_hspf2_table_model()
    sample = {
        "H01": (12500, 980),
        "H11": (12000, 1000),
        "H12": (24000, 2200),
        "H1N": (22000, 2000),
        "H22": (23200, 2160),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
    }
    for col_idx, point_id in enumerate(AHRI_HSPF2_COLUMNS):
        capacity, power = sample[point_id]
        model.set_cell(0, col_idx, str(capacity))
        model.set_cell(1, col_idx, str(power))

    points = model.as_point_dict(capacity_row=0, power_row=1)

    assert points == {point_id: (float(c), float(p)) for point_id, (c, p) in sample.items()}


def test_ahri_hspf2_as_point_dict_rejects_missing_value():
    model = make_ahri_hspf2_table_model()
    # Fill every column except H22 capacity.
    model.set_cell(0, 0, "12500")
    model.set_cell(1, 0, "980")
    # Leave H22 capacity empty; point_id index 4 → column 4.
    with pytest.raises(ValueError, match="non-numeric capacity or power"):
        model.as_point_dict()


# ---------- EN14825 SEER factory ----------


def test_en14825_seer_columns_and_rows_match_design_doc():
    assert EN14825_SEER_COLUMNS == ("A", "B", "C", "D")
    assert EN14825_SEER_ROW_LABELS == ("능력 [W]", "전력 [W]")


def test_en14825_seer_factory_uses_locked_column_and_row_labels():
    model = make_en14825_seer_table_model()

    assert model.column_labels == list(EN14825_SEER_COLUMNS)
    assert model.row_labels == list(EN14825_SEER_ROW_LABELS)
    assert model.rowCount() == 2
    assert model.columnCount() == 4


def test_en14825_seer_as_point_dict_returns_w_values():
    """UI 입력은 W이므로 as_point_dict()도 W/W를 그대로 돌려준다.

    W → kW 변환은 calc_window가 core 호출 직전에 수행한다.
    """
    model = make_en14825_seer_table_model()
    sample = {
        "A": (3623.3, 847.0),
        "B": (2469.1, 389.0),
        "C": (1515.0, 137.0),
        "D": (1127.7, 62.0),
    }
    for col_idx, point_id in enumerate(EN14825_SEER_COLUMNS):
        capacity_w, power_w = sample[point_id]
        model.set_cell(0, col_idx, str(capacity_w))
        model.set_cell(1, col_idx, str(power_w))

    points = model.as_point_dict(capacity_row=0, power_row=1)
    assert points == {
        point_id: (float(c), float(p))
        for point_id, (c, p) in sample.items()
    }


# ---------- EN14825 SCOP factory ----------


def test_en14825_scop_columns_and_rows_match_design_doc():
    assert EN14825_SCOP_COLUMNS == ("A", "B", "C", "D", "TOL", "Tbiv")
    assert EN14825_SCOP_ROW_LABELS == ("능력 [W]", "전력 [W]")


def test_en14825_scop_factory_uses_locked_column_and_row_labels():
    model = make_en14825_scop_table_model()

    assert model.column_labels == list(EN14825_SCOP_COLUMNS)
    assert model.row_labels == list(EN14825_SCOP_ROW_LABELS)
    assert model.rowCount() == 2
    assert model.columnCount() == 6


def test_en14825_scop_as_point_dict_returns_w_values():
    model = make_en14825_scop_table_model()
    sample = {
        "A": (2159.8, 606.2),
        "B": (1329.3, 254.2),
        "C": (908.3, 154.0),
        "D": (929.9, 123.1),
        "TOL": (2369.8, 806.7),
        "Tbiv": (2366.9, 782.0),
    }
    for col_idx, point_id in enumerate(EN14825_SCOP_COLUMNS):
        capacity_w, power_w = sample[point_id]
        model.set_cell(0, col_idx, str(capacity_w))
        model.set_cell(1, col_idx, str(power_w))

    points = model.as_point_dict(capacity_row=0, power_row=1)
    assert points == {
        point_id: (float(c), float(p))
        for point_id, (c, p) in sample.items()
    }


def test_en14825_scop_as_point_dict_rejects_missing_tbiv():
    model = make_en14825_scop_table_model()
    # Fill all columns except TBiv (last column).
    for col_idx in range(len(EN14825_SCOP_COLUMNS) - 1):
        model.set_cell(0, col_idx, "1000")
        model.set_cell(1, col_idx, "200")
    with pytest.raises(ValueError, match="non-numeric capacity or power"):
        model.as_point_dict()
