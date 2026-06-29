"""Diagnostic comparison for EN14825 and AHRI visible-content sizing."""

from __future__ import annotations

import json

import pytest


def _collect(label, app, tab) -> dict[str, object]:
    snapshot = tab._measurement.snapshot()
    diagnostics = snapshot.diagnostics
    canvas = tab._scrollable.canvas
    current_height = diagnostics["nested_current_tab_height"]
    notebook_height = diagnostics["nested_notebook_height"]
    return {
        "label": label,
        "root_geometry": app.root.geometry(),
        "top_notebook_size": (app.notebook.winfo_width(), app.notebook.winfo_height()),
        "preferred_initial_size": tab.preferred_initial_size(),
        "snapshot_preferred_size": snapshot.preferred_size,
        "content_req_size": (
            diagnostics["content_reqwidth"], diagnostics["content_reqheight"]
        ),
        "nested_current_tab_size": (
            diagnostics["nested_current_tab_width"],
            diagnostics["nested_current_tab_height"],
        ),
        "nested_notebook_size": (
            diagnostics["nested_notebook_width"],
            notebook_height,
        ),
        "nested_tallest_tab_height": diagnostics["nested_max_tab_height"],
        "nested_height_gap": notebook_height - current_height,
        "chrome_estimate": (
            diagnostics["chrome_width_estimate"],
            diagnostics["chrome_height_estimate"],
        ),
        "vertical_overflow_delta": diagnostics["vertical_overflow_delta"],
        "canvas_size": (canvas.winfo_width(), canvas.winfo_height()),
        "scrollregion_bbox": canvas.bbox("all"),
    }


def _select_fit(app, tab, metric_notebook, index, label):
    app.notebook.select(tab)
    metric_notebook.select(index)
    app.root.update_idletasks()
    tab.fit_toplevel_to_current_content_once()
    app.root.update_idletasks()
    return _collect(label, app, tab)


def test_en14825_vs_ahri_visible_sizing_diagnostics() -> None:
    tk = pytest.importorskip("tkinter")
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        app = CalculatorTkApp(root)
        root.deiconify()
        root.update_idletasks()
        en = app.en14825_tab
        ahri = app.ahri210240_tab
        iso = app.iso_tab
        app.notebook.select(iso)
        iso._mode_combo.set("Hong Kong")
        iso._on_mode_changed()
        root.update_idletasks()
        rows = [
            _select_fit(app, iso, iso._metric_notebook, 0, "ISO HK CSPF"),
            _select_fit(app, iso, iso._metric_notebook, 1, "ISO HK HSPF"),
            _select_fit(app, iso, iso._metric_notebook, 0, "ISO HK CSPF return"),
            _select_fit(app, en, en._standard_notebook, 0, "EN SEER"),
            _select_fit(app, en, en._standard_notebook, 1, "EN SCOP"),
            _select_fit(app, en, en._standard_notebook, 0, "EN SEER return"),
            _select_fit(app, ahri, ahri.metric_notebook, 0, "AHRI SEER2"),
            _select_fit(app, ahri, ahri.metric_notebook, 1, "AHRI HSPF2"),
            _select_fit(app, ahri, ahri.metric_notebook, 0, "AHRI SEER2 return"),
        ]
        ahri.metric_notebook.select(1)
        root.update_idletasks()
        ahri.hspf2_section.batch_button.invoke()
        root.update_idletasks()
        rows.append(_collect("AHRI HSPF2 batch open", app, ahri))
        dialog = ahri.hspf2_section._batch_access.dialog
        assert dialog is not None
        dialog.close()
        root.update_idletasks()
        rows.append(_collect("AHRI HSPF2 batch close", app, ahri))
        rows.append(
            _select_fit(
                app, ahri, ahri.metric_notebook, 0, "AHRI SEER2 after batch"
            )
        )

        by_label = {row["label"]: row for row in rows}
        assert by_label["EN SEER"]["snapshot_preferred_size"] == (
            by_label["EN SEER return"]["snapshot_preferred_size"]
        )
        assert by_label["ISO HK CSPF"]["snapshot_preferred_size"] == (
            by_label["ISO HK CSPF return"]["snapshot_preferred_size"]
        )
        assert by_label["AHRI SEER2"]["snapshot_preferred_size"] == (
            by_label["AHRI SEER2 return"]["snapshot_preferred_size"]
        )
        assert by_label["AHRI SEER2"]["nested_notebook_size"] == (
            by_label["AHRI HSPF2"]["nested_notebook_size"]
        )
        assert by_label["AHRI SEER2"]["nested_current_tab_size"][1] < (
            by_label["AHRI HSPF2"]["nested_current_tab_size"][1]
        )
        assert by_label["EN SEER"]["nested_height_gap"] >= 0
        assert by_label["AHRI SEER2"]["nested_height_gap"] >= 0
        assert by_label["AHRI SEER2"]["nested_height_gap"] == (
            by_label["AHRI SEER2 return"]["nested_height_gap"]
        )
        for label in ("ISO HK CSPF", "EN SEER", "AHRI SEER2"):
            row = by_label[label]
            assert row["chrome_estimate"][1] == (
                row["nested_notebook_size"][1]
                - row["nested_tallest_tab_height"]
            )
        assert by_label["AHRI SEER2"]["chrome_estimate"][1] < (
            by_label["AHRI SEER2"]["nested_height_gap"]
        )
        assert by_label["AHRI HSPF2 batch open"]["root_geometry"] == (
            by_label["AHRI HSPF2 batch close"]["root_geometry"]
        )
        for row in rows:
            print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    finally:
        root.destroy()
