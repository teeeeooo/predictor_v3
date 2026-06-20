"""Focused AHRI visible-content refit lifecycle tests."""

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


def _build_outer_notebook(tk_root):
    from tkinter import ttk

    from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab

    notebook = ttk.Notebook(tk_root)
    placeholder = ttk.Frame(notebook)
    notebook.add(placeholder, text="Other")
    ahri = Ahri210240Tab(notebook)
    notebook.add(ahri, text="AHRI 210/240")
    notebook.pack(fill="both", expand=True)
    tk_root.update_idletasks()
    return notebook, placeholder, ahri


def test_hidden_ahri_metric_change_does_not_request_refit(tk_root) -> None:
    notebook, placeholder, ahri = _build_outer_notebook(tk_root)
    calls = []
    ahri._refit_scheduler.request_refit = lambda **kwargs: calls.append(kwargs)

    notebook.select(placeholder)
    ahri._on_metric_changed()

    assert calls == []
    assert ahri._measurement._nested_notebook_active() is False


def test_visible_ahri_metric_change_requests_settled_refit(tk_root) -> None:
    notebook, _placeholder, ahri = _build_outer_notebook(tk_root)
    calls = []
    ahri._refit_scheduler.request_refit = lambda **kwargs: calls.append(kwargs)

    notebook.select(ahri)
    ahri._on_metric_changed()

    assert calls == [{"settle_cycles": 2}]
    assert ahri._measurement._nested_notebook_active() is True


def test_repeated_visible_metric_events_coalesce_to_one_fit(tk_root) -> None:
    notebook, _placeholder, ahri = _build_outer_notebook(tk_root)
    fits = []
    ahri._refit_scheduler._refit_callback = lambda: fits.append("fit")
    notebook.select(ahri)

    ahri._on_metric_changed()
    ahri._on_metric_changed()
    assert ahri._refit_scheduler.is_pending
    ahri._refit_scheduler._schedule_settled_refit()
    ahri._refit_scheduler._schedule_settled_refit()
    ahri._refit_scheduler._run_refit()

    assert fits == ["fit"]
    assert not ahri._refit_scheduler.is_pending
