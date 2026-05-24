"""Vertical-slice tests for ISO Hong Kong table input and auto-calc."""

from __future__ import annotations

import sys

import pytest

from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.layout_constants import (
    ISO_SECTION_CONTENT_WIDTH,
    ISO_SECTION_DATA_COLUMNS,
    ISO_SECTION_PADX,
    MATRIX_DATA_COLUMN_WIDTH,
    MATRIX_ROW_HEADER_WIDTH,
)
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


def _result_text(tab, metric: str) -> str:
    import tkinter as tk

    return tab.sections[metric].result_panel._text.get("1.0", tk.END).strip()


def _label_texts(widget) -> list[str]:
    labels = []
    stack = [widget]
    while stack:
        current = stack.pop()
        stack.extend(current.winfo_children())
        if current.winfo_class() in {"Label", "TLabel"}:
            labels.append(current.cget("text"))
    return labels


def _surface_roles(widget) -> list[str]:
    roles = []
    stack = [widget]
    while stack:
        current = stack.pop()
        stack.extend(current.winfo_children())
        role = getattr(current, "surface_role", None)
        if role is not None:
            roles.append(role)
    return roles


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


def test_iso_hong_kong_sections_use_corrected_layout_without_action_buttons(tk_root):
    tab = _make_tab(tk_root)

    assert set(tab.sections) == {"CSPF", "HSPF"}
    cspf = tab.sections["CSPF"]
    hspf = tab.sections["HSPF"]
    assert isinstance(cspf.input_table, MetricInputTable)
    assert isinstance(hspf.input_table, MetricInputTable)
    assert isinstance(cspf.rated_table, MetricInputTable)
    assert isinstance(hspf.rated_table, MetricInputTable)

    buttons = []
    labels = []
    stack = list(tab._sections_holder.winfo_children())
    while stack:
        widget = stack.pop()
        stack.extend(widget.winfo_children())
        if widget.winfo_class() == "TButton":
            buttons.append(widget.cget("text"))
        if widget.winfo_class() in {"Label", "TLabel"}:
            labels.append(widget.cget("text"))
    assert "CSPF 계산" not in buttons
    assert "HSPF 계산" not in buttons
    assert "결과 복사" not in buttons
    assert "결과 지우기" not in buttons
    for label in ("정격 표기치", "35 Full", "35 Half", "7 Full", "7 Half"):
        assert label in labels
    assert "정격" not in labels
    assert "정격 난방" not in labels
    assert labels.count("능력 [W]") == 4
    assert labels.count("전력 [W]") == 2
    assert "전력 [W]" not in _label_texts(cspf.rated_table)
    assert "전력 [W]" not in _label_texts(hspf.rated_table)
    assert set(_label_texts(cspf.input_table)) >= {"35 Full", "35 Half"}
    assert set(_label_texts(hspf.input_table)) >= {"7 Full", "7 Half"}
    assert "정격 표기치" not in _label_texts(cspf.input_table)
    assert "정격 표기치" not in _label_texts(hspf.input_table)
    assert cspf._frame.cget("text") == "CSPF 입력 (Hong Kong)"
    assert cspf.result_panel.title_label.cget("text") == "CSPF 결과"
    assert hspf._frame.cget("text") == "HSPF 입력 (Hong Kong)"
    assert hspf.result_panel.title_label.cget("text") == "HSPF 결과"

    rendered_sections = tab._sections_holder.winfo_children()
    assert rendered_sections == [cspf._frame, hspf._frame]
    for section in (cspf, hspf):
        assert section.rated_table.grid_info()["row"] < section.input_table.grid_info()["row"]
        assert (
            section.input_table.grid_info()["row"]
            < section.result_panel._frame.grid_info()["row"]
        )
        assert section.rated_table.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.input_table.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.result_panel._frame.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.result_panel._frame.grid_info()["sticky"] == "w"


def test_metric_inputs_render_bordered_matrix_cell_roles(tk_root):
    tab = _make_tab(tk_root)

    for metric in ("CSPF", "HSPF"):
        section = tab.sections[metric]
        table = section.input_table
        roles = _surface_roles(table)

        assert table.table_frame.surface_role == "table_frame"
        assert table.row_header_width == MATRIX_ROW_HEADER_WIDTH
        assert table.data_column_width == MATRIX_DATA_COLUMN_WIDTH
        assert table.total_columns_hint == ISO_SECTION_DATA_COLUMNS
        assert table.content_width == ISO_SECTION_CONTENT_WIDTH
        assert table.table_frame.content_width == ISO_SECTION_CONTENT_WIDTH
        assert len(table.header_cells) == 2
        assert len(table.row_header_cells) == 2
        assert len(table.editable_cell_frames) == 4
        assert not table.static_cell_frames
        assert roles.count("header_cell") == 3  # includes the corner cell
        assert roles.count("row_header_cell") == 2
        assert roles.count("editable_cell") == 4
        assert "static_cell" not in roles

        rated = section.rated_table
        rated_roles = _surface_roles(rated)
        assert rated.row_header_width == table.row_header_width
        assert rated.data_column_width == table.data_column_width
        assert rated.total_columns_hint == table.total_columns_hint
        assert rated.content_width == table.content_width
        assert rated.table_frame.content_width == table.table_frame.content_width
        assert len(rated.header_cells) == 1
        assert len(rated.row_header_cells) == 1
        assert len(rated.editable_cell_frames) == 1
        assert not rated.static_cell_frames
        assert rated_roles.count("header_cell") == 2
        assert rated_roles.count("row_header_cell") == 1
        assert rated_roles.count("editable_cell") == 1
        assert "전력 [W]" not in _label_texts(rated)
        for entry in (*table._entries.values(), *rated._entries.values()):
            assert entry.cget("justify") == "center"


def test_default_autocalc_results_are_section_local_without_append_growth(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)

    cspf_text = _result_text(tab, "CSPF")
    hspf_text = _result_text(tab, "HSPF")
    assert "4.939 | 1769.6 | 358.3" in cspf_text
    assert "[HSPF]" not in cspf_text
    assert "3.643 | 273.2 | 75.0" in hspf_text
    assert "[CSPF]" not in hspf_text
    for text in (cspf_text, hspf_text):
        assert "None" not in text
        assert "74991.00727784102" not in text
        assert "{" not in text
    for metric, labels in (
        ("CSPF", ("CSPF", "CSTL [kWh]", "CSEC [kWh]")),
        ("HSPF", ("HSPF", "HSTL [kWh]", "HSEC [kWh]")),
    ):
        panel = tab.sections[metric].result_panel
        result_labels = _label_texts(panel._summary_holder)
        for label in labels:
            assert label in result_labels
        assert panel.summary_tables[metric].surface_role == "summary_table"
        assert panel.content_width == ISO_SECTION_CONTENT_WIDTH
        assert panel.summary_tables[metric].content_width == panel.content_width
        assert panel.content_width == tab.sections[metric].input_table.content_width
        assert len(panel.summary_header_cells[metric]) == 3
        assert len(panel.summary_value_cells[metric]) == 3
        assert panel.summary_status_labels[metric].surface_role == "summary_status"

    tab.sections["CSPF"].recalculate_now()
    assert _result_text(tab, "CSPF").count("[CSPF]") == 1
    assert _result_text(tab, "HSPF").count("[HSPF]") == 1

    tab.sections["CSPF"].result_panel.clear()
    assert _result_text(tab, "CSPF") == ""
    assert not tab.sections["CSPF"].result_panel._summary_holder.winfo_children()
    assert _result_text(tab, "HSPF").count("[HSPF]") == 1


def test_cell_change_updates_cspf_and_invalid_value_shows_input_error(tk_root):
    tab = _make_tab(tk_root)
    _flush_defaults(tab)
    cspf = tab.sections["CSPF"]

    assert cspf.input_table.set_value("full_power", "1000") is True
    cspf._auto_calc.flush_now()
    updated = _result_text(tab, "CSPF")
    assert "4.939 | 1769.6 | 358.3" not in updated
    assert "3.643 | 273.2 | 75.0" in _result_text(tab, "HSPF")

    assert cspf.input_table.set_value("full_power", "bad") is True
    cspf._auto_calc.flush_now()
    invalid = _result_text(tab, "CSPF")
    assert "입력 오류: 숫자 입력을 확인하세요." in invalid
    assert "Traceback" not in invalid
    assert "None" not in invalid
    assert "74991.00727784102" not in invalid
    panel = cspf.result_panel
    assert panel.summary_tables["CSPF"].surface_role == "status_surface"
    assert panel.summary_tables["CSPF"].content_width == panel.content_width
    assert "summary_title" not in _surface_roles(panel._summary_holder)
    assert "summary_header_cell" not in _surface_roles(panel._summary_holder)
    assert "summary_value_cell" not in _surface_roles(panel._summary_holder)
    assert "CSPF" not in panel.summary_header_cells
    assert "CSPF" not in panel.summary_value_cells
    assert panel.summary_status_labels["CSPF"].cget("text") == (
        "입력 오류: 숫자 입력을 확인하세요."
    )


def test_same_value_does_not_schedule_recalculation(tk_root):
    tab = _make_tab(tk_root)
    cspf = tab.sections["CSPF"]
    cspf._auto_calc.cancel()
    calls = []
    cspf.input_table.set_values_changed_callback(lambda: calls.append("changed"))

    assert cspf.input_table.set_value("full_capacity", "3600") is False
    assert calls == []
