import importlib
import sys

from apps.calculator.ui.sections.iso16358_helpers import (
    build_cspf_input,
    build_hspf_input,
    format_cspf_result,
    format_hspf_result,
)


def test_helper_module_import_does_not_require_tkinter_or_qt_binding():
    qt_binding = "Py" + "Qt5"
    for name in list(sys.modules):
        if (
            name == "tkinter"
            or name.startswith("tkinter.")
            or name.startswith(qt_binding)
            or name == "apps.calculator.ui.sections.iso16358_helpers"
        ):
            del sys.modules[name]

    importlib.import_module("apps.calculator.ui.sections.iso16358_helpers")

    tkinter_loaded = any(
        name == "tkinter" or name.startswith("tkinter.") for name in sys.modules
    )
    pyqt_loaded = any(name.startswith(qt_binding) for name in sys.modules)
    assert not tkinter_loaded
    assert not pyqt_loaded


def test_build_cspf_input_matches_section_contract():
    measured, declared = build_cspf_input(
        full_capacity=3600,
        full_power=900,
        half_capacity=1700,
        half_power=380,
        declared_capacity=3500,
    )

    assert measured == {
        "35_full": {"capacity": 3600, "power": 900},
        "35_half": {"capacity": 1700, "power": 380},
    }
    assert declared == 3500


def test_build_hspf_input_matches_section_contract():
    measured = build_hspf_input(
        full_capacity=6300,
        full_power=1500,
        half_capacity=3200,
        half_power=800,
    )

    assert measured == {
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800},
    }


def test_build_hspf_input_can_include_optional_rated_capacity():
    measured = build_hspf_input(
        full_capacity=6300,
        full_power=1500,
        half_capacity=3200,
        half_power=800,
        rated_heating_capacity=6300,
    )

    assert measured["rated_heating_capacity"] == 6300


def test_format_cspf_result_contains_existing_result_lines():
    text = format_cspf_result(
        {
            "cspf": 4.939,
            "annual_cooling_kwh": 1769.595,
            "annual_power_kwh": 358.266,
        }
    )

    assert "[CSPF]" in text
    assert "CSPF | CSTL [kWh] | CSEC [kWh]" in text
    assert "4.939 | 1769.6 | 358.3" in text
    assert "None" not in text


def test_format_cspf_result_converts_wh_aliases_to_kwh():
    text = format_cspf_result(
        {
            "cspf": 4.939,
            "cstl_wh": 123400.0,
            "csec_wh": 25000.0,
        }
    )

    assert "4.939 | 123.4 | 25.0" in text


def test_format_hspf_result_contains_existing_result_lines():
    text = format_hspf_result(
        {
            "hspf": 3.643,
            "hstl_wh": 273190.23529411765,
            "hsec_wh": 74991.00727784102,
        }
    )

    assert "[HSPF]" in text
    assert "HSPF | HSTL [kWh] | HSEC [kWh]" in text
    assert "3.643 | 273.2 | 75.0" in text
    assert "273190.23529411765" not in text


def test_format_result_missing_values_render_dash_not_none():
    assert "None" not in format_cspf_result({"cspf": 4.939})
    assert "4.939 | - | -" in format_cspf_result({"cspf": 4.939})
    assert "None" not in format_hspf_result({"hspf": 3.643})
