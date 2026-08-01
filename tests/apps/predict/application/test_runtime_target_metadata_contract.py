"""Identity-bound destination Target metadata contract regressions."""

from dataclasses import replace

import pytest

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
    validate_runtime_target_contract,
)
from apps.predict.composition import build_predict_workspace_composition


def _replace_descriptors(runtime, descriptors):  # noqa: ANN001, ANN202
    return replace(runtime, target_descriptors=tuple(descriptors))


def _forged_runtime(kind: str):  # noqa: ANN202
    runtime = compatibility_predict_runtime_snapshot()
    descriptors = list(runtime.target_descriptors)
    first = descriptors[0]
    if kind == "target_identity":
        descriptors[0] = replace(first, target_identity="forged-target")
    elif kind == "canonical_unit":
        descriptors[0] = replace(first, canonical_unit="forged-unit")
    elif kind == "value_source":
        descriptors[0] = replace(first, value_source="forged-source")
    elif kind == "ml_name":
        descriptors[0] = replace(first, ml_name="forged-ml-name")
        runtime = replace(
            runtime,
            active_targets=("forged-ml-name", *runtime.active_targets[1:]),
            target_result_keys=(
                ("forged-ml-name", first.result_key),
                *runtime.target_result_keys[1:],
            ),
        )
    elif kind == "result_feature_identity":
        second = descriptors[1]
        descriptors[0] = replace(
            first,
            result_feature_identity=second.result_feature_identity,
            result_key=second.result_key,
        )
        descriptors[1] = replace(
            second,
            result_feature_identity=first.result_feature_identity,
            result_key=first.result_key,
        )
        runtime = replace(
            runtime,
            target_result_keys=tuple(
                (item.ml_name, item.result_key) for item in descriptors
            ),
        )
    elif kind == "result_key":
        descriptors[0] = replace(first, result_key="forged-result-key")
        runtime = replace(
            runtime,
            target_result_keys=(
                (first.ml_name, "forged-result-key"),
                *runtime.target_result_keys[1:],
            ),
        )
    elif kind == "active_set":
        descriptors.pop()
        runtime = replace(
            runtime,
            active_targets=runtime.active_targets[:-1],
            target_result_keys=runtime.target_result_keys[:-1],
        )
    else:  # pragma: no cover - test helper guard
        raise AssertionError(f"unsupported forge kind: {kind}")
    return _replace_descriptors(runtime, descriptors)


def _case_projection(session):  # noqa: ANN001, ANN202
    return tuple(
        (
            case_id,
            dict(case.input_values),
            dict(case.autofill_values),
            set(case.dirty_fields),
            case.input_revision,
        )
        for case_id in session.case_order
        for case in (session.case_store.get_case(case_id),)
    )


def _session_state(session):  # noqa: ANN001, ANN202
    return (
        session.case_order,
        _case_projection(session),
        dict(session.results_by_case_id),
        session.revision,
        tuple(
            (case_id, session.allowed_context_for_case(case_id))
            for case_id in session.case_order
        ),
        session.issued_projection_count,
    )


@pytest.mark.parametrize(
    "kind",
    (
        "target_identity",
        "canonical_unit",
        "value_source",
        "ml_name",
        "result_feature_identity",
        "result_key",
        "active_set",
    ),
)
def test_forged_descriptor_metadata_fails_closed_before_composition(kind):
    runtime = _forged_runtime(kind)

    with pytest.raises(ValueError, match="Predict"):
        validate_runtime_target_contract(runtime)
    with pytest.raises(ValueError, match="Predict"):
        build_predict_workspace_composition(runtime_snapshot=runtime)


@pytest.mark.parametrize(
    "kind",
    (
        "target_identity",
        "canonical_unit",
        "value_source",
        "ml_name",
        "result_feature_identity",
        "result_key",
        "active_set",
    ),
)
def test_forged_zero_result_destination_does_not_issue_or_mutate(kind):
    valid_runtime = compatibility_predict_runtime_snapshot()
    composition = build_predict_workspace_composition(
        runtime_snapshot=valid_runtime,
        initial_empty_rows=1,
    )
    session = composition.session
    case_id = session.case_order[0]
    model = PredictionModelIdentity("candidate", 1, valid_runtime.generation_id)
    context = PredictionExecutionContext(
        session.session_id,
        case_id,
        "before-forged-destination",
        session.case_store.get_case(case_id).input_revision,
        execution_semantics_from_runtime(valid_runtime),
        model,
    )
    session.allow_result(context, valid_runtime.target_descriptors)
    before = _session_state(session)

    with pytest.raises(ValueError, match="Predict"):
        session.prepare_runtime_projection(
            cases=_case_projection(session),
            results=(),
            runtime_snapshot=_forged_runtime(kind),
            model_identity=model,
        )

    assert _session_state(session) == before
    session.revoke_run(context.run_id)
    next_context = replace(context, run_id="genuine-next-execution")
    session.allow_result(next_context, valid_runtime.target_descriptors)
    assert session.allowed_context_for_case(case_id) == next_context


def test_valid_five_target_authority_and_descriptor_contract_is_accepted():
    runtime = compatibility_predict_runtime_snapshot()

    validate_runtime_target_contract(runtime)
    composition = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=1,
    )

    assert len(runtime.target_registry_targets) == 5
    assert runtime.active_targets == tuple(
        item.ml_name for item in runtime.target_registry_targets
    )
    assert composition.runtime_snapshot is runtime
