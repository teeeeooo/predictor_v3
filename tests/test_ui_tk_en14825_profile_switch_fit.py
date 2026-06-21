"""Focused EN14825 profile-switch sizing and detail-refit regressions."""

from __future__ import annotations

import pytest

from apps.calculator.ui.window_geometry import parse_window_geometry


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


def test_profile_switch_to_en14825_seer_keeps_positive_geometry(tk_root) -> None:
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    app = CalculatorTkApp(root=tk_root)
    tk_root.update()
    app._ignore_initial_tab_changed = False
    app.en14825_tab._standard_notebook.select(app.en14825_tab._seer_frame)
    app.notebook.select(app.ahri210240_tab)
    tk_root.update_idletasks()
    app.notebook.select(app.en14825_tab)
    tk_root.update_idletasks()

    app.en14825_tab.fit_toplevel_to_current_content_once()

    width, height, _x, _y = parse_window_geometry(tk_root.geometry())
    assert width > 0
    assert height > 0


def test_en14825_tab_wires_seer_detail_to_visible_refit(tk_root) -> None:
    from apps.calculator.ui.tabs.en14825_tab import En14825Tab

    tab = En14825Tab(tk_root)
    refit_calls: list[int] = []
    tab._refit_scheduler.request_refit = (
        lambda *, settle_cycles=1: refit_calls.append(settle_cycles)
    )

    tab.seer_section.detail_toggle.invoke()

    assert refit_calls == [1]
