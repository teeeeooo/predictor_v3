"""Concrete Predict, Train, and Mapping participant state preservation."""

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest

from apps.common.runtime_generation import GenerationCandidate
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.application.models import PredictionModelStatus
from apps.predict.controllers.table_edit_controller import TableEditController
from apps.predict.state.result_row import ResultRow
from apps.train.adapters.data_definition_generation_repository import DataDefinitionGenerationRepository
from apps.train.application.runtime_generation.participants import (
    MappingRuntimeParticipant,
    ModelCompatibilityEvidence,
    ParticipantPrepareError,
    PredictRuntimeParticipant,
    TrainRuntimeParticipant,
)
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from core.data_definition.contract import bootstrap_manifest
from tests.helpers.predict_results import install_projection_results


def _published_pair(tmp_path, *, mutate=None):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    candidate = mutate(first) if mutate else first
    second = replace(
        candidate,
        generation=replace(
            candidate.generation,
            generation_id=f"generation-{uuid4().hex}",
            parent_generation_id=first.generation.generation_id,
        ),
    )
    repository.publish(second)
    return repository.read_generation(first.generation.generation_id), repository.read_active()


def _candidate(snapshot, participant):  # noqa: ANN001
    return GenerationCandidate(
        snapshot,
        snapshot.manifest.generation.generation_id,
        ((participant.name, participant.revision_token()),),
        uuid4().hex,
    )


def test_predict_prepare_preserves_rows_results_and_commit_keeps_identity_values(tmp_path):
    active, candidate = _published_pair(tmp_path)
    composition = build_predict_workspace_composition(
        initial_empty_rows=1,
        one_hot_snapshot=active.projections.one_hot_runtime,
        predict_projection=active.projections.predict,
    )
    case_id = composition.session.case_order[0]
    case = composition.session.case_store.get_case(case_id)
    case.set_input_value("cooling_capa", "3500")
    result = ResultRow(
        case_id=case_id,
        status="complete",
        result_values={"cooling_power": 1.0},
    )
    install_projection_results(composition.session, result)
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence("compatible", "ok"),
    )

    prepared = participant.prepare(_candidate(candidate, participant))
    assert case.input_values["cooling_capa"] == "3500"
    assert composition.session.result_for_case(case_id) == result

    prior = participant.commit(prepared)
    assert participant.active_generation_id == candidate.manifest.generation.generation_id
    assert case.input_values["cooling_capa"] == "3500"
    assert composition.session.result_for_case(case_id) == result
    participant.rollback(prior)
    assert participant.active_generation_id == active.manifest.generation.generation_id


def test_predict_prepare_commit_rollback_moves_actual_runtime_semantics(tmp_path):
    active, candidate = _published_pair(
        tmp_path,
        mutate=lambda manifest: replace(
            manifest,
            derived=(replace(manifest.derived[0], zero_value=6.0), *manifest.derived[1:]),
        ),
    )
    composition = build_predict_workspace_composition(
        initial_empty_rows=1,
        runtime_snapshot=build_predict_runtime_snapshot(active),
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )

    prepared = participant.prepare(_candidate(candidate, participant))
    assert participant.composition.runtime_snapshot.derived.definitions[0].zero_value == 0.0
    prior = participant.commit(prepared)
    assert participant.composition.runtime_snapshot.derived.definitions[0].zero_value == 6.0
    participant.rollback(prior)
    assert participant.composition.runtime_snapshot.derived.definitions[0].zero_value == 0.0


@pytest.mark.parametrize(
    "mutation",
    ("input", "autofill", "paste", "add", "delete", "reset"),
)
def test_predict_case_mutation_after_prepare_rejects_commit_without_overwrite(
    tmp_path, mutation
):
    active, candidate = _published_pair(tmp_path)
    composition = build_predict_workspace_composition(
        initial_empty_rows=2,
        runtime_snapshot=build_predict_runtime_snapshot(active),
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    prepared = participant.prepare(_candidate(candidate, participant))
    session = composition.session
    first = session.case_order[0]
    if mutation == "input":
        session.case_store.get_case(first).set_input_value("cooling_capa", "4100")
    elif mutation == "autofill":
        session.set_autofill_value(first, "id_volume", "0.42")
    elif mutation == "paste":
        session.case_store.update_cell_value(first, "cooling_capa", "4200")
    elif mutation == "add":
        session.case_store.append_empty_rows(1)
    elif mutation == "delete":
        session.case_store.remove_rows((first,))
    else:
        TableEditController(session).reset_rows(3)
    latest = (
        session.revision,
        session.case_order,
        tuple(
            (
                case_id,
                dict(session.case_store.get_case(case_id).input_values),
                dict(session.case_store.get_case(case_id).autofill_values),
                set(session.case_store.get_case(case_id).dirty_fields),
            )
            for case_id in session.case_order
        ),
    )

    with pytest.raises(ParticipantPrepareError) as error:
        participant.commit(prepared)

    assert error.value.code == "predict_revision_stale"
    assert participant.active_generation_id == active.manifest.generation.generation_id
    assert latest == (
        session.revision,
        session.case_order,
        tuple(
            (
                case_id,
                dict(session.case_store.get_case(case_id).input_values),
                dict(session.case_store.get_case(case_id).autofill_values),
                set(session.case_store.get_case(case_id).dirty_fields),
            )
            for case_id in session.case_order
        ),
    )


class _Event:
    def connect(self, callback):  # noqa: ANN001
        return callback


class _HoldingRunner:
    def __init__(self):
        self.row_result = _Event()
        self.progress = _Event()
        self.finished = _Event()
        self.cancelled = _Event()
        self.failed = _Event()

    def start(self, job):  # noqa: ANN001
        self.job = job

    def cancel(self):
        return None


class _RunnableService:
    def model_status(self):
        return PredictionModelStatus("fake", "loaded")


def test_prediction_start_after_prepare_makes_candidate_stale(tmp_path):
    active, candidate = _published_pair(tmp_path)
    runner = _HoldingRunner()
    composition = build_predict_workspace_composition(
        initial_empty_rows=1,
        runtime_snapshot=build_predict_runtime_snapshot(active),
        prediction_service=_RunnableService(),
        runner_factory=lambda _service: runner,
    )
    composition.session.case_store.get_case(
        composition.session.case_order[0]
    ).set_input_value("cooling_capa", "3500")
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    prepared = participant.prepare(_candidate(candidate, participant))

    composition.prediction_controller.start_all()
    assert composition.prediction_controller.is_running
    with pytest.raises(ParticipantPrepareError) as error:
        participant.commit(prepared)

    assert error.value.code == "predict_revision_stale"
    assert participant.active_generation_id == active.manifest.generation.generation_id


def test_predict_incompatible_type_blocks_before_case_or_result_mutation(tmp_path):
    def mutate(manifest):  # noqa: ANN001
        features = tuple(
            replace(item, data_type="string") if item.column_key == "cooling_capa" else item
            for item in manifest.features
        )
        return replace(manifest, features=features)

    active, _candidate_snapshot = _published_pair(tmp_path)
    changed_manifest = mutate(active.manifest)
    changed_manifest = replace(
        changed_manifest,
        generation=replace(changed_manifest.generation, generation_id="type-change"),
    )
    candidate = replace(active, manifest=changed_manifest)
    composition = build_predict_workspace_composition(
        initial_empty_rows=1,
        one_hot_snapshot=active.projections.one_hot_runtime,
        predict_projection=active.projections.predict,
    )
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    case.set_input_value("cooling_capa", "3500")
    participant = PredictRuntimeParticipant(
        active, composition, model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence("compatible", "ok"),
    )

    with pytest.raises(ParticipantPrepareError) as error:
        participant.prepare(_candidate(candidate, participant))

    assert error.value.code == "predict_case_type_incompatible"
    assert case.input_values == {"cooling_capa": "3500"}


def test_train_registry_swap_changes_new_run_snapshot_without_touching_frozen_value(tmp_path):
    active, candidate = _published_pair(tmp_path)
    participant = TrainRuntimeParticipant(active)
    frozen = participant.registry_snapshot
    prepared = participant.prepare(_candidate(candidate, participant))
    participant.commit(prepared)

    assert frozen.generation_id == active.manifest.generation.generation_id
    assert participant.registry_snapshot.generation_id == candidate.manifest.generation.generation_id


def test_train_prepare_revalidates_selected_training_headers(tmp_path):
    active, candidate = _published_pair(tmp_path)
    selected = tmp_path / "selected.csv"
    selected.write_text("unrelated\n", encoding="utf-8")
    participant = TrainRuntimeParticipant(
        active, selected_data_path_provider=lambda: str(selected)
    )

    with pytest.raises(ParticipantPrepareError) as error:
        participant.prepare(_candidate(candidate, participant))

    assert error.value.code == "training_data_header_incompatible"
    assert participant.active_generation_id == active.manifest.generation.generation_id


@pytest.mark.parametrize("mutation", ("path", "replace", "header", "delete"))
def test_train_selected_csv_change_after_prepare_rejects_commit(tmp_path, mutation):
    active, candidate = _published_pair(tmp_path)
    headers = ",".join(TrainRuntimeParticipant(active).registry_snapshot.training_headers)
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text(headers + "\n", encoding="utf-8")
    second.write_text(headers + "\n", encoding="utf-8")
    selected = [str(first)]
    participant = TrainRuntimeParticipant(
        active, selected_data_path_provider=lambda: selected[0]
    )
    prepared = participant.prepare(_candidate(candidate, participant))
    if mutation == "path":
        selected[0] = str(second)
    elif mutation == "replace":
        first.write_text(headers + "\n1\n", encoding="utf-8")
    elif mutation == "header":
        first.write_text("changed\n", encoding="utf-8")
    else:
        first.unlink()

    with pytest.raises(ParticipantPrepareError) as error:
        participant.commit(prepared)

    assert error.value.code == "training_data_revision_stale"
    assert participant.active_generation_id == active.manifest.generation.generation_id


def test_dirty_mapping_requires_review_and_preserves_mapping_file_and_draft(tmp_path):
    active, candidate = _published_pair(tmp_path)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(
        '{"idu":{"IDU-A":{"ID Volume":1.25,"Size":"S"}}}',
        encoding="utf-8",
    )
    before_bytes = mapping_path.read_bytes()
    service = DataMappingService(provider=RuntimeMappingCatalogProvider(str(mapping_path)))
    participant = MappingRuntimeParticipant(active, service)
    snapshot = service.load_snapshot()
    group = next(item for item in snapshot.draft.groups if item.rows)
    editable_column = group.columns[-1]
    original = group.rows[0].value_for(editable_column)
    service.edit_cell(group.group_key, 0, editable_column, f"{original}-dirty")

    with pytest.raises(ParticipantPrepareError) as error:
        participant.prepare(_candidate(candidate, participant))

    assert error.value.code == "mapping_reconciliation_required"
    assert service.is_dirty
    assert mapping_path.read_bytes() == before_bytes
    assert participant.review_update()
