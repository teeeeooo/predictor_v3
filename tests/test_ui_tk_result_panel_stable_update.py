"""Tests for ResultPanel stable summary update (same-shape value-only update).

These tests verify that ResultPanel.set_summaries reuses existing widgets
when the summary shape (title + field labels) is unchanged, and falls back
to full rebuild when the shape changes.
"""

from __future__ import annotations

import pytest

from ui_tk.result_models import ResultSummary
from ui_tk.result_panel import ResultPanel


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
        assert labels[0].cget("text") == "1"

        panel.set_summaries(
            (ResultSummary(title="CSPF", fields=(("A", "99"),)),)
        )
        tk_root.update_idletasks()
        assert labels[0].cget("text") == "99"

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
