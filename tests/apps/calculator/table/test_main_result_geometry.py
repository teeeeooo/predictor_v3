"""Exercise result appearance through real main tabs, with one isolated Tk root."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


def test_main_result_placeholders_keep_geometry_and_empty_exports():
    # A full app after earlier same-process Tk roots can hang on macOS. Run the
    # actual shell in a fresh interpreter, as in the existing foundation smoke.
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "tests.apps.calculator.table.test_main_result_geometry"],
        cwd=Path(__file__).resolve().parents[4],
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )
    if completed.returncode == 77:
        pytest.skip("Native Tk is not available")
    assert completed.returncode == 0, completed.stdout + completed.stderr


def _descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


def _visible_height(widget):
    top = widget.winfo_rooty()
    bottom = top + widget.winfo_height()
    parent = widget.master
    while parent is not None:
        y = parent.winfo_rooty()
        top = max(top, y)
        bottom = min(bottom, y + parent.winfo_height())
        parent = parent.master
    return max(0, bottom - top)


def _exercise_case(root, app, tab, notebook, page, section, values, column_count):
    from apps.calculator.ui.metric_input_table import MetricInputTable
    from apps.calculator.ui.table.visual_policy import SemanticTone

    app.notebook.select(tab)
    root.update()
    notebook.select(page)
    section._auto_calc.flush_now()
    root.update()
    tables = tuple(
        widget for widget in _descendants(section._frame)
        if isinstance(widget, MetricInputTable) and widget.winfo_ismapped()
    )
    initial_values = [(table, table.get_text_values()) for table in tables]
    values = {k: v for k, v in values.items() if any(k in t.field_order for t in tables)}
    key = next(k for k in values if "capacity" in k)
    edited_table = next(t for t in tables if key in t.field_order)
    panel = section.result_panel
    grid, = panel.summary_grids.values()
    assert len(grid.headers) == column_count
    initial_height = page.winfo_reqheight()

    def assert_geometry():
        root.update()
        assert tuple(panel.summary_grids.values()) == (grid,)
        assert page.winfo_reqheight() == initial_height
        assert page.winfo_height() >= page.winfo_reqheight()
        scroll = tab._scrollable
        scroll.canvas.yview_moveto(1)
        root.update()
        assert _visible_height(section.batch_button) == section.batch_button.winfo_height()
        scroll.reset_scroll_position()

    def assert_empty():
        assert panel._summaries == ()
        assert grid.rows == (("-",) * column_count,)
        assert panel._text.get("1.0", "end").strip() == ""
        assert panel.sectioned_csv_rows() == (("Status", "No results"),)

    def flush():
        section._auto_calc.flush_now()
        assert_geometry()

    assert_empty()
    assert_geometry()
    # The reported EN failure starts with only Tested A/B, before a full result.
    partial = {k: values[k] for k in (
        "tested_capacity_A", "tested_power_A", "tested_capacity_B", "tested_power_B"
    ) if k in values} or {key: values[key]}
    for table in tables:
        table.set_values_batch({k: v for k, v in partial.items() if k in table.field_order})
    flush()
    for table in tables:
        table.set_values_batch({k: v for k, v in values.items() if k in table.field_order})
    flush()
    assert panel._summaries
    assert grid.rows[0][0] != "-"
    assert tuple(label for label, _ in panel._summaries[0].fields) == grid.headers

    # A manually smaller window must remain scrollable and retain that size on
    # subsequent invalid/empty input, without relying on a tab round trip.
    root.geometry(f"{root.winfo_width()}x{min(500, root.winfo_screenheight() // 2)}")
    root.update()
    manual_size = root.winfo_width(), root.winfo_height()
    edited_table.set_value(key, "bad")
    flush()
    assert_empty()
    assert grid.cell_tone((0, 0)) == SemanticTone.INVALID
    for table, original in initial_values:
        table.set_values_batch(original)
    flush()
    assert_empty()
    assert grid.cell_tone((0, 0)) == SemanticTone.PENDING
    assert (root.winfo_width(), root.winfo_height()) == manual_size


def _run_native_probe():
    try:
        import tkinter as tk
    except ImportError:
        raise SystemExit(77)
    try:
        root = tk.Tk()
    except tk.TclError:
        raise SystemExit(77)

    from apps.calculator.ui.calculator_app import CalculatorTkApp
    from tests.apps.calculator.combinations.seeds import contexts

    errors = []
    root.report_callback_exception = lambda *error: errors.append(error)
    try:
        app = CalculatorTkApp(root)
        root.update()
        root.deiconify()
        root.update()
        samples = contexts()
        en = app.en14825_tab
        values = dict(next(c for c in samples if c.kind == "en_seer").values)
        values["p_design_c"] = "3500"
        _exercise_case(root, app, en, en._standard_notebook, en._seer_frame,
                       en.seer_section, values, 5)

        ahri = app.ahri210240_tab
        for metric, product, label, columns in (
            ("seer2", "variable_capacity", "Variable Capacity", 3),
            ("seer2", "dual_stage", "Dual Stage", 4),
            ("hspf2", "variable_capacity", "Variable Capacity", 3),
            ("hspf2", "dual_stage", "Dual Stage", 6),
            ("hspf2", "triple_capacity_northern", "Triple Stage Northern", 6),
        ):
            section = getattr(ahri, f"{metric}_section")
            page = getattr(ahri, f"{metric}_frame")
            app.notebook.select(ahri)
            ahri.metric_notebook.select(page)
            root.update()
            section.product_var.set(label)
            root.update()
            sample = next(c for c in samples if c.kind == metric and c.product == product)
            values = dict(sample.values)
            if product == "triple_capacity_northern":
                values["low_min_c"] = "0"
            _exercise_case(root, app, ahri, ahri.metric_notebook, page,
                           section, values, columns)

        for section in (ahri.seer2_section, ahri.hspf2_section):
            section.product_var.set("Variable Capacity")
            section._auto_calc.flush_now()
            grid, = section.result_panel.summary_grids.values()
            assert len(grid.headers) == 3
            assert section.result_panel.sectioned_csv_rows() == (("Status", "No results"),)
        root.update()
        assert not errors, errors
    finally:
        root.destroy()


if __name__ == "__main__":
    _run_native_probe()
