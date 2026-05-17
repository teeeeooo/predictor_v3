import json
from pathlib import Path

import pytest

from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator


FIXTURE_PATH = Path(
    "tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json"
)


def load_workbook_current_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_workbook_current_fixture_identity():
    fixture = load_workbook_current_fixture()

    assert fixture["reference_type"] == "ASNZS_EXCEL_COMPAT"
    assert fixture["calculator_id"] == "asnzs_excel_hspf"
    assert fixture["case_id"] == "workbook_inverter_ac_current"
    assert fixture["source"]["workbook_path"] == "reference_files/iso16358_test_sheet.xlsx"
    assert len(fixture["workbook_rows"]) == 27


def test_workbook_current_exact_match():
    fixture = load_workbook_current_fixture()
    expected = fixture["expected"]
    calc = ASNZSExcelHSPFCompatibilityCalculator()

    result = calc.calculate_hspf(fixture)

    assert result["reference_type"] == "ASNZS_EXCEL_COMPAT"
    assert result["calculator_id"] == "asnzs_excel_hspf"
    assert result["hstl_wh"] == pytest.approx(expected["hstl_wh"], abs=1e-9)
    assert result["hsec_wh"] == pytest.approx(expected["hsec_wh"], abs=1e-9)
    assert round(result["hsec_wh"] / 1000.0) == expected["hsec_kwh_display"]
    assert result["hspf"] == pytest.approx(expected["hspf"], abs=1e-9)

    component_details = result["workbook_diagnostics"]["component_details"]
    assert sum(row["energy_wh"] for row in component_details) == pytest.approx(
        expected["hsec_wh"],
        abs=2.0,
    )
