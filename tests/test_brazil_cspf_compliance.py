"""Focused Brazil CSPF capability, profile, golden, and rule tests."""

from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from core.calculators.capability import (
    BrazilCspfComplianceError,
    BrazilCspfComplianceRequest,
    CapabilityConfigurationError,
    Iso16358CspfRequest,
    execute_standard_calculation,
)
from core.calculators.capability.brazil import BrazilCspfComplianceHandler
from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.profiles import resolve_calculator_profile


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/brazil_cspf_compliance_golden.json"
CONFIG_PATH = ROOT / "data/region_configs/brazil.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_brazil_profile_resolves_as_the_single_enabled_profile():
    profile = resolve_calculator_profile(
        standard="ISO_16358",
        region="brazil",
        metric="CSPF",
        mode="cooling",
    )

    assert profile.profile_id == "brazil_cspf_compliance"
    assert profile.capability_ids == ("brazil.cspf_compliance",)


def test_brazil_production_config_keeps_t1_required_only_and_2080_hours():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    assert config["cspf_test_profile"] == {
        "climate_profile": "T1",
        "test_selection": "required_only",
    }
    assert config["points"]["29_full"] == "default"
    assert config["points"]["29_half"] == "default"
    assert config["derived_rules"]["29_half"] == {
        "source": "35_half",
        "capacity_factor": 1.077,
        "power_factor": 0.914,
    }
    assert sum(item["nj"] for item in config["bin_hours"]) == 2080
    assert [item["tj"] for item in config["bin_hours"]] == list(range(15, 46))


def test_brazil_t1_resolver_preserves_three_point_29_half_and_derives_two_point():
    fixture = load_fixture()
    calculator = create_calculator_for_profile(profile_id="brazil_cspf_compliance")
    three_point = fixture["measured_points"]
    two_point = {key: value for key, value in three_point.items() if key != "29_half"}

    resolved_three = calculator._resolve_cspf_profile_points(three_point)
    resolved_two = calculator._resolve_cspf_profile_points(two_point)

    assert resolved_three["29_half"] == three_point["29_half"]
    assert resolved_two["29_half"]["capacity"] == pytest.approx(1587 * 1.077)
    assert resolved_two["29_half"]["power"] == pytest.approx(384 * 0.914)
    assert "29_min" not in resolved_three
    assert "29_min" not in resolved_two


def test_brazil_golden_matches_exact_and_display_references():
    fixture = load_fixture()
    result = execute_standard_calculation(
        "brazil.cspf_compliance",
        BrazilCspfComplianceRequest(fixture["measured_points"]),
    )
    expected = fixture["expected"]

    assert result.three_point_exact_cspf == pytest.approx(
        expected["three_point"]["exact_cspf"], abs=1e-10
    )
    assert result.two_point_exact_cspf == pytest.approx(
        expected["two_point"]["exact_cspf"], abs=1e-10
    )
    assert result.three_point_result["cspf"] == pytest.approx(
        6.023, abs=0.001
    )
    assert result.two_point_result["cspf"] == pytest.approx(
        4.55, abs=0.001
    )
    assert result.three_point_result["annual_cooling_kwh"] == pytest.approx(2461.278, abs=0.001)
    assert result.three_point_result["annual_power_kwh"] == pytest.approx(408.643, abs=0.001)
    assert result.two_point_result["annual_cooling_kwh"] == pytest.approx(2461.278, abs=0.001)
    assert result.two_point_result["annual_power_kwh"] == pytest.approx(540.939, abs=0.001)
    assert result.rule_2.left_value == pytest.approx(expected["measured_29_half_eer"])
    assert result.rule_2.right_value == pytest.approx(expected["calculated_29_bin_eer"])
    assert result.rule_1.passed is True
    assert result.rule_2.passed is False
    assert result.final_passed is True


def _raw_result(exact_cspf: float, *, eer_29: float = 5.0, csec: float = 1.0) -> dict:
    return {
        "cspf": -999.0,
        "annual_cooling_kwh": exact_cspf * csec / 1000.0,
        "annual_power_kwh": csec / 1000.0,
        "bin_details": [
            {
                "bin_no": 1,
                "tj": 29.0,
                "nj": 1.0,
                "cstl_bin": exact_cspf * csec,
                "csec_bin": csec,
                "eer": eer_29,
            }
        ],
    }


def _run_with_fake_results(monkeypatch, three_point, two_point, measured=None):
    measured = measured or {
        "35_full": {"capacity": 100.0, "power": 10.0},
        "35_half": {"capacity": 80.0, "power": 10.0},
        "29_half": {"capacity": 50.0, "power": 10.0},
    }
    created = []

    class FakeCalculator:
        def __init__(self, raw_result):
            self.raw_result = raw_result
            self.inputs = None

        def calculate_cspf(self, inputs):
            self.inputs = inputs
            return self.raw_result

    def factory(*, profile_id):
        assert profile_id == "brazil_cspf_compliance"
        raw_result = three_point if not created else two_point
        calculator = FakeCalculator(raw_result)
        created.append(calculator)
        return calculator

    monkeypatch.setattr(
        "core.calculators.capability.brazil.create_calculator_for_profile", factory
    )
    request = BrazilCspfComplianceRequest(measured_points=measured)
    result = BrazilCspfComplianceHandler().execute(request)
    return result, created, request


@pytest.mark.parametrize("bad_value", [0, -1, math.nan, math.inf, -math.inf, "bad"])
def test_brazil_input_requires_finite_positive_values(monkeypatch, bad_value):
    measured = {
        "35_full": {"capacity": 100.0, "power": 10.0},
        "35_half": {"capacity": 80.0, "power": 10.0},
        "29_half": {"capacity": bad_value, "power": 10.0},
    }

    with pytest.raises(BrazilCspfComplianceError):
        _run_with_fake_results(monkeypatch, _raw_result(5), _raw_result(4), measured)


def test_brazil_handler_uses_two_independent_mappings_and_preserves_request(monkeypatch):
    measured = {
        "35_full": {"capacity": 100.0, "power": 10.0},
        "35_half": {"capacity": 80.0, "power": 10.0},
        "29_half": {"capacity": 50.0, "power": 10.0},
    }
    original = deepcopy(measured)
    result, calculators, request = _run_with_fake_results(
        monkeypatch, _raw_result(5), _raw_result(4), measured
    )

    assert len(calculators) == 2
    assert calculators[0] is not calculators[1]
    assert set(calculators[0].inputs) == {"35_full", "35_half", "29_half"}
    assert set(calculators[1].inputs) == {"35_full", "35_half"}
    assert request.measured_points == original
    assert calculators[0].inputs is not calculators[1].inputs
    assert result.three_point_result is calculators[0].raw_result
    assert result.two_point_result is calculators[1].raw_result


@pytest.mark.parametrize(
    "mutate",
    (
        lambda result: result.pop("bin_details"),
        lambda result: result.__setitem__(
            "bin_details", result["bin_details"] + [dict(result["bin_details"][0])]
        ),
        lambda result: result["bin_details"][0].pop("cstl_bin"),
        lambda result: result["bin_details"][0].__setitem__("eer", math.inf),
        lambda result: result["bin_details"][0].__setitem__("csec_bin", 0.0),
    ),
)
def test_brazil_diagnostic_integrity_fails_fast(monkeypatch, mutate):
    three_point = _raw_result(5)
    mutate(three_point)

    with pytest.raises(BrazilCspfComplianceError):
        _run_with_fake_results(monkeypatch, three_point, _raw_result(4))


@pytest.mark.parametrize("rule_1_passed", [False, True])
@pytest.mark.parametrize("rule_2_passed", [False, True])
def test_brazil_final_is_or_of_the_two_rule_results(
    monkeypatch, rule_1_passed, rule_2_passed
):
    exact_two = 10.0
    exact_three = 14.0 if rule_1_passed else 14.000001
    measured_eer = 6.0 if rule_2_passed else 5.0
    measured = {
        "35_full": {"capacity": 100.0, "power": 10.0},
        "35_half": {"capacity": 80.0, "power": 10.0},
        "29_half": {"capacity": measured_eer, "power": 1.0},
    }
    result, _calculators, _request = _run_with_fake_results(
        monkeypatch,
        _raw_result(exact_three),
        _raw_result(exact_two, eer_29=5.0),
        measured,
    )

    assert result.rule_1.passed is rule_1_passed
    assert result.rule_2.passed is rule_2_passed
    assert result.final_passed is (rule_1_passed or rule_2_passed)


def test_brazil_rule_boundaries_are_equality_sensitive(monkeypatch):
    result, _calculators, _request = _run_with_fake_results(
        monkeypatch,
        _raw_result(14.0, eer_29=5.0),
        _raw_result(10.0, eer_29=5.0),
        {
            "35_full": {"capacity": 100.0, "power": 10.0},
            "35_half": {"capacity": 80.0, "power": 10.0},
            "29_half": {"capacity": 5.0, "power": 1.0},
        },
    )

    assert result.rule_1.left_value == pytest.approx(result.rule_1.right_value)
    assert result.rule_1.passed is True
    assert result.rule_2.left_value == pytest.approx(result.rule_2.right_value)
    assert result.rule_2.passed is False


def test_brazil_profile_cannot_use_generic_iso_cspf_capability(monkeypatch):
    constructed = []
    monkeypatch.setattr(
        "core.calculators.capability.gateway.create_calculator_for_profile",
        lambda **kwargs: constructed.append(kwargs),
    )

    with pytest.raises(CapabilityConfigurationError):
        execute_standard_calculation(
            "iso16358.cspf",
            Iso16358CspfRequest("brazil_cspf_compliance", {}),
        )
    assert constructed == []


def test_brazil_unknown_or_non_brazil_profile_fails_as_configuration_error():
    with pytest.raises(CapabilityConfigurationError):
        execute_standard_calculation(
            "brazil.cspf_compliance",
            BrazilCspfComplianceRequest({}, profile_id="missing_profile"),
        )
    with pytest.raises(CapabilityConfigurationError):
        execute_standard_calculation(
            "brazil.cspf_compliance",
            BrazilCspfComplianceRequest(
                {}, profile_id="iso_t1_default_2point_cspf"
            ),
        )
