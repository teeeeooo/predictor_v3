"""Focused EN14825 SEER detail formatter and section lifecycle tests."""

from __future__ import annotations

import pytest

from apps.calculator.ui.en14825 import SeerResultSummary
from apps.calculator.ui.sections.bin_detail_schema import (
    EN14825_SEER_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.en14825_seer_detail import format_seer_bin_details
from tests.calculator_ui_sample_values import EN14825_SEER_SAMPLE_VALUES


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


def test_seer_detail_formatter_uses_compact_schema() -> None:
    rows = format_seer_bin_details(
        (
            {
                "temp_c": 24.95,
                "hours": 123.45,
                "pc": 1.23456,
                "eer_pl": 5.67891,
                "energy_contribution": 26.7891,
                "interpolation": "linear_C_B",
                "raw_debug_only": "not exposed",
            },
        )
    )

    assert tuple(rows[0]) == EN14825_SEER_BIN_DETAIL_SCHEMA.column_keys
    assert rows[0]["tj"] == "24.9"
    assert rows[0]["cooling_load"] == "1.235"
    assert "raw_debug_only" not in rows[0]


def test_seer_detail_panel_tracks_completed_sources_and_visibility(tk_root) -> None:
    from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
    from apps.calculator.ui.layout_constants import (
        DETAIL_GRAPH_BG,
        DETAIL_GRAPH_BORDER_COLOR,
    )

    refit_calls: list[str] = []
    section = En14825SeerSection(
        tk_root,
        on_trace_visibility_changed=lambda: refit_calls.append("changed"),
    )
    section.design_table.set_values_batch({"p_design_c": "3000"})
    section.input_table.set_values_batch(EN14825_SEER_SAMPLE_VALUES)
    section.recalculate_now()

    assert section.detail_panel.graph.canvas.cget("background") == DETAIL_GRAPH_BG
    assert section.detail_panel.graph.canvas.cget("highlightbackground") == (
        DETAIL_GRAPH_BORDER_COLOR
    )
    assert tuple(section._detail_sources) == ("Declared", "Tested")
    assert section._detail_sources["Declared"].rows
    assert not section.detail_panel.is_visible()
    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert refit_calls[-1] == "changed"


def test_seer_detail_invalid_input_clears_stale_rows(tk_root) -> None:
    from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection

    section = En14825SeerSection(tk_root)
    section.design_table.set_values_batch({"p_design_c": "3000"})
    section.input_table.set_values_batch(EN14825_SEER_SAMPLE_VALUES)
    section.recalculate_now()
    assert section._detail_sources
    section.input_table.set_values_batch(
        {"declared_capacity_A": "bad", "tested_capacity_A": "bad"}
    )
    section.recalculate_now()

    assert section._detail_sources == {}
    assert section.detail_panel.table.table_export_data() == (
        ("Status",),
        (("입력 오류: 숫자 입력을 확인하세요.",),),
    )


def test_seer_detail_calculation_error_clears_sources(monkeypatch, tk_root) -> None:
    from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection

    section = En14825SeerSection(tk_root)
    section.design_table.set_values_batch({"p_design_c": "3000"})
    section.input_table.set_values_batch(EN14825_SEER_SAMPLE_VALUES)
    section.recalculate_now()
    assert section._detail_sources
    monkeypatch.setattr(
        section.adapter,
        "calculate",
        lambda **_kwargs: SeerResultSummary(status_code="declared_error"),
    )
    section.recalculate_now()

    assert section._detail_sources == {}
    assert section._detail_status == "Declared 계산 오류"
