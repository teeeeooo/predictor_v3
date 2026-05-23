"""Vertical-slice tests for ISO Hong Kong table input and auto-calc."""

from __future__ import annotations

import sys

import pytest

from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.metric_input_table import MetricInputTable


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


def _label_texts(widget) -> list[str]:
    labels = []
    stack = [widget]
    while stack:
        current = stack.pop()
        stack.extend(current.winfo_children())
        if current.winfo_class() == "TLabel":
            labels.append(current.cget("text"))
    return labels


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
    tab = _make_tab(tk_root)

    assert set(tab.sections) == {"CSPF", "HSPF"}
    assert isinstance(tab.sections["CSPF"].input_table, MetricInputTable)
    assert isinstance(tab.sections["HSPF"].input_table, MetricInputTable)

    buttons = []
    labels = []
    stack = list(tab._sections_holder.winfo_children())
    while stack:
        widget = stack.pop()
        stack.extend(widget.winfo_children())
        if widget.winfo_class() == "TButton":
            buttons.append(widget.cget("text"))
        if widget.winfo_class() == "TLabel":
            labels.append(widget.cget("text"))
    assert "CSPF 계산" not in buttons
    assert "HSPF 계산" not in buttons
    for label in ("정격", "35 Full", "35 Half", "정격 난방", "7 Full", "7 Half"):
        assert label in labels
    assert labels.count("능력 [W]") == 2
    assert labels.count("전력 [W]") == 2


def test_default_autocalc_results_are_combined_without_append_growth(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)

    text = _result_text(tab)
    assert "4.939 | 1769.6 | 358.3" in text
    assert "3.643 | 273.2 | 75.0" in text
    assert "None" not in text
    assert "74991.00727784102" not in text
    assert text.count("[CSPF]") == 1
    assert text.count("[HSPF]") == 1
    result_labels = _label_texts(tab.result_panel._summary_holder)
    for label in (
        "CSPF",
        "CSTL [kWh]",
        "CSEC [kWh]",
        "HSPF",
        "HSTL [kWh]",
        "HSEC [kWh]",
    ):
        assert label in result_labels

    tab.sections["CSPF"].recalculate_now()
    assert _result_text(tab).count("[CSPF]") == 1

    tab.result_panel.clear()
    assert _result_text(tab) == ""
    assert not tab.result_panel._summary_holder.winfo_children()


def test_cell_change_updates_cspf_and_invalid_value_shows_input_error(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)
    cspf = tab.sections["CSPF"]

    assert cspf.input_table.set_value("full_power", "1000") is True
    cspf._auto_calc.flush_now()
    updated = _result_text(tab)
    assert "4.939 | 1769.6 | 358.3" not in updated
    assert "3.643 | 273.2 | 75.0" in updated

    assert cspf.input_table.set_value("full_power", "bad") is True
    cspf._auto_calc.flush_now()
    invalid = _result_text(tab)
    assert "입력 오류: 숫자 입력을 확인하세요." in invalid
    assert "Traceback" not in invalid


def test_same_value_does_not_schedule_recalculation(tk_root):
    tab = _make_tab(tk_root)
    cspf = tab.sections["CSPF"]
    cspf._auto_calc.cancel()
    calls = []
    cspf.input_table.set_values_changed_callback(lambda: calls.append("changed"))

    assert cspf.input_table.set_value("full_capacity", "3600") is False
    assert calls == []
