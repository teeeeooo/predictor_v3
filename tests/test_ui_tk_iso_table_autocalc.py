"""Vertical-slice tests for ISO Hong Kong table input and auto-calc."""

from __future__ import annotations

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


def _saso_text(tab) -> str:
    import tkinter as tk

    return tab._saso_t3_section.result_table._text.get("1.0", tk.END).strip()


def _saso_tree_values(tab) -> list[tuple[str, ...]]:
    tree = tab._saso_t3_section.result_table.table
    return [tuple(tree.item(item_id, "values")) for item_id in tree.get_children()]


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
    assert section.optional_min_toggle.cget("text") == "35 Min optional test 사용"
    assert section.input_table.editable_entries["min_35_capacity"].cget("state") == "disabled"
    assert section.input_table.editable_entries["min_35_power"].cget("state") == "disabled"

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
    assert len(rows) == 1
    assert rows[0][0] == "Required only (3-point)"
    assert rows[0][4] == "-"
    assert table.row_labels == ("Required only (3-point)",)

    text = _saso_text(tab)
    for label in table.column_labels:
        assert label in text
    assert "Required only (3-point)" in text
    assert "With 35 Min (4-point)" not in text
    assert "Traceback" not in text
    assert "{" not in text
    assert "None" not in text


def test_saso_t3_optional_min_valid_compares_3point_and_4point(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    section.optional_min_enabled.set(True)
    section._on_optional_min_toggled()
    section._auto_calc.flush_now()
    before_rows = _saso_tree_values(tab)

    assert len(before_rows) == 2
    assert [row[0] for row in before_rows] == [
        "Required only (3-point)",
        "With 35 Min (4-point)",
    ]
    assert before_rows[0][4] == "-"
    assert before_rows[1][4] != "-"

    assert section.input_table.set_value("min_35_capacity", "1500") is True
    section._auto_calc.flush_now()
    after_rows = _saso_tree_values(tab)

    assert after_rows[0] == before_rows[0]
    assert after_rows[1] != before_rows[1]
    assert len(after_rows) == 2
    assert _saso_text(tab).count("Required only (3-point)") == 1
    assert _saso_text(tab).count("With 35 Min (4-point)") == 1


def test_saso_t3_optional_min_invalid_keeps_3point_and_safe_4point_status(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

    section.optional_min_enabled.set(True)
    section._on_optional_min_toggled()
    assert section.input_table.set_value("min_35_power", "bad") is True
    section._auto_calc.flush_now()

    rows = _saso_tree_values(tab)
    text = _saso_text(tab)
    assert len(rows) == 2
    assert rows[0][0] == "Required only (3-point)"
    assert rows[0][4] == "-"
    assert rows[1] == (
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


def test_saso_t3_required_input_invalid_shows_safe_status(tk_root):
    tab = _make_saso_tab(tk_root)
    section = tab._saso_t3_section

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
    assert tab._saso_t3_section.result_table.row_labels == ("Required only (3-point)",)

    _select_mode(tab, "Hong Kong")
    assert set(tab.sections) == {"CSPF", "HSPF"}


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
    assert tab._saso_t3_section.result_table.row_labels == ("Required only (3-point)",)


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
    assert isinstance(hspf.rated_table, MetricInputTable)
    for section in (cspf, hspf):
        assert isinstance(section.rated_controller, ExcelLikeTableController)
        assert isinstance(section.input_controller, ExcelLikeTableController)
        assert section.rated_table.interaction_controller is section.rated_controller
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

    rendered_sections = [
        tab._metric_notebook.nametowidget(t) for t in tab._metric_notebook.tabs()
    ]
    assert rendered_sections == [cspf._frame, hspf._frame]

    # preferred_initial_size should use the largest metric tab, not sum them.
    pref_w, pref_h = tab.preferred_initial_size()
    # With two metric tabs, height should reflect the larger tab, not both stacked.
    assert pref_h < cspf._frame.winfo_reqheight() + hspf._frame.winfo_reqheight() + 50
    for section in (cspf, hspf):
        assert section.rated_table.grid_info()["row"] < section.input_table.grid_info()["row"]
        assert (
            section.input_table.grid_info()["row"]
            < section.result_panel._frame.grid_info()["row"]
        )
        assert section.rated_table.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.input_table.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.result_panel._frame.grid_info()["padx"] == ISO_SECTION_PADX
        assert section.rated_table.grid_info()["sticky"] == "ew"
        assert section.input_table.grid_info()["sticky"] == "ew"
        assert section.result_panel._frame.grid_info()["sticky"] == "ew"


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
        from tkinter import font as tk_font

        for entry in (*table.editable_entries.values(), *rated.editable_entries.values()):
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
        return (
            section.rated_table.table_frame.winfo_width(),
            section.input_table.table_frame.winfo_width(),
            section.result_panel.summary_tables[metric].winfo_width(),
        )

    def left_offsets(section, metric):
        tab._metric_notebook.select(section._frame)
        tk_root.update_idletasks()
        return tuple(
            widget.winfo_rootx() - section._frame.winfo_rootx()
            for widget in (
                section.rated_table.table_frame,
                section.input_table.table_frame,
                section.result_panel.summary_tables[metric],
            )
        )

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
