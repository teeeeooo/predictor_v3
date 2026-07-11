"""Focused AHRI SEER2 detail formatter and lifecycle contracts."""

from __future__ import annotations

import pytest

from apps.calculator.ui.sections.ahri_seer2_detail import format_seer2_bin_details
from apps.calculator.ui.sections.bin_detail_schema import AHRI_SEER2_BIN_DETAIL_SCHEMA
from tests.test_apps_calculator_ui_ahri_seer2 import (
    FakeSeer2Calculator,
    SAMPLE_VALUES,
    _executor,
)


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


def test_seer2_detail_formatter_exposes_schema_only() -> None:
    raw = FakeSeer2Calculator().calculate_seer2({})["bin_details"]

    rows = format_seer2_bin_details(raw)

    assert tuple(rows[0]) == AHRI_SEER2_BIN_DETAIL_SCHEMA.column_keys
    assert rows[0]["tj"] == "67.0"
    assert rows[0]["eer_bin"] == "13.500"


def _build_section(tk_root, *, callback=None):
    from apps.calculator.ui.ahri import AhriSeer2Adapter
    from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section

    section = AhriSeer2Section(
        tk_root,
        adapter=AhriSeer2Adapter(_executor(FakeSeer2Calculator())),
        on_trace_visibility_changed=callback,
    )
    section.input_table.set_values_batch(SAMPLE_VALUES)
    section.recalculate_now()
    return section


def test_seer2_detail_panel_is_single_source_and_refits(tk_root) -> None:
    calls: list[str] = []
    section = _build_section(tk_root, callback=lambda: calls.append("refit"))

    assert section.detail_panel.source_combo.winfo_manager() == ""
    assert section.detail_panel.table.table_rows()
    assert not section.detail_panel.is_visible()

    section.detail_toggle.invoke()

    assert section.detail_panel.is_visible()
    assert calls == ["refit"]


def test_seer2_incomplete_input_clears_detail(tk_root) -> None:
    section = _build_section(tk_root)

    section.input_table.set_values_batch({"power_F_Low": ""})
    section.recalculate_now()

    assert section._detail_status == "입력 대기"
    assert section.detail_panel.table.table_rows() == ()


def test_seer2_invalid_input_clears_detail_with_status(tk_root) -> None:
    section = _build_section(tk_root)

    section.input_table.set_values_batch({"power_A_Full": "bad"})
    section.recalculate_now()

    assert section._detail_status == "입력 오류: 숫자 입력을 확인하세요."
    assert section.detail_panel.table.table_rows() == ()


def test_ahri_tab_routes_seer2_detail_through_lifecycle(tk_root) -> None:
    from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab

    tab = Ahri210240Tab(tk_root)
    calls: list[int] = []
    tab._refit_scheduler.request_refit = (
        lambda *, settle_cycles=1: calls.append(settle_cycles) or True
    )

    tab.seer2_section.detail_toggle.invoke()

    assert calls == [1]
