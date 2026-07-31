"""Regressions for PR #44 canonical result acceptance repair."""

from dataclasses import replace

import pytest

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.application.models import PredictionInputOutcome, PredictionInputRequest
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.application.result_contract import (
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import compatibility_predict_runtime_snapshot
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow


class _InputMapper:
    def build_request(self, case):  # noqa: ANN001
        return PredictionInputOutcome(
            case.case_id,
            PredictionInputRequest(case.case_id, dict(case.input_values)),
        )


def _prepared():  # noqa: ANN202
    runtime = compatibility_predict_runtime_snapshot()
    session = PredictSession(session_id="canonical-repair")
    case = session.case_store.append_empty_rows(1)[0]
    usecase = PredictionUseCase(
        session,
        _InputMapper(),
        PredictionResultAdapter(target_descriptors=runtime.target_descriptors),
        execution_semantics_from_runtime(runtime),
        PredictionModelIdentity("candidate-a", 1, runtime.generation_id),
    )
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    return session, case, usecase, request, runtime.target_descriptors


def _outcome(descriptor, status="available"):  # noqa: ANN001, ANN202
    return TargetOutcome(
        descriptor.target_identity,
        descriptor.result_feature_identity,
        descriptor.result_key,
        descriptor.canonical_unit,
        status,
        value_source=descriptor.value_source,
        raw_value=1.234567890123 if status == "available" else None,
        reason_code="not_provided" if status != "available" else "",
        message="Expected output was not provided." if status != "available" else "",
    )


def _accept(session, usecase, result):  # noqa: ANN001, ANN202
    semantics, model = usecase.execution_environment
    return session.accept_result(result, semantics, model)


@pytest.mark.parametrize(
    ("mutate", "reason"),
    (
        (lambda items, descriptors: tuple(items[:1]), "missing_expected_target"),
        (
            lambda items, descriptors: (_outcome(descriptors[0], "unavailable"),),
            "missing_expected_target",
        ),
        (
            lambda items, descriptors: (
                replace(items[0], target_identity="unknown-target"), *items[1:]
            ),
            "unknown_target_identity",
        ),
        (
            lambda items, descriptors: (items[0], items[0], *items[1:]),
            "duplicate_target_identity",
        ),
        (
            lambda items, descriptors: (
                replace(items[0], result_feature_identity="wrong-feature"), *items[1:]
            ),
            "result_feature_identity_mismatch",
        ),
        (
            lambda items, descriptors: (
                replace(items[0], result_key="wrong_key"), *items[1:]
            ),
            "result_key_mismatch",
        ),
        (
            lambda items, descriptors: (
                replace(items[0], canonical_unit="wrong-unit"), *items[1:]
            ),
            "canonical_unit_mismatch",
        ),
        (
            lambda items, descriptors: (
                replace(items[0], value_source="wrong-source"), *items[1:]
            ),
            "value_source_mismatch",
        ),
    ),
)
def test_canonical_gate_rejects_malformed_expected_target_projection(mutate, reason):
    session, case, usecase, request, descriptors = _prepared()
    before = session.result_for_case(case.case_id)
    outcomes = tuple(_outcome(item) for item in descriptors)
    malformed = ResultRow(
        case.case_id,
        "complete",
        target_outcomes=mutate(outcomes, descriptors),
        execution_context=request.context,
    )

    acceptance = _accept(session, usecase, malformed)

    assert not acceptance.accepted
    assert acceptance.reason_code == reason
    assert session.result_for_case(case.case_id) == before
    assert session.acceptance_diagnostics[-1] == acceptance


def test_complete_with_unavailable_target_is_rejected_by_aggregate_gate():
    session, case, usecase, request, descriptors = _prepared()
    outcomes = tuple(_outcome(item) for item in descriptors)
    malformed = ResultRow(
        case.case_id,
        "complete",
        target_outcomes=(
            _outcome(descriptors[0], "unavailable"), *outcomes[1:]
        ),
        execution_context=request.context,
    )

    acceptance = _accept(session, usecase, malformed)

    assert not acceptance.accepted
    assert acceptance.reason_code == "aggregate_status_mismatch"
    assert session.result_for_case(case.case_id).status == "running"


@pytest.mark.parametrize(
    ("status", "outcome_statuses"),
    (
        ("complete", ("available",) * 5),
        ("partial", ("available", "unavailable", "available", "failed", "available")),
        ("error", ("unavailable", "failed", "unavailable", "failed", "unavailable")),
    ),
)
def test_canonical_gate_accepts_valid_target_aggregate(status, outcome_statuses):
    session, case, usecase, request, descriptors = _prepared()
    result = ResultRow(
        case.case_id,
        status,
        target_outcomes=tuple(
            _outcome(descriptor, outcome_status)
            for descriptor, outcome_status in zip(
                descriptors, outcome_statuses, strict=True
            )
        ),
        execution_context=request.context,
    )

    assert _accept(session, usecase, result).accepted
    assert session.result_for_case(case.case_id) == result


def test_row_wide_error_requires_detail_and_uses_canonical_acceptance():
    session, case, usecase, request, _descriptors = _prepared()
    missing_detail = ResultRow(
        case.case_id, "error", execution_context=request.context
    )
    assert _accept(session, usecase, missing_detail).reason_code == (
        "row_wide_error_detail_missing"
    )

    result = ResultRow(
        case.case_id,
        "error",
        message="Bounded infrastructure failure.",
        execution_context=request.context,
    )
    assert _accept(session, usecase, result).accepted


@pytest.mark.parametrize("status", ("pending", "running", "invalid"))
def test_non_executed_status_cannot_pose_as_an_accepted_terminal(status):
    session, case, usecase, request, _descriptors = _prepared()
    result = ResultRow(
        case.case_id,
        status,
        message="not an executed terminal",
        execution_context=request.context,
    )

    acceptance = _accept(session, usecase, result)

    assert not acceptance.accepted
    assert acceptance.reason_code == "non_terminal_execution_status"


def test_cancelled_terminal_without_synthetic_targets_is_accepted():
    session, case, usecase, request, _descriptors = _prepared()
    result = ResultRow(
        case.case_id,
        "cancelled",
        message="Prediction cancelled.",
        execution_context=request.context,
    )

    assert _accept(session, usecase, result).accepted
    assert session.result_for_case(case.case_id).target_outcomes == ()


def test_executed_result_cannot_bypass_canonical_acceptance_with_set_result():
    session, case, _usecase, request, descriptors = _prepared()
    result = ResultRow(
        case.case_id,
        "complete",
        target_outcomes=tuple(_outcome(item) for item in descriptors),
        execution_context=request.context,
    )

    with pytest.raises(ValueError, match="canonical acceptance"):
        session.set_result(result)


def test_malformed_result_preserves_existing_accepted_result_and_only_adds_diagnostic():
    session, case, usecase, request, descriptors = _prepared()
    accepted = ResultRow(
        case.case_id,
        "complete",
        target_outcomes=tuple(_outcome(item) for item in descriptors),
        execution_context=request.context,
    )
    assert _accept(session, usecase, accepted).accepted
    next_context = replace(request.context, run_id="next-run")
    session.allow_result(next_context, descriptors)
    before_diagnostics = session.acceptance_diagnostics
    malformed = ResultRow(
        case.case_id,
        "complete",
        target_outcomes=(_outcome(descriptors[0]),),
        execution_context=next_context,
    )

    assert not _accept(session, usecase, malformed).accepted
    assert session.result_for_case(case.case_id) == accepted
    assert session.acceptance_diagnostics[:-1] == before_diagnostics
    assert session.acceptance_diagnostics[-1].reason_code == "missing_expected_target"
