"""Requested-set acceptance, migration, aggregation, and presentation."""

from dataclasses import replace

from apps.predict.application.models import PredictionServiceResult
from apps.predict.application.result_review.projection import ResultReviewProjection
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.state.result_row import ResultRow
from tests.helpers.predict_target_applicability import (
    TARGET_MATRIX,
    build_stack,
    fill_case,
    prediction_values,
)


def test_mixed_session_maps_only_requested_results_and_preserves_migration_evidence():
    runtime, session, _mapper, _result_mapper, usecase, model = build_stack(4)
    for case_id, (cooling, heating, _expected) in zip(
        session.case_order, TARGET_MATRIX, strict=True
    ):
        fill_case(session.case_store.get_case(case_id), cooling, heating)

    plan = usecase.prepare_run(list(session.case_order))
    assert plan.job is not None
    requested_by_case = {
        request.case_id: tuple(item.ml_name for item in request.requested_targets)
        for request in plan.job.requests
    }
    assert tuple(requested_by_case.values()) == tuple(item[2] for item in TARGET_MATRIX)

    for request in plan.job.requests:
        assert usecase.apply_service_result(PredictionServiceResult(
            request.case_id,
            "complete",
            prediction_values(request),
            context=request.context,
        ))
        row = session.result_for_case(request.case_id)
        assert row.status == "complete"
        assert len(row.target_outcomes) == len(request.requested_targets)
    assert tuple(
        len(session.result_for_case(request.case_id).derived_metrics)
        for request in plan.job.requests
    ) == (2, 1, 1, 0)

    revision = session.revision
    projection = session.prepare_runtime_projection(
        cases=tuple(
            (
                case_id,
                dict(case.input_values),
                dict(case.autofill_values),
                set(case.dirty_fields),
                case.input_revision,
            )
            for case_id in session.case_order
            for case in (session.case_store.get_case(case_id),)
        ),
        results=tuple(session.results_by_case_id.values()),
        runtime_snapshot=runtime,
        model_identity=model,
    )
    session.apply_runtime_projection(projection, expected_revision=revision)
    assert tuple(
        session.result_for_case(case_id).execution_context.requested_target_identities
        for case_id in session.case_order
    ) == tuple(
        tuple(item.target_identity for item in request.requested_targets)
        for request in plan.job.requests
    )


def test_missing_requested_output_is_partial_or_error_without_opposite_mode_outcomes():
    _runtime, session, _mapper, _result_mapper, usecase, _model = build_stack(2)
    for case_id in session.case_order:
        fill_case(session.case_store.get_case(case_id), 3500, "")

    plan = usecase.prepare_run(list(session.case_order))
    assert plan.job is not None
    partial_request, error_request = plan.job.requests
    assert usecase.apply_service_result(PredictionServiceResult(
        partial_request.case_id,
        "complete",
        prediction_values(partial_request, omit=("Cooling Hz",)),
        context=partial_request.context,
    ))
    assert usecase.apply_service_result(PredictionServiceResult(
        error_request.case_id,
        "complete",
        {},
        context=error_request.context,
    ))

    partial = session.result_for_case(partial_request.case_id)
    error = session.result_for_case(error_request.case_id)
    assert partial.status == "partial"
    assert error.status == "error"
    assert {item.result_key for item in partial.target_outcomes} == {
        "cooling_power", "ref_qty", "cooling_hz"
    }
    assert tuple(
        item.reason_code
        for item in partial.target_outcomes
        if item.reason_code
    ) == ("missing_service_output",)


def test_forged_omitted_and_late_results_cannot_bypass_canonical_acceptance():
    _runtime, session, _mapper, result_mapper, usecase, model = build_stack(2)
    for case_id in session.case_order:
        fill_case(session.case_store.get_case(case_id), 3500, "")
    plan = usecase.prepare_run(list(session.case_order))
    assert plan.job is not None
    forged_request, late_request = plan.job.requests
    assert forged_request.context is not None
    forged_context = replace(
        forged_request.context,
        requested_target_identities=(
            forged_request.context.requested_target_identities[:-1]
        ),
    )
    forged = result_mapper.from_service_result(PredictionServiceResult(
        forged_request.case_id,
        "complete",
        prediction_values(forged_request),
        context=forged_context,
    ))
    assert not session.accept_result(
        forged, usecase.execution_environment[0], model
    ).accepted
    assert session.acceptance_diagnostics[-1].reason_code == (
        "requested_target_contract_changed"
    )

    canonical = result_mapper.from_service_result(PredictionServiceResult(
        forged_request.case_id,
        "complete",
        prediction_values(forged_request),
        context=forged_request.context,
    ))
    reordered = ResultRow(
        canonical.case_id,
        canonical.status,
        message=canonical.message,
        target_outcomes=canonical.target_outcomes,
        derived_metrics=canonical.derived_metrics,
        execution_context=replace(
            forged_request.context,
            requested_target_identities=tuple(
                reversed(forged_request.context.requested_target_identities)
            ),
        ),
    )
    assert not session.accept_result(
        reordered, usecase.execution_environment[0], model
    ).accepted
    assert session.acceptance_diagnostics[-1].reason_code == (
        "requested_target_contract_changed"
    )

    only = forged_request.requested_targets[0]
    omitted = ResultRow(
        forged_request.case_id,
        "complete",
        target_outcomes=(TargetOutcome(
            only.target_identity,
            only.result_feature_identity,
            only.result_key,
            only.canonical_unit,
            "available",
            value_source=only.value_source,
            raw_value=10.0,
        ),),
        execution_context=forged_request.context,
    )
    assert not session.accept_result(
        omitted, usecase.execution_environment[0], model
    ).accepted
    assert session.acceptance_diagnostics[-1].reason_code == "missing_expected_target"

    session.case_store.update_cell_value(late_request.case_id, "cooling_capa", 3600)
    assert not usecase.apply_service_result(PredictionServiceResult(
        late_request.case_id,
        "complete",
        prediction_values(late_request),
        context=late_request.context,
    ))
    assert session.acceptance_diagnostics[-1].reason_code == "input_revision_changed"


def test_ref_qty_only_result_review_and_clipboard_keep_mode_outputs_na():
    runtime, session, _mapper, _result_mapper, usecase, _model = build_stack()
    case = session.case_store.get_case(session.case_order[0])
    fill_case(case, "", "")
    plan = usecase.prepare_run([case.case_id])
    assert plan.job is not None
    request = plan.job.requests[0]
    assert usecase.apply_service_result(PredictionServiceResult(
        case.case_id,
        "complete",
        {"Ref Qty": 1.25},
        context=request.context,
    ))

    projection = ResultReviewProjection(session, runtime.column_descriptors)
    row = projection.rows()[0]
    assert row.status == "complete"
    assert row.eer is None and row.cop is None
    assert row.cooling_frequency is None and row.heating_frequency is None
    assert row.refrigerant_quantity is not None
    assert row.issues == ()
    grid_row = projection.clipboard_document((case.case_id,)).grid()[1]
    assert grid_row[5:9] == ("", "", "", "")
    assert grid_row[9] == 1.25
