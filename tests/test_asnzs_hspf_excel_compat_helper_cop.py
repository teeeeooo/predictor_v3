import pytest
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator
import core.calculator_asnzs_hspf_excel as mod
import inspect

def test_cop_from_capacity_power():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert calc._cop_from_capacity_power(5000.0, 1000.0) == pytest.approx(5.0)

def test_cop_from_capacity_power_rejects_zero_or_negative_power():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._cop_from_capacity_power(5000.0, 0.0)
    with pytest.raises(ValueError):
        calc._cop_from_capacity_power(5000.0, -100.0)

def test_cop_from_capacity_power_rejects_negative_capacity():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._cop_from_capacity_power(-1000.0, 1000.0)

def test_interpolate_cop_by_temperature_midpoint():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert calc._interpolate_cop_by_temperature(-2.5, -7.0, 2.0, 2.0, 3.8) == pytest.approx(2.9)

def test_interpolate_cop_by_temperature_returns_boundary_values():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert calc._interpolate_cop_by_temperature(-7.0, -7.0, 2.0, 2.0, 3.8) == pytest.approx(2.0)
    assert calc._interpolate_cop_by_temperature(2.0, -7.0, 2.0, 2.0, 3.8) == pytest.approx(3.8)

def test_interpolate_cop_by_temperature_rejects_equal_temperatures():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._interpolate_cop_by_temperature(0.0, 1.0, 2.0, 1.0, 3.0)

def test_interpolate_cop_by_temperature_rejects_extrapolation():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._interpolate_cop_by_temperature(-8.0, -7.0, 2.0, 2.0, 3.8)
    with pytest.raises(ValueError):
        calc._interpolate_cop_by_temperature(3.0, -7.0, 2.0, 2.0, 3.8)

def test_boundary_cop_from_point():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    point = {"capacity_w": 4200.0, "power_w": 1200.0}
    assert calc._boundary_cop_from_point(point) == pytest.approx(3.5)

def test_helper_cop_reconstruction_stays_in_asnzs_module():
    # Structural guard: ensure logic is in the compatibility module
    import core.calculator_asnzs_hspf_excel as mod
    assert hasattr(mod.ASNZSExcelHSPFCompatibilityCalculator, "_cop_from_capacity_power")
    
    # Check common path does not have these
    import core.calculator_iso16358_legacy as iso
    assert not hasattr(iso.ISO16358Calculator, "_cop_from_capacity_power")
