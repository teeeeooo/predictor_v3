"""Identity-bound destination Target metadata contract regressions."""

from dataclasses import replace
from pathlib import Path

import pytest

from apps.common.runtime_generation import GenerationSnapshot
from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)
from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.result_enrichment import (
    COOLING_CAPACITY_FEATURE_ID,
    HEATING_CAPACITY_FEATURE_ID,
    enrich_target_outcomes,
)
from apps.predict.application.runtime_snapshot import (
    build_predict_runtime_snapshot,
    compatibility_predict_runtime_snapshot,
    validate_runtime_target_contract,
)
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
)
from tests.helpers.predict_results import accept_result_fixtures


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


def _coherently_forged_runtime(kind: str):  # noqa: ANN202
    runtime = compatibility_predict_runtime_snapshot()
    targets = list(runtime.target_registry_targets)
    descriptors = list(runtime.target_descriptors)
    fingerprint = runtime.target_registry_fingerprint
    if kind in {"active_set_genuine_fingerprint", "active_set_forged_fingerprint"}:
        targets.pop()
        descriptors.pop()
        if kind == "active_set_forged_fingerprint":
            fingerprint = "caller-forged-four-target-fingerprint"
    elif kind == "ml_name":
        targets[0] = replace(targets[0], ml_name="forged-ml-name")
        descriptors[0] = replace(descriptors[0], ml_name="forged-ml-name")
        fingerprint = "caller-forged-ml-name-fingerprint"
    elif kind == "result_feature_rebind":
        first_target, second_target = targets[:2]
        first_descriptor, second_descriptor = descriptors[:2]
        targets[0] = replace(
            first_target,
            result_feature_identity=second_target.result_feature_identity,
        )
        targets[1] = replace(
            second_target,
            result_feature_identity=first_target.result_feature_identity,
        )
        descriptors[0] = replace(
            first_descriptor,
            result_feature_identity=second_descriptor.result_feature_identity,
            result_key=second_descriptor.result_key,
        )
        descriptors[1] = replace(
            second_descriptor,
            result_feature_identity=first_descriptor.result_feature_identity,
            result_key=first_descriptor.result_key,
        )
        fingerprint = "caller-forged-result-feature-fingerprint"
    elif kind == "canonical_unit":
        descriptors[0] = replace(descriptors[0], canonical_unit="forged-unit")
        fingerprint = "caller-forged-unit-fingerprint"
    elif kind == "value_source":
        descriptors[0] = replace(descriptors[0], value_source="forged-source")
        fingerprint = "caller-forged-source-fingerprint"
    else:  # pragma: no cover - test helper guard
        raise AssertionError(f"unsupported coherent forge kind: {kind}")
    return replace(
        runtime,
        target_registry_targets=tuple(targets),
        target_descriptors=tuple(descriptors),
        active_targets=tuple(item.ml_name for item in descriptors),
        target_result_keys=tuple(
            (item.ml_name, item.result_key) for item in descriptors
        ),
        target_registry_fingerprint=fingerprint,
    )


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


def _install_capacity_inputs(composition, case_id):  # noqa: ANN001, ANN202
    case = composition.session.case_store.get_case(case_id)
    case.set_input_value("cooling_capa", 3500.125)
    case.set_input_value("heating_capa", 4200.875)
    outcome = composition.input_mapper.build_request(case)

    assert outcome.is_valid
    assert outcome.request is not None
    identities = {item.feature_identity for item in outcome.request.capacity_inputs}
    assert identities == {
        COOLING_CAPACITY_FEATURE_ID,
        HEATING_CAPACITY_FEATURE_ID,
    }
    return outcome.request.capacity_inputs


def _assert_canonical_enrichment(result):  # noqa: ANN001, ANN202
    assert result.execution_context is not None
    identities = {
        item.feature_identity for item in result.execution_context.capacity_inputs
    }
    assert identities == {
        COOLING_CAPACITY_FEATURE_ID,
        HEATING_CAPACITY_FEATURE_ID,
    }
    assert result.derived_metrics == enrich_target_outcomes(
        result.execution_context.capacity_inputs,
        result.target_outcomes,
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
    capacity_inputs = _install_capacity_inputs(composition, case_id)
    model = PredictionModelIdentity("candidate", 1, valid_runtime.generation_id)
    context = PredictionExecutionContext(
        session.session_id,
        case_id,
        "before-forged-destination",
        session.case_store.get_case(case_id).input_revision,
        execution_semantics_from_runtime(valid_runtime),
        model,
        capacity_inputs,
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
    result = accept_result_fixtures(
        composition,
        ResultRow(case_id, "complete"),
        model_identity=model,
    )[0]

    _assert_canonical_enrichment(result)
    assert session.result_for_case(case_id) == result


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


@pytest.mark.parametrize(
    "kind",
    (
        "active_set_genuine_fingerprint",
        "active_set_forged_fingerprint",
        "ml_name",
        "result_feature_rebind",
        "canonical_unit",
        "value_source",
    ),
)
def test_coherent_caller_forgery_cannot_acquire_runtime_authority(
    kind,
    monkeypatch,
):
    runtime = _coherently_forged_runtime(kind)
    mapper_built = False

    def forbidden_mapper(*_args, **_kwargs):  # noqa: ANN002, ANN003, ANN202
        nonlocal mapper_built
        mapper_built = True
        raise AssertionError("result mapper must not be built")

    monkeypatch.setattr(
        "apps.predict.composition.PredictionResultAdapter",
        forbidden_mapper,
    )

    with pytest.raises(ValueError, match="authority provenance"):
        validate_runtime_target_contract(runtime)
    with pytest.raises(ValueError, match="authority provenance"):
        build_predict_workspace_composition(runtime_snapshot=runtime)

    assert not mapper_built


@pytest.mark.parametrize(
    "kind",
    (
        "active_set_genuine_fingerprint",
        "active_set_forged_fingerprint",
        "ml_name",
        "result_feature_rebind",
        "canonical_unit",
        "value_source",
    ),
)
def test_coherent_forged_zero_result_migration_is_atomic_and_genuine_next_runs(
    kind,
):
    valid_runtime = compatibility_predict_runtime_snapshot()
    composition = build_predict_workspace_composition(
        runtime_snapshot=valid_runtime,
        initial_empty_rows=1,
    )
    session = composition.session
    case_id = session.case_order[0]
    _install_capacity_inputs(composition, case_id)
    model = PredictionModelIdentity("candidate", 1, valid_runtime.generation_id)
    before = _session_state(session)

    with pytest.raises(ValueError, match="authority provenance"):
        session.prepare_runtime_projection(
            cases=_case_projection(session),
            results=(),
            runtime_snapshot=_coherently_forged_runtime(kind),
            model_identity=model,
        )

    assert _session_state(session) == before
    result = accept_result_fixtures(
        composition,
        ResultRow(case_id, "complete"),
        model_identity=model,
    )[0]

    _assert_canonical_enrichment(result)
    assert session.result_for_case(case_id) == result


def test_repository_issued_generation_builds_shared_standalone_embedded_runtime(
    tmp_path,
):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(bootstrap_manifest())
    generation = repository.read_active()
    runtime = build_predict_runtime_snapshot(generation)

    standalone = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=0,
    )
    embedded = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=0,
    )

    assert standalone.runtime_snapshot is embedded.runtime_snapshot is runtime
    assert standalone.result_mapper.active_targets == embedded.result_mapper.active_targets


def test_caller_assembled_generation_cannot_issue_predict_runtime():
    manifest = bootstrap_manifest()
    generation = GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )

    with pytest.raises(ValueError, match="repository-issued generation"):
        build_predict_runtime_snapshot(generation)
