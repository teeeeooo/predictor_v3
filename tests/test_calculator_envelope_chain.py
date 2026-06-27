"""End-to-end smoke for the AHRI SEER2 envelope adapter chain.

Chain under test::

    PredictedPointsEnvelope (source=ml_prediction, W/W)
      -> CalculatorInputEnvelope (Btu/h, W; units_trace)
      -> AHRICalculator.calculate_seer2()
      -> CalculatorResultEnvelope
      -> RankingCandidateEnvelope

The smoke does not exercise ranking algorithms or ML callers; it only
verifies that the adapter layer composes end-to-end and that
candidate_id, model_version, units_trace, calculator-native measured
inputs, and the ranking-layer envelope boundary are preserved.
"""

import pytest

from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.adapters.input_adapter import measured_inputs_as_test_points
from core.calculators.adapters.prediction_adapter import (
    build_predicted_points_envelope,
    predicted_points_to_calculator_input_envelope,
)
from core.calculator_ranking_adapter import build_ranking_candidate_envelope
from core.calculator_result_adapter import wrap_calculator_result_envelope
from core.calculators.adapters.unit_adapter import W_TO_BTU_PER_HOUR


PROFILE_ID = "ahri_usa_seer2"
CANDIDATE_ID = "cand-007"
MODEL_VERSION = "lgbm-2026.05.17"


def _ml_canonical_points():
    return {
        "A_Full": {"capacity": 10000.0, "power": 3000.0, "capacity_unit": "W", "power_unit": "W"},
        "B_Full": {"capacity": 8500.0, "power": 2200.0, "capacity_unit": "W", "power_unit": "W"},
        "B_Low": {"capacity": 5000.0, "power": 1200.0, "capacity_unit": "W", "power_unit": "W"},
        "E_Int": {"capacity": 7000.0, "power": 1700.0, "capacity_unit": "W", "power_unit": "W"},
        "F_Low": {"capacity": 3500.0, "power": 900.0, "capacity_unit": "W", "power_unit": "W"},
    }


@pytest.fixture
def chain():
    """Run the full envelope chain once and return every stage's envelope."""
    predicted = build_predicted_points_envelope(
        PROFILE_ID,
        _ml_canonical_points(),
        source="ml_prediction",
        model_target="cooling",
        metadata={"model_version": MODEL_VERSION, "candidate_id": CANDIDATE_ID},
    )

    calc_input = predicted_points_to_calculator_input_envelope(
        predicted, profile_id=PROFILE_ID
    )

    calculator = create_calculator_for_profile(profile_id=PROFILE_ID)
    raw_result = calculator.calculate_seer2(
        measured_inputs_as_test_points(calc_input)
    )

    result_envelope = wrap_calculator_result_envelope(PROFILE_ID, raw_result)

    candidate_envelope = build_ranking_candidate_envelope(
        CANDIDATE_ID, result_envelope
    )

    return {
        "predicted": predicted,
        "calc_input": calc_input,
        "raw_result": raw_result,
        "result_envelope": result_envelope,
        "candidate_envelope": candidate_envelope,
    }


def test_chain_converts_ml_w_capacity_to_ahri_native_btu_per_hour(chain):
    measured = chain["calc_input"]["measured_inputs"]

    assert measured["A_Full"]["capacity"] == pytest.approx(
        10000.0 * W_TO_BTU_PER_HOUR
    )
    assert measured["A_Full"]["power"] == 3000.0
    # measured_inputs_as_test_points round-trips into the tuple form the
    # calculator already accepts.
    points_for_calculator = measured_inputs_as_test_points(chain["calc_input"])
    assert points_for_calculator["A_Full"] == (
        pytest.approx(10000.0 * W_TO_BTU_PER_HOUR),
        3000.0,
    )


def test_chain_preserves_units_trace_on_calculator_input(chain):
    assert chain["calc_input"]["options"]["units_trace"] == {
        "source_units": {"capacity": "W", "power": "W"},
        "target_units": {"capacity": "Btu/h", "power": "W"},
        "conversion_applied": True,
    }


def test_chain_preserves_candidate_id_through_all_stages(chain):
    assert chain["predicted"]["metadata"]["candidate_id"] == CANDIDATE_ID
    assert chain["calc_input"]["options"]["candidate_id"] == CANDIDATE_ID
    assert chain["candidate_envelope"]["candidate_id"] == CANDIDATE_ID


def test_chain_preserves_model_version_through_all_stages(chain):
    assert chain["predicted"]["metadata"]["model_version"] == MODEL_VERSION
    assert chain["calc_input"]["options"]["model_version"] == MODEL_VERSION


def test_chain_produces_result_envelope_with_seer2_metric(chain):
    result_envelope = chain["result_envelope"]
    assert result_envelope["calculator_profile_id"] == PROFILE_ID
    assert result_envelope["metric"] == "SEER2"
    assert result_envelope["units"] == "Btu/Wh"
    assert result_envelope["value"] > 0


def test_chain_ranking_envelope_consumes_result_envelope_fields_only(chain):
    candidate = chain["candidate_envelope"]
    result = chain["result_envelope"]

    assert candidate["calculator_profile_id"] == PROFILE_ID
    assert candidate["metric"] == "SEER2"
    assert candidate["units"] == result["units"]
    assert candidate["value"] == float(result["value"])
    assert candidate["score"] == candidate["value"]
    assert candidate["ranking_features"] == {}


def test_chain_ranking_envelope_does_not_expose_raw_calculator_result(chain):
    candidate = chain["candidate_envelope"]

    # The ranking layer must consume envelopes, not raw calculator dicts.
    assert "raw_result" not in candidate
    assert "diagnostics" not in candidate
    # bin_details (a calculator-internal diagnostic key) must not leak.
    assert "bin_details" not in candidate
