"""Vertical-slice tests for ISO Hong Kong table input and auto-calc."""

from __future__ import annotations

import csv
import sys

import pytest

from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.excel_like_table_controller import ExcelLikeTableController
import ui_tk.layout_constants as layout_constants
from ui_tk.layout_constants import (
    ISO_SECTION_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
    TABLE_FONT_SIZE,
    TABLE_ROW_HEADER_CHARS,
)
from ui_tk.metric_input_table import MetricInputTable
from ui_tk import table_csv_export
from ui_tk import table_clipboard


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


def _two_point_text(tab) -> str:
    import tkinter as tk

    return tab._two_point_section.result_table._text.get("1.0", tk.END).strip()


def _two_point_tree_values(tab) -> list[tuple[str, ...]]:
    tree = tab._two_point_section.result_table.table
    return [tuple(tree.item(item_id, "values")) for item_id in tree.get_children()]


def _bin_trace_rows(tab) -> tuple[tuple[str, ...], ...]:
    return tab._two_point_section.trace_table.table_rows()


def _joined_rows(rows: tuple[tuple[str, ...], ...]) -> str:
    return "\n".join("\t".join(row) for row in rows)


def _saso_text(tab) -> str:
    import tkinter as tk

    return tab._saso_t3_section.result_table._text.get("1.0", tk.END).strip()


def _saso_tree_values(tab) -> list[tuple[str, ...]]:
    tree = tab._saso_t3_section.result_table.table
    return [tuple(tree.item(item_id, "values")) for item_id in tree.get_children()]


def _saso_bin_trace_rows(tab) -> tuple[tuple[str, ...], ...]:
    return tab._saso_t3_section.trace_table.table_rows()


def _hong_kong_cspf_bin_trace_rows(tab) -> tuple[tuple[str, ...], ...]:
    return tab.sections["CSPF"].trace_table.table_rows()


def _label_texts(widget) -> list[str]:
    labels = []
    stack = [widget]
    while stack:
        current = stack.pop()
        stack.extend(current.winfo_children())
        if current.winfo_class() in {"Label", "TLabel"}:
            labels.append(current.cget("text"))
    return labels


def _widget_texts(widget) -> list[str]:
    texts = []
    stack = [widget]
    while stack:
        current = stack.pop()
        stack.extend(current.winfo_children())
        try:
            text = current.cget("text")
        except Exception:
            continue
        if text:
            texts.append(text)
    return texts


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


def _canvas_texts(canvas) -> set[str]:
    return {
        canvas.itemcget(item_id, "text")
        for item_id in canvas.find_all()
        if canvas.type(item_id) == "text"
    }


def _assert_canvas_has_scale_label(canvas, series_label: str) -> None:
    texts = _canvas_texts(canvas)
    assert any(
        text.startswith(f"{series_label} (min ") and ", max " in text
        for text in texts
    )


def test_bin_detail_graph_returns_y_scale_for_selected_series():
    from ui_tk.sections.bin_detail_panel import BinDetailGraph

    graph = BinDetailGraph.__new__(BinDetailGraph)
    graph._rows = (
        {"tj": 20.0, "eer": 3.25},
        {"tj": 25.0, "eer": 4.5},
        {"tj": 30.0, "eer": 4.0},
    )
    graph._series_key = "eer"

    points, x_axis_label, x_min, x_max, y_min, y_max = graph._plot_points(
        plot_width=100,
        plot_height=80,
        margin_left=10,
        margin_top=5,
    )

    assert len(points) == 3
    assert x_axis_label == "Outdoor Temp [°C]"
    assert (x_min, x_max) == (20.0, 30.0)
    assert (y_min, y_max) == (3.25, 4.5)
    assert graph._series_scale_label(y_min, y_max) == "EER [W/W] (min 3.25, max 4.50)"


def _make_tab(root):
    from ui_tk.tabs.iso16358_tab import Iso16358Tab

    tab = Iso16358Tab(root)
    tab.pack(fill="both", expand=True)
    return tab


def _flush_defaults(tab) -> None:
    tab.sections["CSPF"]._auto_calc.flush_now()
    tab.sections["HSPF"]._auto_calc.flush_now()


def _select_mode(tab, mode_label: str) -> None:
    tab._mode_combo.set(mode_label)
    tab._on_mode_changed()
    tab.update_idletasks()


def _make_hong_kong_tab(root):
    tab = _make_tab(root)
    _select_mode(tab, "Hong Kong")
    return tab


def _make_saso_tab(root):
    tab = _make_tab(root)
    _select_mode(tab, "SASO T3")
    return tab


def test_table_csv_export_writes_headers_and_rows(tmp_path):
    path = tmp_path / "result.csv"

    table_csv_export.write_csv(path, ("이름", "Value"), (("냉방", "4.939"),))

    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        assert list(csv.reader(handle)) == [["이름", "Value"], ["냉방", "4.939"]]


def test_table_csv_export_writes_header_for_empty_rows(tmp_path):
    path = tmp_path / "empty.csv"

    table_csv_export.write_csv(path, ("A", "B"), ())

    with path.open(newline="", encoding="utf-8-sig") as handle:
        assert list(csv.reader(handle)) == [["A", "B"]]


def test_table_csv_export_cancel_is_noop(monkeypatch):
    monkeypatch.setattr(
        table_csv_export.filedialog,
        "asksaveasfilename",
        lambda **_kwargs: "",
    )

    assert table_csv_export.export_table_to_csv(None, "cancel.csv", ("A",), (("B",),)) is False


def test_table_copy_helper_encodes_headers_and_rows():
    assert table_clipboard.encode_table_tsv(
        ("Name", "Value"), (("CSPF", "4.939"), ("Status", "OK"))
    ) == "Name\tValue\nCSPF\t4.939\nStatus\tOK"


def test_table_copy_helper_encodes_header_for_empty_rows():
    assert table_clipboard.encode_table_tsv(("Name", "Value"), ()) == "Name\tValue"


def test_iso_tab_defaults_to_2point_profile_with_results(tk_root):
    tab = _make_tab(tk_root)

    assert tab._mode_combo.get() == "ISO / ISEER 2-point"
    assert tab.sections == {}
    assert tab._two_point_section is not None
    assert set(tab._two_point_section.result_table.row_labels) == {
        "ISO 16358-1",
        "India ISEER",
    }


def test_iso_iseer_2point_mode_renders_default_summaries(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    assert section is not None
    assert tab.sections == {}
    assert section.input_table.columns == (("full", "35 Full"), ("half", "35 Half"))
    assert section.input_table.rows == (("capacity", "능력 [W]"), ("power", "전력 [W]"))
    assert section.input_table.get_text_values() == {
        "full_capacity": "3600",
        "full_power": "900",
        "half_capacity": "1700",
        "half_power": "380",
    }
    assert isinstance(section.input_controller, ExcelLikeTableController)

    table = section.result_table
    assert table.surface_role == "two_point_result_surface"
    assert table.table.surface_role == "two_point_comparison_table"
    assert table.column_labels == (
        "Region/Profile",
        "EER Full",
        "EER Half",
        "CSPF/ISEER",
        "CSTL [kWh]",
        "CSEC [kWh]",
    )
    assert table.row_labels == ("ISO 16358-1", "India ISEER")
    rows = _two_point_tree_values(tab)
    assert len(rows) == 2
    assert {row[0] for row in rows} == {"ISO 16358-1", "India ISEER"}
    assert all(len(row) == len(table.column_labels) for row in rows)
    assert not section.detail_panel.is_visible()
    assert section.trace_profile_combo.get() == "ISO 16358-1"
    assert section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert "Bin trace" not in _widget_texts(section._frame)
    assert "Trace 복사" not in _widget_texts(section._frame)
    assert "Trace CSV 내보내기" not in _widget_texts(section._frame)

    text = _two_point_text(tab)
    for label in table.column_labels:
        assert label in text
    assert "ISO 16358-1" in text
    assert "India ISEER" in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text


def test_iso_iseer_2point_input_change_updates_both_summaries(tk_root):
    tab = _make_tab(tk_root)
    _select_mode(tab, "ISO / ISEER 2-point")
    section = tab._two_point_section
    before = _two_point_text(tab)
    before_rows = _two_point_tree_values(tab)

    assert section.input_table.set_value("full_power", "1000") is True
    section._auto_calc.flush_now()
    after = _two_point_text(tab)
    after_rows = _two_point_tree_values(tab)

    assert after != before
    assert after_rows != before_rows
    assert len(after_rows) == 2
    assert {row[0] for row in after_rows} == {"ISO 16358-1", "India ISEER"}
    assert "ISO 16358-1" in after
    assert "India ISEER" in after
    assert after.count("ISO 16358-1") == 1
    assert after.count("India ISEER") == 1


def test_iso_iseer_2point_invalid_input_shows_safe_status(tk_root):
    tab = _make_tab(tk_root)
    _select_mode(tab, "ISO / ISEER 2-point")
    section = tab._two_point_section

    assert section.input_table.set_value("full_power", "bad") is True
    section._auto_calc.flush_now()
    text = _two_point_text(tab)

    assert "입력 오류: 숫자 입력을 확인하세요." in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text
    assert _two_point_tree_values(tab) == []
    assert section.result_table.row_labels == ()
    assert section.result_table.status_label.surface_role == "two_point_result_status"
    assert section.result_table.status_label.cget("text") == "입력 오류: 숫자 입력을 확인하세요."

    assert section.input_table.set_value("full_power", "900") is True
    section._auto_calc.flush_now()
    assert len(_two_point_tree_values(tab)) == 2
    assert set(section.result_table.row_labels) == {"ISO 16358-1", "India ISEER"}


def test_iso_iseer_detail_panel_opens_with_bin_details(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section
    fit_calls = []
    section._on_detail_visibility_changed = lambda: fit_calls.append("fit")

    assert section is not None
    assert not section.detail_panel.is_visible()
    assert set(section._trace_results) == {"ISO 16358-1", "India ISEER"}
    assert all(section._trace_results[label] for label in section._trace_results)

    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert fit_calls == ["fit"]
    assert section.detail_panel.graph.canvas.winfo_exists()
    assert section.detail_panel.graph_label.cget("text") == "그래프 항목"
    assert section.detail_panel.graph_combo.get() == "Bin Hours [h]"
    assert "EER [W/W]" in section.detail_panel.graph_combo.cget("values")
    tk_root.update_idletasks()
    assert "Outdoor Temp [°C]" in _canvas_texts(section.detail_panel.graph.canvas)
    _assert_canvas_has_scale_label(section.detail_panel.graph.canvas, "Bin Hours [h]")
    assert section.detail_panel.copy_button.cget("text") == "상세 복사"
    assert section.detail_panel.csv_button.cget("text") == "상세 CSV 내보내기"
    assert section.trace_table.column_labels == (
        "Bin No",
        "Temp [°C]",
        "Hours",
        "Load [W]",
        "Capacity [W]",
        "Power [W]",
        "EER",
        "CSTL [Wh]",
        "CSEC [Wh]",
    )
    rows = _bin_trace_rows(tab)
    assert rows
    assert all(len(row) == len(section.trace_table.column_labels) for row in rows)
    assert rows[0][0]
    assert rows[0][1]
    rendered = _joined_rows(rows)
    assert "Traceback" not in rendered
    assert "{" not in rendered
    assert "None" not in rendered

    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert not section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert fit_calls == ["fit", "fit"]


def test_iso_iseer_detail_graph_scale_label_updates_with_selected_series(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    section.detail_panel.graph_combo.set("EER [W/W]")
    section.detail_panel._on_graph_changed()
    tk_root.update_idletasks()

    texts = _canvas_texts(section.detail_panel.graph.canvas)
    assert "Outdoor Temp [°C]" in texts
    _assert_canvas_has_scale_label(section.detail_panel.graph.canvas, "EER [W/W]")


def test_iso_iseer_detail_source_selector_updates_rows(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    iso_rows = _bin_trace_rows(tab)
    assert iso_rows

    section.trace_profile_combo.set("India ISEER")
    section.detail_panel._on_source_changed()
    iseer_rows = _bin_trace_rows(tab)

    assert section.trace_profile_combo.get() == "India ISEER"
    assert iseer_rows
    assert iseer_rows != iso_rows
    rendered = _joined_rows(iseer_rows)
    assert "Traceback" not in rendered
    assert "{" not in rendered
    assert "None" not in rendered


def test_iso_iseer_detail_invalid_input_clears_stale_rows(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert _bin_trace_rows(tab)

    assert section.input_table.set_value("full_power", "bad") is True
    section._auto_calc.flush_now()

    assert section._trace_results == {}
    assert _bin_trace_rows(tab) == ()
    text = section.trace_table.as_text()
    assert "입력 오류: 숫자 입력을 확인하세요." in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text


def test_iso_iseer_table_export_data_hooks_cover_result_and_trace(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    result_headers, result_rows = section.result_table.table_export_data()
    assert result_headers == section.result_table.column_labels
    assert len(result_rows) == 2
    assert {row[0] for row in result_rows} == {"ISO 16358-1", "India ISEER"}

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    trace_headers, trace_rows = section.trace_table.table_export_data()
    assert trace_headers == section.trace_table.column_labels
    assert trace_rows == _bin_trace_rows(tab)
    assert trace_rows


def test_iso_iseer_detail_copy_button_uses_header_included_tsv(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    assert section.result_table.copy_table() is True
    result_clipboard = tk_root.clipboard_get()
    assert result_clipboard.splitlines()[0] == "\t".join(
        section.result_table.column_labels
    )
    assert "ISO 16358-1" in result_clipboard
    assert "India ISEER" in result_clipboard

    section.detail_toggle.invoke()
    section.trace_profile_combo.set("India ISEER")
    assert section.detail_panel.copy_button.invoke() == 1
    trace_clipboard = tk_root.clipboard_get()
    assert trace_clipboard.splitlines()[0] == "\t".join(
        section.trace_table.column_labels
    )
    assert "Traceback" not in trace_clipboard
    assert "{" not in trace_clipboard
    assert "None" not in trace_clipboard


def test_iso_iseer_detail_csv_export_button_still_calls_helper(monkeypatch, tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section
    calls = []

    def fake_export(parent, default_filename, headers, rows):
        calls.append((parent, default_filename, headers, rows))
        return True

    monkeypatch.setattr(table_csv_export, "export_table_to_csv", fake_export)

    assert not hasattr(section, "result_csv_button")
    section.detail_toggle.invoke()
    section.trace_profile_combo.set("India ISEER")
    assert section.detail_panel.csv_button.invoke() == 1
    assert calls[-1][1] == "iso_iseer_bin_detail.csv"
    assert calls[-1][2] == section.trace_table.column_labels
    assert calls[-1][3] == section.trace_table.rows

    monkeypatch.setattr(
        table_csv_export,
        "export_table_to_csv",
        lambda *_args, **_kwargs: False,
    )
    assert section.detail_panel.csv_button.invoke() == 0


def test_read_only_table_keyboard_copy_and_select_all_are_safe(tk_root):
    tab = _make_tab(tk_root)
    table = tab._two_point_section.result_table

    assert table.select_all() == "break"
    assert table.copy() == "break"

    clipboard = tk_root.clipboard_get()
    assert clipboard.splitlines()[0] == "\t".join(table.column_labels)


def test_saso_t3_profile_renders_default_result(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    assert section is not None
    assert tab.sections == {}
    assert tab.result_panel is section.result_table
    assert section.input_table.columns == (
        ("full_46", "46 Full"),
        ("full_35", "35 Full"),
        ("half_35", "35 Half"),
        ("min_35", "35 Min"),
    )
    assert section.input_table.rows == (("capacity", "능력 [W]"), ("power", "전력 [W]"))
    assert isinstance(section.input_controller, ExcelLikeTableController)
    assert section.optional_min_enabled.get() is True
    assert section.optional_min_toggle.winfo_manager() == ""
    assert "35 Min optional test 사용" not in _widget_texts(section._frame)
    assert section.input_table.editable_entries["min_35_capacity"].cget("state") == "normal"
    assert section.input_table.editable_entries["min_35_power"].cget("state") == "normal"
    assert not section.detail_panel.is_visible()
    assert section.trace_profile_combo.get() == "With 35 Min (4-point)"
    assert section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert "Bin trace" not in _widget_texts(section._frame)
    assert "Trace 복사" not in _widget_texts(section._frame)
    assert "Trace CSV 내보내기" not in _widget_texts(section._frame)

    table = section.result_table
    assert table.surface_role == "saso_t3_result_surface"
    assert table.table.surface_role == "saso_t3_comparison_table"
    assert table.column_labels == (
        "Scenario",
        "EER 46 Full",
        "EER 35 Full",
        "EER 35 Half",
        "EER 35 Min",
        "CSPF",
        "CSTL [kWh]",
        "CSEC [kWh]",
    )
    rows = _saso_tree_values(tab)
    assert len(rows) == 2
    assert [row[0] for row in rows] == [
        "With 35 Min (4-point)",
        "Required only (3-point)",
    ]
    assert rows[0][4] != "-"
    assert rows[1][4] == "-"
    assert table.row_labels == (
        "With 35 Min (4-point)",
        "Required only (3-point)",
    )

    text = _saso_text(tab)
    for label in table.column_labels:
        assert label in text
    assert "Required only (3-point)" in text
    assert "With 35 Min (4-point)" in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text


def test_saso_t3_detail_panel_opens_with_required_bin_details(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section
    fit_calls = []
    section._on_detail_visibility_changed = lambda: fit_calls.append("fit")

    assert section is not None
    assert not section.detail_panel.is_visible()
    assert set(section._trace_results) == {
        "With 35 Min (4-point)",
        "Required only (3-point)",
    }
    assert section._trace_results["Required only (3-point)"]
    assert section._trace_results["With 35 Min (4-point)"]

    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert fit_calls == ["fit"]
    assert section.detail_panel.graph.canvas.winfo_exists()
    assert section.detail_panel.graph_label.cget("text") == "그래프 항목"
    assert section.detail_panel.graph_combo.get() == "Bin Hours [h]"
    assert "EER [W/W]" in section.detail_panel.graph_combo.cget("values")
    tk_root.update_idletasks()
    assert "Outdoor Temp [°C]" in _canvas_texts(section.detail_panel.graph.canvas)
    assert section.detail_panel.copy_button.cget("text") == "상세 복사"
    assert section.detail_panel.csv_button.cget("text") == "상세 CSV 내보내기"
    assert section.trace_table.column_labels == (
        "Bin No",
        "Temp [°C]",
        "Hours",
        "Load [W]",
        "Capacity [W]",
        "Power [W]",
        "EER",
        "CSTL [Wh]",
        "CSEC [Wh]",
    )
    rows = _saso_bin_trace_rows(tab)
    assert rows
    assert all(len(row) == len(section.trace_table.column_labels) for row in rows)
    rendered = _joined_rows(rows)
    assert "Traceback" not in rendered
    assert "{" not in rendered
    assert "None" not in rendered

    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert not section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert fit_calls == ["fit", "fit"]


def test_saso_t3_detail_optional_selector_uses_4point_bin_details(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    optional_rows = _saso_bin_trace_rows(tab)
    assert optional_rows

    section.trace_profile_combo.set("Required only (3-point)")
    section.detail_panel._on_source_changed()
    required_rows = _saso_bin_trace_rows(tab)
    assert required_rows

    assert set(section._trace_results) == {
        "With 35 Min (4-point)",
        "Required only (3-point)",
    }
    assert optional_rows != required_rows
    rendered = _joined_rows(optional_rows)
    assert "Traceback" not in rendered
    assert "{" not in rendered
    assert "None" not in rendered


def test_saso_t3_table_export_data_hooks_cover_result_and_trace(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    result_headers, result_rows = section.result_table.table_export_data()
    assert result_headers == section.result_table.column_labels
    assert len(result_rows) == 2
    assert [row[0] for row in result_rows] == [
        "With 35 Min (4-point)",
        "Required only (3-point)",
    ]

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    trace_headers, trace_rows = section.trace_table.table_export_data()
    assert trace_headers == section.trace_table.column_labels
    assert trace_rows == _saso_bin_trace_rows(tab)
    assert trace_rows


def test_saso_t3_detail_copy_button_uses_header_included_tsv(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    assert section.result_table.copy_table() is True
    result_clipboard = tk_root.clipboard_get()
    assert result_clipboard.splitlines()[0] == "\t".join(
        section.result_table.column_labels
    )
    assert "Required only (3-point)" in result_clipboard
    assert "With 35 Min (4-point)" in result_clipboard

    section.detail_toggle.invoke()
    section.trace_profile_combo.set("With 35 Min (4-point)")
    assert section.detail_panel.copy_button.invoke() == 1
    trace_clipboard = tk_root.clipboard_get()
    assert trace_clipboard.splitlines()[0] == "\t".join(
        section.trace_table.column_labels
    )
    assert "Traceback" not in trace_clipboard
    assert "{" not in trace_clipboard
    assert "None" not in trace_clipboard


def test_saso_t3_detail_csv_export_button_still_calls_helper(monkeypatch, tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section
    calls = []

    def fake_export(parent, default_filename, headers, rows):
        calls.append((parent, default_filename, headers, rows))
        return True

    monkeypatch.setattr(table_csv_export, "export_table_to_csv", fake_export)

    assert not hasattr(section, "result_csv_button")
    section.detail_toggle.invoke()
    section.trace_profile_combo.set("With 35 Min (4-point)")
    assert section.detail_panel.csv_button.invoke() == 1
    assert calls[-1][1] == "saso_t3_bin_detail.csv"
    assert calls[-1][2] == section.trace_table.column_labels
    assert calls[-1][3] == section.trace_table.rows

    monkeypatch.setattr(
        table_csv_export,
        "export_table_to_csv",
        lambda *_args, **_kwargs: False,
    )
    assert section.detail_panel.csv_button.invoke() == 0


def test_saso_t3_optional_min_valid_compares_3point_and_4point(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    before_rows = _saso_tree_values(tab)

    assert len(before_rows) == 2
    assert [row[0] for row in before_rows] == [
        "With 35 Min (4-point)",
        "Required only (3-point)",
    ]
    assert before_rows[0][4] != "-"
    assert before_rows[1][4] == "-"

    assert section.input_table.set_value("min_35_capacity", "1500") is True
    section._auto_calc.flush_now()
    after_rows = _saso_tree_values(tab)

    assert after_rows[0] != before_rows[0]
    assert after_rows[1] == before_rows[1]
    assert len(after_rows) == 2
    assert _saso_text(tab).count("Required only (3-point)") == 1
    assert _saso_text(tab).count("With 35 Min (4-point)") == 1


def test_saso_t3_optional_min_invalid_keeps_3point_and_safe_4point_status(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    required_trace_before = _saso_bin_trace_rows(tab)
    assert required_trace_before

    assert section.input_table.set_value("min_35_power", "bad") is True
    section._auto_calc.flush_now()

    rows = _saso_tree_values(tab)
    text = _saso_text(tab)
    assert len(rows) == 2
    assert rows[1][0] == "Required only (3-point)"
    assert rows[1][4] == "-"
    assert rows[0] == (
        "With 35 Min (4-point)",
        "-",
        "-",
        "-",
        "입력 오류",
        "-",
        "-",
        "-",
    )
    assert "4-point 입력 오류" in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text
    assert section._trace_results["Required only (3-point)"]
    section.trace_profile_combo.set("Required only (3-point)")
    section.detail_panel._on_source_changed()
    assert _saso_bin_trace_rows(tab)
    section.trace_profile_combo.set("With 35 Min (4-point)")
    section.detail_panel._on_source_changed()
    assert _saso_bin_trace_rows(tab) == ()
    assert "상세 데이터 없음" in section.trace_table.as_text()


def test_saso_t3_required_input_invalid_shows_safe_status(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert _saso_bin_trace_rows(tab)

    assert section.input_table.set_value("full_46_power", "bad") is True
    section._auto_calc.flush_now()
    text = _saso_text(tab)

    assert "입력 오류: 필수 시험점 숫자 입력을 확인하세요." in text
    assert _saso_tree_values(tab) == []
    assert section.result_table.row_labels == ()
    assert section.result_table.status_label.surface_role == "saso_t3_result_status"
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text
    assert section._trace_results == {}
    assert _saso_bin_trace_rows(tab) == ()
    assert "입력 오류: 필수 시험점 숫자 입력을 확인하세요." in section.trace_table.as_text()


def test_mode_switch_restores_hong_kong_metric_sections(tk_root):
    tab = _make_tab(tk_root)

    _select_mode(tab, "SASO T3")
    assert tab.sections == {}
    assert tab._saso_t3_section is not None
    assert tab._saso_t3_frame.winfo_manager() == "pack"
    assert tab._hong_kong_frame.winfo_manager() == ""
    assert tab._two_point_frame.winfo_manager() == ""
    assert tab._region_row.winfo_manager() == ""

    _select_mode(tab, "Hong Kong")
    assert set(tab.sections) == {"CSPF", "HSPF"}
    assert [tab._metric_notebook.tab(t, "text") for t in tab._metric_notebook.tabs()] == [
        "CSPF",
        "HSPF",
    ]
    assert tab._region_row.winfo_manager() == ""
    assert tab._region_label.winfo_manager() == "pack"
    assert tab._region_combo.winfo_manager() == "pack"
    assert tab.result_panel is tab.sections["CSPF"].result_panel

    _select_mode(tab, "ISO / ISEER 2-point")
    assert tab.sections == {}

    _select_mode(tab, "SASO T3")
    assert tab.sections == {}
    assert tab._saso_t3_section.result_table.row_labels == (
        "With 35 Min (4-point)",
        "Required only (3-point)",
    )

    _select_mode(tab, "Hong Kong")
    assert set(tab.sections) == {"CSPF", "HSPF"}


def test_profile_switch_with_open_detail_panel_is_lifecycle_safe(tk_root):
    tab = _make_tab(tk_root)
    section = tab._two_point_section

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert section.detail_panel.is_visible()
    assert _bin_trace_rows(tab)

    _select_mode(tab, "Hong Kong")
    assert set(tab.sections) == {"CSPF", "HSPF"}

    _select_mode(tab, "SASO T3")
    assert tab._saso_t3_section is not None
    saso_section = tab._saso_t3_section
    assert saso_section.result_table.row_labels == (
        "With 35 Min (4-point)",
        "Required only (3-point)",
    )
    saso_section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert saso_section.detail_panel.is_visible()
    assert _saso_bin_trace_rows(tab)

    _select_mode(tab, "ISO / ISEER 2-point")
    assert tab._two_point_section is section
    assert section.detail_panel.is_visible()
    assert _bin_trace_rows(tab)

    _select_mode(tab, "SASO T3")
    assert tab._saso_t3_section is saso_section
    assert saso_section.detail_panel.is_visible()
    assert _saso_bin_trace_rows(tab)


def test_profile_switch_fits_current_content_without_breaking_sections(tk_root):
    tk_root.geometry("650x300")
    tab = _make_tab(tk_root)
    tk_root.update_idletasks()
    _iso_preferred_width, iso_preferred_height = tab.preferred_initial_size()
    reset_calls = []
    reset_scroll_position = tab._scrollable.reset_scroll_position

    def reset_and_record() -> None:
        reset_calls.append("reset")
        reset_scroll_position()

    tab._scrollable.reset_scroll_position = reset_and_record

    _select_mode(tab, "Hong Kong")
    tk_root.update_idletasks()
    assert tab.vertical_overflow_delta() == 0
    hong_kong_height = tk_root.winfo_height()
    assert hong_kong_height >= iso_preferred_height
    assert tab._canvas.yview()[0] == 0.0
    assert reset_calls == ["reset"]
    assert set(tab.sections) == {"CSPF", "HSPF"}
    assert tab.sections["CSPF"].result_panel.summary_tables["CSPF"].surface_role == (
        "summary_table"
    )
    assert tab.sections["HSPF"].result_panel.summary_tables["HSPF"].surface_role == (
        "summary_table"
    )

    _select_mode(tab, "ISO / ISEER 2-point")
    tk_root.update_idletasks()
    assert tab.sections == {}
    assert tk_root.winfo_height() <= hong_kong_height
    assert tab.vertical_overflow_delta() == 0
    assert tab._canvas.yview()[0] == 0.0
    assert reset_calls == ["reset", "reset"]
    assert tab._two_point_section.result_table.row_labels == (
        "ISO 16358-1",
        "India ISEER",
    )

    _select_mode(tab, "SASO T3")
    tk_root.update_idletasks()
    assert tab.sections == {}
    assert tab.vertical_overflow_delta() == 0
    assert tab._canvas.yview()[0] == 0.0
    assert reset_calls == ["reset", "reset", "reset"]
    assert tab._saso_t3_section.result_table.row_labels == (
        "With 35 Min (4-point)",
        "Required only (3-point)",
    )


def test_preferred_initial_size_reflects_rendered_result(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    rendered_w, rendered_h = tab.preferred_initial_size()
    # Clear results to get the empty-result baseline.
    for metric in ("CSPF", "HSPF"):
        tab.sections[metric].result_panel.clear()
    tab.update_idletasks()
    empty_w, empty_h = tab.preferred_initial_size()
    # Height should not shrink when results are rendered (regression guard).
    assert rendered_h >= empty_h


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
    tab = _make_hong_kong_tab(tk_root)

    assert set(tab.sections) == {"CSPF", "HSPF"}
    cspf = tab.sections["CSPF"]
    hspf = tab.sections["HSPF"]
    assert isinstance(cspf.input_table, MetricInputTable)
    assert isinstance(hspf.input_table, MetricInputTable)
    assert isinstance(cspf.rated_table, MetricInputTable)
    assert not hasattr(hspf, "rated_table")
    assert isinstance(cspf.rated_controller, ExcelLikeTableController)
    assert cspf.rated_table.interaction_controller is cspf.rated_controller
    for section in (cspf, hspf):
        assert isinstance(section.input_controller, ExcelLikeTableController)
        assert section.input_table.interaction_controller is section.input_controller

    buttons = []
    labels = []
    stack = []
    for metric in ("CSPF", "HSPF"):
        stack.append(tab.sections[metric]._frame)
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
    assert labels.count("능력 [W]") == 3
    assert labels.count("전력 [W]") == 2
    assert "전력 [W]" not in _label_texts(cspf.rated_table)
    assert set(_label_texts(cspf.input_table)) >= {"35 Full", "35 Half"}
    assert set(_label_texts(hspf.input_table)) >= {"7 Full", "7 Half"}
    assert "정격 표기치" not in _label_texts(cspf.input_table)
    assert "정격 표기치" not in _label_texts(hspf.input_table)
    assert cspf._frame.cget("text") == "CSPF 입력 (Hong Kong)"
    assert cspf.result_panel.title_label.cget("text") == "CSPF 결과"
    assert hspf._frame.cget("text") == "HSPF 입력 (Hong Kong)"
    assert hspf.result_panel.title_label.cget("text") == "HSPF 결과"

    rendered_sections = [
        tab._metric_notebook.nametowidget(t) for t in tab._metric_notebook.tabs()
    ]
    assert rendered_sections == [cspf._frame, hspf._frame]

    # preferred_initial_size should use the largest metric tab, not sum them.
    pref_w, pref_h = tab.preferred_initial_size()
    # With two metric tabs, height should reflect the larger tab, not both stacked.
    assert pref_h < cspf._frame.winfo_reqheight() + hspf._frame.winfo_reqheight() + 50
    assert cspf.rated_table.grid_info()["row"] < cspf.input_table.grid_info()["row"]
    for section in (cspf, hspf):
        assert (
            section.input_table.grid_info()["row"]
            < section.result_panel._frame.grid_info()["row"]
        )
        assert section.input_table.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.result_panel._frame.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.input_table.grid_info()["sticky"] == "ew"
        assert section.result_panel._frame.grid_info()["sticky"] == "ew"
    assert cspf.rated_table.grid_info()["padx"] == ISO_SECTION_PADX
    assert cspf.rated_table.grid_info()["sticky"] == "ew"


def test_metric_inputs_render_bordered_matrix_cell_roles(tk_root):
    tab = _make_hong_kong_tab(tk_root)

    for metric in ("CSPF", "HSPF"):
        section = tab.sections[metric]
        table = section.input_table
        roles = _surface_roles(table)

        assert table.table_frame.surface_role == "table_frame"
        assert table.layout_policy == "responsive"
        assert table.table_frame.layout_policy == "responsive"
        assert table.row_header_chars == TABLE_ROW_HEADER_CHARS
        assert table.data_column_chars == TABLE_DATA_COLUMN_CHARS
        assert not hasattr(table, "content_width")
        assert not hasattr(table, "total_columns_hint")
        assert not hasattr(layout_constants, "ISO_SECTION_CONTENT_WIDTH")
        assert not hasattr(layout_constants, "MATRIX_ROW_HEADER_WIDTH")
        assert not hasattr(layout_constants, "MATRIX_DATA_COLUMN_WIDTH")
        expected_columns = (
            (("full", "35 Full"), ("half", "35 Half"))
            if metric == "CSPF"
            else (("full", "7 Full"), ("half", "7 Half"))
        )
        assert table.columns == expected_columns
        assert table.rows == (("capacity", "능력 [W]"), ("power", "전력 [W]"))
        assert set(table.cell_frames) == {
            ("capacity", "full"),
            ("power", "full"),
            ("capacity", "half"),
            ("power", "half"),
        }
        assert tuple(table.editable_entries) == table.field_order
        assert len(table.header_cells) == 2
        assert len(table.row_header_cells) == 2
        assert len(table.editable_cell_frames) == 4
        assert not table.static_cell_frames
        assert roles.count("header_cell") == 3  # includes the corner cell
        assert roles.count("row_header_cell") == 2
        assert roles.count("editable_cell") == 4
        assert "static_cell" not in roles

        from tkinter import font as tk_font

        entries = list(table.editable_entries.values())
        if metric == "CSPF":
            rated = section.rated_table
            rated_roles = _surface_roles(rated)
            assert rated.layout_policy == table.layout_policy
            assert rated.row_header_chars == table.row_header_chars
            assert rated.data_column_chars == table.data_column_chars
            assert set(rated.cell_frames) == {("rated", "capacity")}
            assert tuple(rated.editable_entries) == rated.field_order
            assert len(rated.header_cells) == 1
            assert len(rated.row_header_cells) == 1
            assert len(rated.editable_cell_frames) == 1
            assert not rated.static_cell_frames
            assert rated_roles.count("header_cell") == 2
            assert rated_roles.count("row_header_cell") == 1
            assert rated_roles.count("editable_cell") == 1
            assert "전력 [W]" not in _label_texts(rated)
            entries.extend(rated.editable_entries.values())

        for entry in entries:
            assert entry.cget("justify") == "center"
            assert tk_font.Font(root=tk_root, font=entry.cget("font")).cget("size") >= (
                TABLE_FONT_SIZE
            )
            assert entry.pack_info()["pady"] == TABLE_CELL_PADY
        assert TABLE_CELL_PADY <= 4


def test_metric_surfaces_expand_together_with_window_width(tk_root):
    tk_root.geometry("650x900")
    tab = _make_hong_kong_tab(tk_root)
    _flush_defaults(tab)
    tk_root.update_idletasks()

    def widths(section, metric):
        tab._metric_notebook.select(section._frame)
        tk_root.update_idletasks()
        widgets = [section.input_table.table_frame, section.result_panel.summary_tables[metric]]
        if hasattr(section, "rated_table"):
            widgets.insert(0, section.rated_table.table_frame)
        return tuple(widget.winfo_width() for widget in widgets)

    def left_offsets(section, metric):
        tab._metric_notebook.select(section._frame)
        tk_root.update_idletasks()
        widgets = [section.input_table.table_frame, section.result_panel.summary_tables[metric]]
        if hasattr(section, "rated_table"):
            widgets.insert(0, section.rated_table.table_frame)
        return tuple(widget.winfo_rootx() - section._frame.winfo_rootx() for widget in widgets)

    initial = {metric: widths(tab.sections[metric], metric) for metric in ("CSPF", "HSPF")}
    initial_offsets = {
        metric: left_offsets(tab.sections[metric], metric) for metric in ("CSPF", "HSPF")
    }
    tk_root.geometry("950x900")
    tk_root.update_idletasks()
    expanded = {metric: widths(tab.sections[metric], metric) for metric in ("CSPF", "HSPF")}
    expanded_offsets = {
        metric: left_offsets(tab.sections[metric], metric) for metric in ("CSPF", "HSPF")
    }

    for metric in ("CSPF", "HSPF"):
        assert len(set(initial[metric])) == 1
        assert len(set(expanded[metric])) == 1
        assert len(set(initial_offsets[metric])) == 1
        assert len(set(expanded_offsets[metric])) == 1
        assert expanded[metric][0] > initial[metric][0]


def test_default_autocalc_results_are_section_local_without_append_growth(tk_root):
    tab = _make_hong_kong_tab(tk_root)
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
        assert panel.layout_policy == "responsive"
        assert panel.summary_tables[metric].layout_policy == panel.layout_policy
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


def test_hong_kong_cspf_detail_panel_opens_with_bin_details(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]
    hspf = tab.sections["HSPF"]
    fit_calls = []
    cspf._on_detail_visibility_changed = lambda: fit_calls.append("fit")

    assert not hasattr(hspf, "trace_table")
    assert not cspf.detail_panel.is_visible()
    assert cspf._trace_rows
    assert cspf.detail_toggle.cget("text") == "상세 보기 ↓"
    assert "Bin trace" not in _widget_texts(cspf._frame)
    assert "Trace 복사" not in _widget_texts(cspf._frame)
    assert "Trace CSV 내보내기" not in _widget_texts(cspf._frame)

    cspf.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert cspf.detail_panel.is_visible()
    assert cspf.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert fit_calls == ["fit"]
    assert cspf.detail_panel.graph.canvas.winfo_exists()
    assert cspf.detail_panel.graph_label.cget("text") == "그래프 항목"
    assert cspf.detail_panel.graph_combo.get() == "Bin Hours [h]"
    assert "EER [W/W]" in cspf.detail_panel.graph_combo.cget("values")
    tk_root.update_idletasks()
    assert "Outdoor Temp [°C]" in _canvas_texts(cspf.detail_panel.graph.canvas)
    assert cspf.detail_panel.copy_button.cget("text") == "상세 복사"
    assert cspf.detail_panel.csv_button.cget("text") == "상세 CSV 내보내기"
    assert cspf.trace_table.column_labels == (
        "Bin No",
        "Temp [°C]",
        "Hours",
        "Load [W]",
        "Capacity [W]",
        "Power [W]",
        "EER",
        "CSTL [Wh]",
        "CSEC [Wh]",
    )
    rows = _hong_kong_cspf_bin_trace_rows(tab)
    assert rows
    assert all(len(row) == len(cspf.trace_table.column_labels) for row in rows)
    rendered = _joined_rows(rows)
    assert "Traceback" not in rendered
    assert "{" not in rendered
    assert "None" not in rendered

    cspf.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert not cspf.detail_panel.is_visible()
    assert cspf.detail_toggle.cget("text") == "상세 보기 ↓"
    assert fit_calls == ["fit", "fit"]


def test_hong_kong_cspf_bin_trace_invalid_input_clears_stale_rows(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]

    cspf.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert _hong_kong_cspf_bin_trace_rows(tab)

    assert cspf.input_table.set_value("full_power", "bad") is True
    cspf._auto_calc.flush_now()

    assert cspf._trace_rows == []
    assert _hong_kong_cspf_bin_trace_rows(tab) == ()
    text = cspf.trace_table.as_text()
    assert "입력 오류: 숫자 입력을 확인하세요." in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text


def test_hong_kong_cspf_detail_csv_export_button_calls_helper(monkeypatch, tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]
    calls = []

    def fake_export(parent, default_filename, headers, rows):
        calls.append((parent, default_filename, headers, rows))
        return True

    monkeypatch.setattr(table_csv_export, "export_table_to_csv", fake_export)

    cspf.detail_toggle.invoke()
    assert cspf.detail_panel.csv_button.invoke() == 1
    assert calls[-1][1] == "hong_kong_cspf_bin_detail.csv"
    assert calls[-1][2] == cspf.trace_table.column_labels
    assert calls[-1][3] == cspf.trace_table.rows

    monkeypatch.setattr(
        table_csv_export,
        "export_table_to_csv",
        lambda *_args, **_kwargs: False,
    )
    assert cspf.detail_panel.csv_button.invoke() == 0


def test_hong_kong_cspf_detail_copy_button_uses_header_included_tsv(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]

    cspf.detail_toggle.invoke()
    assert cspf.detail_panel.copy_button.invoke() == 1
    clipboard = tk_root.clipboard_get()

    assert clipboard.splitlines()[0] == "\t".join(cspf.trace_table.column_labels)
    assert "Traceback" not in clipboard
    assert "{" not in clipboard
    assert "None" not in clipboard


def test_profile_switch_with_open_hong_kong_cspf_detail_is_lifecycle_safe(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]

    cspf.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert cspf.detail_panel.is_visible()
    assert _hong_kong_cspf_bin_trace_rows(tab)

    _select_mode(tab, "ISO / ISEER 2-point")
    assert tab._two_point_section is not None

    _select_mode(tab, "SASO T3")
    assert tab._saso_t3_section is not None

    _select_mode(tab, "Hong Kong")
    new_cspf = tab.sections["CSPF"]
    assert new_cspf is not cspf
    assert not new_cspf.detail_panel.is_visible()
    assert new_cspf._trace_rows


def test_cell_change_updates_cspf_and_invalid_value_shows_input_error(tk_root):
    tab = _make_hong_kong_tab(tk_root)
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
    assert panel.summary_tables["CSPF"].layout_policy == panel.layout_policy
    assert "summary_title" not in _surface_roles(panel._summary_holder)
    assert "summary_header_cell" not in _surface_roles(panel._summary_holder)
    assert "summary_value_cell" not in _surface_roles(panel._summary_holder)
    assert "CSPF" not in panel.summary_header_cells
    assert "CSPF" not in panel.summary_value_cells
    assert panel.summary_status_labels["CSPF"].cget("text") == (
        "입력 오류: 숫자 입력을 확인하세요."
    )


def test_same_value_does_not_schedule_recalculation(tk_root):
    tab = _make_hong_kong_tab(tk_root)
    cspf = tab.sections["CSPF"]
    cspf._auto_calc.cancel()
    calls = []
    cspf.input_table.set_values_changed_callback(lambda: calls.append("changed"))

    assert cspf.input_table.set_value("full_capacity", "3600") is False
    assert calls == []
