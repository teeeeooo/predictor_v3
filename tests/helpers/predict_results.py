"""Test-owned canonical Predict result preparation."""

from __future__ import annotations

from itertools import count

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from apps.predict.application.result_enrichment import enrich_target_outcomes
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow


_RUNS = count(1)


def accept_result_fixtures(
    owner: PredictSession | object,
    *templates: ResultRow,
) -> tuple[ResultRow, ...]:
    """Create test results through the same canonical gate as production.

    ``owner`` may be a composition (preferred for generation tests) or a bare
    session. Templates select status/message and optional numeric values; they
    are never installed as canonical state themselves.
    """
    session = owner if isinstance(owner, PredictSession) else owner.session
    runtime = (
        compatibility_predict_runtime_snapshot()
        if isinstance(owner, PredictSession)
        else owner.runtime_snapshot
    )
    if isinstance(owner, PredictSession):
        semantics = execution_semantics_from_runtime(runtime)
        model = PredictionModelIdentity("test-candidate", 1, runtime.generation_id)
    else:
        semantics, model = owner.prediction_controller.execution_environment

    accepted = []
    for template in templates:
        if template.status in {"pending", "running", "invalid"}:
            result = ResultRow(
                template.case_id, template.status, message=template.message
            )
            session.set_result(result)
            accepted.append(result)
            continue

        case = session.case_store.get_case(template.case_id)
        input_outcome = (
            owner.input_mapper.build_request(case)
            if not isinstance(owner, PredictSession)
            else None
        )
        capacity_inputs = (
            input_outcome.request.capacity_inputs
            if input_outcome is not None and input_outcome.request is not None
            else ()
        )
        context = PredictionExecutionContext(
            session.session_id,
            template.case_id,
            f"test-result-{next(_RUNS)}",
            case.input_revision,
            semantics,
            model,
            capacity_inputs,
        )
        outcomes = _outcomes_for_template(template, runtime.target_descriptors)
        result = ResultRow(
            template.case_id,
            template.status,
            message=template.message,
            target_outcomes=outcomes,
            derived_metrics=(
                enrich_target_outcomes(context.capacity_inputs, outcomes)
                if outcomes else ()
            ),
            execution_context=context,
        )
        session.allow_result(context, runtime.target_descriptors)
        acceptance = session.accept_result(result, semantics, model)
        if not acceptance.accepted:
            raise AssertionError(
                f"invalid canonical test fixture: {acceptance.reason_code}"
            )
        accepted.append(result)
    return tuple(accepted)


def _outcomes_for_template(template, descriptors):  # noqa: ANN001
    if template.status in {"cancelled", "error"} and not template.result_values:
        return ()
    values = template.result_values
    outcomes = []
    for index, descriptor in enumerate(descriptors):
        raw = _numeric(values.get(descriptor.result_key))
        if template.status == "complete":
            status = "available"
            raw = raw if raw is not None else float(index + 1)
        elif template.status == "partial":
            status = "available" if raw is not None or index == 0 else "unavailable"
            raw = raw if raw is not None else (1.0 if index == 0 else None)
        elif template.status == "error":
            status = "failed"
            raw = None
        else:
            return ()
        outcomes.append(
            TargetOutcome(
                descriptor.target_identity,
                descriptor.result_feature_identity,
                descriptor.result_key,
                descriptor.canonical_unit,
                status,
                value_source=descriptor.value_source,
                raw_value=raw,
                reason_code="fixture_unavailable" if status != "available" else "",
                message="fixture target state" if status != "available" else "",
            )
        )
    return tuple(outcomes)


def _numeric(value):  # noqa: ANN001
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
