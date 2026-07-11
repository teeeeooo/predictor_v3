"""Focused Brazil single-surface, result, mode, and batch UI tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps.calculator.ui.sections.brazil_cspf_section import BrazilCspfSection
from apps.calculator.ui.tabs.iso16358_tab import Iso16358Tab


FIXTURE_PATH = Path("tests/fixtures/brazil_cspf_compliance_golden.json")


@pytest.fixture
def tk_root():
    tk_module = pytest.importorskip("tkinter")
    try:
        root = tk_module.Tk()
    except tk_module.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def _raw_values() -> dict[str, str]:
    measured = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["measured_points"]
    return {
        "full_capacity": str(measured["35_full"]["capacity"]),
        "full_power": str(measured["35_full"]["power"]),
        "half_capacity": str(measured["35_half"]["capacity"]),
        "half_power": str(measured["35_half"]["power"]),
        "half_29_capacity": str(measured["29_half"]["capacity"]),
        "half_29_power": str(measured["29_half"]["power"]),
    }


def test_brazil_result_surface_renders_two_rows_rules_and_export_data(tk_root):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()
    tk_root.update_idletasks()

    table = section.result_table
    assert table.row_labels == ("3-point", "2-point")
    assert len(table.table.get_children()) == 2
    assert "Rule 1" in table.as_text()
    assert "Rule 2" in table.as_text()
    assert "최종 판정: OK" in table.as_text()
    headers, rows = table.table_export_data()
    assert headers == ("Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]")
    assert any(row[0] == "Rule 1" for row in rows)
    assert any(row[0] == "Rule 2" for row in rows)
    assert any(row[0] == "Final" for row in rows)

    section.input_table.set_value("half_power", "bad")
    section.recalculate_now()
    assert table.rows == ()
    assert table.rules == ()
    assert table.final_status is None
    assert len(table.table.get_children()) == 0


def test_brazil_mode_is_composed_as_an_independent_iso_tab_surface(tk_root):
    tab = Iso16358Tab(tk_root)
    tab._mode_combo.set("Brazil CSPF")
    tab._on_mode_changed()
    tk_root.update_idletasks()

    assert tab._brazil_section is not None
    assert tab._brazil_frame.winfo_manager() == "pack"
    assert tab._two_point_frame.winfo_manager() == ""
    assert tab._saso_t3_frame.winfo_manager() == ""
    assert tab.result_panel is tab._brazil_section.result_panel


def test_brazil_batch_dialog_opens_and_preserves_input_snapshot(tk_root):
    section = BrazilCspfSection(tk_root)
    section.batch_button.invoke()
    dialog = section._batch_dialog

    assert dialog is not None
    assert dialog.window.winfo_exists()
    assert dialog.adapter.title == "Brazil CSPF Compliance Batch"
    dialog.section.table.cases[0].update(_raw_values())
    dialog.section._recalculate_now()
    assert dialog.section.table.cases[0]["three_point_cspf"] == "6.02"

    dialog.close()
    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert section._batch_snapshot[0]["full_capacity"] == "2978"


def test_brazil_mode_keeps_result_surface_stale_free_when_input_is_incomplete(tk_root):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()
    assert section.result_table.rows

    section.input_table.set_values_batch({"half_29_power": ""})
    section.recalculate_now()
    assert section.result_table.rows == ()
    assert section.result_table.rules == ()
