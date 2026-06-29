"""Focused EN14825 profile-switch sizing and detail-refit regressions."""

from __future__ import annotations

import pytest

from tests.helpers.tk import (
    cancel_pending_after_callbacks,
    destroy_tk_root,
    drain_tk_events,
    make_hidden_root,
)
from apps.calculator.ui.window_geometry import parse_window_geometry


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = make_hidden_root()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        yield root
    finally:
        destroy_tk_root(root)


def test_profile_switch_to_en14825_seer_keeps_positive_geometry(tk_root) -> None:
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    app = CalculatorTkApp(root=tk_root)
    cancel_pending_after_callbacks(tk_root)
    drain_tk_events(tk_root)
    app._apply_initial_iso_fit()
    app._ignore_initial_tab_changed = False
    app.en14825_tab._standard_notebook.select(app.en14825_tab._seer_frame)
    app.notebook.select(app.ahri210240_tab)
    drain_tk_events(tk_root)
    app.notebook.select(app.en14825_tab)
    drain_tk_events(tk_root)

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


def test_en14825_parent_selection_requests_two_cycle_settled_refit(tk_root) -> None:
    from apps.calculator.ui.tabs.en14825_tab import En14825Tab

    tab = En14825Tab(tk_root)
    refit_calls: list[int] = []
    tab._refit_scheduler.request_refit = (
        lambda *, settle_cycles=1: refit_calls.append(settle_cycles)
    )

    tab.on_parent_tab_selected()

    assert refit_calls == [2]


def test_top_level_switch_keeps_immediate_fit_then_requests_settled_refit(
) -> None:
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    calls: list[object] = []

    class SelectedTab:
        def preferred_initial_size(self) -> tuple[int, int]:
            calls.append("preferred-size")
            return (700, 600)

        def fit_toplevel_to_current_content_once(self) -> None:
            calls.append("immediate-fit")

        def on_parent_tab_selected(self) -> None:
            calls.append("settled-refit")

    class Notebook:
        def select(self) -> str:
            return "selected"

        def nametowidget(self, _widget_id: str) -> SelectedTab:
            return SelectedTab()

    app = object.__new__(CalculatorTkApp)
    app._ignore_initial_tab_changed = False
    app._set_notebook_content_size = lambda size: calls.append(size)
    notebook = Notebook()

    app._on_tab_changed(type("Event", (), {"widget": notebook})())

    assert calls == [
        "preferred-size",
        (700, 600),
        "immediate-fit",
        "settled-refit",
    ]
