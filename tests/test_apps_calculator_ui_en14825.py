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

    # D (20°C) load ratio = (20-16)/(35-16) * 100 = 4/19 * 100 approx 21.05%
    ratio_d, load_d = SeerAdapter.get_part_load_info(20.0, 3000.0, 35.0)
    assert pytest.approx(ratio_d) == (4.0 / 19.0) * 100.0
    assert pytest.approx(load_d) == 3000.0 * (4.0 / 19.0)

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
    assert pytest.approx(computed["A"].declared_power) == 1000.0
    # Check point A tested EER (3400 / 950 approx 3.5789)
    assert pytest.approx(computed["A"].tested_eer) == 3400.0 / 950.0

    # Check comparison percentages
    # Capacity % for A = 3400 / 3500 * 100 approx 97.14% (within 90% - 110%, so pass)
    assert pytest.approx(computed["A"].capacity_percent) == (3400.0 / 3500.0) * 100.0
    assert computed["A"].capacity_percent_state == "pass"

    # EER % for A = (3400/950) / 3.5 * 100 approx 102.25% (>= 90%, so pass)
    assert pytest.approx(computed["A"].eer_percent) == ((3400.0 / 950.0) / 3.5) * 100.0
    assert computed["A"].eer_percent_state == "pass"

    # Capacity % invalid threshold (< 90%)
    # tested capacity = 2200, declared = 2500 -> 2200 / 2500 = 88% (invalid/red)
    assert computed["B"].capacity_percent_state == "invalid"
    
    # missing states
    assert computed["C"].tested_eer_state == "unavailable"
    assert computed["C"].capacity_percent_state == "unavailable"
    assert computed["D"].declared_capacity_state == "unavailable"


def test_seer_adapter_zero_denominator_no_crash():
    """Verify that zero or negative values do not crash adapter logic."""
    inputs = {
        "A": SeerPointInput(declared_capacity=3500.0, declared_eer=0.0, tested_capacity=3400.0, tested_power=0.0),
        "B": SeerPointInput(declared_capacity=0.0, declared_eer=3.5, tested_capacity=-100.0, tested_power=500.0),
    }
    adapter = SeerAdapter()
    computed = adapter.compute_points(inputs)
    
    assert computed["A"].declared_power is None
    assert computed["A"].tested_eer is None
    assert computed["A"].declared_eer_state == "unavailable"
    assert computed["A"].tested_power_state == "unavailable"
    
    assert computed["B"].declared_power is None
    assert computed["B"].capacity_percent_state == "unavailable"


def test_seer_adapter_calculate_declared_only():
    """Verify SEER calculation with declared inputs only (no tested)."""
    # Using typical design condition with cd=0.25, p_design_c=3000 W
    inputs = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0), # derived power: 900W
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6), # derived power: 576W
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4), # derived power: 314.8W
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2), # derived power: 193.5W
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
    
    assert summary.status == "자동 계산 완료"
    assert summary.declared_seer is not None
    assert summary.declared_qc_kwh is not None
    assert summary.tested_seer is None
    assert summary.tested_qc_kwh is None
    assert summary.seer_percent is None
    assert summary.seer_percent_state == "unavailable"


def test_seer_adapter_calculate_tested_only():
    """Verify SEER calculation with tested inputs only (no declared)."""
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
    
    assert summary.status == "자동 계산 완료"
    assert summary.tested_seer is not None
    assert summary.tested_qc_kwh is not None
    assert summary.declared_seer is None
    assert summary.declared_qc_kwh is None
    assert summary.seer_percent is None


def test_seer_adapter_calculate_both_pass_and_fail():
    """Verify calculation results and red-tinting thresholds (< 92%) for both declared & tested."""
    # Case 1: Both declared and tested values match closely (SEER % is close to 100%, pass)
    inputs_pass = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=576.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=315.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=194.0),
    }
    adapter = SeerAdapter()
    summary_pass = adapter.calculate(
        inputs=inputs_pass,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )
    assert summary_pass.status == "자동 계산 완료"
    assert summary_pass.declared_seer is not None
    assert summary_pass.tested_seer is not None
    assert summary_pass.seer_percent is not None
    assert summary_pass.seer_percent >= 92.0
    assert summary_pass.seer_percent_state == "pass"

    # Case 2: Tested EER/capacity are poor, driving SEER % below 92% (invalid/red)
    inputs_fail = {
        "A": SeerPointInput(declared_capacity=3600.0, declared_eer=4.0, tested_capacity=3600.0, tested_power=1200.0), # EER = 3.0 instead of 4.0
        "B": SeerPointInput(declared_capacity=2650.0, declared_eer=4.6, tested_capacity=2650.0, tested_power=800.0),
        "C": SeerPointInput(declared_capacity=1700.0, declared_eer=5.4, tested_capacity=1700.0, tested_power=500.0),
        "D": SeerPointInput(declared_capacity=1200.0, declared_eer=6.2, tested_capacity=1200.0, tested_power=300.0),
    }
    summary_fail = adapter.calculate(
        inputs=inputs_fail,
        p_design_c_w=3000.0,
        p_to_w=50.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
    )
    assert summary_fail.status == "자동 계산 완료"
    assert summary_fail.seer_percent is not None
    assert summary_fail.seer_percent < 92.0
    assert summary_fail.seer_percent_state == "invalid"


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
    assert "오류:" in summary.status
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
