"""Focused tests for the AHRI 210/240 SEER2 main UI foundation."""

from __future__ import annotations

import pytest

from apps.calculator.ui.ahri import (
    AHRI_SEER2_POINT_ORDER,
    AHRI_SEER2_TEMPERATURES_C,
    AhriSeer2Adapter,
    AhriSeer2InputError,
)


SAMPLE_VALUES = {
    "capacity_A_Full": "36000",
    "power_A_Full": "3000",
    "capacity_B_Full": "30000",
    "power_B_Full": "2200",
    "capacity_B_Low": "18000",
    "power_B_Low": "1200",
    "capacity_E_Int": "24000",
    "power_E_Int": "1700",
    "capacity_F_Low": "12000",
    "power_F_Low": "900",
}


class FakeSeer2Calculator:
    def __init__(self) -> None:
        self.points = None
        self.system_type = None
        self.config = {"constants": {"cooling_season_hours": 1000}}

    def calculate_seer2(
        self,
        test_points,
        system_type="HP",
        p_w_off=0.0,
        cd_low=None,
    ):
        self.points = test_points
        self.system_type = system_type
        return {
            "SEER2": 13.677,
            "total_cooling_Btu": 11961.491,
            "total_energy_Wh": 874.552,
            "bin_details": [
                {
                    "bin": 1,
                    "temp_F": 67.0,
                    "BL": 1200.0,
                    "q_Low": 13000.0,
                    "q_Int": 18000.0,
                    "q_Full": 30000.0,
                    "EER_Low": 14.0,
                    "EER_Int": 13.0,
                    "EER_Full": 12.0,
                    "EER_IntBin": 13.5,
                    "case": 1,
                    "q_j": 158400.0,
                    "E_j": 10930.0,
                },
                {
                    "bin": 2,
                    "temp_F": 72.0,
                    "BL": 2400.0,
                    "q_Low": 13200.0,
                    "q_Int": 18500.0,
                    "q_Full": 30500.0,
                    "EER_Low": 13.8,
                    "EER_Int": 12.8,
                    "EER_Full": 11.8,
                    "EER_IntBin": 13.2,
                    "case": 2.1,
                    "q_j": 172800.0,
                    "E_j": 12700.0,
                },
            ],
        }


def test_seer2_adapter_maps_exact_point_order_and_type() -> None:
    calculator = FakeSeer2Calculator()
    summary = AhriSeer2Adapter(calculator).calculate(
        SAMPLE_VALUES,
        system_type="AC",
    )

    assert tuple(calculator.points) == AHRI_SEER2_POINT_ORDER
    assert calculator.system_type == "AC"
    assert summary is not None
    assert summary.seer2 == 13.677
    assert summary.total_cooling_kbtu == pytest.approx(11961.491)
    assert summary.total_energy_kwh == pytest.approx(874.552)
    assert summary.eer2_by_point["A_Full"] == 12.0
    assert summary.bin_details[0]["bin"] == 1


def test_seer2_adapter_keeps_incomplete_blank_and_rejects_invalid() -> None:
    adapter = AhriSeer2Adapter(FakeSeer2Calculator())
    incomplete = dict(SAMPLE_VALUES)
    incomplete["power_F_Low"] = ""
    assert adapter.calculate(incomplete, system_type="HP") is None

    invalid = dict(SAMPLE_VALUES)
    invalid["power_A_Full"] = "bad"
    with pytest.raises(AhriSeer2InputError) as exc_info:
        adapter.calculate(invalid, system_type="HP")
    assert exc_info.value.field_errors == {"power_A_Full": "숫자 입력 필요"}


@pytest.mark.parametrize(
    ("result", "invalid_key"),
    (
        ({"SEER2": 13.677, "total_energy_Wh": 874.552}, "total_cooling_Btu"),
        (
            {
                "SEER2": 13.677,
                "total_cooling_Btu": 11961.491,
                "total_energy_Wh": "invalid",
            },
            "total_energy_Wh",
        ),
    ),
)
def test_seer2_adapter_rejects_missing_or_invalid_required_core_result(
    result,
    invalid_key,
) -> None:
    class ContractMismatchCalculator(FakeSeer2Calculator):
        def calculate_seer2(self, *args, **kwargs):
            return result

    adapter = AhriSeer2Adapter(ContractMismatchCalculator())

    with pytest.raises(
        ValueError,
        match=f"Invalid AHRI SEER2 core result: {invalid_key}",
    ):
        adapter.calculate(SAMPLE_VALUES, system_type="HP")


@pytest.mark.parametrize("bin_details", (None, ["invalid-row"]))
def test_seer2_adapter_rejects_invalid_bin_details(bin_details) -> None:
    class ContractMismatchCalculator(FakeSeer2Calculator):
        def calculate_seer2(self, *args, **kwargs):
            result = dict(super().calculate_seer2(*args, **kwargs))
            result["bin_details"] = bin_details
            return result

    with pytest.raises(
        ValueError,
        match="Invalid AHRI SEER2 core result: bin_details",
    ):
        AhriSeer2Adapter(ContractMismatchCalculator()).calculate(
            SAMPLE_VALUES,
            system_type="HP",
        )


@pytest.mark.parametrize(
    "constants",
    ({}, {"cooling_season_hours": "invalid"}, {"cooling_season_hours": 0}),
)
def test_seer2_adapter_rejects_missing_or_invalid_cooling_season_hours(
    constants,
) -> None:
    calculator = FakeSeer2Calculator()
    calculator.config = {"constants": constants}

    with pytest.raises(
        ValueError,
        match="Invalid AHRI SEER2 calculator config: cooling_season_hours",
    ):
        AhriSeer2Adapter(calculator).calculate(SAMPLE_VALUES, system_type="HP")


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


def test_seer2_section_table_roles_labels_autocalc_and_result(tk_root) -> None:
    from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section
    from apps.calculator.ui.table.roles import CellRole

    calculator = FakeSeer2Calculator()
    section = AhriSeer2Section(
        tk_root,
        adapter=AhriSeer2Adapter(calculator),
    )
    section.pack()
    tk_root.update_idletasks()

    assert section.type_var.get() == "HP"
    assert tuple(section.type_selector.cget("values")) == ("HP", "AC")
    from apps.calculator.ui.layout_constants import (
        CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
    )
    assert int(section.type_selector.cget("width")) == (
        CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS
    )
    assert tuple(key for key, _label in section.input_table.columns) == (
        AHRI_SEER2_POINT_ORDER
    )
    assert section.batch_button.master is section.detail_toggle.master
    assert section.batch_button.winfo_manager() == "pack"
    assert section.detail_toggle.winfo_manager() == "pack"
    assert section.input_table.cell_role((0, 0)) == CellRole.READONLY
    assert section.input_table.cell_role((1, 0)) == CellRole.EDITABLE
    assert section.input_table.cell_role((3, 0)) == CellRole.READONLY
    for point in AHRI_SEER2_POINT_ORDER:
        condition = section.input_table.static_cell_labels[("condition_temp", point)]
        assert condition.cget("text").endswith(
            f"{AHRI_SEER2_TEMPERATURES_C[point]:.1f} °C"
        )
        assert section.input_table.static_cell_labels[("eer2", point)].cget(
            "text"
        ) == ""

    section.input_table.set_values_batch(SAMPLE_VALUES)
    section._auto_calc.flush_now()

    assert calculator.system_type == "HP"
    assert section.input_table.static_cell_labels[("eer2", "A_Full")].cget(
        "text"
    ) == "12.00"
    result_values = section.result_panel.summary_value_labels["SEER2"]
    assert [label.cget("text") for label in result_values] == [
        "13.677",
        "11961.491",
        "874.552",
    ]
    assert section.result_panel.summary_status_labels["SEER2"].cget("text") == (
        "자동 계산 완료"
    )


def test_calculator_app_registers_ahri_metric_tabs(tk_root) -> None:
    from apps.calculator.ui.calculator_app import CalculatorTkApp

    app = CalculatorTkApp(root=tk_root)
    tab_names = [
        app.notebook.tab(tab_id, "text") for tab_id in app.notebook.tabs()
    ]
    metric_names = [
        app.ahri210240_tab.metric_notebook.tab(tab_id, "text")
        for tab_id in app.ahri210240_tab.metric_notebook.tabs()
    ]

    assert tab_names == [
        "ISO 16358",
        "EN14825",
        "AHRI 210/240",
        "KS C 9306",
    ]
    assert metric_names == ["SEER2", "HSPF2"]
