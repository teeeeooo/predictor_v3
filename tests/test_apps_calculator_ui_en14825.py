"""Unit tests for EN14825 SEER models, adapter, and table model without GUI dependence."""

import pytest
from apps.calculator.ui.en14825 import (
    SeerPointInput,
    SeerPointComputed,
    SeerResultSummary,
    SeerAdapter,
    SeerTableModel,
)
from core.calculator_en14825 import EN14825Calculator


class FakeCalculator:
    """Stub core calculator to capture raw inputs and verify W -> kW conversion."""

    def __init__(self):
        self.captured_test_points = None
        self.captured_p_to = None
        self.captured_p_sb = None
        self.captured_p_ck = None
        self.captured_p_off = None
        self.captured_p_design_c = None
        self.captured_t_design_c = None
        self.captured_cd = None

    def calculate_seer(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                       p_design_c: float, t_design_c: float, cd: float) -> dict:
        self.captured_test_points = test_points
        self.captured_p_to = p_to
        self.captured_p_sb = p_sb
        self.captured_p_ck = p_ck
        self.captured_p_off = p_off
        self.captured_p_design_c = p_design_c
        self.captured_t_design_c = t_design_c
        self.captured_cd = cd
        return {
            "seer": 5.0,
            "seer_on": 5.2,
            "qc_kwh": p_design_c * 350.0,  # h_ce = 350
        }


def test_seer_point_input_init():
    """Verify initialization of SeerPointInput model."""
    inp = SeerPointInput(
        declared_capacity=3500.0,
        declared_eer=3.5,
        tested_capacity=3400.0,
        tested_power=950.0,
    )
    assert inp.declared_capacity == 3500.0
    assert inp.declared_eer == 3.5
    assert inp.tested_capacity == 3400.0
    assert inp.tested_power == 950.0


def test_seer_part_load_calculations():
    """Verify part load ratio (%) and part load (W) calculations."""
    # A (35°C) load ratio = 100%
    ratio_a, load_a = SeerAdapter.get_part_load_info(35.0, 3000.0, 35.0)
    assert pytest.approx(ratio_a) == 100.0
    assert pytest.approx(load_a) == 3000.0

    # B (30°C) load ratio = (30-16)/(35-16) * 100 = 14/19 * 100 approx 73.68%
    ratio_b, load_b = SeerAdapter.get_part_load_info(30.0, 3000.0, 35.0)
    assert pytest.approx(ratio_b) == (14.0 / 19.0) * 100.0
    assert pytest.approx(load_b) == 3000.0 * (14.0 / 19.0)

    # Edge cases: zero p_design_c or invalid t_design_c
    r, l = SeerAdapter.get_part_load_info(35.0, 0.0, 35.0)
    assert r == 0.0 and l == 0.0

    r, l = SeerAdapter.get_part_load_info(35.0, 3000.0, 16.0)
    assert r == 0.0 and l == 0.0


def test_seer_adapter_compute_points():
    """Verify intermediate computation logic on point level."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3500.0, declared_eer=3.5, tested_capacity=3400.0, tested_power=950.0),
        "B": SeerPointInput(declared_capacity=2500.0, declared_eer=4.0, tested_capacity=2200.0, tested_power=500.0),
        "C": SeerPointInput(declared_capacity=1500.0, declared_eer=5.0), # tested missing
        "D": SeerPointInput(tested_capacity=1000.0, tested_power=150.0), # declared missing
    }

    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    # Check point A derived power (3500 / 3.5 = 1000 W)
    assert pytest.approx(computed["A"].declared_power_w_for_core) == 1000.0
    # Check point A tested EER (3400 / 950 approx 3.5789)
    assert pytest.approx(computed["A"].tested_eer) == 3400.0 / 950.0


def test_seer_adapter_w_to_kw_conversion_with_stub():
    """Verify W -> kW conversion for all parameters using FakeCalculator stub."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=576.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=315.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=194.0),
    }
    fake_core = FakeCalculator()
    adapter = SeerAdapter(calculator=fake_core)

    adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=10.0,
        t_design_c=35.0,
        cd=0.25,
    )

    # Verify W -> kW conversion on auxiliary bounds
    assert fake_core.captured_p_design_c == 3.0
    assert fake_core.captured_p_to == 0.05
    assert fake_core.captured_p_sb == 0.01
    assert fake_core.captured_p_ck == 0.02
    assert fake_core.captured_p_off == 0.01
    assert fake_core.captured_t_design_c == 35.0
    assert fake_core.captured_cd == 0.25

    # Verify W -> kW conversion on test points
    # Point A: declared capacity 3600W -> 3.6kW, derived power 900W -> 0.9kW
    assert fake_core.captured_test_points["A"] == (3.6, 0.9)


def test_seer_adapter_zero_negative_values_no_crash():
    """Verify that negative/zero inputs do not crash calculation and yield invalid or unavailable states consistently."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=0.0, tested_capacity=3600.0, tested_power=0.0),
        "B": SeerPointInput(declared_capacity=0.0, declared_eer=4.6, tested_capacity=-100.0, tested_power=576.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=-5.4, tested_capacity=1700.0, tested_power=-315.0),
        "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    # Negative/Zero input state is marked as 'invalid'
    assert computed["A"].declared_eer_state == "invalid"
    assert computed["A"].tested_power_state == "invalid"
    assert computed["B"].declared_capacity_state == "invalid"
    assert computed["B"].tested_capacity_state == "invalid"
    assert computed["C"].declared_eer_state == "invalid"
    assert computed["C"].tested_power_state == "invalid"

    # Unsupplied input state is marked as 'unavailable'
    assert computed["D"].declared_capacity_state == "unavailable"

    # Zero/negative division is prevented and returns None
    assert computed["A"].declared_power_w_for_core is None
    assert computed["A"].tested_eer is None
    assert computed["B"].declared_power_w_for_core is None

    # Check that calculate returns 'input_incomplete' status code without crashing
    summary = adapter.calculate(inputs=inputs, p_design_c_w=3000.0)
    assert summary.status_code == "input_incomplete"
    assert summary.declared_seer is None


def test_seer_adapter_calculate_declared_only():
    """Verify SEER calculation with declared inputs only (tested missing)."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2),
    }
    adapter = SeerAdapter()
    summary = adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )

    assert summary.status_code == "complete"
    assert summary.declared_seer is not None
    assert summary.tested_seer is None
    assert summary.seer_percent is None
    assert summary.seer_percent_state == "unavailable"


def test_seer_adapter_calculate_tested_only():
    """Verify SEER calculation with tested inputs only (declared missing)."""
    inputs = {
        "A": SeerPointInput(tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(tested_capacity=2650.0, tested_power=576.0),
        "C": SeerPointInput(tested_capacity=1700.0, tested_power=315.0),
        "D": SeerPointInput(tested_capacity=1200.0, tested_power=194.0),
    }
    adapter = SeerAdapter()
    summary = adapter.calculate(
        inputs=inputs,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )

    assert summary.status_code == "complete"
    assert summary.tested_seer is not None
    assert summary.declared_seer is None
    assert summary.seer_percent is None


def test_point_level_threshold_pass_fail():
    """Verify point-level comparison thresholds: capacity <90 or >=110, EER <90."""
    inputs = {
        "A": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=89.0, tested_power=25.0),  # cap_pct = 89% (<90, invalid)
        "B": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=110.0, tested_power=25.0), # cap_pct = 110% (>=110, invalid)
        "C": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=100.0, tested_power=28.0), # eer_pct = 3.57/4.0 = 89.2% (<90, invalid)
        "D": SeerPointInput(declared_capacity=100.0, declared_eer=4.0, tested_capacity=100.0, tested_power=25.0), # cap = 100%, eer = 100% (pass)
    }
    adapter = SeerAdapter()
    comp = adapter.compute_points(inputs)

    assert comp["A"].capacity_percent_state == "invalid"
    assert comp["B"].capacity_percent_state == "invalid"
    assert comp["C"].eer_percent_state == "invalid"
    assert comp["D"].capacity_percent_state == "pass"
    assert comp["D"].eer_percent_state == "pass"


def test_final_seer_threshold_pass_fail():
    """Verify final SEER % pass/fail logic: invalid if < 92%, pass if >= 92% (no upper bound)."""
    # Case 1: tested SEER / declared SEER >= 92%
    inputs_pass = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=950.0), # slight drop
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=600.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=330.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=200.0),
    }
    adapter = SeerAdapter()
    res_pass = adapter.calculate(inputs=inputs_pass, p_design_c_w=3000.0)
    assert res_pass.status_code == "complete"
    assert res_pass.seer_percent_state == "pass"

    # Case 2: tested SEER / declared SEER < 92%
    inputs_fail = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=1400.0), # large drop
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=1000.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=600.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=400.0),
    }
    res_fail = adapter.calculate(inputs=inputs_fail, p_design_c_w=3000.0)
    assert res_fail.status_code == "complete"
    assert res_fail.seer_percent_state == "invalid"


def test_seer_table_model_and_row_protection():
    """Verify SeerTableModel row definitions and verify declared power is NOT exposed."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(), "C": SeerPointInput(), "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)
    model = SeerTableModel(inputs, computed, 3000.0)

    # Assert row keys exists but declared power is excluded
    row_keys = model.get_row_keys()
    assert "declared_capacity" in row_keys
    assert "declared_eer" in row_keys

    # Search for any string containing "power" representing declared power row
    assert "declared_power" not in row_keys
    assert "declared_power_w_for_core" not in row_keys
    assert "derived_power" not in row_keys


def test_seer_adapter_validation_failure():
    """Verify that calculator validations do not crash but return structured errors."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2),
    }
    adapter = SeerAdapter()

    # p_design_c_w <= 0 triggers validation error
    summary = adapter.calculate(inputs=inputs, p_design_c_w=0.0)
    assert summary.status_code == "invalid_design_load"
    assert summary.declared_seer is None


def test_seer_table_model_behavior():
    """Verify that SeerTableModel exposes rows, columns, values, and states correctly."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2385.0, tested_power=576.0), # tested capacity = 2385 -> 90% (pass)
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4), # tested missing
        "D": SeerPointInput(),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)

    model = SeerTableModel(
        inputs=inputs,
        computed=computed,
        p_design_c_w=3000.0,
        t_design_c=35.0,
    )

    # Check metadata structure
    assert model.get_row_keys() == SeerTableModel.ROW_KEYS
    assert model.get_col_keys() == SeerTableModel.COL_KEYS
    assert model.get_row_label("condition_temp") == "Condition / Temp"
    assert model.get_col_label("A") == "A (35°C)"

    # Check editability
    assert model.is_editable("declared_capacity", "A") is True
    assert model.is_editable("tested_eer", "A") is False

    # Check cell values
    assert model.get_value("condition_temp", "A") == "35°C"
    assert model.get_value("part_load_ratio", "A") == "100.0%"
    assert model.get_value("part_load_w", "A") == "3000"

    assert model.get_value("declared_capacity", "A") == "3600"
    assert model.get_value("declared_eer", "A") == "4.00"
    assert model.get_value("tested_capacity", "A") == "3600"
    assert model.get_value("tested_power", "A") == "900"
    assert model.get_value("tested_eer", "A") == "4.00"
    assert model.get_value("capacity_percent", "A") == "100.0%"
    assert model.get_value("eer_percent", "A") == "100.0%"

    # Check missing cell representations
    assert model.get_value("tested_capacity", "C") == ""
    assert model.get_value("tested_eer", "C") == ""
    assert model.get_value("capacity_percent", "C") == ""

    # Check cell states
    assert model.get_state("condition_temp", "A") == "neutral"
    assert model.get_state("declared_capacity", "A") == "neutral"
    assert model.get_state("capacity_percent", "A") == "pass"
    assert model.get_state("capacity_percent", "C") == "unavailable"
    assert model.get_state("tested_capacity", "C") == "unavailable"
