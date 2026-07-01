"""Focused KOREA calculator tab skeleton tests."""

from __future__ import annotations

import pytest

from tests.helpers.tk import destroy_tk_root


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
        destroy_tk_root(root)


def _tab_labels(notebook) -> list[str]:
    return [notebook.tab(tab_id, "text") for tab_id in notebook.tabs()]


def test_calculator_app_registers_korea_top_level_tab(tk_root) -> None:
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    app = CalculatorTkApp(tk_root)

    assert _tab_labels(app.notebook) == [
        "ISO 16358",
        "EN14825",
        "AHRI 210/240",
        "KOREA",
    ]
    assert app.korea_tab.master is app.notebook


def test_korea_tab_contains_cspf_hspf_metric_notebook(tk_root) -> None:
    from tkinter import ttk

    from apps.calculator.ui.tabs.korea_tab import KoreaTab

    outer = ttk.Notebook(tk_root)
    korea = KoreaTab(outer)
    outer.add(korea, text="KOREA")
    outer.pack(fill="both", expand=True)
    tk_root.update_idletasks()

    assert _tab_labels(korea.metric_notebook) == ["CSPF", "HSPF"]
    assert korea.cspf_frame.master is korea.metric_notebook
    assert korea.hspf_frame.master is korea.metric_notebook
    assert korea.cspf_section.result_panel is not None
    assert korea.hspf_section.result_panel is not None
    assert korea.cspf_section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert korea.hspf_section.detail_toggle.cget("text") == "상세 보기 ↓"
    assert not korea.cspf_section.detail_panel.is_visible()
    assert not korea.hspf_section.detail_panel.is_visible()
    assert korea.cspf_section.guide_table.text_at_address(("current_tc", "value")) == (
        "입력 대기"
    )
    assert korea.hspf_section.guide_table.text_at_address(("current_tc", "value")) == (
        "입력 대기"
    )
