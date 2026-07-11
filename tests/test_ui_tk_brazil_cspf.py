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
    assert table.column_labels == ("Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]")
    assert len(table.table.get_children()) == 2
    assert "Rule 1" in table.as_text()
    assert "Rule 2" in table.as_text()
    assert "조건" in table.as_text()
    assert "CSPF 3pt ≤ CSPF 2pt × 1.4" in table.as_text()
    assert "29°C EER 실측 > 계산" in table.as_text()
    assert "최종 판정: OK" in table.as_text()
    headers, rows = table.table_export_data()
    assert headers == ("Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]", "판정")
    assert any(row[0] == "Rule 1" for row in rows)
    assert any(row[0] == "Rule 2" for row in rows)
    assert any(row[0] == "Final" for row in rows)
    rule_rows = [
        table.rule_table.item(item_id, "values")
        for item_id in table.rule_table.get_children()
    ]
    assert rule_rows == [
        ("Rule 1", "CSPF 3pt ≤ CSPF 2pt × 1.4", "6.02", "6.37", "OK"),
        ("Rule 2", "29°C EER 실측 > 계산", "5.56", "5.75", "NG"),
    ]

    section.input_table.set_value("half_power", "bad")
    section.recalculate_now()
    assert table.rows == ()
    assert table.rules == ()
    assert table.final_status is None
    assert len(table.table.get_children()) == 0
    assert len(table.rule_table.get_children()) == 0


def test_brazil_detail_panel_switches_sources_and_supports_copy_export(
    tk_root, monkeypatch
):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()

    assert section.detail_toggle.cget("text") == "상세 보기 ↓"
    section.detail_toggle.invoke()
    tk_root.update_idletasks()

    assert section.detail_toggle.cget("text") == "상세 닫기 ↑"
    assert section.detail_panel.is_visible()
    assert tuple(section.detail_panel.source_combo["values"]) == ("3-point", "2-point")
    assert section.detail_panel.selected_source() == "3-point"
    assert section.detail_panel.table.table_rows()
    assert section.detail_panel.summary_label.cget("text").startswith("CSPF: 6.02")
    assert section.detail_panel.graph._rows

    section.detail_panel.source_combo.set("2-point")
    section.detail_panel._on_source_changed()
    assert section.detail_panel.selected_source() == "2-point"
    assert section.detail_panel.summary_label.cget("text").startswith("CSPF: 4.55")
    assert section.detail_panel.table.table_rows()

    assert section.detail_panel.copy_table() is True
    exports = []
    monkeypatch.setattr(
        "apps.calculator.ui.table_csv_export.export_table_to_csv",
        lambda *args: exports.append(args) or True,
    )
    assert section.detail_panel.export_csv() is True
    assert exports and exports[0][1] == "brazil_cspf_bin_detail.csv"


def test_brazil_detail_visibility_notifies_tab_lifecycle_callback(tk_root):
    fit_calls = []
    section = BrazilCspfSection(
        tk_root,
        on_trace_visibility_changed=lambda: fit_calls.append("fit"),
    )

    section.detail_toggle.invoke()
    section.detail_toggle.invoke()

    assert fit_calls == ["fit", "fit"]


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
    fit_calls = []
    tab._lifecycle.on_detail_visibility_changed = lambda: fit_calls.append("fit")
    tab._brazil_section.detail_toggle.invoke()
    assert fit_calls == ["fit"]


def test_brazil_batch_dialog_opens_and_preserves_input_snapshot(tk_root, monkeypatch):
    section = BrazilCspfSection(tk_root)
    section.batch_button.invoke()
    dialog = section._batch_dialog

    assert dialog is not None
    assert dialog.window.winfo_exists()
    assert dialog.adapter.title == "Brazil CSPF Compliance Batch"
    dialog.section.table.cases[0].update(_raw_values())
    dialog.section._recalculate_now()
    assert dialog.section.table.cases[0]["three_point_cspf"] == "6.02"
    assert "two_point_cstl" not in dialog.section.table.cases[0]
    assert "two_point_csec" not in dialog.section.table.cases[0]
    headers, _rows = dialog.section.table.table_export_data()
    assert "2-point CSTL" not in headers
    assert "2-point CSEC" not in headers
    copied = []
    monkeypatch.setattr(
        "apps.calculator.ui.table_clipboard.copy_table_to_clipboard",
        lambda _widget, export_headers, export_rows: copied.append(
            (export_headers, export_rows)
        )
        or True,
    )
    assert dialog.section.table.copy_all() is True
    assert copied
    assert "2-point CSTL" not in copied[0][0]
    assert "2-point CSEC" not in copied[0][0]
    exported = []
    monkeypatch.setattr(
        "apps.calculator.ui.batch_dialogs.profiles.brazil_cspf.section.export_table_to_csv",
        lambda _parent, filename, export_headers, export_rows: exported.append(
            (filename, export_headers, export_rows)
        ),
    )
    dialog.section._export_csv()
    assert exported
    assert "2-point CSTL" not in exported[0][1]
    assert "2-point CSEC" not in exported[0][1]

    dialog.close()
    assert section._batch_dialog is None
    assert section._batch_snapshot is not None
    assert section._batch_snapshot[0]["full_capacity"] == "2978"
    assert "two_point_cstl" not in section._batch_snapshot[0]
    assert "two_point_csec" not in section._batch_snapshot[0]


def test_brazil_mode_keeps_result_surface_stale_free_when_input_is_incomplete(tk_root):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()
    assert section.result_table.rows
    section.detail_toggle.invoke()
    assert section.detail_panel.table.table_rows()

    section.input_table.set_values_batch({"half_29_power": ""})
    section.recalculate_now()
    assert section.result_table.rows == ()
    assert section.result_table.rules == ()
    assert section.detail_panel.table.table_rows() == ()
    assert section.detail_panel.graph._rows == ()
