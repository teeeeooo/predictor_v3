"""Raw applicability, input validation, and exact inference selection."""

from math import inf, nan

import pytest

from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from apps.predict.services.prediction_service import PredictionService
from tests.helpers.predict_target_applicability import (
    TARGET_MATRIX,
    build_stack,
    fill_case,
)


@pytest.mark.parametrize(("cooling", "heating", "expected"), TARGET_MATRIX)
def test_raw_capacity_presence_selects_exact_runtime_ordered_subset(
    cooling, heating, expected
):
    runtime, session, mapper, _result_mapper, _usecase, _model = build_stack()
    case = session.case_store.get_case(session.case_order[0])
    fill_case(case, cooling, heating)

    outcome = mapper.build_request(case)

    assert outcome.errors == ()
    assert outcome.request is not None
    assert tuple(item.ml_name for item in outcome.request.requested_targets) == expected
    assert runtime.active_targets == tuple(
        item.ml_name for item in runtime.target_descriptors
    )
    assert len(runtime.active_targets) == 5


@pytest.mark.parametrize("invalid", (0, -1, nan, inf, "not-a-number"))
def test_nonblank_invalid_capacity_is_not_silently_treated_as_absent(invalid):
    _runtime, session, mapper, _result_mapper, _usecase, _model = build_stack()
    case = session.case_store.get_case(session.case_order[0])
    fill_case(case, invalid, "")

    outcome = mapper.build_request(case)

    assert outcome.request is None
    assert outcome.errors
    assert any("cooling_capa" in item for item in outcome.errors)


def test_empty_row_is_invalid_but_ref_qty_artifact_requirements_can_authorize_case():
    runtime = compatibility_predict_runtime_snapshot()
    ref_target = next(
        item for item in runtime.target_registry_targets if item.ml_name == "Ref Qty"
    )
    service = PredictionService(runtime_snapshot=runtime)
    service._model_data = {  # noqa: SLF001 - bounded artifact-selected test seam
        "features": {"Ref Qty": list(ref_target.policy_ml_names)},
        "models": {},
    }
    _runtime, session, _mapper, result_mapper, usecase, model = build_stack(
        request_validator=service.validate_request
    )
    empty = session.case_order[0]
    ref_only = session.case_store.append_empty_rows(1)[0].case_id

    empty_plan = usecase.prepare_run([empty])
    assert empty_plan.job is None
    assert session.result_for_case(empty).status == "invalid"
    assert "냉방능력" not in session.result_for_case(empty).message

    ref_case = session.case_store.get_case(ref_only)
    fill_case(ref_case, "", "")
    missing_plan = usecase.prepare_run([ref_only])
    assert missing_plan.job is None
    assert session.result_for_case(ref_only).status == "invalid"

    for key, value in (
        ("id_volume", 1.1),
        ("evap_volume", 1.2),
        ("od_volume", 1.5),
        ("cond_volume", 1.6),
    ):
        session.set_autofill_value(ref_only, key, value)
    valid_plan = usecase.prepare_run([ref_only])
    assert valid_plan.job is not None
    request = valid_plan.job.requests[0]
    assert tuple(item.ml_name for item in request.requested_targets) == ("Ref Qty",)
    assert request.context is not None
    assert request.context.requested_target_identities == tuple(
        item.target_identity for item in request.requested_targets
    )
    assert model == usecase.execution_environment[1]
    assert result_mapper.active_targets == runtime.active_targets


@pytest.mark.parametrize(("cooling", "heating", "expected"), TARGET_MATRIX)
def test_service_inference_receives_exact_requested_subset(
    monkeypatch, cooling, heating, expected
):
    runtime, session, mapper, _result_mapper, _usecase, _model = build_stack()
    case = session.case_store.get_case(session.case_order[0])
    fill_case(case, cooling, heating)
    request = mapper.build_request(case).request
    assert request is not None
    captured = []

    def fake_predict_row(_model_data, _row_input, **kwargs):  # noqa: ANN001, ANN202
        captured.append(tuple(kwargs["targets"]))
        return {
            target: float(index + 1)
            for index, target in enumerate(kwargs["targets"])
        }

    monkeypatch.setattr(
        "apps.predict.services.prediction_service.predict_row", fake_predict_row
    )
    service = PredictionService(runtime_snapshot=runtime)
    service._model_data = {"features": {}, "models": {}}  # noqa: SLF001

    result = service.predict_one(request)

    assert result.status == "complete"
    assert captured == [expected]
    assert runtime.active_targets == tuple(
        item.ml_name for item in runtime.target_descriptors
    )
