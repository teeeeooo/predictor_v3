"""Vertical-slice tests for ISO Hong Kong table input and auto-calc."""

from __future__ import annotations

import sys

import pytest

from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.table_grid import TableGrid


class FakeAfterOwner:
    def __init__(self) -> None:
        self.callbacks = {}
        self.cancelled = []
        self.next_id = 0

    def after(self, delay_ms, callback):
        self.next_id += 1
        callback_id = f"pending-{self.next_id}"
        self.callbacks[callback_id] = (delay_ms, callback)
        return callback_id

    def after_cancel(self, callback_id):
        self.cancelled.append(callback_id)
        self.callbacks.pop(callback_id, None)


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


def _result_text(tab) -> str:
    import tkinter as tk

    return tab.result_panel._text.get("1.0", tk.END).strip()


def _make_tab(root):
    from ui_tk.tabs.iso16358_tab import Iso16358Tab

    tab = Iso16358Tab(root)
    tab.pack()
    return tab


def _flush_defaults(tab) -> None:
    tab.sections["CSPF"]._auto_calc.flush_now()
    tab.sections["HSPF"]._auto_calc.flush_now()


def test_debounce_reschedules_flushes_and_disposes():
    owner = FakeAfterOwner()
    calls = []
    debounce = DebouncedAutoCalc(owner, lambda: calls.append("calculated"), delay_ms=180)

    debounce.schedule()
    first_id = next(iter(owner.callbacks))
    debounce.schedule()

    assert first_id in owner.cancelled
    assert len(owner.callbacks) == 1
    assert next(iter(owner.callbacks.values()))[0] == 180

    debounce.flush_now()
    assert calls == ["calculated"]
    assert not owner.callbacks

    debounce.schedule()
    debounce.dispose()
    debounce.schedule()
    assert not owner.callbacks
    assert calls == ["calculated"]


def test_iso_tab_import_does_not_pull_in_pyqt5():
    for name in list(sys.modules):
        if name.startswith("PyQt5"):
            del sys.modules[name]

    import ui_tk.tabs.iso16358_tab  # noqa: F401

    assert not any(name.startswith("PyQt5") for name in sys.modules)


def test_iso_hong_kong_sections_use_grids_without_calculate_buttons(tk_root):
    import tkinter as tk
    from tkinter import ttk

    tab = _make_tab(tk_root)

    assert set(tab.sections) == {"CSPF", "HSPF"}
    assert isinstance(tab.sections["CSPF"].declared_grid, TableGrid)
    assert isinstance(tab.sections["CSPF"].points_grid, TableGrid)
    assert isinstance(tab.sections["HSPF"].rated_grid, TableGrid)
    assert isinstance(tab.sections["HSPF"].points_grid, TableGrid)

    buttons = []
    stack = list(tab._sections_holder.winfo_children())
    while stack:
        widget = stack.pop()
        stack.extend(widget.winfo_children())
        if isinstance(widget, ttk.Button):
            buttons.append(widget.cget("text"))
    assert "CSPF 계산" not in buttons
    assert "HSPF 계산" not in buttons


def test_default_autocalc_results_are_combined_without_append_growth(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)

    text = _result_text(tab)
    assert "CSPF = 4.939" in text
    assert "HSPF = 3.643" in text
    assert text.count("[CSPF]") == 1
    assert text.count("[HSPF]") == 1

    tab.sections["CSPF"].recalculate_now()
    assert _result_text(tab).count("[CSPF]") == 1


def test_cell_change_updates_cspf_and_invalid_value_shows_input_error(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)
    cspf = tab.sections["CSPF"]

    assert cspf.points_grid.set_cell("35_full", "power_w", "1000") is True
    cspf._auto_calc.flush_now()
    updated = _result_text(tab)
    assert "CSPF = 4.939" not in updated
    assert "HSPF = 3.643" in updated

    assert cspf.points_grid.set_cell("35_full", "power_w", "bad") is True
    cspf._auto_calc.flush_now()
    invalid = _result_text(tab)
    assert "[CSPF 입력 오류] 숫자 입력을 확인하세요." in invalid
    assert "Traceback" not in invalid


def test_same_value_does_not_schedule_recalculation(tk_root):
    tab = _make_tab(tk_root)
    cspf = tab.sections["CSPF"]
    cspf._auto_calc.cancel()
    calls = []
    cspf.points_grid.set_values_changed_callback(lambda: calls.append("changed"))

    assert cspf.points_grid.set_cell("35_full", "capacity_w", "3600") is False
    assert calls == []
