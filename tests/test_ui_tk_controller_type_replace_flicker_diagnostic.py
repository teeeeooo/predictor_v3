"""Diagnostic tests for controller type-replace ResultPanel flicker.

These tests instrument the CSPF (TkTableController) and HSPF
(ExcelLikeTableController) sections to compare callback/render counts
per keystroke and verify ResultPanel rebuild behavior.

No production code changes.
"""

from __future__ import annotations

import pytest


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
def cspf_section(tk_root):
    from ui_tk.sections.hong_kong_cspf_section import HongKongCspfSection

    sec = HongKongCspfSection(tk_root, region_label="Hong Kong")
    sec.pack()
    tk_root.update_idletasks()
    return sec


@pytest.fixture
def hspf_section(tk_root):
    from ui_tk.sections.hong_kong_hspf_section import HongKongHspfSection

    sec = HongKongHspfSection(tk_root, region_label="Hong Kong")
    sec.pack()
    tk_root.update_idletasks()
    return sec


class TestScheduleCountAfterTypeReplace:
    """One type-replace keystroke should schedule exactly one auto-calc."""

    def _wrap_schedule(self, section):
        calls = []
        original = section._auto_calc.schedule

        def wrapper():
            calls.append(None)
            original()

        section._auto_calc.schedule = wrapper
        # Re-register so tables hit the wrapper, not the original bound method.
        if hasattr(section, "rated_table"):
            section.rated_table.set_values_changed_callback(section._auto_calc.schedule)
        if hasattr(section, "input_table"):
            section.input_table.set_values_changed_callback(section._auto_calc.schedule)
        return calls

    def test_cspf_input_type_replace_schedules_once(self, cspf_section, tk_root) -> None:
        calls = self._wrap_schedule(cspf_section)
        ctrl = cspf_section.input_controller
        ctrl.select((0, 0))
        tk_root.update_idletasks()

        event = type("Event", (), {"keysym": "5", "char": "5", "state": 0})()
        ctrl._type_replace(event, (0, 0))
        tk_root.update_idletasks()

        assert len(calls) == 1, f"Expected 1 schedule call, got {len(calls)}"

    def test_hspf_input_type_replace_schedules_once(self, hspf_section, tk_root) -> None:
        calls = self._wrap_schedule(hspf_section)
        ctrl = hspf_section.input_controller
        ctrl.select((0, 0))
        tk_root.update_idletasks()

        event = type("Event", (), {"keysym": "5", "char": "5", "state": 0})()
        ctrl._type_replace(event, (0, 0))
        tk_root.update_idletasks()

        assert len(calls) == 1, f"Expected 1 schedule call, got {len(calls)}"


class TestScheduleCountAfterNativeEdit:
    """Subsequent native edit keystrokes should schedule once per change."""

    def _wrap_schedule(self, section):
        calls = []
        original = section._auto_calc.schedule

        def wrapper():
            calls.append(None)
            original()

        section._auto_calc.schedule = wrapper
        # Re-register so tables hit the wrapper, not the original bound method.
        if hasattr(section, "rated_table"):
            section.rated_table.set_values_changed_callback(section._auto_calc.schedule)
        if hasattr(section, "input_table"):
            section.input_table.set_values_changed_callback(section._auto_calc.schedule)
        return calls

    def test_cspf_native_edit_schedules_once_per_keystroke(self, cspf_section, tk_root) -> None:
        calls = self._wrap_schedule(cspf_section)
        # Enter edit mode first via type_replace
        ctrl = cspf_section.input_controller
        ctrl.select((0, 0))
        tk_root.update_idletasks()
        event = type("Event", (), {"keysym": "5", "char": "5", "state": 0})()
        ctrl._type_replace(event, (0, 0))
        tk_root.update_idletasks()
        calls.clear()

        # Simulate a native edit keystroke by writing the StringVar directly
        var = cspf_section.input_table._variables["full_capacity"]
        var.set("55")
        tk_root.update_idletasks()

        assert len(calls) == 1, f"Expected 1 schedule call after native edit, got {len(calls)}"

    def test_hspf_native_edit_schedules_once_per_keystroke(self, hspf_section, tk_root) -> None:
        calls = self._wrap_schedule(hspf_section)
        ctrl = hspf_section.input_controller
        ctrl.select((0, 0))
        tk_root.update_idletasks()
        event = type("Event", (), {"keysym": "5", "char": "5", "state": 0})()
        ctrl._type_replace(event, (0, 0))
        tk_root.update_idletasks()
        calls.clear()

        var = hspf_section.input_table._variables["full_capacity"]
        var.set("55")
        tk_root.update_idletasks()

        assert len(calls) == 1, f"Expected 1 schedule call after native edit, got {len(calls)}"


class TestSetSummariesCountAfterFlush:
    """Flush should call set_summaries exactly once per section."""

    def _wrap_set_summaries(self, section):
        calls = []
        original = section.result_panel.set_summaries

        def wrapper(summaries):
            calls.append(None)
            original(summaries)

        section.result_panel.set_summaries = wrapper
        return calls

    def test_cspf_flush_calls_set_summaries_once(self, cspf_section) -> None:
        calls = self._wrap_set_summaries(cspf_section)
        cspf_section._auto_calc.flush_now()
        assert len(calls) == 1, f"Expected 1 set_summaries call, got {len(calls)}"

    def test_hspf_flush_calls_set_summaries_once(self, hspf_section) -> None:
        calls = self._wrap_set_summaries(hspf_section)
        hspf_section._auto_calc.flush_now()
        assert len(calls) == 1, f"Expected 1 set_summaries call, got {len(calls)}"


class TestResultPanelRebuild:
    """ResultPanel set_summaries destroys and recreates child widgets."""

    def test_result_panel_rebuilds_children(self, cspf_section, tk_root) -> None:
        from ui_tk.result_models import ResultSummary

        panel = cspf_section.result_panel
        panel.set_summaries(
            (ResultSummary(title="Test", fields=(("A", "1"),)),)
        )
        tk_root.update_idletasks()
        first_children = list(panel._summary_holder.winfo_children())

        panel.set_summaries(
            (ResultSummary(title="Test", fields=(("A", "2"),)),)
        )
        tk_root.update_idletasks()
        second_children = list(panel._summary_holder.winfo_children())

        # Full rebuild: widget identities differ
        assert first_children != second_children
        assert len(first_children) == len(second_children) == 1


class TestCspfHspfScheduleParity:
    """CSPF and HSPF should have identical schedule counts for the same interaction."""

    def _wrap_schedule(self, section):
        calls = []
        original = section._auto_calc.schedule

        def wrapper():
            calls.append(None)
            original()

        section._auto_calc.schedule = wrapper
        # Re-register so tables hit the wrapper, not the original bound method.
        if hasattr(section, "rated_table"):
            section.rated_table.set_values_changed_callback(section._auto_calc.schedule)
        if hasattr(section, "input_table"):
            section.input_table.set_values_changed_callback(section._auto_calc.schedule)
        return calls

    def test_type_replace_schedule_count_is_equal(self, cspf_section, hspf_section, tk_root) -> None:
        cspf_calls = self._wrap_schedule(cspf_section)
        hspf_calls = self._wrap_schedule(hspf_section)

        for sec, ctrl_attr in (
            (cspf_section, "input_controller"),
            (hspf_section, "input_controller"),
        ):
            ctrl = getattr(sec, ctrl_attr)
            ctrl.select((0, 0))
        tk_root.update_idletasks()

        event = type("Event", (), {"keysym": "5", "char": "5", "state": 0})()
        for sec, ctrl_attr in (
            (cspf_section, "input_controller"),
            (hspf_section, "input_controller"),
        ):
            ctrl = getattr(sec, ctrl_attr)
            ctrl._type_replace(event, (0, 0))
        tk_root.update_idletasks()

        assert len(cspf_calls) == len(hspf_calls), (
            f"CSPF schedule calls: {len(cspf_calls)}, HSPF schedule calls: {len(hspf_calls)}"
        )
