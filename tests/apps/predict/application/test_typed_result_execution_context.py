"""Typed Predict outcome, freshness, and deterministic stale-event gates."""

from dataclasses import replace

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.application.models import (
    PredictionInputOutcome,
    PredictionInputRequest,
    PredictionServiceResult,
)
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.application.result_contract import (
    PredictionExecutionSemantics,
    PredictionModelIdentity,
)
from apps.predict.application.runtime_snapshot import compatibility_predict_runtime_snapshot
from apps.predict.state.predict_session import PredictSession


class _InputMapper:
    def build_request(self, case):  # noqa: ANN001
        return PredictionInputOutcome(
            case.case_id,
            PredictionInputRequest(case.case_id, dict(case.input_values)),
        )


def _usecase(session: PredictSession):
    runtime = compatibility_predict_runtime_snapshot()
    semantics = PredictionExecutionSemantics(
        runtime.generation_id,
        runtime.ordered_ml_fingerprint,
        runtime.preprocessing_fingerprint,
        runtime.derived_fingerprint,
        runtime.one_hot_fingerprint,
        runtime.target_registry_fingerprint,
    )
    model = PredictionModelIdentity("candidate-a", 7, runtime.generation_id)
    return PredictionUseCase(
        session,
        _InputMapper(),
        PredictionResultAdapter(target_descriptors=runtime.target_descriptors),
        semantics,
        model,
    )


def _service_result(request, values):  # noqa: ANN001
    return PredictionServiceResult(
        request.case_id,
        "complete",
        values,
        context=request.context,
    )


def test_target_outcomes_keep_raw_precision_and_aggregate_mixed_states():
    session = PredictSession(session_id="session-a")
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    plan = usecase.prepare_run([case.case_id])
    request = plan.job.requests[0]
    runtime = compatibility_predict_runtime_snapshot()
    values = {
        runtime.target_descriptors[0].ml_name: 1.234567890123,
        runtime.target_descriptors[1].ml_name: float("nan"),
        runtime.target_descriptors[2].ml_name: "not-numeric",
    }

    assert usecase.apply_service_result(_service_result(request, values))
    result = session.result_for_case(case.case_id)

    assert result.status == "partial"
    assert [item.status for item in result.target_outcomes] == [
        "available", "failed", "failed", "unavailable", "unavailable"
    ]
    available = result.target_outcomes[0]
    assert available.raw_value == 1.234567890123
    assert available.canonical_unit == "W"
    assert available.target_identity == runtime.target_descriptors[0].target_identity
    assert available.result_feature_identity == runtime.target_descriptors[0].result_feature_identity
    assert result.result_values[available.result_key] == "1.2346"
    assert result.target_outcomes[1].reason_code == "non_finite_output"
    assert result.target_outcomes[2].reason_code == "invalid_numeric_output"
    assert result.target_outcomes[3].reason_code == "missing_service_output"


def test_no_available_target_is_row_error_without_fake_numeric_values():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]

    assert usecase.apply_service_result(_service_result(request, {}))
    result = session.result_for_case(case.case_id)

    assert result.status == "error"
    assert result.result_values == {}
    assert all(item.status == "unavailable" for item in result.target_outcomes)


def test_same_case_edit_rejects_old_result_but_other_case_edit_does_not():
    session = PredictSession(session_id="session-a")
    first, second = session.case_store.append_empty_rows(2)
    usecase = _usecase(session)
    plan = usecase.prepare_run([first.case_id, second.case_id])
    first_request, second_request = plan.job.requests
    values = {
        item.ml_name: index + 0.125
        for index, item in enumerate(compatibility_predict_runtime_snapshot().target_descriptors)
    }

    first.set_input_value("cooling_capa", 3500)
    assert session.result_for_case(first.case_id).status == "pending"
    assert not usecase.apply_service_result(_service_result(first_request, values))

    first.set_input_value("cooling_capa", 3600)
    assert usecase.apply_service_result(_service_result(second_request, values))
    assert session.result_for_case(second.case_id).status == "complete"
    assert session.acceptance_diagnostics[-1].reason_code == "input_revision_changed"


def test_superseded_terminal_removed_and_other_session_results_fail_closed():
    session = PredictSession(session_id="session-a")
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    old = usecase.prepare_run([case.case_id]).job.requests[0]
    new = usecase.prepare_run([case.case_id]).job.requests[0]
    values = {
        item.ml_name: 1.0
        for item in compatibility_predict_runtime_snapshot().target_descriptors
    }

    assert not usecase.apply_service_result(_service_result(old, values))
    assert session.acceptance_diagnostics[-1].reason_code == "run_superseded"
    assert usecase.apply_service_result(_service_result(new, values))
    accepted = session.result_for_case(case.case_id)
    late_values = {key: 999.0 for key in values}
    assert not usecase.apply_service_result(_service_result(new, late_values))
    assert session.result_for_case(case.case_id) == accepted
    assert session.acceptance_diagnostics[-1].reason_code == "run_not_active"

    other_session = replace(old.context, session_id="session-b")
    assert not usecase.apply_service_result(replace(_service_result(old, values), context=other_session))
    session.case_store.remove_rows([case.case_id])
    assert not usecase.apply_service_result(_service_result(old, values))
    assert session.acceptance_diagnostics[-1].reason_code == "case_removed"


def test_currentness_ignores_generation_id_but_stales_on_semantics_or_model():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    values = {
        item.ml_name: 9.87654321
        for item in compatibility_predict_runtime_snapshot().target_descriptors
    }
    usecase.apply_service_result(_service_result(request, values))
    result = session.result_for_case(case.case_id)
    semantics, model = usecase.execution_environment

    presentation_only = replace(semantics, runtime_generation_id="presentation-b")
    session.reconcile_result_currentness(presentation_only, model)
    assert session.result_for_case(case.case_id).freshness == "current"

    session.reconcile_result_currentness(semantics, replace(model, active_revision=8))
    stale = session.result_for_case(case.case_id)
    assert stale.freshness == "stale"
    assert stale.stale_reason == "loaded_model_changed"
    assert stale.target_outcomes == result.target_outcomes
    assert stale.execution_context == result.execution_context


def test_semantic_change_preserves_typed_data_and_marks_stale():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    values = {
        item.ml_name: 5.0
        for item in compatibility_predict_runtime_snapshot().target_descriptors
    }
    usecase.apply_service_result(_service_result(request, values))
    original = session.result_for_case(case.case_id)
    semantics, model = usecase.execution_environment

    session.reconcile_result_currentness(
        replace(semantics, preprocessing_fingerprint="changed"), model
    )
    stale = session.result_for_case(case.case_id)

    assert stale.freshness == "stale"
    assert stale.stale_reason == "execution_semantics_changed"
    assert stale.target_outcomes == original.target_outcomes
    assert stale.status == "complete"


def test_event_with_changed_semantics_or_model_is_rejected_without_mutation():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    values = {
        item.ml_name: 3.0
        for item in compatibility_predict_runtime_snapshot().target_descriptors
    }
    original = session.result_for_case(case.case_id)
    changed_semantics = replace(
        request.context,
        semantics=replace(request.context.semantics, one_hot_fingerprint="changed"),
    )

    assert not usecase.apply_service_result(
        replace(_service_result(request, values), context=changed_semantics)
    )
    assert session.result_for_case(case.case_id) == original
    assert session.acceptance_diagnostics[-1].reason_code == "execution_semantics_changed"

    changed_model = replace(
        request.context,
        model=replace(request.context.model, candidate_id="candidate-b"),
    )
    assert not usecase.apply_service_result(
        replace(_service_result(request, values), context=changed_model)
    )
    assert session.result_for_case(case.case_id) == original
    assert session.acceptance_diagnostics[-1].reason_code == "loaded_model_changed"


def test_input_edit_rejects_context_preserving_infrastructure_error():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    case.set_input_value("cooling_capa", 3600)

    usecase.apply_infrastructure_failure(
        (case.case_id,), "worker failed", run_id=request.context.run_id
    )

    assert session.result_for_case(case.case_id).status == "pending"
    assert session.acceptance_diagnostics[-1].reason_code == "input_revision_changed"


def test_semantic_change_rejects_context_preserving_infrastructure_error():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    usecase = _usecase(session)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    semantics, model = usecase.execution_environment
    usecase.update_execution_environment(
        replace(semantics, derived_fingerprint="changed"), model
    )

    usecase.apply_infrastructure_failure(
        (case.case_id,), "worker failed", run_id=request.context.run_id
    )

    assert session.result_for_case(case.case_id).status == "running"
    assert session.acceptance_diagnostics[-1].reason_code == (
        "execution_semantics_changed"
    )
