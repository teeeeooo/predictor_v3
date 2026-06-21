"""Focused EN14825 SCOP bin-detail boundary and section tests."""

from __future__ import annotations

import pytest

from apps.calculator.ui.en14825 import ScopResultSummary
from apps.calculator.ui.sections.bin_detail_schema import (
    EN14825_SCOP_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.en14825_scop_detail import format_scop_bin_details


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


def test_scop_detail_formatter_uses_profile_schema_and_rounding() -> None:
    rows = format_scop_bin_details(
        (
            {
                "temp_c": -7.04,
                "hours": 123.45,
                "ph": 2.34567,
                "pdh": 3.45678,
                "cop_pl": 4.56789,
                "equivalent_power": 0.75678,
                "elbu": 0.12345,
                "operating_case": "capacity_shortfall_with_backup",
                "capacity_source": "interpolated",
                "cop_source": "measured",
                "raw_debug_only": "not exposed",
            },
        )
    )

    assert tuple(rows[0]) == EN14825_SCOP_BIN_DETAIL_SCHEMA.column_keys
    assert rows[0]["tj"] == "-7.0"
    assert rows[0]["heating_load"] == "2.346"
    assert "raw_debug_only" not in rows[0]


def test_scop_detail_panel_tracks_completed_sources_and_visibility(
    tk_root,
) -> None:
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection

    refit_calls: list[str] = []
    section = En14825ScopSection(
        tk_root,
        on_trace_visibility_changed=lambda: refit_calls.append("changed"),
    )
    section.recalculate_now()

    assert tuple(section._detail_sources) == (
        "Average Declared",
        "Average Tested",
    )
    assert section._detail_sources["Average Declared"].rows
    assert not section.detail_panel.is_visible()

    section.detail_toggle.invoke()
    tk_root.update_idletasks()
    assert section.detail_panel.is_visible()
    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert refit_calls[-1] == "changed"


def test_scop_detail_invalid_input_clears_stale_rows(tk_root) -> None:
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection

    section = En14825ScopSection(tk_root)
    section.recalculate_now()
    assert section._detail_sources

    section.input_tables["average"].set_values_batch(
        {
            "declared_capacity_A": "bad",
            "tested_capacity_A": "bad",
        }
    )
    section.recalculate_now()

    assert section._detail_sources == {}
    headers, rows = section.detail_panel.table.table_export_data()
    assert headers == ("Status",)
    assert rows == (("입력 오류: 숫자 입력을 확인하세요.",),)


def test_scop_detail_calculation_error_clears_sources(monkeypatch, tk_root) -> None:
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection

    section = En14825ScopSection(tk_root)
    section.recalculate_now()
    assert section._detail_sources

    monkeypatch.setattr(
        section.adapter,
        "calculate",
        lambda **_kwargs: ScopResultSummary(
            status_code="declared_error",
            message="Declared calculation error: boom",
        ),
    )
    section.recalculate_now()

    assert section._detail_sources == {}
    headers, rows = section.detail_panel.table.table_export_data()
    assert headers == ("Status",)
    assert rows == (("Declared calculation error: boom",),)


def test_scop_detail_source_invalidation_falls_back_to_waiting(tk_root) -> None:
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection

    section = En14825ScopSection(tk_root)
    section.recalculate_now()
    section.climate_active_vars["average"].set(False)
    section._on_climate_toggle()
    section.recalculate_now()

    assert section._detail_sources == {}
    assert section._detail_status == "입력 대기"
