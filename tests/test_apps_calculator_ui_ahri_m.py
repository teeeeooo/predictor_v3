"""Focused application/UI regressions for AHRI 210/240 Appendix M."""

import pytest

from apps.calculator.application.ahri_m import (
    AHRI_M_HSPF_POINT_ORDER, AHRI_M_SEER_POINT_ORDER,
    AhriHspfAdapter, AhriHspfInputError, AhriHspfOptions, AhriSeerAdapter,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.table.roles import CellRole

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
    assert hspf.defrost_credit == 1.0


def test_m_hspf_optional_pair_semantics_and_disabled_stale_values():
    adapter = AhriHspfAdapter()
    partial = dict(HSPF_VALUES); partial["power_H12"] = ""
    with pytest.raises(AhriHspfInputError) as exc:
        adapter.calculate(partial, options=AhriHspfOptions(measured_h12=True))
    assert "power_H12" in exc.value.field_errors
    stale = dict(HSPF_VALUES); stale["capacity_H22"] = "bad"; stale["power_H22"] = "bad"
    result = adapter.calculate(stale, options=AhriHspfOptions(measured_h12=True, measured_h22=False))
    assert result is not None and result.h22_source == "appendix_m_fallback"


def test_m_batch_handlers_reproduce_single_surface_goldens():
    from apps.calculator.ui.ahri_m.batch import (
        AHRI_M_HSPF_BATCH_SPEC,
        AhriMHspfBatchCommon,
        AhriMHspfBatchHandler,
        AhriMSeerBatchHandler,
    )

    seer_row = {key: value for key, value in SEER_VALUES.items() if key != "cd"}
    seer = AhriMSeerBatchHandler("0.25").calculate_row(seer_row)
    assert seer.state is BatchRowState.OK
    assert seer.values == {"seer": "18.05", "cstl": "5349.7", "csec": "296.4"}
    from apps.calculator.ui.ahri_m.batch import AHRI_M_SEER_BATCH_SPEC
    assert {point.key: point.label for point in AHRI_M_SEER_BATCH_SPEC.measurement_points}["EV"] == "Ev"

    hspf_row = {key: value for key, value in HSPF_VALUES.items() if key.startswith(("capacity_", "power_"))}
    common = AhriMHspfBatchCommon(
        cd="0.25", defrost_test_minutes="90", defrost_max_minutes="720",
        cut_out_c="-17.7777778", cut_in_c="-15.0",
        h1n_same_speed_as_h32=False, automatic_cutout=True, demand_defrost=False,
    )
    hspf = AhriMHspfBatchHandler(common).calculate_row(hspf_row)
    assert hspf.state is BatchRowState.OK
    assert hspf.values == {"hspf": "10.45", "dhr": "15000", "load": "4605.6", "comp": "359.5", "aux": "80.7"}
    labels = {point.key: point.label for point in AHRI_M_HSPF_BATCH_SPEC.measurement_points}
    assert labels["H2V"] == "H2v"
    assert labels["H1N"] == "H1N(STD)"

    partial_h12 = dict(hspf_row)
    partial_h12["power_H12"] = ""
    assert AhriMHspfBatchHandler(common).calculate_row(partial_h12).state is BatchRowState.ERROR


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
    assert dict(seer.input_table.columns)["EV"] == "Ev"
    assert seer.batch_button.cget("text") == "일괄 입력"
    seer.input_table.set_values_batch({k: v for k, v in SEER_VALUES.items() if k != "cd"})
    seer._auto_calc.flush_now()
    assert [label.cget("text") for label in seer.result_panel.summary_value_labels["SEER"]][:2] == ["18.04867", "18.05"]
    assert seer.result_panel._summary_shapes["SEER"][1] == (
        "Raw SEER", "Published SEER", "CSTL [Btu/h]", "CSEC [W]"
    )

    hspf = AhriMHspfSection(tk_root); hspf.pack()
    assert tuple(key for key, _ in hspf.heating_table.columns) == AHRI_M_HSPF_POINT_ORDER
    assert "H42" not in tuple(key for key, _ in hspf.heating_table.columns)
    assert "A2" not in tuple(key for key, _ in hspf.heating_table.columns)
    assert not hasattr(hspf, "minimum_speed_var")
    assert hspf.batch_button.cget("text") == "일괄 입력"
    labels = dict(hspf.heating_table.columns)
    assert labels["H2V"] == "H2v"
    assert labels["H1N"] == "H1N(STD)"
    hspf.h12_var.set(True)
    hspf.heating_table.set_values_batch({k: v for k, v in HSPF_VALUES.items() if k.startswith(("capacity_", "power_"))})
    hspf.numeric_table.set_values_batch({k: v for k, v in HSPF_VALUES.items() if k in {"cd", "defrost_test_minutes", "defrost_max_minutes", "cut_out_c", "cut_in_c"}})
    hspf._auto_calc.flush_now()
    values = [label.cget("text") for label in hspf.result_panel.summary_value_labels["HSPF"]]
    assert values == ["10.46286", "10.45", "15000", "4605.6", "359.5", "80.7"]
    assert hspf.result_panel._summary_shapes["HSPF"][1] == (
        "Raw HSPF", "Published HSPF", "DHRmin [Btu/h]", "Heating Load [Btu/h]", "Compressor Input [W]", "Auxiliary Input [W]"
    )
    assert hspf.numeric_table.static_cell_labels[("value", "defrost_credit")].cget("text") == "1.000"

    hspf.demand_defrost_var.set(True)
    hspf.numeric_table.set_values_batch({"defrost_test_minutes": "180", "defrost_max_minutes": "720"})
    hspf._auto_calc.flush_now()
    assert hspf.numeric_table.static_cell_labels[("value", "defrost_credit")].cget("text") == "1.026"


def test_m_batch_buttons_open_appendix_m_matrix_dialogs(tk_root):
    from apps.calculator.ui.ahri_m import AhriMSeerSection, AhriMHspfSection
    from apps.calculator.ui.ahri_m.batch import AHRI_M_HSPF_BATCH_SPEC, AHRI_M_SEER_BATCH_SPEC

    seer = AhriMSeerSection(tk_root); seer.pack()
    seer.batch_button.invoke(); tk_root.update_idletasks()
    assert seer._batch_access.dialog is not None
    assert seer._batch_access.dialog.section.table.spec is AHRI_M_SEER_BATCH_SPEC
    seer._batch_access.dialog.close()

    hspf = AhriMHspfSection(tk_root); hspf.pack()
    hspf.batch_button.invoke(); tk_root.update_idletasks()
    assert hspf._batch_access.dialog is not None
    section = hspf._batch_access.dialog.section
    assert section.table.spec is AHRI_M_HSPF_BATCH_SPEC
    assert section.numeric_table.cell_role((0, 2)) is CellRole.READONLY
    assert section.numeric_table.cell_role((0, 3)) is CellRole.READONLY
    assert section.numeric_table.static_cell_labels[("value", "defrost_credit")].cget("text") == "1.000"
    section._vars["demand_defrost"].set("1")
    assert section.numeric_table.cell_role((0, 2)) is CellRole.EDITABLE
    assert section.numeric_table.cell_role((0, 3)) is CellRole.EDITABLE
    section.numeric_table.set_values_batch({"defrost_test_minutes": "180", "defrost_max_minutes": "720"})
    section.table.restore_snapshot([{key: value for key, value in HSPF_VALUES.items() if key.startswith(("capacity_", "power_"))}])
    section._auto_calc.flush_now()
    assert section.numeric_table.static_cell_labels[("value", "defrost_credit")].cget("text") == "1.026"
    hspf._batch_access.dialog.close()


def test_calculator_app_exposes_m_and_m1_navigation(tk_root):
    from apps.calculator.ui.calculator_app import CalculatorTkApp
    app = CalculatorTkApp(tk_root)
    top = [app.notebook.tab(tab, "text") for tab in app.notebook.tabs()]
    assert top == ["ISO 16358", "EN14825", "AHRI 210/240 M", "AHRI 210/240 M1", "KS C 9306"]
    assert [app.ahri210240_m_tab.metric_notebook.tab(tab, "text") for tab in app.ahri210240_m_tab.metric_notebook.tabs()] == ["SEER", "HSPF"]
    assert [app.ahri210240_tab.metric_notebook.tab(tab, "text") for tab in app.ahri210240_tab.metric_notebook.tabs()] == ["SEER2", "HSPF2"]
