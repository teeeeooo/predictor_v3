import pytest
from core.calculator_profiles import CalculatorProfile, resolve_calculator_profile, list_calculator_profiles
import core.calculator_profiles as cp

# Helper to build a test-local registry
def get_mock_registry(profiles):
    return tuple(profiles)

def test_ambiguous_selector_raises_error(monkeypatch):
    p1 = CalculatorProfile("p1", "std", "reg", "met", "mod", "c1", "cfg1")
    p2 = CalculatorProfile("p2", "std", "reg", "met", "mod", "c2", "cfg2")
    
    monkeypatch.setattr(cp, "_CALCULATOR_PROFILES", get_mock_registry([p1, p2]))
    
    with pytest.raises(ValueError, match="match exactly one enabled profile"):
        resolve_calculator_profile(standard="std", region="reg", metric="met", mode="mod")

def test_disabled_profile_is_excluded_by_default(monkeypatch):
    p1 = CalculatorProfile("p1", "std1", "reg1", "met1", "mod1", "c1", "cfg1", enabled=True)
    p2 = CalculatorProfile("asnzs_compat", "ASNZS", "au_nz", "HSPF", "heating", "asnzs_hspf", "cfg2", enabled=False)
    
    monkeypatch.setattr(cp, "_CALCULATOR_PROFILES", get_mock_registry([p1, p2]))
    
    # Should resolve p1
    assert resolve_calculator_profile(profile_id="p1").profile_id == "p1"
    
    # Should fail for p2 by default
    with pytest.raises(ValueError):
        resolve_calculator_profile(profile_id="asnzs_compat")
    
    # Check manual list
    assert len(list_calculator_profiles(enabled_only=True)) == 1
    assert len(list_calculator_profiles(enabled_only=False)) == 2

def test_asnzs_metadata_only_does_not_auto_select_compat_profile(monkeypatch):
    p1 = CalculatorProfile("common", "ISO", "common", "HSPF", "heating", "common_calc", "cfg1", enabled=True)
    p2 = CalculatorProfile("asnzs_compat", "ASNZS", "au_nz", "HSPF", "heating", "asnzs_hspf", "cfg2", enabled=False)
    
    monkeypatch.setattr(cp, "_CALCULATOR_PROFILES", get_mock_registry([p1, p2]))
    
    # Automatic selection should only find p1
    resolved = resolve_calculator_profile(standard="ISO", region="common", metric="HSPF", mode="heating")
    assert resolved.profile_id == "common"
    
    # Selecting via ASNZS metadata should fail (because p2 is disabled)
    with pytest.raises(ValueError):
        resolve_calculator_profile(standard="ASNZS", region="au_nz", metric="HSPF", mode="heating")

def test_explicit_opt_in_enabled_only_false(monkeypatch):
    p2 = CalculatorProfile("asnzs_compat", "ASNZS", "au_nz", "HSPF", "heating", "asnzs_hspf", "cfg2", enabled=False)
    monkeypatch.setattr(cp, "_CALCULATOR_PROFILES", get_mock_registry([p2]))
    
    # Explicitly list all profiles and find the disabled one
    profiles = list_calculator_profiles(enabled_only=False)
    resolved = [p for p in profiles if p.profile_id == "asnzs_compat"][0]
    assert resolved.profile_id == "asnzs_compat"
