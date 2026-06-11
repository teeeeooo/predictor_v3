"""Unit tests for EN14825 SCOP models, adapter, and table model without GUI dependence."""

import pytest
from apps.calculator.ui.en14825 import (
    ScopPointInput,
    ScopPointComputed,
    ScopResultSummary,
    ScopAdapter,
    ScopTableModel,
)
from core.calculator_en14825 import EN14825Calculator


class FakeHeatingCalculator:
    """Stub core calculator to capture raw inputs and verify W -> kW conversion for SCOP."""

    def __init__(self):
        self.calls = []
        
        # Stub config for climates lookup
        self.scop_config = {
            "climates": {
                "average": {
                    "t_design_h_c": -10.0,
                    "tbiv_max_c": 2.0,
                    "tol_max_c": -7.0,
                },
                "warmer": {
                    "t_design_h_c": 2.0,
                    "tbiv_max_c": 7.0,
                    "tol_max_c": 2.0,
                },
                "colder": {
                    "t_design_h_c": -22.0,
                    "tbiv_max_c": -7.0,
                    "tol_max_c": -15.0,
                }
            }
        }

    def calculate_scop(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_h: float,
        climate: str,
        cd: float = None,
        appliance_type: str = None,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        self.calls.append({
            "test_points": test_points,
            "p_to": p_to,
            "p_sb": p_sb,
            "p_ck": p_ck,
            "p_off": p_off,
            "p_design_h": p_design_h,
            "climate": climate,
            "cd": cd,
            "appliance_type": appliance_type,
            "tbiv_temp_c": tbiv_temp_c,
            "tol_temp_c": tol_temp_c,
        })
        return {
            "scop": 4.0,
            "SCOP": 4.0,
            "scop_on": 4.2,
            "qh_kwh": p_design_h * 1400.0,
            "active_kwh": p_design_h * 1400.0 / 4.2,
            "standby_kwh": p_to * 179.0,
            "total_kwh": (p_design_h * 1400.0 / 4.2) + (p_to * 179.0),
            "climate": climate,
            "appliance_type": appliance_type or "reversible",
            "p_design_h": p_design_h,
            "operational_hours": {},
            "source": {},
            "bin_details": [],
        }


def test_scop_imports():
    """Verify that all SCOP foundation elements are correctly exported and importable."""
    import apps.calculator.ui.en14825 as ui_pkg
    assert hasattr(ui_pkg, "ScopPointInput")
    assert hasattr(ui_pkg, "ScopPointComputed")
    assert hasattr(ui_pkg, "ScopResultSummary")
    assert hasattr(ui_pkg, "ScopAdapter")
    assert hasattr(ui_pkg, "ScopTableModel")


def test_scop_point_input_init():
    """Verify initialization of ScopPointInput model."""
    inp = ScopPointInput(
        declared_capacity=4500.0,
        declared_cop=3.2,
        tested_capacity=4400.0,
        tested_power=1400.0,
        temp_c=-7.0,
    )
    assert inp.declared_capacity == 4500.0
    assert inp.declared_cop == 3.2
    assert inp.tested_capacity == 4400.0
    assert inp.tested_power == 1400.0
    assert inp.temp_c == -7.0


def test_scop_part_load_calculations():
    """Verify heating part load ratio (%) and load (W) calculations."""
    # Average climate (Tdesignh = -10°C)
    # Point A (-7°C) part load ratio = (-7 - 16)/(-10 - 16) = -23 / -26 approx 88.46%
    ratio_a, load_a = ScopAdapter.get_part_load_info(-7.0, 3000.0, -10.0)
    assert pytest.approx(ratio_a) == (-23.0 / -26.0) * 100.0
    assert pytest.approx(load_a) == 3000.0 * (-23.0 / -26.0)

    # Tj >= 16.0 -> 0% ratio
    ratio_warm, load_warm = ScopAdapter.get_part_load_info(17.0, 3000.0, -10.0)
    assert ratio_warm == 0.0
    assert load_warm == 0.0

    # Edge case: design load <= 0
    ratio_zero, load_zero = ScopAdapter.get_part_load_info(-7.0, 0.0, -10.0)
    assert ratio_zero == 0.0 and load_zero == 0.0

    # Edge case: t_design_h == 16.0
    ratio_err, load_err = ScopAdapter.get_part_load_info(-7.0, 3000.0, 16.0)
    assert ratio_err == 0.0 and load_err == 0.0


def test_scop_adapter_compute_points():
    """Verify intermediate point-level computations and cell state checks."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0, tested_capacity=3900.0, tested_power=1200.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5, tested_capacity=3400.0, tested_power=900.0),  # Tested capacity = 3400 -> 113.3% (>110%, invalid)
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),  # Tested missing
        "D": ScopPointInput(tested_capacity=1000.0, tested_power=200.0),  # Declared missing
    }
    adapter = ScopAdapter()
    computed = adapter.compute_points(inputs)

    # Point A: declared power (4000 / 3.0 approx 1333.3 W)
    assert pytest.approx(computed["A"].declared_power_w_for_core) == 4000.0 / 3.0
    # Point A: tested COP (3900 / 1200 = 3.25)
    assert computed["A"].tested_cop == 3.25
    # Point A comparison states: capacity percent (3900 / 4000 = 97.5% -> pass), COP percent (3.25 / 3.00 = 108.3% -> pass)
    assert computed["A"].capacity_percent_state == "pass"
    assert computed["A"].cop_percent_state == "pass"

    # Point B: tested capacity = 3400 / 3000 = 113.3% (invalid)
    assert computed["B"].capacity_percent_state == "invalid"

    # Point C: tested missing -> unavailable
    assert computed["C"].tested_cop_state == "unavailable"
    assert computed["C"].capacity_percent_state == "unavailable"

    # Point D: declared missing -> unavailable
    assert computed["D"].declared_capacity_state == "unavailable"


def test_scop_adapter_w_to_kw_conversion():
    """Verify W -> kW conversion boundary for all inputs in adapter calculation."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0, tested_capacity=3800.0, tested_power=1200.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5, tested_capacity=2800.0, tested_power=800.0),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0, tested_capacity=1800.0, tested_power=420.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5, tested_capacity=900.0, tested_power=180.0),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0, tested_capacity=750.0, tested_power=350.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5, tested_capacity=2800.0, tested_power=800.0),
    }

    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)

    adapter.calculate(
        inputs=inputs,
        p_design_h_w=3000.0,
        climate="average",
        p_to_w=60.0,
        p_sb_w=10.0,
        p_ck_w=20.0,
        p_off_w=0.0,
        cd=0.25,
        appliance_type="reversible",
        tbiv_temp_c=-10.0,
        tol_temp_c=-11.0,
    )

    # There should be exactly two calls: call[0] for declared, call[1] for tested
    assert len(fake_core.calls) == 2
    
    # 1. Verify declared call conversions (call[0])
    call_dec = fake_core.calls[0]
    assert call_dec["p_design_h"] == 3.0
    assert call_dec["p_to"] == 0.06
    assert call_dec["p_sb"] == 0.01
    assert call_dec["p_ck"] == 0.02
    assert call_dec["p_off"] == 0.0
    assert call_dec["tbiv_temp_c"] == -10.0
    assert call_dec["tol_temp_c"] == -11.0
    assert call_dec["test_points"]["A"]["capacity"] == 4.0
    assert pytest.approx(call_dec["test_points"]["A"]["power"]) == (4000.0 / 3.0) / 1000.0

    # 2. Verify tested call conversions (call[1])
    call_test = fake_core.calls[1]
    assert call_test["p_design_h"] == 3.0
    assert call_test["test_points"]["A"]["capacity"] == 3.8
    assert call_test["test_points"]["A"]["power"] == 1.2


def test_scop_adapter_fallback_scenarios():
    """Verify declared-only, tested-only, and both calculation fallback paths."""
    all_points = {
        "A": {"declared_capacity": 4000.0, "declared_cop": 3.0, "tested_capacity": 3800.0, "tested_power": 1200.0},
        "B": {"declared_capacity": 3000.0, "declared_cop": 3.5, "tested_capacity": 2800.0, "tested_power": 800.0},
        "C": {"declared_capacity": 2000.0, "declared_cop": 4.0, "tested_capacity": 1800.0, "tested_power": 420.0},
        "D": {"declared_capacity": 1000.0, "declared_cop": 4.5, "tested_capacity": 900.0, "tested_power": 180.0},
        "TOL": {"declared_capacity": 800.0, "declared_cop": 2.0, "tested_capacity": 750.0, "tested_power": 350.0},
        "Tbiv": {"declared_capacity": 3000.0, "declared_cop": 3.5, "tested_capacity": 2800.0, "tested_power": 800.0},
    }

    # Helper to convert raw dict to input objects
    def make_inputs(modes):
        res = {}
        for key, vals in all_points.items():
            inp = ScopPointInput()
            if "declared" in modes:
                inp.declared_capacity = vals["declared_capacity"]
                inp.declared_cop = vals["declared_cop"]
            if "tested" in modes:
                inp.tested_capacity = vals["tested_capacity"]
                inp.tested_power = vals["tested_power"]
            res[key] = inp
        return res

    adapter = ScopAdapter()

    # Case 1: Declared-only
    summary_dec = adapter.calculate(make_inputs(["declared"]), p_design_h_w=3000.0, climate="average")
    assert summary_dec.status_code == "complete"
    assert summary_dec.declared_scop is not None
    assert summary_dec.tested_scop is None
    assert summary_dec.scop_percent is None
    assert summary_dec.scop_percent_state == "unavailable"

    # Case 2: Tested-only
    summary_test = adapter.calculate(make_inputs(["tested"]), p_design_h_w=3000.0, climate="average")
    assert summary_test.status_code == "complete"
    assert summary_test.tested_scop is not None
    assert summary_dec.declared_scop is not None
    assert summary_test.declared_scop is None

    # Case 3: Both Declared + Tested
    summary_both = adapter.calculate(make_inputs(["declared", "tested"]), p_design_h_w=3000.0, climate="average")
    assert summary_both.status_code == "complete"
    assert summary_both.declared_scop is not None
    assert summary_both.tested_scop is not None
    assert summary_both.scop_percent is not None
    assert summary_both.scop_percent_state in ("pass", "invalid")


def test_scop_adapter_validation_failures():
    """Verify that bad parameters or overrides return clean status codes instead of crashing."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(), "C": ScopPointInput(), "D": ScopPointInput(), "TOL": ScopPointInput(), "Tbiv": ScopPointInput()
    }
    adapter = ScopAdapter()

    # 1. p_design_h_w <= 0
    res = adapter.calculate(inputs, p_design_h_w=0.0, climate="average")
    assert res.status_code == "invalid_design_load"

    # 2. invalid climate
    res = adapter.calculate(inputs, p_design_h_w=3000.0, climate="unknown_zone")
    assert res.status_code == "invalid_climate"

    # 3. TOL > Tbiv override (e.g. TOL = -5°C, Tbiv = -10°C)
    res = adapter.calculate(inputs, p_design_h_w=3000.0, climate="average", tbiv_temp_c=-10.0, tol_temp_c=-5.0)
    assert res.status_code == "invalid_temp_override"

    # 4. Incomplete inputs
    res = adapter.calculate(inputs, p_design_h_w=3000.0, climate="average")
    assert res.status_code == "input_incomplete"


def test_scop_table_model_definitions():
    """Verify table row structure and confirm declared power row is NOT exposed."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(), "C": ScopPointInput(), "D": ScopPointInput(), "TOL": ScopPointInput(), "Tbiv": ScopPointInput()
    }
    adapter = ScopAdapter()
    computed = adapter.compute_points(inputs)
    model = ScopTableModel(
        inputs=inputs,
        computed=computed,
        p_design_h_w=3000.0,
        climate="average",
        t_design_h=-10.0,
        tbiv_temp_c=-10.0,
        tol_temp_c=-11.0,
    )

    row_keys = model.get_row_keys()
    assert "declared_capacity" in row_keys
    assert "declared_cop" in row_keys
    assert "tested_capacity" in row_keys
    assert "tested_power" in row_keys

    # Exclusions
    assert "declared_power" not in row_keys
    assert "declared_power_w_for_core" not in row_keys
    assert "derived_power" not in row_keys


def test_scop_table_model_formatting_and_labels():
    """Verify table model labels reflect overrides and formatting is consistent."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0, tested_capacity=3800.0, tested_power=1200.0),
        "B": ScopPointInput(), "C": ScopPointInput(), "D": ScopPointInput(), "TOL": ScopPointInput(), "Tbiv": ScopPointInput()
    }
    adapter = ScopAdapter()
    computed = adapter.compute_points(inputs)
    model = ScopTableModel(
        inputs=inputs,
        computed=computed,
        p_design_h_w=3000.0,
        climate="average",
        t_design_h=-10.0,
        tbiv_temp_c=-9.0,   # override
        tol_temp_c=-12.0,  # override
    )

    # Dynamic column labels
    assert model.get_col_label("A") == "A (-7°C)"
    assert model.get_col_label("TOL") == "TOL (-12°C)"
    assert model.get_col_label("Tbiv") == "Tbiv (-9°C)"

    # Editability
    assert model.is_editable("declared_capacity", "A") is True
    assert model.is_editable("tested_cop", "A") is False

    # Formatting of values
    assert model.get_value("condition_temp", "A") == "-7°C"
    assert model.get_value("condition_temp", "TOL") == "-12°C"
    assert model.get_value("condition_temp", "Tbiv") == "-9°C"

    # Part load info: B (2°C) load ratio = (2 - 16)/(-10 - 16) = -14 / -26 = 53.8% -> rounded 54%
    assert model.get_value("part_load_ratio", "B") == "54%"
    assert model.get_value("part_load_w", "B") == "1615"  # 3000 * 14/26 approx 1615.38 W

    # Editables
    assert model.get_value("declared_capacity", "A") == "4000"
    assert model.get_value("declared_cop", "A") == "3.00"

    # Computes
    assert model.get_value("tested_cop", "A") == "3.17"  # 3800 / 1200 = 3.1666...
    assert model.get_value("capacity_percent", "A") == "95.0%"
    assert model.get_value("cop_percent", "A") == "105.6%"  # 3.1666 / 3.00 = 105.55...


def test_scop_table_section_breaks():
    """Verify table model contains the section breaks matching SEER expectations."""
    assert "declared_capacity" in ScopTableModel.SECTION_BREAK_BEFORE_ROWS
    assert "tested_capacity" in ScopTableModel.SECTION_BREAK_BEFORE_ROWS
    assert "capacity_percent" in ScopTableModel.SECTION_BREAK_BEFORE_ROWS


def test_scop_integration_with_real_calculator():
    """Smoke test calling the actual core calculator to ensure no schema/invocation mismatch."""
    all_points = {
        "A": ScopPointInput(declared_capacity=3600.0, declared_cop=4.0, tested_capacity=3600.0, tested_power=900.0),
        "B": ScopPointInput(declared_capacity=2650.0, declared_cop=4.6, tested_capacity=2650.0, tested_power=576.0),
        "C": ScopPointInput(declared_capacity=1700.0, declared_cop=5.4, tested_capacity=1700.0, tested_power=315.0),
        "D": ScopPointInput(declared_capacity=1200.0, declared_cop=6.2, tested_capacity=1200.0, tested_power=194.0),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0, tested_capacity=800.0, tested_power=400.0),
        "Tbiv": ScopPointInput(declared_capacity=2650.0, declared_cop=4.6, tested_capacity=2650.0, tested_power=576.0),
    }

    adapter = ScopAdapter()
    res = adapter.calculate(
        inputs=all_points,
        p_design_h_w=3000.0,
        climate="average",
        p_to_w=50.0,
        p_sb_w=5.0,
        p_ck_w=10.0,
        p_off_w=0.0,
        tbiv_temp_c=-10.0,
        tol_temp_c=-11.0,
    )

    assert res.status_code == "complete"
    assert res.declared_scop is not None and res.declared_scop > 0
    assert res.tested_scop is not None and res.tested_scop > 0
    assert res.scop_percent is not None
    assert res.declared_qh_kwh is not None
    assert res.declared_total_kwh is not None


def test_scop_adapter_resolved_defaults_average():
    """Verify that average climate defaults are used when overrides are omitted."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
    }
    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)
    adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="average")
    assert len(fake_core.calls) == 1
    assert fake_core.calls[0]["tbiv_temp_c"] == -10.0
    assert fake_core.calls[0]["tol_temp_c"] == -11.0


def test_scop_adapter_resolved_defaults_warmer():
    """Verify that warmer climate defaults are used when overrides are omitted."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
    }
    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)
    adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="warmer")
    assert len(fake_core.calls) == 1
    assert fake_core.calls[0]["tbiv_temp_c"] == 2.0
    assert fake_core.calls[0]["tol_temp_c"] == -11.0


def test_scop_adapter_resolved_defaults_colder():
    """Verify that colder climate defaults are used when overrides are omitted."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
    }
    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)
    adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="colder")
    assert len(fake_core.calls) == 1
    assert fake_core.calls[0]["tbiv_temp_c"] == -15.0
    assert fake_core.calls[0]["tol_temp_c"] == -22.0


def test_scop_adapter_resolved_partial_overrides():
    """Verify that partial overrides correctly fallback or preserve entered values."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
    }
    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)

    # Tbiv only overridden, TOL should use average default (-11.0)
    adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="average", tbiv_temp_c=-5.0)
    assert fake_core.calls[0]["tbiv_temp_c"] == -5.0
    assert fake_core.calls[0]["tol_temp_c"] == -11.0

    # TOL only overridden, Tbiv should use average default (-10.0)
    adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="average", tol_temp_c=-15.0)
    assert fake_core.calls[1]["tbiv_temp_c"] == -10.0
    assert fake_core.calls[1]["tol_temp_c"] == -15.0


def test_scop_adapter_invalid_override_prevention():
    """Verify that TOL > Tbiv check blocks calling the core calculator and returns a status error."""
    inputs = {
        "A": ScopPointInput(declared_capacity=4000.0, declared_cop=3.0),
        "B": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
        "C": ScopPointInput(declared_capacity=2000.0, declared_cop=4.0),
        "D": ScopPointInput(declared_capacity=1000.0, declared_cop=4.5),
        "TOL": ScopPointInput(declared_capacity=800.0, declared_cop=2.0),
        "Tbiv": ScopPointInput(declared_capacity=3000.0, declared_cop=3.5),
    }
    fake_core = FakeHeatingCalculator()
    adapter = ScopAdapter(calculator=fake_core)

    # Override average TOL to -5 and Tbiv to -10 -> TOL > Tbiv
    res = adapter.calculate(inputs=inputs, p_design_h_w=3000.0, climate="average", tbiv_temp_c=-10.0, tol_temp_c=-5.0)

    assert res.status_code == "invalid_temp_override"
    assert len(fake_core.calls) == 0  # Should NOT call core
