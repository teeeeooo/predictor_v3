"""Tests for MetricInputTable visible invalid-field validation foundation.

These tests verify that MetricInputTable can store, query, and visually mark
invalid editable fields without changing existing behavior.
"""

from __future__ import annotations

import pytest

from ui_tk.layout_constants import TABLE_EDITABLE_BG, TABLE_INVALID_BG
from ui_tk.metric_input_table import MetricInputTable


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


class TestInvalidFieldStateStorage:
    def test_set_invalid_fields_stores_state(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "invalid number", "b": "too high"})
        assert sample_table.invalid_fields() == {"a": "invalid number", "b": "too high"}

    def test_invalid_fields_returns_copy(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        copy = sample_table.invalid_fields()
        copy["a"] = "changed"
        assert sample_table.invalid_fields() == {"a": "msg"}

    def test_is_field_invalid(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        assert sample_table.is_field_invalid("a") is True
        assert sample_table.is_field_invalid("b") is False

    def test_invalid_message(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "bad value"})
        assert sample_table.invalid_message("a") == "bad value"
        assert sample_table.invalid_message("b") is None

    def test_set_invalid_fields_unknown_key_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(KeyError):
            sample_table.set_invalid_fields({"unknown": "msg"})

    def test_clear_invalid_fields_all(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg", "b": "msg2"})
        sample_table.clear_invalid_fields()
        assert sample_table.invalid_fields() == {}
        assert sample_table.is_field_invalid("a") is False
        assert sample_table.is_field_invalid("b") is False

    def test_clear_invalid_fields_one(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg", "b": "msg2"})
        sample_table.clear_invalid_fields(["a"])
        assert sample_table.is_field_invalid("a") is False
        assert sample_table.is_field_invalid("b") is True

    def test_clear_invalid_fields_unknown_key_raises(self, sample_table: MetricInputTable) -> None:
        with pytest.raises(KeyError):
            sample_table.clear_invalid_fields(["unknown"])


class TestInvalidVisualMarking:
    def test_invalid_field_entry_background_changes(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        bg = sample_table.editable_entries["a"].cget("background")
        assert bg == TABLE_INVALID_BG

    def test_valid_field_entry_background_unchanged(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        bg = sample_table.editable_entries["b"].cget("background")
        assert bg == TABLE_EDITABLE_BG

    def test_clear_invalid_restores_background(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        sample_table.clear_invalid_fields(["a"])
        bg = sample_table.editable_entries["a"].cget("background")
        assert bg == TABLE_EDITABLE_BG

    def test_default_cell_background_invalid(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        assert sample_table.default_cell_background((0, 0)) == TABLE_INVALID_BG
        assert sample_table.default_cell_background((0, 1)) == TABLE_EDITABLE_BG

    def test_default_cell_background_after_clear(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        sample_table.clear_invalid_fields(["a"])
        assert sample_table.default_cell_background((0, 0)) == TABLE_EDITABLE_BG


class TestInvalidStateDoesNotChangeExistingBehavior:
    def test_set_values_batch_does_not_auto_clear_invalid(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        sample_table.set_values_batch({"a": "99"})
        assert sample_table.is_field_invalid("a") is True
        assert sample_table.invalid_message("a") == "msg"

    def test_set_positions_batch_does_not_auto_clear_invalid(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "msg"})
        sample_table.set_positions_batch({(0, 0): "99"})
        assert sample_table.is_field_invalid("a") is True

    def test_get_numeric_values_still_raises(self, sample_table: MetricInputTable) -> None:
        sample_table.set_values_batch({"a": "bad"})
        with pytest.raises(ValueError):
            sample_table.get_numeric_values()

    def test_get_numeric_values_marks_invalid_fields(self, sample_table: MetricInputTable) -> None:
        sample_table.set_values_batch({"a": "bad", "b": "also_bad"})
        with pytest.raises(ValueError):
            sample_table.get_numeric_values()
        assert sample_table.is_field_invalid("a") is True
        assert sample_table.is_field_invalid("b") is True
        assert sample_table.is_field_invalid("c") is False
        assert sample_table.is_field_invalid("d") is False

    def test_get_numeric_values_clears_previous_invalid_for_valid(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "previous"})
        assert sample_table.is_field_invalid("a") is True
        sample_table.set_values_batch({"a": "10"})
        numeric = sample_table.get_numeric_values()
        assert numeric["a"] == 10.0
        assert sample_table.is_field_invalid("a") is False

    def test_get_numeric_values_clears_all_then_remarks_on_revalidation(self, sample_table: MetricInputTable) -> None:
        sample_table.set_invalid_fields({"a": "previous"})
        sample_table.set_values_batch({"b": "bad"})
        with pytest.raises(ValueError):
            sample_table.get_numeric_values()
        assert sample_table.is_field_invalid("a") is False
        assert sample_table.is_field_invalid("b") is True

    def test_get_text_values_unchanged(self, sample_table: MetricInputTable) -> None:
        sample_table.set_values_batch({"a": "bad"})
        assert sample_table.get_text_values()["a"] == "bad"


class TestInvalidStateWithReadOnlyCells:
    def test_read_only_cell_cannot_be_invalid(self, tk_root) -> None:
        table = MetricInputTable(
            tk_root,
            columns=(("c1", "Col1"), ("c2", "Col2")),
            rows=(("r1", "Row1"),),
            editable_cells={("r1", "c1"): "a"},
        )
        table.set_values({"a": "1"})
        # Setting invalid for editable field works
        table.set_invalid_fields({"a": "msg"})
        assert table.is_field_invalid("a") is True
        # Read-only position default background is static, not invalid
        assert table.default_cell_background((0, 1)) == TABLE_STATIC_BG
