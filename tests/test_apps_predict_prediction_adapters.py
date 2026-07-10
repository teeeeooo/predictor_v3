"""Predict row-to-ML and result adapter recovery tests."""

import pytest

from apps.predict.adapters.prediction_result_adapter import (
    PredictionResultAdapter,
    apply_prediction_result,
)
from apps.predict.adapters.row_to_ml_input_adapter import (
    RowToMlInputAdapter,
    build_prediction_input_request,
)
from apps.predict.application.models import PredictionServiceResult
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.case_row import CaseRow


def _case(**values) -> CaseRow:
    return CaseRow(case_id="case-0001", input_values=values)


def test_row_to_ml_adapter_uses_schema_ml_feature_metadata():
    case = _case(
        cooling_capa="3500",
        heating_capa="4000",
        ref_type="R32",
        exp_type="EEV",
    )
    case.autofill_values.update(
        {
            "id_volume": "1.1",
            "evap_area": "2.2",
            "evap_volume": "3.3",
            "od_volume": "4.4",
            "cond_area": "5.5",
            "cond_volume": "6.6",
            "comp_eer": "7.7",
            "comp_cc": "8.8",
        }
    )

    outcome = RowToMlInputAdapter().build_request(case)

    assert outcome.is_valid
    assert outcome.request is not None
    assert outcome.request.row_input["Cooling Capa"] == 3500.0
    assert outcome.request.row_input["Heating Capa"] == 4000.0
    assert outcome.request.row_input["ID Volume"] == 1.1
    assert outcome.request.row_input["Cond Volume"] == 6.6


def test_row_to_ml_adapter_one_hot_parity():
    outcome = build_prediction_input_request(
        _case(cooling_capa="3500", ref_type="R290", exp_type="Capi")
    )

    assert outcome.request is not None
    row_input = outcome.request.row_input
    assert row_input["R410A"] == 0.0
    assert row_input["R32"] == 0.0
    assert row_input["R290"] == 1.0
    assert row_input["EEV"] == 0.0
    assert row_input["Capi"] == 1.0
    assert [
        key for key in row_input if key in {"R410A", "R32", "R290", "EEV", "Capi"}
    ] == ["R410A", "R32", "R290", "EEV", "Capi"]


def test_row_to_ml_adapter_one_hot_unknown_selection_behavior_is_preserved():
    outcome = build_prediction_input_request(
        _case(cooling_capa="3500", ref_type="UnknownRef", exp_type="UnknownExp")
    )

    assert outcome.request is not None
    row_input = outcome.request.row_input
    assert row_input["R410A"] == 0.0
    assert row_input["R32"] == 0.0
    assert row_input["R290"] == 0.0
    assert row_input["EEV"] == 0.0
    assert row_input["Capi"] == 0.0
    assert outcome.warnings == (
        "Unsupported option ignored: UnknownRef",
        "Unsupported option ignored: UnknownExp",
    )


def test_row_to_ml_adapter_one_hot_groups_can_be_injected_for_tests():
    adapter = RowToMlInputAdapter(
        one_hot_groups={
            "refrigerant": ("R410A", "R32", "R290"),
            "expansion_device": ("EEV", "Capi"),
        }
    )

    outcome = adapter.build_request(
        _case(cooling_capa="3500", ref_type="R410A", exp_type="EEV")
    )

    assert outcome.request is not None
    assert outcome.request.row_input["R410A"] == 1.0
    assert outcome.request.row_input["EEV"] == 1.0


def test_row_to_ml_adapter_missing_one_hot_group_error_is_clear():
    with pytest.raises(
        ValueError,
        match="missing one-hot group 'expansion_device' in feature catalog",
    ):
        RowToMlInputAdapter(
            one_hot_groups={"refrigerant": ("R410A", "R32", "R290")}
        )


def test_row_to_ml_adapter_validation_errors_are_controlled():
    outcome = RowToMlInputAdapter().build_request(_case(cooling_capa="bad"))

    assert not outcome.is_valid
    assert "cooling_capa must be numeric." in outcome.errors


def test_prediction_result_adapter_maps_core_targets_to_result_keys():
    result = PredictionServiceResult(
        case_id="case-0001",
        status="complete",
        predictions={
            "Cooling Power": 1200.0,
            "Heating Power": 1300.5,
            "Ref Qty": 1.23456,
            "Cooling Hz": 58.0,
            "Heating Hz": 59.0,
        },
    )

    row = apply_prediction_result(result)

    assert row.status == "complete"
    assert row.result_values["cooling_power"] == "1200"
    assert row.result_values["heating_power"] == "1300.5"
    assert row.result_values["ref_qty"] == "1.2346"


def test_prediction_result_adapter_handles_missing_targets_as_partial():
    row = PredictionResultAdapter().from_service_result(
        PredictionServiceResult(
            case_id="case-0001",
            status="complete",
            predictions={"Cooling Power": 1200.0},
        )
    )

    assert row.status == "partial"
    assert "Missing prediction target" in row.message


def test_prediction_service_model_missing_is_graceful(tmp_path):
    service = PredictionService(model_file=str(tmp_path / "missing.pkl"))
    outcome = build_prediction_input_request(_case(cooling_capa="3500"))
    assert outcome.request is not None

    result = service.predict_one(outcome.request)

    assert result.status == "error"
    assert "모델 파일을 찾을 수 없습니다" in result.message
