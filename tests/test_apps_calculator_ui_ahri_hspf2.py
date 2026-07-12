"""Focused tests for the AHRI HSPF2 main UI foundation."""

from __future__ import annotations

import pytest

from apps.calculator.ui.ahri.hspf2_adapter import (
    AHRI_HSPF2_HIDDEN_DEFAULTS,
    AHRI_HSPF2_POINT_ORDER,
    AHRI_HSPF2_TEMPERATURES_C,
    AhriHspf2Adapter,
    AhriHspf2InputError,
    AhriHspf2Options,
    AhriHspf2Summary,
)
from apps.calculator.ui.ahri.hspf2_points import AHRI_HSPF2_UI_POINT_ORDER
from tests.calculator_ui_sample_values import (
    HSPF2_HEATING_SAMPLE_VALUES,
    HSPF2_SAMPLE_VALUES,
)

TEST_MEASUREMENTS = {
    "a2_capacity": "24000",
    "capacity_H01": "12500",
    "power_H01": "980",
    "capacity_H11": "12000",
    "power_H11": "1000",
    "capacity_H1N": "22000",
    "power_H1N": "2000",
    "capacity_H2Int": "13000",
    "power_H2Int": "1200",
    "capacity_H32": "22000",
    "power_H32": "2100",
    "capacity_H42": "18000",
    "power_H42": "1900",
    "capacity_H12": "24000",
    "power_H12": "2200",
    "capacity_H22": "23200",
    "power_H22": "2160",
}

TEST_BIN_DETAIL = {
    "bin_no": 1,
    "temp_F": 62.0,
    "hours": 132.0,
    "operating_case": "Case I",
    "building_load": 1200.0,
    "q_low": 12500.0,
    "q_int": 13000.0,
    "q_full": 22000.0,
    "COP_bin": 4.25,
    "q_comp": 158400.0,
    "e_comp": 10930.0,
    "q_aux": 0.0,
    "e_aux": 0.0,
    "q_j": 158400.0,
    "E_j": 10930.0,
    "debug_info": {"not_for_ui": True},
}


def complete_values() -> dict[str, str]:
    return {
        "cd": "0.25",
        "defrost_credit": "1.0",
        "cut_out_c": "-10.0",
        "cut_in_c": "-5.0",
        **TEST_MEASUREMENTS,
    }


class FakeHspf2Calculator:
    def __init__(self, result=None) -> None:
        self.result = result or {
            "HSPF2": 9.875,
            "total_heating_btu": 22500.0,
            "total_energy_wh": 2278.481,
            "summary": {
                "metadata": {
                    "h12_source": "tested",
                    "h22_source": "calculated from H2Int and H32",
                }
            },
            "h42_source": "provided",
            "bin_details": [TEST_BIN_DETAIL],
        }
        self.result.setdefault("bin_details", [TEST_BIN_DETAIL])
        self.points = None
        self.kwargs = None

    def calculate_hspf2(self, test_points, **kwargs):
        self.points = dict(test_points)
        self.kwargs = dict(kwargs)
        return self.result


def _executor(calculator):
    def execute(capability_id, request):
        assert capability_id == "ahri210240.hspf2"
        return calculator.calculate_hspf2(
            request.test_points, **dict(request.parameters)
        )

    return execute


def test_hspf2_adapter_omits_inactive_points_and_injects_hidden_defaults() -> None:
    calculator = FakeHspf2Calculator()
    values = complete_values()
    values["a2_power"] = "invalid legacy input is ignored"
    values["capacity_H12"] = "invalid but inactive"
    adapter = AhriHspf2Adapter(_executor(calculator))

    summary = adapter.calculate(values, options=AhriHspf2Options())

    assert summary == AhriHspf2Summary(
        hspf2=9.875,
        total_heating_kbtu=22.5,
        total_energy_kwh=2.278481,
        h12_source="measured",
        h22_source="calculated",
        h42_source="measured",
        bin_details=(TEST_BIN_DETAIL,),
    )
    assert tuple(calculator.points) == (
        "H01",
        "H11",
        "H1N",
        "H2Int",
        "H32",
        "H42",
        "A2",
    )
    assert "H12" not in calculator.points
    assert "H22" not in calculator.points
    assert calculator.points["A2"] == (24000.0, 1.0)
    assert calculator.kwargs["t_off"] == pytest.approx(14.0)
    assert calculator.kwargs["t_on"] == pytest.approx(23.0)
    assert calculator.kwargs["c_d_heating"] == 0.25
    assert calculator.kwargs["fdef_override"] == 1.0
    assert calculator.kwargs["h1n_same_speed_as_h3"] is False
    assert calculator.kwargs["minimum_speed_limited"] is True
    for key, value in AHRI_HSPF2_HIDDEN_DEFAULTS.items():
        assert calculator.kwargs[key] == value

    cops = adapter.compute_display_cops(values, options=AhriHspf2Options())
    assert cops["H01"] == pytest.approx(12500 / 980)
    assert "H12" not in cops
    assert "H22" not in cops


@pytest.mark.parametrize(
    ("h12_source", "h22_source", "h42_source", "expected"),
    (
        (
            "tested",
            "eq_11_44_11_50",
            "provided",
            ("measured", "calculated", "measured"),
        ),
        (
            "eq_11_183",
            "tested",
            "not_provided",
            ("calculated", "measured", "not provided"),
        ),
        (
            "eq_11_185",
            "eq_11_44_11_50",
            "provided",
            ("calculated", "calculated", "measured"),
        ),
    ),
)
def test_hspf2_adapter_maps_v3_source_contract(
    h12_source: str,
    h22_source: str,
    h42_source: str,
    expected: tuple[str, str, str],
) -> None:
    result = {
        "HSPF2": 9.875,
        "total_heating_btu": 22500.0,
        "total_energy_wh": 2278.481,
        "summary": {
            "metadata": {
                "h12_source": h12_source,
                "h22_source": h22_source,
            }
        },
        "h42_source": h42_source,
    }

    summary = AhriHspf2Adapter(_executor(FakeHspf2Calculator(result))).calculate(
        complete_values(), options=AhriHspf2Options()
    )

    assert summary is not None
    assert (summary.h12_source, summary.h22_source, summary.h42_source) == expected


def test_hspf2_adapter_includes_enabled_optional_points_and_flags() -> None:
    calculator = FakeHspf2Calculator()
    options = AhriHspf2Options(
        measured_h42=False,
        measured_h12=True,
        measured_h22=True,
        h1n_same_speed_as_h32=True,
        minimum_speed_limited=False,
    )

    AhriHspf2Adapter(_executor(calculator)).calculate(complete_values(), options=options)

    assert "H42" not in calculator.points
    assert calculator.points["H12"] == (24000.0, 2200.0)
    assert calculator.points["H22"] == (23200.0, 2160.0)
    assert calculator.kwargs["h1n_same_speed_as_h3"] is True
    assert calculator.kwargs["minimum_speed_limited"] is False


def test_hspf2_adapter_blanks_incomplete_and_marks_invalid_active_input() -> None:
    adapter = AhriHspf2Adapter(_executor(FakeHspf2Calculator()))
    incomplete = complete_values()
    incomplete["power_H42"] = ""
    assert adapter.calculate(incomplete, options=AhriHspf2Options()) is None

    invalid = complete_values()
    invalid["power_H42"] = "bad"
    cops = adapter.compute_display_cops(invalid, options=AhriHspf2Options())
    assert "H42" not in cops
    with pytest.raises(AhriHspf2InputError) as exc_info:
        adapter.calculate(invalid, options=AhriHspf2Options())
    assert exc_info.value.field_errors == {"power_H42": "숫자 입력 필요"}


def test_hspf2_adapter_runs_existing_core_with_dev_sample() -> None:
    values = complete_values()
    values["cut_out_c"] = "-40.0"
    values["cut_in_c"] = "-40.0"

    summary = AhriHspf2Adapter().calculate(values, options=AhriHspf2Options())

    assert summary is not None
    assert summary.hspf2 > 0.0


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


def test_hspf2_section_defaults_tables_optional_roles_and_result(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section
    from apps.calculator.ui.table.roles import CellRole

    section = AhriHspf2Section(tk_root)
    section.pack()
    tk_root.update_idletasks()

    assert section.numeric_table.visual_style == "shared"
    assert section.a2_table.visual_style == "shared"
    assert section.heating_table.visual_style == "shared"

    assert section.region_var.get() == "IV"
    assert (section.h42_var.get(), section.h12_var.get(), section.h22_var.get()) == (
        True,
        False,
        False,
    )
    assert section.h1n_same_speed_var.get() is False
    assert section.minimum_speed_var.get() is True
    assert section.numeric_table.get_text_values() == {
        "cd": "0.25",
        "defrost_credit": "1.0",
        "cut_out_c": "-40.0",
        "cut_in_c": "-40.0",
    }
    assert tuple(key for key, _label in section.heating_table.columns) == (
        AHRI_HSPF2_UI_POINT_ORDER
    )
    assert tuple(label for _key, label in section.heating_table.columns) == (
        "H01",
        "H11",
        "H2v",
        "H32",
        "H42",
        "H1N(STD)",
        "H12",
        "H22",
    )
    assert "A2" not in tuple(key for key, _label in section.heating_table.columns)
    assert "capacity_H2Int" in section.heating_table.field_order
    assert "power_H2Int" in section.heating_table.field_order
    assert "capacity_H1N" in section.heating_table.field_order
    assert "power_H1N" in section.heating_table.field_order
    assert section.a2_table.columns == (("A2", "A2"),)
    assert section.a2_table.rows == (("capacity", "Capacity [Btu/h]"),)
    assert section.heating_table.rows == (
        ("condition_temp", "Condition / Temp"),
        ("capacity", "Capacity [Btu/h]"),
        ("power", "Power [W]"),
        ("cop", "COP"),
    )
    for point in AHRI_HSPF2_UI_POINT_ORDER:
        label = section.heating_table.static_cell_labels[("condition_temp", point)]
        assert label.cget("text").endswith(
            f"{AHRI_HSPF2_TEMPERATURES_C[point]:.1f} °C"
        )
    assert section.batch_button.master is section.detail_toggle.master
    assert section.batch_button.winfo_manager() == "pack"
    assert section.detail_toggle.winfo_manager() == "pack"
    assert section.heating_table.cell_role((1, 4)) is CellRole.EDITABLE
    assert section.heating_table.cell_role((1, 5)) is CellRole.EDITABLE
    assert section.heating_table.cell_role((1, 6)) is CellRole.READONLY
    assert section.heating_table.cell_role((1, 7)) is CellRole.READONLY
    assert section.heating_table.cell_widget((1, 6)).cget("text") == ""
    assert section.a2_table.get_text_values()["a2_capacity"] == ""
    assert "a2_power" not in section.a2_table.field_order
    assert section.heating_table.static_cell_labels[("cop", "H01")].cget(
        "text"
    ) == ""
    assert section.heating_table.static_cell_labels[("cop", "H12")].cget(
        "text"
    ) == ""
    assert section.result_panel.summary_tables == {}
    assert section._detail_status == "입력 대기"
    visible_fields = {
        *section.numeric_table.field_order,
        *section.a2_table.field_order,
        *section.heating_table.field_order,
    }
    assert "defrost_t_test_minutes" not in visible_fields
    assert "defrost_t_max_minutes" not in visible_fields


def test_hspf2_optional_toggle_restores_editability_and_calculates(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section
    from apps.calculator.ui.table.roles import CellRole

    section = AhriHspf2Section(tk_root)
    section.h12_var.set(True)
    section.a2_table.set_values_batch(
        {"a2_capacity": HSPF2_SAMPLE_VALUES["a2_capacity"]}
    )
    section.heating_table.set_values_batch(HSPF2_HEATING_SAMPLE_VALUES)
    section._auto_calc.flush_now()

    assert section.heating_table.cell_role((1, 6)) is CellRole.EDITABLE
    assert section.heating_table.get_text_values()["capacity_H12"] == (
        HSPF2_SAMPLE_VALUES["capacity_H12"]
    )
    assert section.heating_table.static_cell_labels[("cop", "H12")].cget(
        "text"
    ) == "10.91"
    assert section.result_panel.summary_value_labels["HSPF2"][0].cget("text")


def test_ahri_tab_registers_seer2_and_hspf2_metrics(tk_root) -> None:
    from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab

    tab = Ahri210240Tab(tk_root)
    tab.pack()
    tk_root.update_idletasks()

    assert [
        tab.metric_notebook.tab(tab_id, "text")
        for tab_id in tab.metric_notebook.tabs()
    ] == ["SEER2", "HSPF2"]
