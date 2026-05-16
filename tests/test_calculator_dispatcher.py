import pytest

from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator
from core.calculator_ahri_seer2 import AHRICalculator
from core.calculator_dispatcher import create_calculator_for_profile
from core.calculator_ks_c9306 import KSC9306Calculator


def test_dispatcher_returns_ks_calculator_for_ks_cspf_profile_id():
    calculator = create_calculator_for_profile(profile_id="ks_c9306_cspf")

    assert isinstance(calculator, KSC9306Calculator)


def test_dispatcher_returns_ks_calculator_for_ks_hspf_profile_id():
    calculator = create_calculator_for_profile(profile_id="ks_c9306_hspf")

    assert isinstance(calculator, KSC9306Calculator)


def test_dispatcher_returns_ks_calculator_for_ks_cspf_selector():
    calculator = create_calculator_for_profile(
        standard="KS_C_9306",
        region="korea",
        metric="CSPF",
        mode="cooling",
    )

    assert isinstance(calculator, KSC9306Calculator)


def test_dispatcher_returns_ks_calculator_for_ks_hspf_selector():
    calculator = create_calculator_for_profile(
        standard="KS_C_9306",
        region="korea",
        metric="HSPF",
        mode="heating",
    )

    assert isinstance(calculator, KSC9306Calculator)


def test_dispatcher_returns_ahri_seer2_calculator_for_ahri_seer2_profile_id():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")

    assert isinstance(calculator, AHRICalculator)


def test_dispatcher_returns_ahri_hspf2_calculator_for_ahri_hspf2_profile_id():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_hspf2")

    assert isinstance(calculator, AHRIHSPF2Calculator)


def test_dispatcher_fail_fast_on_unknown_profile_id():
    with pytest.raises(ValueError, match="match exactly one enabled profile"):
        create_calculator_for_profile(profile_id="unknown_profile_xyz")
