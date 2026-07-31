"""Typed result freshness across atomic Predict generation transitions."""

from dataclasses import replace
from pathlib import Path

from apps.common.runtime_generation import GenerationCandidate, GenerationSnapshot
from apps.predict.application.model_compatibility import ModelCompatibilityEvidence
from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_generation_participant import PredictRuntimeParticipant
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
)


def _snapshot(manifest):  # noqa: ANN001
    return GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )


def _setup(active, candidate, tmp_path):  # noqa: ANN001
    model_file = str(tmp_path / "model.pkl")
    runtime = build_predict_runtime_snapshot(active)
    composition = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        model_file=model_file,
        initial_empty_rows=1,
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=model_file,
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    transition = GenerationCandidate(
        candidate,
        candidate.manifest.generation.generation_id,
        ((participant.name, participant.revision_token()),),
        "typed-result-transition",
    )
    return composition, participant, transition, model_file


def _install_typed_result(composition, model_file):  # noqa: ANN001
    case_id = composition.session.case_order[0]
    descriptors = composition.runtime_snapshot.target_descriptors
    context = PredictionExecutionContext(
        composition.session.session_id,
        case_id,
        "accepted-run",
        composition.session.case_store.get_case(case_id).input_revision,
        execution_semantics_from_runtime(composition.runtime_snapshot),
        PredictionModelIdentity(
            f"unmanaged:{model_file}", 0, composition.runtime_snapshot.generation_id
        ),
    )
    result = ResultRow(
        case_id,
        "complete",
        message="accepted",
        target_outcomes=tuple(
            TargetOutcome(
                descriptor.target_identity,
                descriptor.result_feature_identity,
                descriptor.result_key,
                descriptor.canonical_unit,
                "available",
                value_source=descriptor.value_source,
                raw_value=123.456789,
            )
            for descriptor in descriptors
        ),
        execution_context=context,
    )
    composition.session.allow_result(context, descriptors)
    semantics, model = composition.prediction_controller.execution_environment
    assert composition.session.accept_result(result, semantics, model).accepted
    return result


def test_presentation_only_cutover_keeps_current_and_renames_result_key(tmp_path):
    manifest = bootstrap_manifest()
    target = manifest.targets[0]
    feature = next(item for item in manifest.features if item.identity == target.feature_identity)
    candidate_manifest = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="presentation-b"),
        features=tuple(
            replace(item, column_key="cooling_power_presented", label="표시명", visible=False)
            if item.identity == feature.identity else item
            for item in manifest.features
        ),
    )
    active, candidate = _snapshot(manifest), _snapshot(candidate_manifest)
    composition, participant, transition, model_file = _setup(active, candidate, tmp_path)
    original = _install_typed_result(composition, model_file)
    revision = composition.session.case_store.get_case(original.case_id).input_revision

    prior = participant.commit(participant.prepare(transition))
    migrated = composition.session.result_for_case(original.case_id)

    assert migrated.freshness == "current"
    assert migrated.target_outcomes[0].raw_value == 123.456789
    assert migrated.target_outcomes[0].result_feature_identity == feature.identity
    assert migrated.target_outcomes[0].result_key == "cooling_power_presented"
    assert composition.session.case_store.get_case(original.case_id).input_revision == revision

    participant.rollback(prior)
    assert composition.session.result_for_case(original.case_id) == original


def test_semantic_cutover_preserves_outcome_and_provenance_but_marks_stale(tmp_path):
    manifest = bootstrap_manifest()
    candidate_manifest = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="semantic-b"),
        preprocessing_version=f"{manifest.preprocessing_version}-changed",
    )
    active, candidate = _snapshot(manifest), _snapshot(candidate_manifest)
    composition, participant, transition, model_file = _setup(active, candidate, tmp_path)
    original = _install_typed_result(composition, model_file)
    revision = composition.session.case_store.get_case(original.case_id).input_revision

    prior = participant.commit(participant.prepare(transition))
    migrated = composition.session.result_for_case(original.case_id)

    assert migrated.status == "complete"
    assert migrated.freshness == "stale"
    assert migrated.stale_reason == "execution_semantics_changed"
    assert migrated.target_outcomes == original.target_outcomes
    assert migrated.execution_context == original.execution_context
    assert composition.session.case_store.get_case(original.case_id).input_revision == revision + 1

    participant.rollback(prior)
    assert composition.session.result_for_case(original.case_id) == original
    assert composition.session.case_store.get_case(original.case_id).input_revision == revision


def test_target_registry_change_stales_result_without_bumping_input_revision(tmp_path):
    manifest = bootstrap_manifest()
    target = manifest.targets[0]
    candidate_manifest = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="target-registry-b"),
        targets=(
            replace(target, policy_owner_identities=target.policy_owner_identities[:-1]),
            *manifest.targets[1:],
        ),
    )
    active, candidate = _snapshot(manifest), _snapshot(candidate_manifest)
    composition, participant, transition, model_file = _setup(active, candidate, tmp_path)
    original = _install_typed_result(composition, model_file)
    revision = composition.session.case_store.get_case(original.case_id).input_revision

    participant.commit(participant.prepare(transition))
    migrated = composition.session.result_for_case(original.case_id)

    assert migrated.freshness == "stale"
    assert migrated.stale_reason == "execution_semantics_changed"
    assert migrated.target_outcomes == original.target_outcomes
    assert composition.session.case_store.get_case(original.case_id).input_revision == revision
