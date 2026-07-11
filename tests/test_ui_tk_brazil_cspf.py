"""Focused Brazil single-surface, result, mode, and batch UI tests."""

from __future__ import annotations

import json
import csv
from pathlib import Path

import pytest

from apps.calculator.ui.brazil_cspf import BrazilCspfSection
from apps.calculator.ui.tabs.iso16358_tab import Iso16358Tab
from apps.calculator.ui.layout_constants import TABLE_ERROR_BG, TABLE_PASS_BG
from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf import (
    BRAZIL_CSPF_MATRIX_SPEC,
    FINAL,
    RULE_1,
    RULE_2,
    THREE_POINT_CSPF,
)


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


def test_brazil_result_surface_renders_two_rows_rules_and_export_data(
    tk_root, tmp_path, monkeypatch
):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()
    tk_root.update_idletasks()

    table = section.result_table
    assert table.row_labels == ("3-point", "2-point")
    assert table.column_labels == ("Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]")
    assert len(table.result_value_labels) == 8
    assert "Rule 1" in table.as_text()
    assert "Rule 2" in table.as_text()
    assert "조건" in table.as_text()
    assert "CSPF 3pt ≤ CSPF 2pt × 1.4" in table.as_text()
    assert "29°C EER 실측 > 계산" in table.as_text()
    assert "[Final]" in table.as_text()
    assert "Final\tOK" in table.as_text()
    headers, rows = table.table_export_data()
    assert headers == ("Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]")
    assert rows == (
        ("3-point", "6.02", "2461", "409"),
        ("2-point", "4.55", "2461", "541"),
    )
    rule_rows = [tuple(table.rule_value_labels[(row, column)].cget("text") for column in range(5)) for row in range(2)]
    assert rule_rows == [
        ("Rule 1", "CSPF 3pt ≤ CSPF 2pt × 1.4", "6.02", "6.37", "OK"),
        ("Rule 2", "29°C EER 실측 > 계산", "5.56", "5.75", "NG"),
    ]
    assert all(
        label.cget("anchor") == "center"
        for label in (*table.table.winfo_children(), *table.rule_table.winfo_children())
    )
    assert table.result_value_labels[(0, 1)].cget("background") == TABLE_PASS_BG
    assert table.result_value_labels[(1, 3)].cget("background") == TABLE_PASS_BG
    assert table.rule_value_labels[(0, 4)].cget("background") == TABLE_PASS_BG
    assert table.rule_value_labels[(1, 4)].cget("background") == TABLE_ERROR_BG
    assert table.final_status_label.cget("background") == TABLE_PASS_BG
    expected_tsv = "\n".join(
        (
            "[Result]",
            "Scenario\tCSPF\tCSTL [kWh]\tCSEC [kWh]",
            "3-point\t6.02\t2461\t409",
            "2-point\t4.55\t2461\t541",
            "[Rule]",
            "Rule\t조건\t대상값\t기준값\t판정",
            "Rule 1\tCSPF 3pt ≤ CSPF 2pt × 1.4\t6.02\t6.37\tOK",
            "Rule 2\t29°C EER 실측 > 계산\t5.56\t5.75\tNG",
            "[Final]",
            "Final\tOK",
        )
    )
    assert table.as_text() == expected_tsv
    assert table.export_document().as_tsv() == expected_tsv
    assert table.copy_table() is True
    assert tk_root.clipboard_get() == expected_tsv

    csv_path = tmp_path / "brazil_result.csv"
    monkeypatch.setattr(
        "apps.calculator.ui.brazil_cspf.export_adapter.filedialog.asksaveasfilename",
        lambda **_kwargs: str(csv_path),
    )
    section._export_csv()
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        assert list(csv.reader(handle)) == [
            ["[Result]"],
            ["Scenario", "CSPF", "CSTL [kWh]", "CSEC [kWh]"],
            ["3-point", "6.02", "2461", "409"],
            ["2-point", "4.55", "2461", "541"],
            ["[Rule]"],
            ["Rule", "조건", "대상값", "기준값", "판정"],
            ["Rule 1", "CSPF 3pt ≤ CSPF 2pt × 1.4", "6.02", "6.37", "OK"],
            ["Rule 2", "29°C EER 실측 > 계산", "5.56", "5.75", "NG"],
            ["[Final]"],
            ["Final", "OK"],
        ]

    section.input_table.set_value("half_power", "bad")
    section.recalculate_now()
    assert table.rows == ()
    assert table.rules == ()
    assert table.final_status is None
    assert table.result_value_labels == {}
    assert table.rule_value_labels == {}
    assert table.table_export_data() == (
        ("Status",),
        (("입력 오류: 숫자 입력을 확인하세요.",),),
    )
    assert table.as_text() == "입력 오류: 숫자 입력을 확인하세요."
    assert table.copy_table() is True
    assert tk_root.clipboard_get() == "Status\n입력 오류: 숫자 입력을 확인하세요."
    section._export_csv()
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        assert list(csv.reader(handle)) == [
            ["Status"],
            ["입력 오류: 숫자 입력을 확인하세요."],
        ]


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
    expected_result_headers = (
        "CSPF 3pt",
        "CSTL 3pt",
        "CSEC 3pt",
        "CSPF 2pt",
        "Rule 1",
        "29°C EER 실측",
        "29°C EER 계산",
        "Rule 2",
        "Final",
    )
    assert headers[-9:] == expected_result_headers
    assert "Row Status" not in headers
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

    table = dialog.section.table
    first_result_column = BRAZIL_CSPF_MATRIX_SPEC.result_start_column
    key_to_column = {
        key: first_result_column + offset
        for offset, (key, _label, _width) in enumerate(
            BRAZIL_CSPF_MATRIX_SPEC.result_metrics
        )
    }
    assert table.cell_widget((0, key_to_column[THREE_POINT_CSPF])).cget(
        "background"
    ) == TABLE_PASS_BG
    assert table.cell_widget((0, key_to_column[RULE_1])).cget("background") == TABLE_PASS_BG
    assert table.cell_widget((0, key_to_column[RULE_2])).cget("background") == TABLE_ERROR_BG
    assert table.cell_widget((0, key_to_column[FINAL])).cget("background") == TABLE_PASS_BG
    for cell in table.table_frame.grid_slaves(row=0):
        labels = cell.winfo_children()
        if labels:
            label = labels[0]
            assert label.winfo_reqwidth() <= cell.winfo_reqwidth()

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


def test_brazil_final_ng_uses_error_background_without_losing_text(tk_root):
    section = BrazilCspfSection(tk_root)
    section.input_table.set_values_batch(_raw_values())
    section.recalculate_now()
    table = section.result_table

    table.set_result(
        table.rows,
        table.rules,
        final_status="NG",
        status="최종 판정: NG",
    )

    assert table.final_status_label.cget("text") == "최종 판정: NG"
    assert table.final_status_label.cget("background") == TABLE_ERROR_BG
