import pytest

from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.adapters.ranking_adapter import build_ranking_candidate_envelope
from core.calculators.adapters.result_adapter import wrap_calculator_result_envelope


AHRI_SEER2_SAMPLE_POINTS = {
    "A_Full": (36000, 3000),
    "B_Full": (30000, 2200),
    "B_Low": (18000, 1200),
    "E_Int": (24000, 1700),
    "F_Low": (12000, 900),
}


def _result_envelope():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")
    raw_result = calculator.calculate_seer2(AHRI_SEER2_SAMPLE_POINTS)
    return wrap_calculator_result_envelope("ahri_usa_seer2", raw_result)


def test_ranking_envelope_shape_uses_first_slice_field_set():
    candidate = build_ranking_candidate_envelope("cand-001", _result_envelope())

    assert set(candidate.keys()) == {
        "candidate_id",
        "calculator_profile_id",
        "metric",
        "value",
        "units",
        "score",
        "ranking_features",
    }


def test_ranking_envelope_copies_identity_fields_from_result_envelope():
    result = _result_envelope()
    candidate = build_ranking_candidate_envelope("cand-001", result)

    assert candidate["candidate_id"] == "cand-001"
    assert candidate["calculator_profile_id"] == result["calculator_profile_id"]
    assert candidate["metric"] == result["metric"]
    assert candidate["units"] == result["units"]
    assert candidate["value"] == float(result["value"])


def test_ranking_envelope_defaults_score_to_metric_value():
    result = _result_envelope()
    candidate = build_ranking_candidate_envelope("cand-001", result)

    assert candidate["score"] == candidate["value"]


def test_ranking_envelope_accepts_score_override():
    result = _result_envelope()
    candidate = build_ranking_candidate_envelope(
        "cand-001", result, score=42.0
    )

    assert candidate["score"] == 42.0
    # value remains the original metric reading
    assert candidate["value"] != 42.0


def test_ranking_envelope_default_ranking_features_is_empty_dict():
    result = _result_envelope()
    candidate = build_ranking_candidate_envelope("cand-001", result)

    assert candidate["ranking_features"] == {}


def test_ranking_envelope_copies_ranking_features_through():
    result = _result_envelope()
    features = {"compressor_cost": 120.0, "weight_kg": 38}
    candidate = build_ranking_candidate_envelope(
        "cand-001", result, ranking_features=features
    )

    assert candidate["ranking_features"] == features
    # caller mutation should not leak into the envelope
    features["new"] = "value"
    assert "new" not in candidate["ranking_features"]


def test_ranking_envelope_does_not_expose_raw_result_or_diagnostics():
    """Ranking layer must consume envelope fields, not raw calculator output."""
    result = _result_envelope()
    candidate = build_ranking_candidate_envelope("cand-001", result)

    assert "raw_result" not in candidate
    assert "diagnostics" not in candidate


def test_ranking_envelope_rejects_empty_candidate_id():
    with pytest.raises(ValueError, match="candidate_id"):
        build_ranking_candidate_envelope("", _result_envelope())


def test_ranking_envelope_rejects_non_string_candidate_id():
    with pytest.raises(ValueError, match="candidate_id"):
        build_ranking_candidate_envelope(123, _result_envelope())  # type: ignore[arg-type]


def test_ranking_envelope_rejects_non_mapping_result_envelope():
    with pytest.raises(TypeError, match="result_envelope"):
        build_ranking_candidate_envelope("cand-001", ["not", "a", "dict"])  # type: ignore[arg-type]


def test_ranking_envelope_rejects_result_envelope_missing_required_keys():
    bad = {"calculator_profile_id": "ahri_usa_seer2", "metric": "SEER2"}
    with pytest.raises(KeyError, match="missing required keys"):
        build_ranking_candidate_envelope("cand-001", bad)


def test_ranking_envelope_rejects_non_mapping_ranking_features():
    with pytest.raises(TypeError, match="ranking_features"):
        build_ranking_candidate_envelope(
            "cand-001", _result_envelope(), ranking_features=["feature"]
        )
