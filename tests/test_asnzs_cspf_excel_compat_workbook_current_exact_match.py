import pytest

from core.calculators.standards.asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator


def workbook_current_cooling_fixture():
    return {
        "reference_type": "ASNZS_EXCEL_COMPAT",
        "calculator_id": "asnzs_excel_hspf",
        "case_id": "workbook_inverter_ac_current_cooling",
        "source": {
            "workbook_path": "reference_files/iso16358_test_sheet.xlsx",
            "sheet": "Inverter AC",
            "row_range": "18:32",
            "anchors": {
                "hours": "U",
                "load_w": "V",
                "selected_power_w": "AM",
                "row_energy_wh": "AN",
                "total_load_wh": "X48",
                "total_energy_wh": "AN48",
                "cspf": "G13",
            },
        },
        "expected": {
            "cstl_wh": 1960399.0,
            "csec_wh": 255116.0,
            "cspf": 7.684,
            "csec_kwh_display": 255.0,
        },
        "workbook_rows": [
            {"row_number": 18, "temperature_c": 21.0, "hours": 100.0, "load_w": 178.0, "selected_power_w": 18.0, "row_energy_wh": 1786.0},
            {"row_number": 19, "temperature_c": 22.0, "hours": 139.0, "load_w": 357.0, "selected_power_w": 37.0, "row_energy_wh": 5136.0},
            {"row_number": 20, "temperature_c": 23.0, "hours": 165.0, "load_w": 535.0, "selected_power_w": 57.0, "row_energy_wh": 9437.0},
            {"row_number": 21, "temperature_c": 24.0, "hours": 196.0, "load_w": 713.0, "selected_power_w": 79.0, "row_energy_wh": 15394.0},
            {"row_number": 22, "temperature_c": 25.0, "hours": 210.0, "load_w": 891.0, "selected_power_w": 101.0, "row_energy_wh": 21196.0},
            {"row_number": 23, "temperature_c": 26.0, "hours": 215.0, "load_w": 1070.0, "selected_power_w": 124.0, "row_energy_wh": 26729.0},
            {"row_number": 24, "temperature_c": 27.0, "hours": 210.0, "load_w": 1248.0, "selected_power_w": 149.0, "row_energy_wh": 31217.0},
            {"row_number": 25, "temperature_c": 28.0, "hours": 181.0, "load_w": 1426.0, "selected_power_w": 181.0, "row_energy_wh": 32675.0},
            {"row_number": 26, "temperature_c": 29.0, "hours": 150.0, "load_w": 1604.0, "selected_power_w": 220.0, "row_energy_wh": 32960.0},
            {"row_number": 27, "temperature_c": 30.0, "hours": 120.0, "load_w": 1783.0, "selected_power_w": 263.0, "row_energy_wh": 31527.0},
            {"row_number": 28, "temperature_c": 31.0, "hours": 75.0, "load_w": 1961.0, "selected_power_w": 313.0, "row_energy_wh": 23459.0},
            {"row_number": 29, "temperature_c": 32.0, "hours": 35.0, "load_w": 2139.0, "selected_power_w": 372.0, "row_energy_wh": 13014.0},
            {"row_number": 30, "temperature_c": 33.0, "hours": 11.0, "load_w": 2317.0, "selected_power_w": 443.0, "row_energy_wh": 4868.0},
            {"row_number": 31, "temperature_c": 34.0, "hours": 6.0, "load_w": 2496.0, "selected_power_w": 529.0, "row_energy_wh": 3172.0},
            {"row_number": 32, "temperature_c": 35.0, "hours": 4.0, "load_w": 2674.0, "selected_power_w": 636.0, "row_energy_wh": 2544.0},
        ],
    }


def test_workbook_current_cooling_exact_match():
    fixture = workbook_current_cooling_fixture()
    expected = fixture["expected"]
    calc = ASNZSExcelHSPFCompatibilityCalculator()

    result = calc.calculate_cspf(fixture)

    assert result["reference_type"] == "ASNZS_EXCEL_COMPAT"
    assert result["calculator_id"] == "asnzs_excel_hspf"
    assert result["metric"] == "cooling"
    assert result["cstl_wh"] == pytest.approx(expected["cstl_wh"], abs=1e-9)
    assert result["csec_wh"] == pytest.approx(expected["csec_wh"], abs=1e-9)
    assert round(result["csec_wh"] / 1000.0) == expected["csec_kwh_display"]
    assert result["cspf"] == pytest.approx(expected["cspf"], abs=1e-9)

    component_details = result["workbook_diagnostics"]["component_details"]
    assert sum(row["energy_wh"] for row in component_details) == pytest.approx(
        expected["csec_wh"],
        abs=2.0,
    )
    assert {row["anchor"] for row in component_details} == {"AM/AN"}


def test_calculate_cspf_requires_workbook_rows():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError, match="workbook_rows is required"):
        calc.calculate_cspf({"reference_type": "ASNZS_EXCEL_COMPAT"})
