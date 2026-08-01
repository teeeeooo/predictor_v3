"""Qt-free Predict EER/COP enrichment and canonical lifecycle regressions."""

from dataclasses import replace
from math import isfinite

import pytest

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.models import PredictionServiceResult
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.application.result_contract import (
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.result_enrichment import (
    CAPACITY_UNIT,
    COOLING_CAPACITY_FEATURE_ID,
    COOLING_POWER_FEATURE_ID,
    COOLING_POWER_TARGET_ID,
    EFFICIENCY_UNIT,
    HEATING_CAPACITY_FEATURE_ID,
    HEATING_POWER_FEATURE_ID,
    HEATING_POWER_TARGET_ID,
    DerivedMetricOutcome,
    ExecutionInputEvidence,
    enrich_target_outcomes,
)
from apps.predict.application.runtime_snapshot import (
    build_predict_runtime_snapshot,
    compatibility_predict_runtime_snapshot,
)
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.schema.column_schema_adapter import (
    build_predict_column_schema,
    build_result_column_schema,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from core.data_definition.contract import bootstrap_manifest
from tests.helpers.generation_authority import repository_issued_generation


def _capacity(identity, value, *, unit=CAPACITY_UNIT, key="capacity", ml_name="Capacity"):
    return ExecutionInputEvidence(identity, key, ml_name, unit, value)


def _power(
    target_identity,
    feature_identity,
    value=1000.0,
    *,
    status="available",
    unit="W",
    source="model_prediction",
):
    return TargetOutcome(
        target_identity,
        feature_identity,
        "power",
        unit,
        status,
        value_source=source,
        raw_value=value if status == "available" else None,
        reason_code="power_evidence" if status != "available" else "",
        message="Power evidence is unavailable." if status != "available" else "",
    )


def _metric_by_key(metrics):  # noqa: ANN001, ANN202
    return {item.metric_key: item for item in metrics}


def test_exact_eer_and_cop_preserve_raw_python_precision_and_provenance():
    cooling = _capacity(COOLING_CAPACITY_FEATURE_ID, 3500.123456789)
    heating = _capacity(HEATING_CAPACITY_FEATURE_ID, 4200.987654321)
    metrics = _metric_by_key(enrich_target_outcomes(
        (cooling, heating),
        (
            _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, 1234.56789),
            _power(HEATING_POWER_TARGET_ID, HEATING_POWER_FEATURE_ID, 987.654321),
        ),
    ))

    assert metrics["eer"].raw_value == 3500.123456789 / 1234.56789
    assert metrics["cop"].raw_value == 4200.987654321 / 987.654321
    assert metrics["eer"].capacity_input is cooling
    assert metrics["cop"].capacity_input is heating
    assert metrics["eer"].semantic_unit == metrics["cop"].semantic_unit == EFFICIENCY_UNIT


def test_cooling_and_heating_availability_is_independent():
    metrics = _metric_by_key(enrich_target_outcomes(
        (
            _capacity(COOLING_CAPACITY_FEATURE_ID, 3500),
            _capacity(HEATING_CAPACITY_FEATURE_ID, 4200),
        ),
        (
            _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, 1000),
            _power(
                HEATING_POWER_TARGET_ID,
                HEATING_POWER_FEATURE_ID,
                status="unavailable",
            ),
        ),
    ))

    assert metrics["eer"].status == "available"
    assert metrics["eer"].raw_value == 3.5
    assert metrics["cop"].status == "unavailable"
    assert metrics["cop"].reason_code == "power_unavailable"


@pytest.mark.parametrize(
    ("status", "reason"),
    (("unavailable", "power_unavailable"), ("failed", "power_failed")),
)
def test_unavailable_or_failed_power_has_no_numeric_metric(status, reason):
    metric = enrich_target_outcomes(
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500),),
        (_power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, status=status),),
    )[0]

    assert metric.status == "unavailable"
    assert metric.raw_value is None
    assert metric.reason_code == reason


@pytest.mark.parametrize(
    ("value", "reason"),
    (
        (0, "power_non_positive"),
        (-1, "power_non_positive"),
    ),
)
def test_invalid_power_denominator_never_produces_numeric_output(value, reason):
    metric = enrich_target_outcomes(
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500),),
        (_power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, value),),
    )[0]

    assert metric.status == "unavailable"
    assert metric.raw_value is None
    assert metric.reason_code == reason


@pytest.mark.parametrize("value", (float("inf"), float("nan")))
def test_non_finite_power_is_rejected_by_typed_target_owner(value):
    with pytest.raises(ValueError, match="finite value"):
        _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, value)


@pytest.mark.parametrize(
    ("inputs", "reason"),
    (
        ((), "capacity_source_missing"),
        ((_capacity(COOLING_CAPACITY_FEATURE_ID, "bad"),), "capacity_not_numeric"),
        ((_capacity(COOLING_CAPACITY_FEATURE_ID, float("inf")),), "capacity_non_finite"),
        ((_capacity(COOLING_CAPACITY_FEATURE_ID, float("nan")),), "capacity_non_finite"),
        ((_capacity(COOLING_CAPACITY_FEATURE_ID, 0),), "capacity_non_positive"),
        ((_capacity(COOLING_CAPACITY_FEATURE_ID, -1),), "capacity_non_positive"),
    ),
)
def test_invalid_or_missing_capacity_numerator_never_produces_numeric_output(inputs, reason):
    metric = enrich_target_outcomes(
        inputs,
        (_power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID),),
    )[0]

    assert metric.status == "unavailable"
    assert metric.raw_value is None
    assert metric.reason_code == reason


def test_non_finite_division_result_is_rejected():
    metric = enrich_target_outcomes(
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 1e308),),
        (_power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, 5e-324),),
    )[0]

    assert metric.status == "unavailable"
    assert metric.reason_code == "division_non_finite"
    assert metric.raw_value is None


@pytest.mark.parametrize(
    ("capacity", "power", "reason"),
    (
        (_capacity("wrong-capacity", 3500), _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID), "capacity_source_missing"),
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500, unit="kW"), _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID), "capacity_unit_mismatch"),
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500), _power(COOLING_POWER_TARGET_ID, "wrong-feature"), "power_result_feature_mismatch"),
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500), _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, unit="kW"), "power_unit_mismatch"),
        (_capacity(COOLING_CAPACITY_FEATURE_ID, 3500), _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, source="forged"), "power_value_source_mismatch"),
    ),
)
def test_wrong_source_identity_unit_or_owner_fails_closed(capacity, power, reason):
    metric = enrich_target_outcomes((capacity,), (power,))[0]

    assert metric.status == "unavailable"
    assert metric.reason_code == reason
    assert metric.raw_value is None


def _usecase(rows=1):
    runtime = compatibility_predict_runtime_snapshot()
    session = PredictSession(session_id="enrichment-session")
    cases = session.case_store.append_empty_rows(rows)
    columns = build_predict_column_schema(runtime.column_descriptors)
    input_columns = tuple(item for item in columns if item.group in {"input", "auto"})
    mapper = RowToMlInputAdapter(
        columns=input_columns,
        one_hot_snapshot=runtime.one_hot,
    )
    result_mapper = PredictionResultAdapter(
        build_result_column_schema(runtime.column_descriptors),
        input_columns=input_columns,
        active_targets=runtime.active_targets,
        target_result_keys=runtime.target_result_keys,
        target_descriptors=runtime.target_descriptors,
        generation_id=runtime.generation_id,
    )
    usecase = PredictionUseCase(
        session,
        mapper,
        result_mapper,
        execution_semantics_from_runtime(runtime),
        PredictionModelIdentity("candidate", 1, runtime.generation_id),
    )
    return runtime, session, cases, usecase


def _set_capacities(case, cooling, heating):  # noqa: ANN001
    case.set_input_value("cooling_capa", cooling)
    case.set_input_value("heating_capa", heating)


def _service_result(runtime, context, *, cooling_power=1000.0, heating_power=1200.0, missing=()):  # noqa: ANN001
    values = {item.ml_name: float(index + 1) for index, item in enumerate(runtime.target_descriptors)}
    values[runtime.target_descriptors[0].ml_name] = cooling_power
    values[runtime.target_descriptors[1].ml_name] = heating_power
    for name in missing:
        values.pop(name, None)
    return PredictionServiceResult(context.case_id, "complete", values, context=context)


def _execute(runtime, session, usecase, case):  # noqa: ANN001
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    assert usecase.apply_service_result(_service_result(runtime, request.context))
    return session.result_for_case(case.case_id)


def test_partial_target_success_keeps_aggregate_partial_while_eer_is_available():
    runtime, session, (case,), usecase = _usecase()
    _set_capacities(case, 3500, 4200)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    result = _service_result(
        runtime,
        request.context,
        missing=(runtime.target_descriptors[1].ml_name,),
    )

    assert usecase.apply_service_result(result)
    accepted = session.result_for_case(case.case_id)
    metrics = _metric_by_key(accepted.derived_metrics)
    assert accepted.status == "partial"
    assert metrics["eer"].status == "available"
    assert metrics["cop"].reason_code == "power_unavailable"


def test_same_case_edit_preserves_original_metric_evidence_as_stale_and_new_success_replaces_it():
    runtime, session, (case,), usecase = _usecase()
    _set_capacities(case, 3500.123456, 4200.654321)
    original = _execute(runtime, session, usecase, case)
    original_metrics = original.derived_metrics

    case.set_input_value("cooling_capa", 7000)
    stale = session.result_for_case(case.case_id)

    assert stale.freshness == "stale"
    assert stale.stale_reason == "input_changed"
    assert stale.derived_metrics == original_metrics
    assert _metric_by_key(stale.derived_metrics)["eer"].capacity_input.raw_value == 3500.123456

    replacement = _execute(runtime, session, usecase, case)
    assert replacement.freshness == "current"
    assert replacement.derived_metrics != original_metrics
    assert _metric_by_key(replacement.derived_metrics)["eer"].capacity_input.raw_value == 7000.0


def test_edit_after_prepare_rejects_old_power_without_attaching_enrichment():
    runtime, session, (case,), usecase = _usecase()
    _set_capacities(case, 3500, 4200)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    case.set_input_value("cooling_capa", 9000)

    assert not usecase.apply_service_result(_service_result(runtime, request.context))
    assert session.result_for_case(case.case_id).derived_metrics == ()


def test_unrelated_case_edit_does_not_change_other_case_metric():
    runtime, session, cases, usecase = _usecase(rows=2)
    for index, case in enumerate(cases, start=1):
        _set_capacities(case, 3000 + index, 4000 + index)
        _execute(runtime, session, usecase, case)
    second_before = session.result_for_case(cases[1].case_id)

    cases[0].set_input_value("cooling_capa", 9999)

    assert session.result_for_case(cases[0].case_id).freshness == "stale"
    assert session.result_for_case(cases[1].case_id) == second_before


def test_allowed_execution_rejects_forged_capacity_context():
    runtime, session, (case,), usecase = _usecase()
    _set_capacities(case, 3500, 4200)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    forged = replace(
        request.context,
        capacity_inputs=(
            _capacity(COOLING_CAPACITY_FEATURE_ID, 999999),
            _capacity(HEATING_CAPACITY_FEATURE_ID, 4200),
        ),
    )

    assert not usecase.apply_service_result(_service_result(runtime, forged))
    assert session.acceptance_diagnostics[-1].reason_code == "execution_input_changed"
    assert session.result_for_case(case.case_id).derived_metrics == ()


def test_canonical_acceptance_rejects_fabricated_metric_attachment():
    runtime, session, (case,), usecase = _usecase()
    _set_capacities(case, 3500, 4200)
    request = usecase.prepare_run([case.case_id]).job.requests[0]
    mapper = PredictionResultAdapter(
        build_result_column_schema(runtime.column_descriptors),
        input_columns=tuple(
            item
            for item in build_predict_column_schema(runtime.column_descriptors)
            if item.group in {"input", "auto"}
        ),
        active_targets=runtime.active_targets,
        target_result_keys=runtime.target_result_keys,
        target_descriptors=runtime.target_descriptors,
        generation_id=runtime.generation_id,
    )
    canonical = mapper.from_service_result(_service_result(runtime, request.context))
    fabricated = replace(
        canonical.derived_metrics[0],
        raw_value=999999.0,
    )
    forged = ResultRow(
        canonical.case_id,
        canonical.status,
        None,
        canonical.message,
        target_outcomes=canonical.target_outcomes,
        derived_metrics=(fabricated, *canonical.derived_metrics[1:]),
        execution_context=canonical.execution_context,
    )

    acceptance = session.accept_result(
        forged,
        *usecase.execution_environment,
    )

    assert not acceptance.accepted
    assert acceptance.reason_code == "derived_metric_mismatch"
    assert session.result_for_case(case.case_id).derived_metrics == ()


def test_direct_non_executed_state_cannot_inject_metric_evidence():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    fabricated = DerivedMetricOutcome(
        "eer",
        "available",
        COOLING_CAPACITY_FEATURE_ID,
        COOLING_POWER_TARGET_ID,
        raw_value=3.5,
        capacity_input=_capacity(COOLING_CAPACITY_FEATURE_ID, 3500),
    )

    with pytest.raises(ValueError, match="canonical acceptance"):
        session.set_result(
            ResultRow(case.case_id, "pending", derived_metrics=(fabricated,))
        )


def test_capacity_evidence_uses_stable_identity_across_key_label_and_ml_name_change():
    manifest = bootstrap_manifest()
    manifest = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="capacity-presentation"),
        features=tuple(
            replace(
                item,
                column_key="cooling_capacity_presented",
                label="Cooling Capacity Presented",
                ml_name="Cooling Capacity Presented",
                zero_fill_policy="disallow",
            )
            if item.identity == COOLING_CAPACITY_FEATURE_ID else item
            for item in manifest.features
        ),
    )
    runtime = build_predict_runtime_snapshot(repository_issued_generation(manifest))
    columns = tuple(
        item for item in build_predict_column_schema(runtime.column_descriptors)
        if item.group in {"input", "auto"}
    )
    mapper = RowToMlInputAdapter(columns=columns, one_hot_snapshot=runtime.one_hot)
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    case.set_input_value("cooling_capacity_presented", 3555.25)
    outcome = mapper.build_request(case)

    assert outcome.request is not None
    evidence = next(
        item for item in outcome.request.capacity_inputs
        if item.feature_identity == COOLING_CAPACITY_FEATURE_ID
    )
    assert evidence.source_key == "cooling_capacity_presented"
    assert evidence.ml_name == "Cooling Capacity Presented"
    assert evidence.raw_value == 3555.25
    assert evidence.semantic_unit == "W"


def test_available_metrics_are_always_finite_and_never_nan_or_infinity():
    metrics = enrich_target_outcomes(
        (
            _capacity(COOLING_CAPACITY_FEATURE_ID, 3500),
            _capacity(HEATING_CAPACITY_FEATURE_ID, 4200),
        ),
        (
            _power(COOLING_POWER_TARGET_ID, COOLING_POWER_FEATURE_ID, 1000),
            _power(HEATING_POWER_TARGET_ID, HEATING_POWER_FEATURE_ID, 1200),
        ),
    )

    assert all(item.raw_value is None or isfinite(item.raw_value) for item in metrics)
