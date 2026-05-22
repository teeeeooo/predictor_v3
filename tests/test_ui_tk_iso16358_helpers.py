import importlib
import sys

from ui_tk.sections.iso16358_helpers import (
    build_cspf_input,
    build_hspf_input,
    format_cspf_result,
    format_hspf_result,
)


def test_helper_module_import_does_not_require_tkinter_or_pyqt():
    for name in list(sys.modules):
        if (
            name == "tkinter"
            or name.startswith("tkinter.")
            or name.startswith("PyQt5")
            or name == "ui_tk.sections.iso16358_helpers"
        ):
            del sys.modules[name]

    importlib.import_module("ui_tk.sections.iso16358_helpers")

    tkinter_loaded = any(
        name == "tkinter" or name.startswith("tkinter.") for name in sys.modules
    )
    pyqt_loaded = any(name.startswith("PyQt5") for name in sys.modules)
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
        rated_heating_capacity=6300,
        full_capacity=6300,
        full_power=1500,
        half_capacity=3200,
        half_power=800,
    )

    assert measured == {
        "rated_heating_capacity": 6300,
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800},
    }


def test_format_cspf_result_contains_existing_result_lines():
    text = format_cspf_result(
        {
            "cspf": 4.939,
            "cstl_wh": 123.4,
            "csec_wh": 25.0,
        }
    )

    assert "[CSPF]" in text
    assert "CSPF = 4.939" in text
    assert "CSTL = 123.4" in text
    assert "CSEC = 25.0" in text


def test_format_cspf_result_keeps_legacy_non_wh_fallback():
    text = format_cspf_result(
        {
            "cspf": 4.939,
            "cstl": 123.4,
            "csec": 25.0,
        }
    )

    assert "CSTL = 123.4" in text
    assert "CSEC = 25.0" in text


def test_format_hspf_result_contains_existing_result_lines():
    text = format_hspf_result(
        {
            "hspf": 3.643,
            "hstl_wh": 456.7,
            "hsec_wh": 125.4,
        }
    )

    assert "[HSPF]" in text
    assert "HSPF = 3.643" in text
    assert "HSTL_Wh = 456.7" in text
    assert "HSEC_Wh = 125.4" in text
