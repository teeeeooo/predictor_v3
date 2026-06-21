"""Focused AHRI HSPF2 detail formatter and section lifecycle tests."""

from __future__ import annotations

import pytest

from apps.calculator.ui.sections.ahri_hspf2_detail import format_hspf2_bin_details
from apps.calculator.ui.sections.bin_detail_schema import AHRI_HSPF2_BIN_DETAIL_SCHEMA
from tests.calculator_ui_sample_values import (
    HSPF2_HEATING_SAMPLE_VALUES,
    HSPF2_SAMPLE_VALUES,
)

TEST_BIN_DETAIL = {
    "temp_F": 62.0,
    "hours": 132.0,
    "operating_case": "Case I",
    "building_load": 1200.0,
    "q_low": 12500.0,
    "q_int": 13000.0,
    "q_full": 22000.0,
    "COP_bin": 4.25,
    "q_comp": 158400.0,
    "e_comp": 10930.0,
    "q_aux": 0.0,
    "e_aux": 0.0,
    "q_j": 158400.0,
    "E_j": 10930.0,
    "debug_info": {"not_for_ui": True},
}


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


def test_hspf2_detail_formatter_exposes_schema_only() -> None:
    rows = format_hspf2_bin_details((TEST_BIN_DETAIL,))

    assert tuple(rows[0]) == AHRI_HSPF2_BIN_DETAIL_SCHEMA.column_keys
    assert rows[0]["tj"] == "62.0"
    assert rows[0]["cop_bin"] == "4.250"
    assert "debug_info" not in rows[0]


def test_hspf2_detail_panel_is_single_source_and_refits(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section

    refit_calls: list[str] = []
    section = AhriHspf2Section(
        tk_root,
        on_trace_visibility_changed=lambda: refit_calls.append("changed"),
    )
    section.a2_table.set_values_batch(
        {"a2_capacity": HSPF2_SAMPLE_VALUES["a2_capacity"]}
    )
    section.heating_table.set_values_batch(HSPF2_HEATING_SAMPLE_VALUES)
    section.recalculate_now()

    assert section.detail_panel.source_combo.winfo_manager() == ""
    assert section.detail_panel.table.table_rows()
    assert not section.detail_panel.is_visible()
    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert refit_calls == ["changed"]


def test_ahri_tab_wires_hspf2_detail_to_visible_refit(tk_root) -> None:
    from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab

    tab = Ahri210240Tab(tk_root)
    refit_calls: list[int] = []
    tab._refit_scheduler.request_refit = (
        lambda *, settle_cycles=1: refit_calls.append(settle_cycles)
    )

    tab.hspf2_section.detail_toggle.invoke()

    assert refit_calls == [1]


def test_hspf2_invalid_input_clears_stale_detail(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section

    section = AhriHspf2Section(tk_root)
    section.a2_table.set_values_batch(
        {"a2_capacity": HSPF2_SAMPLE_VALUES["a2_capacity"]}
    )
    section.heating_table.set_values_batch(HSPF2_HEATING_SAMPLE_VALUES)
    section.recalculate_now()
    assert section.detail_panel.table.table_rows()
    section.heating_table.set_values_batch({"power_H42": "bad"})
    section.recalculate_now()

    assert section._detail_status == "입력 오류: 숫자 입력을 확인하세요."
    assert section.detail_panel.table.table_export_data() == (
        ("Status",),
        (("입력 오류: 숫자 입력을 확인하세요.",),),
    )


def test_hspf2_optional_change_clears_before_recalculation(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section

    section = AhriHspf2Section(tk_root)
    section.a2_table.set_values_batch(
        {"a2_capacity": HSPF2_SAMPLE_VALUES["a2_capacity"]}
    )
    section.heating_table.set_values_batch(HSPF2_HEATING_SAMPLE_VALUES)
    section.recalculate_now()
    assert section.detail_panel.table.table_rows()
    section.h42_var.set(False)

    assert section._detail_status == "입력 대기"
    assert section.detail_panel.table.table_rows() == ()
    section._auto_calc.flush_now()
    assert section.detail_panel.table.table_rows()


def test_hspf2_calculation_error_clears_detail(monkeypatch, tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section

    section = AhriHspf2Section(tk_root)
    monkeypatch.setattr(
        section.adapter,
        "calculate",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("boom")),
    )
    section.recalculate_now()

    assert section._detail_status == "계산 오류"
    assert section.detail_panel.table.table_rows() == ()
