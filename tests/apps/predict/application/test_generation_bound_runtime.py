"""Behavioral proof that Predict execution semantics move with generation."""

from dataclasses import replace
from pathlib import Path

from apps.common.runtime_generation import GenerationSnapshot
from apps.predict.application.models import PredictionInputRequest, PredictionServiceResult
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.application.model_compatibility import ModelCompatibilityEvidence
from apps.predict.application.runtime_generation import StandalonePredictGenerationGuard
from apps.predict.application.runtime_generation_participant import PredictRuntimeParticipant
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.case_row import CaseRow
from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
)
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)


class _ColumnModel:
    def __init__(self, column: str) -> None:
        self.column = column

    def predict(self, frame):  # noqa: ANN001, ANN201
        return [float(frame[self.column].iloc[0])]


def _snapshot(manifest) -> GenerationSnapshot:  # noqa: ANN001
    return GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )


def _changed_manifest():  # noqa: ANN201
    bootstrap = bootstrap_manifest()
    active = replace(
        bootstrap,
        features=tuple(
            replace(item, zero_fill_policy="disallow")
            if item.ml_name == "Cooling Capa" else item
            for item in bootstrap.features
        ),
    )
    first_target = active.targets[0]
    result_identity = first_target.feature_identity
    zero_feature_identity = next(
        item.identity for item in active.features if item.ml_name == "Cooling Capa"
    )
    features = tuple(
        replace(item, ml_name="Cooling Power Audit")
        if item.identity == result_identity
        else replace(item, zero_fill_policy="mode_missing_allowed")
        if item.identity == zero_feature_identity
        else item
        for item in active.features
    )
    first_group = active.one_hot_groups[0]
    first_group = replace(
        first_group,
        categories=(
            replace(first_group.categories[0], source_value="AUDIT"),
            *first_group.categories[1:],
        ),
    )
    return active, replace(
        active,
        generation=replace(active.generation, generation_id="generation-b"),
        features=features,
        derived=(replace(active.derived[0], zero_value=7.0), *active.derived[1:]),
        one_hot_groups=(first_group, *active.one_hot_groups[1:]),
        targets=(
            replace(first_target, ml_name="Cooling Power Audit"),
            *active.targets[1:],
        ),
        ordering=replace(
            active.ordering,
            ml=(active.ordering.ml[1], active.ordering.ml[0], *active.ordering.ml[2:]),
        ),
    )


def _model(runtime, target: str, feature: str) -> dict[str, object]:  # noqa: ANN001
    return {
        "preprocess_version": runtime.preprocessing_version,
        "training_contract": runtime.expected_model_contract,
        "features": {target: [feature]},
        "models": {target: _ColumnModel(feature)},
    }


def test_a_b_runtime_controls_derived_one_hot_target_result_zero_fill_and_order():
    manifest_a, manifest_b = _changed_manifest()
    runtime_a = build_predict_runtime_snapshot(_snapshot(manifest_a))
    runtime_b = build_predict_runtime_snapshot(_snapshot(manifest_b))

    assert runtime_a.derived.definitions[0].zero_value == 0.0
    assert runtime_b.derived.definitions[0].zero_value == 7.0
    assert runtime_a.one_hot.groups[0].categories[0].source_value != "AUDIT"
    assert runtime_b.one_hot.groups[0].categories[0].source_value == "AUDIT"
    assert runtime_a.active_targets[0] == "Cooling Power"
    assert runtime_b.active_targets[0] == "Cooling Power Audit"
    assert runtime_b.target_result_keys[0] == ("Cooling Power Audit", "cooling_power")
    assert runtime_a.ordered_input_ml_names[:2] == ("Cooling Capa", "Heating Capa")
    assert runtime_b.ordered_input_ml_names[:2] == ("Heating Capa", "Cooling Capa")

    composition_a = build_predict_workspace_composition(
        runtime_snapshot=runtime_a, initial_empty_rows=0
    )
    composition_b = build_predict_workspace_composition(
        runtime_snapshot=runtime_b, initial_empty_rows=0
    )
    selector = runtime_b.one_hot.groups[0].selector_column_key
    encoded_a = composition_a.input_mapper.build_request(
        CaseRow("a", input_values={"cooling_capa": 1, selector: "AUDIT"})
    ).request.row_input
    encoded_b = composition_b.input_mapper.build_request(
        CaseRow("b", input_values={"cooling_capa": 1, selector: "AUDIT"})
    ).request.row_input
    emitted = runtime_b.one_hot.groups[0].categories[0].emitted_ml_name
    assert encoded_a[emitted] == 0.0
    assert encoded_b[emitted] == 1.0

    derived_name = runtime_b.derived.definitions[0].output_ml_name
    numerator = runtime_b.derived.definitions[0].numerator_ml_name
    denominator = runtime_b.derived.definitions[0].denominator_ml_name
    service_a = PredictionService(runtime_snapshot=runtime_a)
    service_b = PredictionService(runtime_snapshot=runtime_b)
    service_a._model_data = _model(runtime_a, runtime_a.active_targets[0], derived_name)
    service_b._model_data = _model(runtime_b, runtime_b.active_targets[0], derived_name)
    request = PredictionInputRequest("case", {numerator: 10.0, denominator: 0.0})
    result_a = service_a.predict_one(request)
    result_b = service_b.predict_one(request)
    assert result_a.predictions[runtime_a.active_targets[0]] == 0.0
    assert result_b.predictions[runtime_b.active_targets[0]] == 7.0

    mapped = composition_b.result_mapper.from_service_result(PredictionServiceResult(
        "case", "complete", {"Cooling Power Audit": 123.0}
    ))
    assert mapped.result_values["cooling_power"] == "123"

    zero_feature = "Cooling Capa"
    zero_service_a = PredictionService(runtime_snapshot=runtime_a)
    zero_service_b = PredictionService(runtime_snapshot=runtime_b)
    zero_service_a._model_data = _model(runtime_a, runtime_a.active_targets[0], zero_feature)
    zero_service_b._model_data = _model(runtime_b, runtime_b.active_targets[0], zero_feature)
    assert zero_service_a.predict_one(PredictionInputRequest("a", {})).status == "error"
    zero_result_b = zero_service_b.predict_one(PredictionInputRequest("b", {}))
    assert zero_result_b.status == "complete"
    assert zero_result_b.predictions[runtime_b.active_targets[0]] == 0.0


def test_production_composition_binds_every_execution_owner_to_one_generation():
    _manifest_a, manifest_b = _changed_manifest()
    runtime = build_predict_runtime_snapshot(_snapshot(manifest_b))
    composition = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=0,
    )

    assert {
        composition.generation_id,
        composition.runtime_snapshot.generation_id,
        composition.input_mapper.generation_id,
        composition.result_mapper.generation_id,
        composition.prediction_service.generation_id,
        composition.runtime_snapshot.derived.generation_id,
        composition.runtime_snapshot.one_hot.generation_id,
    } == {"generation-b"}


def test_standalone_reload_commits_b_execution_semantics_and_preserves_session(tmp_path):
    manifest_a, manifest_b = _changed_manifest()
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(manifest_a)
    active = repository.read_active()
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        initial_empty_rows=1,
    )
    case_id = composition.session.case_order[0]
    composition.session.case_store.get_case(case_id).set_input_value(
        "cooling_capa", "3500"
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    guard = StandalonePredictGenerationGuard(repository, participant)
    manifest_b = replace(
        manifest_b,
        generation=replace(
            manifest_b.generation,
            parent_generation_id=manifest_a.generation.generation_id,
        ),
    )
    repository.publish(manifest_b)

    assert guard.ensure_current()
    runtime = participant.composition.runtime_snapshot
    assert runtime.generation_id == "generation-b"
    assert runtime.derived.definitions[0].zero_value == 7.0
    assert runtime.one_hot.groups[0].categories[0].source_value == "AUDIT"
    assert runtime.active_targets[0] == "Cooling Power Audit"
    assert runtime.target_result_keys[0][1] == "cooling_power"
    assert participant.composition.session.case_store.get_case(case_id).input_values[
        "cooling_capa"
    ] == "3500"


def test_standalone_incompatible_candidate_is_aborted_without_session_or_active_swap(
    tmp_path,
):
    manifest_a, manifest_b = _changed_manifest()
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(manifest_a)
    active = repository.read_active()
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active), initial_empty_rows=1
    )
    case_id = composition.session.case_order[0]
    case = composition.session.case_store.get_case(case_id)
    case.set_input_value("cooling_capa", "3700")
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, snapshot: ModelCompatibilityEvidence(
            "compatible" if snapshot.manifest.generation.generation_id != "generation-b"
            else "retraining-required",
            "audit",
        ),
    )
    guard = StandalonePredictGenerationGuard(repository, participant)
    repository.publish(replace(
        manifest_b,
        generation=replace(
            manifest_b.generation,
            parent_generation_id=manifest_a.generation.generation_id,
        ),
    ))

    assert not guard.ensure_current()
    assert participant.active_generation_id == manifest_a.generation.generation_id
    assert case.input_values["cooling_capa"] == "3700"
    assert guard.status == "Retraining required"


def test_standalone_case_change_during_reload_rejects_stale_candidate(tmp_path):
    manifest_a, manifest_b = _changed_manifest()
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(manifest_a)
    active = repository.read_active()
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active), initial_empty_rows=1
    )
    case_id = composition.session.case_order[0]

    class _MutatingParticipant(PredictRuntimeParticipant):
        def prepare(self, candidate):  # noqa: ANN001, ANN201
            prepared = super().prepare(candidate)
            self.composition.session.case_store.get_case(case_id).set_input_value(
                "cooling_capa", "latest"
            )
            return prepared

    participant = _MutatingParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    guard = StandalonePredictGenerationGuard(repository, participant)
    repository.publish(replace(
        manifest_b,
        generation=replace(
            manifest_b.generation,
            parent_generation_id=manifest_a.generation.generation_id,
        ),
    ))

    assert not guard.ensure_current()
    assert guard.blocker_code == "stale_candidate"
    assert participant.active_generation_id == manifest_a.generation.generation_id
    assert composition.session.case_store.get_case(case_id).input_values[
        "cooling_capa"
    ] == "latest"
