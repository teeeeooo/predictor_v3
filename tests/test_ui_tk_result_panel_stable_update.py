"""Tests for ResultPanel stable summary update (same-shape value-only update).

These tests verify that ResultPanel.set_summaries reuses existing widgets
when the summary shape (title + field labels) is unchanged, and falls back
to full rebuild when the shape changes.
"""

from __future__ import annotations

import csv
import tkinter as tk

import pytest

from apps.calculator.ui.layout_constants import TABLE_PASS_BG
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel


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
def panel(tk_root):
    p = ResultPanel(tk_root, title="Test Results")
    p.pack()
    tk_root.update_idletasks()
    return p


class TestStableUpdate:
    """Same-shape summaries update in place without destroying widgets."""

    def test_same_shape_keeps_widget_identity(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"), ("B", "2"))),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "10"), ("B", "20"))),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert first_children == second_children
        assert len(first_children) == 1

    def test_same_shape_updates_value_text(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        labels = panel.summary_value_labels["CSPF"]
        value_cell = panel.summary_value_cells["CSPF"][0]
        initial_cell_identity = str(value_cell)
        initial_label_identity = str(labels[0])
        assert labels[0].cget("text") == "1"

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "99"),)),)
        )
        tk_root.update_idletasks()
        assert labels[0].cget("text") == "99"
        assert labels[0].semantic_tone == "calculated"
        assert labels[0].cget("background") == TABLE_PASS_BG
        assert str(value_cell) == initial_cell_identity
        assert str(labels[0]) == initial_label_identity
        assert value_cell.cget("background") == TABLE_PASS_BG
        assert value_cell.semantic_background == TABLE_PASS_BG
        assert value_cell.cget("background") == labels[0].cget("background")

    def test_same_shape_updates_status_text(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(
                title="CSPF", fields=(("A", "1"),), status="계산 중"
            ),)
        )
        tk_root.update_idletasks()
        status = panel.summary_status_labels["CSPF"]
        assert status.cget("text") == "계산 중"

        panel.set_summaries(
            (ResultSummary(
                title="CSPF", fields=(("A", "1"),), status="계산 완료"
            ),)
        )
        tk_root.update_idletasks()
        assert status.cget("text") == "계산 완료"

    def test_summary_columns_use_uniform_width_policy(self, panel, tk_root) -> None:
        panel.set_summaries(
            (
                ResultSummary(
                    title="CSPF",
                    fields=(
                        ("CSPF", "4.939"),
                        ("CSTL [kWh]", "1769.6"),
                        ("CSEC [kWh]", "358.3"),
                    ),
                    status="자동 계산 완료",
                ),
            )
        )
        tk_root.update_idletasks()

        card = panel.summary_tables["CSPF"]
        header_widths = tuple(
            cell.winfo_width() for cell in panel.summary_header_cells["CSPF"]
        )
        value_widths = tuple(
            cell.winfo_width() for cell in panel.summary_value_cells["CSPF"]
        )

        assert {
            card.grid_columnconfigure(column)["uniform"]
            for column in range(3)
        } == {"summary_fields"}
        assert len(set(header_widths)) == 1
        assert len(set(value_widths)) == 1

    def test_content_hug_summary_table_does_not_expand_with_window(self, tk_root) -> None:
        tk_root.geometry("500x300")
        panel = ResultPanel(tk_root, title="Test Results")
        panel.pack(anchor="w")
        panel.set_summaries(
            (
                ResultSummary(
                    title="CSPF",
                    fields=(
                        ("CSPF", "4.939"),
                        ("CSTL [kWh]", "1769.6"),
                        ("CSEC [kWh]", "358.3"),
                    ),
                ),
            )
        )
        tk_root.update_idletasks()
        initial_width = panel.summary_tables["CSPF"].winfo_width()

        tk_root.geometry("900x300")
        tk_root.update_idletasks()

        assert panel.summary_tables["CSPF"].winfo_width() == initial_width

    def test_summary_uses_shared_flat_grid_primitives(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("CSPF", "4.939"),)),)
        )
        tk_root.update_idletasks()

        card = panel.summary_tables["CSPF"]
        header = panel.summary_header_cells["CSPF"][0]
        value = panel.summary_value_cells["CSPF"][0]
        value_label = panel.summary_value_labels["CSPF"][0]
        assert card.outer_edge_policy == "flat_low_contrast"
        assert int(card.cget("borderwidth")) == 0
        assert header.surface_role == "summary_header_cell"
        assert value.surface_role == "summary_value_cell"
        assert value_label.alignment_role == "numeric_result"
        assert value_label.semantic_tone == "calculated"
        assert value_label.cget("background") == TABLE_PASS_BG
        assert value.cget("background") == TABLE_PASS_BG
        assert value.semantic_background == TABLE_PASS_BG
        assert value.cget("background") == value_label.cget("background")


class TestResultActions:
    def test_result_panel_copy_uses_latest_summary_and_status_only(
        self, panel, tk_root
    ) -> None:
        from tkinter import ttk

        from apps.calculator.ui.result_actions import add_result_actions

        row = ttk.Frame(tk_root)
        actions = add_result_actions(
            row,
            parent=tk_root,
            result_owner=panel,
            csv_filename="result.csv",
            surface_prefix="test_result",
        )
        panel.set_summaries(
            (ResultSummary(title="First", fields=(("Value", "1"),), status="old"),)
        )
        panel.set_summaries(
            (ResultSummary(title="Latest", fields=(("Value", "2"),), status="done"),)
        )
        actions.copy_button.invoke()
        copied = tk_root.clipboard_get()
        assert "Latest" in copied and "2" in copied and "done" in copied
        assert "First" not in copied and "old" not in copied

        panel.set_summaries((ResultSummary(title="Latest", fields=(), status="waiting"),))
        actions.copy_button.invoke()
        assert tk_root.clipboard_get() == "[Latest]\nwaiting"

        panel.clear()
        actions.copy_button.invoke()
        assert tk_root.clipboard_get() == "Status\tNo results"

    def test_result_panel_sectioned_csv_preserves_display_order(
        self, panel, tk_root, monkeypatch, tmp_path
    ) -> None:
        from tkinter import ttk

        from apps.calculator.ui.result_actions import add_result_actions

        panel.set_summaries(
            (
                ResultSummary(
                    title="Climate A",
                    fields=(("SCOP", "3.20"), ("QH", "100")),
                    status="complete",
                ),
                ResultSummary(
                    title="Climate B",
                    fields=(("SCOP", "3.10"),),
                    status="warning",
                ),
            )
        )
        row = ttk.Frame(tk_root)
        actions = add_result_actions(
            row,
            parent=tk_root,
            result_owner=panel,
            csv_filename="scop_result.csv",
            surface_prefix="test_scop_result",
        )
        path = tmp_path / "scop.csv"
        monkeypatch.setattr(
            "apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",
            lambda **_kwargs: str(path),
        )
        actions.export_button.invoke()
        with path.open(encoding="utf-8-sig", newline="") as handle:
            assert list(csv.reader(handle)) == [
                ["Climate A"],
                ["Field", "Value"],
                ["SCOP", "3.20"],
                ["QH", "100"],
                ["Status", "complete"],
                [],
                ["Climate B"],
                ["Field", "Value"],
                ["SCOP", "3.10"],
                ["Status", "warning"],
            ]

        monkeypatch.setattr(
            "apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",
            lambda **_kwargs: "",
        )
        assert actions.export_button.invoke() == 0


class TestRebuildOnShapeChange:
    """Shape changes trigger full widget rebuild."""

    def test_field_label_change_rebuilds(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("B", "1"),)),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert first_children != second_children

    def test_title_change_rebuilds(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="HSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert first_children != second_children

    def test_field_count_change_rebuilds(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"), ("B", "2"))),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert first_children != second_children

    def test_status_only_to_fields_rebuilds(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(), status="오류"),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert first_children != second_children


class TestClear:
    """Clear resets state so next set_summaries rebuilds."""

    def test_clear_then_set_rebuilds(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.clear()
        tk_root.update_idletasks()
        assert not panel._summary_holder.winfo_children()

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "2"),)),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        assert len(second_children) == 1
        assert first_children != second_children


class TestCopyText:
    """Copy text is updated even during stable in-place update."""

    def test_copy_text_updated_on_stable_update(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_copy = panel._text.get("1.0", "end-1c")

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "99"),)),)
        )
        tk_root.update_idletasks()
        second_copy = panel._text.get("1.0", "end-1c")

        assert "99" in second_copy
        assert second_copy != first_copy


class TestFocusPreservation:
    """Shape-change rebuild preserves external focus and ignores internal focus."""

    def _focus_entry(self, tk_root, entry):
        tk_root.deiconify()
        entry.focus_force()
        tk_root.update()
        focused = tk_root.focus_get()
        if focused is None:
            pytest.skip("Focus not available in this environment")
        return focused

    def test_external_focus_preserved_on_shape_change(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()

        external_entry = tk.Entry(tk_root)
        external_entry.pack()
        self._focus_entry(tk_root, external_entry)

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(), status="오류"),)
        )
        tk_root.update_idletasks()

        assert tk_root.focus_get() == external_entry

    def test_same_shape_does_not_change_focus(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()

        external_entry = tk.Entry(tk_root)
        external_entry.pack()
        self._focus_entry(tk_root, external_entry)

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "2"),)),)
        )
        tk_root.update_idletasks()

        assert tk_root.focus_get() == external_entry

    def test_internal_focus_not_restored_on_shape_change(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()

        # Place an Entry inside the summary card so it is destroyed during rebuild.
        card = panel._summary_holder.winfo_children()[0]
        internal_entry = tk.Entry(card)
        internal_entry.grid(row=10, column=0)
        self._focus_entry(tk_root, internal_entry)

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(), status="오류"),)
        )
        tk_root.update_idletasks()

        # Internal widget inside _summary_holder is destroyed by _clear_summary_tables;
        # focus should not be forced back to a destroyed (or now absent) widget.
        focused = tk_root.focus_get()
        assert focused is None or focused != internal_entry

    def test_destroyed_external_focus_ignored(self, panel, tk_root) -> None:
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()

        external_entry = tk.Entry(tk_root)
        external_entry.pack()
        self._focus_entry(tk_root, external_entry)

        # Destroy the external widget before shape change
        external_entry.destroy()
        tk_root.update_idletasks()

        # Must not raise even though the previously focused widget is gone
        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(), status="오류"),)
        )
        tk_root.update_idletasks()
