"""Tests for MetricInputTable TkTableSurface adapter compatibility.

These tests verify that MetricInputTable exposes position-based methods
matching the TkTableSurface contract without changing existing behavior.
"""

from __future__ import annotations

import pytest

from ui_tk.layout_constants import TABLE_EDITABLE_BG, TABLE_STATIC_BG
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.table.roles import CellRole


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


@pytest.fixture
def sample_table(tk_root):
    table = MetricInputTable(
        tk_root,
        columns=(("c1", "Col1"), ("c2", "Col2")),
        rows=(("r1", "Row1"), ("r2", "Row2")),
        editable_cells={
            ("r1", "c1"): "a",
            ("r1", "c2"): "b",
            ("r2", "c1"): "c",
            ("r2", "c2"): "d",
        },
    )
    table.pack()
    table.set_values({"a": "1", "b": "2", "c": "3", "d": "4"})
    tk_root.update_idletasks()
    return table


class TestAdapterDimensions:
    def test_row_count(self, sample_table: MetricInputTable) -> None:
        assert sample_table.row_count() == 2

    def test_column_count(self, sample_table: MetricInputTable) -> None:
        assert sample_table.column_count() == 2


class TestAdapterCellRole:
    def test_cell_role_editable(self, sample_table: MetricInputTable) -> None:
        assert sample_table.cell_role((0, 0)) is CellRole.EDITABLE
        assert sample_table.cell_role((0, 1)) is CellRole.EDITABLE
        assert sample_table.cell_role((1, 0)) is CellRole.EDITABLE
        assert sample_table.cell_role((1, 1)) is CellRole.EDITABLE

    def test_cell_roles_tuple(self, sample_table: MetricInputTable) -> None:
        roles = sample_table.cell_roles()
        assert len(roles) == 4
        assert all(role is CellRole.EDITABLE for role in roles)

    def test_cell_role_readonly(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        assert table.cell_role((0, 0)) is CellRole.EDITABLE
        assert table.cell_role((0, 1)) is CellRole.READONLY


class TestAdapterTextAccess:
    def test_text_at_position_matches_text_at_address(self, sample_table: MetricInputTable) -> None:
        assert sample_table.text_at_position((0, 0)) == sample_table.text_at_address(("r1", "c1"))
        assert sample_table.text_at_position((0, 1)) == sample_table.text_at_address(("r1", "c2"))
        assert sample_table.text_at_position((1, 0)) == sample_table.text_at_address(("r2", "c1"))
        assert sample_table.text_at_position((1, 1)) == sample_table.text_at_address(("r2", "c2"))

    def test_text_at_position_static_cell(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        assert table.text_at_position((0, 1)) == "-"


class TestAdapterSetPositions:
    def test_set_positions_batch_updates_values(self, sample_table: MetricInputTable) -> None:
        changed = sample_table.set_positions_batch({(0, 0): "10", (0, 1): "20"})
        assert changed is True
        assert sample_table.get_text_values()["a"] == "10"
        assert sample_table.get_text_values()["b"] == "20"

    def test_set_positions_batch_no_change(self, sample_table: MetricInputTable) -> None:
        changed = sample_table.set_positions_batch({(0, 0): "1"})
        assert changed is False

    def test_set_positions_batch_ignores_readonly(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        table.set_values({"a": "1"})
        changed = table.set_positions_batch({(0, 1): "99"})
        assert changed is False
        assert table.text_at_position((0, 1)) == "-"


class TestAdapterSnapshot:
    def test_snapshot_returns_current_values(self, sample_table: MetricInputTable) -> None:
        snapshot = sample_table.snapshot()
        assert snapshot == {"a": "1", "b": "2", "c": "3", "d": "4"}

    def test_restore_snapshot_reverts_values(self, sample_table: MetricInputTable) -> None:
        before = sample_table.snapshot()
        sample_table.set_positions_batch({(0, 0): "99", (1, 1): "88"})
        sample_table.restore_snapshot(before)
        assert sample_table.get_text_values() == before


class TestAdapterWidgets:
    def test_cell_frame_returns_existing_frame(self, sample_table: MetricInputTable) -> None:
        frame = sample_table.cell_frame((0, 0))
        assert frame is sample_table.cell_frames[("r1", "c1")]

    def test_cell_widget_editable_returns_entry(self, sample_table: MetricInputTable) -> None:
        widget = sample_table.cell_widget((0, 0))
        assert widget is sample_table.editable_entries["a"]

    def test_cell_widget_readonly_returns_frame(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        widget = table.cell_widget((0, 1))
        assert widget is table.cell_frames[("r1", "c2")]

    def test_focus_widget_matches_cell_widget(self, sample_table: MetricInputTable) -> None:
        assert sample_table.focus_widget((0, 0)) is sample_table.cell_widget((0, 0))


class TestAdapterBackground:
    def test_default_cell_background_editable(self, sample_table: MetricInputTable) -> None:
        assert sample_table.default_cell_background((0, 0)) == TABLE_EDITABLE_BG

    def test_default_cell_background_readonly(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        assert table.default_cell_background((0, 1)) == TABLE_STATIC_BG


class TestAdapterEnsureRowCount:
    def test_ensure_row_count_is_noop(self, sample_table: MetricInputTable) -> None:
        original = sample_table.row_count()
        sample_table.ensure_row_count(10)
        assert sample_table.row_count() == original
        sample_table.ensure_row_count(1)
        assert sample_table.row_count() == original


class TestAdapterOutOfRange:
    def test_out_of_range_row_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(IndexError):
            sample_table._address_at_position((5, 0))

    def test_out_of_range_column_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(IndexError):
            sample_table._address_at_position((0, 5))

    def test_negative_row_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(IndexError):
            sample_table._address_at_position((-1, 0))

    def test_negative_column_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(IndexError):
            sample_table._address_at_position((0, -1))


class TestAdapterClipboardNotShadowed:
    def test_clipboard_methods_are_inherited_tk(self, sample_table: MetricInputTable) -> None:
        # Verify that MetricInputTable inherits Tk clipboard methods
        # and they are not shadowed by recursive wrappers.
        assert hasattr(sample_table, "clipboard_clear")
        assert hasattr(sample_table, "clipboard_append")
        assert hasattr(sample_table, "clipboard_get")
        assert hasattr(sample_table, "winfo_containing")

    def test_clipboard_roundtrip(self, sample_table: MetricInputTable) -> None:
        # Verify inherited clipboard methods work for TkTableController
        # copy/paste usage.  This is a smoke test; real clipboard behavior
        # depends on the windowing system.
        sample_table.clipboard_clear()
        sample_table.clipboard_append("test_value")
        result = sample_table.clipboard_get()
        assert result == "test_value"
