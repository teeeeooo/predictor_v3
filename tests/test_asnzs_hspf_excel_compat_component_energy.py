import pytest
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator
import core.calculator_iso16358 as iso
import inspect

def test_component_power_from_load_and_cop():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert calc._component_power_from_load_and_cop(3600.0, 3.0) == pytest.approx(1200.0)

def test_component_power_rejects_invalid_values():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._component_power_from_load_and_cop(3600.0, 0.0)
    with pytest.raises(ValueError):
        calc._component_power_from_load_and_cop(-100.0, 3.0)

def test_component_energy_from_power_and_hours():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert calc._component_energy_from_power(1200.0, 2.5) == pytest.approx(3000.0)

def test_component_energy_rejects_negative_values():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._component_energy_from_power(-100.0, 2.0)
    with pytest.raises(ValueError):
        calc._component_energy_from_power(100.0, -1.0)
    assert calc._component_energy_from_power(100.0, 0.0) == 0.0

def test_build_component_energy_detail():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    detail = calc._build_component_energy_detail("sample", 3600.0, 3.0, 2.0, "CB")
    assert detail["name"] == "sample"
    assert detail["anchor"] == "CB"
    assert detail["power_w"] == 1200.0
    assert detail["energy_wh"] == 2400.0

def test_sum_component_energies():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    components = [
        {"name": "a", "energy_wh": 100.0},
        {"name": "b", "energy_wh": 250.0},
        {"name": "c", "energy_wh": 50.0},
    ]
    assert calc._sum_component_energies(components) == pytest.approx(400.0)

def test_sum_component_energies_rejects_invalid_component():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(KeyError):
        calc._sum_component_energies([{"name": "a"}])
    with pytest.raises(ValueError):
        calc._sum_component_energies([{"name": "a", "energy_wh": -10.0}])

def test_component_energy_helpers_stay_in_asnzs_module():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert hasattr(calc, "_component_power_from_load_and_cop")
    
    # Common path guard
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_component_power_from_load_and_cop" not in source
