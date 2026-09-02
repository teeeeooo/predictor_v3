"""Focused application/UI regressions for AHRI 210/240 Appendix M."""

import pytest

from apps.calculator.application.ahri_m import (
    AHRI_M_HSPF_POINT_ORDER, AHRI_M_SEER_POINT_ORDER,
    AhriHspfAdapter, AhriHspfInputError, AhriHspfOptions, AhriSeerAdapter,
)

SEER_VALUES = {
    "cd": "0.25", "capacity_A2": "15000", "power_A2": "1200",
    "capacity_B2": "16000", "power_B2": "1100", "capacity_EV": "6800", "power_EV": "350",
    "capacity_B1": "3500", "power_B1": "120", "capacity_F1": "3400", "power_F1": "80",
}
HSPF_VALUES = {
    "cd": "0.25", "defrost_test_minutes": "90", "defrost_max_minutes": "720", "cut_out_c": "-17.7777778", "cut_in_c": "-15.0",
    "capacity_H01": "3300", "power_H01": "130", "capacity_H11": "2200", "power_H11": "140",
    "capacity_H1N": "14000", "power_H1N": "1100", "capacity_H2V": "4900", "power_H2V": "360",
    "capacity_H32": "8200", "power_H32": "890", "capacity_H12": "14000", "power_H12": "1100",
    "capacity_H22": "", "power_H22": "",
}


def test_m_application_adapters_reproduce_goldens():
    seer = AhriSeerAdapter().calculate(SEER_VALUES)
    assert seer is not None and seer.published_seer == 18.05
    hspf = AhriHspfAdapter().calculate(HSPF_VALUES, options=AhriHspfOptions(measured_h12=True))
    assert hspf is not None
    assert hspf.published_hspf == 10.45
    assert hspf.heating_load_aggregate == pytest.approx(4605.5625)
    assert hspf.compressor_energy_aggregate == pytest.approx(359.4864442524)
    assert hspf.resistance_energy_aggregate == pytest.approx(80.6956245727)


def test_m_hspf_optional_pair_semantics_and_disabled_stale_values():
    adapter = AhriHspfAdapter()
    partial = dict(HSPF_VALUES); partial["power_H12"] = ""
    with pytest.raises(AhriHspfInputError) as exc:
        adapter.calculate(partial, options=AhriHspfOptions(measured_h12=True))
    assert "power_H12" in exc.value.field_errors
    stale = dict(HSPF_VALUES); stale["capacity_H22"] = "bad"; stale["power_H22"] = "bad"
    result = adapter.calculate(stale, options=AhriHspfOptions(measured_h12=True, measured_h22=False))
    assert result is not None and result.h22_source == "appendix_m_fallback"


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


def test_m_sections_use_exact_scope_and_render_goldens(tk_root):
    from apps.calculator.ui.ahri_m import AhriMSeerSection, AhriMHspfSection
    seer = AhriMSeerSection(tk_root); seer.pack()
    assert tuple(key for key, _ in seer.input_table.columns) == AHRI_M_SEER_POINT_ORDER
    assert not hasattr(seer, "batch_button")
    seer.input_table.set_values_batch({k: v for k, v in SEER_VALUES.items() if k != "cd"})
    seer._auto_calc.flush_now()
    assert [label.cget("text") for label in seer.result_panel.summary_value_labels["SEER"]][:2] == ["18.04867", "18.05"]

    hspf = AhriMHspfSection(tk_root); hspf.pack()
    assert tuple(key for key, _ in hspf.heating_table.columns) == AHRI_M_HSPF_POINT_ORDER
    assert "H42" not in tuple(key for key, _ in hspf.heating_table.columns)
    assert "A2" not in tuple(key for key, _ in hspf.heating_table.columns)
    assert not hasattr(hspf, "minimum_speed_var") and not hasattr(hspf, "batch_button")
    hspf.h12_var.set(True)
    hspf.heating_table.set_values_batch({k: v for k, v in HSPF_VALUES.items() if k.startswith(("capacity_", "power_"))})
    hspf.numeric_table.set_values_batch({k: v for k, v in HSPF_VALUES.items() if k in {"cd", "defrost_test_minutes", "defrost_max_minutes", "cut_out_c", "cut_in_c"}})
    hspf._auto_calc.flush_now()
    values = [label.cget("text") for label in hspf.result_panel.summary_value_labels["HSPF"]]
    assert values == ["10.46286", "10.45", "15000", "4605.6", "359.5", "80.7"]


def test_calculator_app_exposes_m_and_m1_navigation(tk_root):
    from apps.calculator.ui.calculator_app import CalculatorTkApp
    app = CalculatorTkApp(tk_root)
    top = [app.notebook.tab(tab, "text") for tab in app.notebook.tabs()]
    assert top == ["ISO 16358", "EN14825", "AHRI 210/240 M", "AHRI 210/240 M1", "KS C 9306"]
    assert [app.ahri210240_m_tab.metric_notebook.tab(tab, "text") for tab in app.ahri210240_m_tab.metric_notebook.tabs()] == ["SEER", "HSPF"]
    assert [app.ahri210240_tab.metric_notebook.tab(tab, "text") for tab in app.ahri210240_tab.metric_notebook.tabs()] == ["SEER2", "HSPF2"]
