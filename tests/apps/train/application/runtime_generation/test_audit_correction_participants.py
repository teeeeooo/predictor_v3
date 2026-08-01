"""Definition parity and exact Mapping reconciliation audit corrections."""

from dataclasses import replace
from uuid import uuid4

import pytest

from apps.common.runtime_generation import GenerationCandidate
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.runtime_generation import (
    DefinitionRuntimeParticipant,
    MappingRuntimeParticipant,
    PredictRuntimeParticipant,
    RuntimeGenerationCoordinator,
    TrainRuntimeParticipant,
)
from apps.train.application.runtime_generation.participants import ParticipantPrepareError
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from core.data_definition.contract import bootstrap_manifest
from apps.predict.application.model_compatibility import ModelCompatibilityEvidence
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from tests.helpers.predict_results import install_projection_results


def _candidate(snapshot, participant):  # noqa: ANN001
    return GenerationCandidate(
        snapshot,
        snapshot.manifest.generation.generation_id,
        ((participant.name, participant.revision_token()),),
        uuid4().hex,
    )


def _definition_pair(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    active = repository.read_active()
    controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository
    ))
    participant = DefinitionRuntimeParticipant(active, controller)
    controller.refresh()
    second = replace(
        first,
        generation=replace(
            first.generation,
            generation_id="generation-b",
            parent_generation_id=first.generation.generation_id,
        ),
    )
    repository.publish(second)
    return repository, active, repository.read_active(), controller, participant


def test_clean_definition_prepare_is_invisible_then_commit_and_rollback_match_controller(
    tmp_path,
):
    _repository, active, candidate, controller, participant = _definition_pair(tmp_path)
    before = controller.draft_evidence

    prepared = participant.prepare(_candidate(candidate, participant))
    assert controller.draft_evidence == before
    assert controller.runtime_generation_id == active.manifest.generation.generation_id

    prior = participant.commit(prepared)
    assert participant.active_generation_id == "generation-b"
    assert controller.runtime_generation_id == "generation-b"
    assert controller.draft_evidence[0] == "generation-b"
    assert participant.controller_state is not None

    participant.rollback(prior)
    assert participant.active_generation_id == active.manifest.generation.generation_id
    assert controller.runtime_generation_id == active.manifest.generation.generation_id
    assert controller.draft_evidence[0] == active.manifest.generation.generation_id


def test_dirty_definition_external_publication_preserves_draft_until_reset_and_retry(
    tmp_path,
):
    _repository, active, candidate, controller, participant = _definition_pair(tmp_path)
    state = controller.refresh()
    identity = state.draft_row_identities[0]
    dirty = controller.edit_cell(identity, "label", "Unsaved audit label")
    assert dirty.draft_changed
    dirty_evidence = controller.draft_evidence

    with pytest.raises(ParticipantPrepareError) as error:
        participant.prepare(_candidate(candidate, participant))

    assert error.value.code == "definition_draft_reconciliation_required"
    assert controller.draft_evidence == dirty_evidence
    assert participant.active_generation_id == active.manifest.generation.generation_id

    reset = controller.reset_draft()
    assert not reset.draft_changed
    prepared = participant.prepare(_candidate(candidate, participant))
    participant.commit(prepared)
    assert controller.draft_evidence[0] == "generation-b"


def _mapping_setup(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    manifest = bootstrap_manifest()
    repository.publish(manifest)
    active = repository.read_active()
    removed_identity = manifest.mapping_requirements[0].identity
    candidate_manifest = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="generation-b"),
        mapping_requirements=manifest.mapping_requirements[1:],
    )
    candidate = replace(
        active,
        manifest=candidate_manifest,
        projections=replace(
            active.projections,
            generation_id="generation-b",
            mapping_requirements=active.projections.mapping_requirements[1:],
        ),
    )
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(
        """
        {
          "idu":{"IDU-A":{"ID Volume":1.25,"Size":"S"}},
          "evap_index":{"EVAP-A":{"Evap Area":8.2,"Evap Volume":2.1}},
          "odu":{"ODU-A":{"OD Volume":2.5}},
          "compressor":{"CMP-A":{"Comp EER":3.2,"Comp cc":11}},
          "ref_type":{"R32":{}},
          "exp_type":{"EEV":{}},
          "odu_cascade":{"ODU-A":{"Available_Fins":["F&T"],"Available_Pis":["7"],"Available_Rows":["1"]}},
          "cond_specs":{"ODU-A F&T 7 1":{"Cond Area":3.5,"Cond Volume":4.5}}
        }
        """,
        encoding="utf-8",
    )
    service = DataMappingService(
        provider=RuntimeMappingCatalogProvider(str(mapping_path))
    )
    participant = MappingRuntimeParticipant(active, service)
    service.load_snapshot()
    return candidate, removed_identity, mapping_path, service, participant


def _classification(participant, identity):  # noqa: ANN001
    return next(
        item.classification
        for item in participant.review_update()
        if item.identity == identity
    )


def test_mapping_removed_clean_is_not_misclassified_by_unrelated_dirty_cell(tmp_path):
    candidate, identity, mapping_path, service, participant = _mapping_setup(tmp_path)
    before = mapping_path.read_bytes()
    service.edit_cell("idu", 0, "Size", "L")

    with pytest.raises(ParticipantPrepareError):
        participant.prepare(_candidate(candidate, participant))

    assert _classification(participant, identity) == "removed clean requirement"
    assert mapping_path.read_bytes() == before


def test_mapping_review_recomputes_dirty_column_save_and_discard_evidence(tmp_path):
    candidate, identity, mapping_path, service, participant = _mapping_setup(tmp_path)
    service.edit_cell("idu", 0, "Size", "L")
    with pytest.raises(ParticipantPrepareError):
        participant.prepare(_candidate(candidate, participant))
    assert _classification(participant, identity) == "removed clean requirement"

    service.edit_cell("idu", 0, "ID Volume", 9.5)
    assert _classification(participant, identity) == "dirty column removal"

    assert participant.save_mapping()
    assert _classification(participant, identity) == "removed clean requirement"
    saved = mapping_path.read_bytes()
    service.edit_cell("idu", 0, "ID Volume", 7.5)
    assert _classification(participant, identity) == "dirty column removal"
    participant.discard_and_reload()
    assert mapping_path.read_bytes() == saved
    assert _classification(participant, identity) == "removed clean requirement"


def test_mapping_unchanged_requirement_reports_preserved_unsaved_values(tmp_path):
    candidate, identity, _mapping_path, service, participant = _mapping_setup(tmp_path)
    candidate = replace(
        candidate,
        manifest=replace(
            candidate.manifest,
            mapping_requirements=participant.active_snapshot.manifest.mapping_requirements,
        ),
        projections=replace(
            candidate.projections,
            mapping_requirements=participant.active_snapshot.projections.mapping_requirements,
        ),
    )
    service.edit_cell("idu", 0, "ID Volume", 8.5)

    with pytest.raises(ParticipantPrepareError):
        participant.prepare(_candidate(candidate, participant))

    assert _classification(participant, identity) == (
        "compatible requirement with preserved unsaved values"
    )


def _coordinator_setup(tmp_path, *, failing_train=False):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "coordinator-definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    active = repository.read_active()
    controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository
    ))
    definition = DefinitionRuntimeParticipant(active, controller)
    controller.refresh()
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active), initial_empty_rows=1
    )
    predict = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )

    class _FailingTrain(TrainRuntimeParticipant):
        def commit(self, prepared):  # noqa: ANN001
            raise RuntimeError("injected real-participant failure")

    train_type = _FailingTrain if failing_train else TrainRuntimeParticipant
    train = train_type(active)
    mapping_path = tmp_path / "coordinator-mapping.json"
    mapping_path.write_text(
        """
        {"idu":{"IDU-A":{"ID Volume":1.25}},
         "evap_index":{"EVAP-A":{"Evap Area":8.2,"Evap Volume":2.1}},
         "odu":{"ODU-A":{"OD Volume":2.5}},
         "compressor":{"CMP-A":{"Comp EER":3.2,"Comp cc":11}},
         "ref_type":{"R32":{}},"exp_type":{"EEV":{}},
         "odu_cascade":{"ODU-A":{"Available_Fins":["F&T"],"Available_Pis":["7"],"Available_Rows":["1"]}},
         "cond_specs":{"ODU-A F&T 7 1":{"Cond Area":3.5,"Cond Volume":4.5}}}
        """,
        encoding="utf-8",
    )
    mapping_service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_path))
    )
    mapping = MappingRuntimeParticipant(active, mapping_service)
    coordinator = RuntimeGenerationCoordinator(
        repository, (definition, predict, train, mapping)
    )
    first_target = first.targets[0]
    second = replace(
        first,
        generation=replace(
            first.generation,
            generation_id="generation-b",
            parent_generation_id=first.generation.generation_id,
        ),
        features=tuple(
            replace(
                item,
                column_key="cooling_power_runtime_b",
                ml_name="Cooling Power Runtime B",
            )
            if item.identity == first_target.feature_identity else item
            for item in first.features
        ),
        derived=(replace(first.derived[0], zero_value=4.0), *first.derived[1:]),
        targets=(
            replace(first_target, ml_name="Cooling Power Runtime B"),
            *first.targets[1:],
        ),
    )
    repository.publish(second)
    return coordinator, (definition, predict, train, mapping), controller


def test_real_participants_prepare_a_then_commit_b_with_owner_parity(tmp_path):
    coordinator, participants, controller = _coordinator_setup(tmp_path)
    definition, predict, train, mapping = participants
    session = predict.composition.session
    case_id = session.case_order[0]
    install_projection_results(
        session,
        ResultRow(case_id, "complete", {"cooling_power": "123"}, "before cutover"),
    )

    assert coordinator.prepare_all().code == "prepared"
    assert len({item.active_generation_id for item in participants}) == 1
    assert "generation-b" not in {item.active_generation_id for item in participants}
    assert predict.composition.runtime_snapshot.derived.definitions[0].zero_value == 0.0
    status = coordinator.commit_all()

    assert status.code == "applied"
    assert {item.active_generation_id for item in participants} == {"generation-b"}
    assert controller.runtime_generation_id == "generation-b"
    assert predict.composition.runtime_snapshot.derived.definitions[0].zero_value == 4.0
    assert session.result_for_case(case_id) == ResultRow(
        case_id,
        "complete",
        {"cooling_power_runtime_b": "123"},
        "before cutover",
    )
    assert train.registry_snapshot.generation_id == "generation-b"
    assert mapping.active_snapshot.manifest.generation.generation_id == "generation-b"


def test_real_participant_commit_failure_rolls_definition_and_predict_back_to_a(tmp_path):
    coordinator, participants, controller = _coordinator_setup(
        tmp_path, failing_train=True
    )
    _definition, predict, _train, _mapping = participants
    session = predict.composition.session
    case_id = session.case_order[0]
    original = ResultRow(
        case_id, "partial", {"cooling_power": "321"}, "original warning"
    )
    install_projection_results(session, original)

    status = coordinator.request_cutover()

    assert status.blocker_code == "participant_commit_failed"
    assert len({item.active_generation_id for item in participants}) == 1
    assert "generation-b" not in {item.active_generation_id for item in participants}
    assert controller.runtime_generation_id != "generation-b"
    assert predict.composition.runtime_snapshot.derived.definitions[0].zero_value == 0.0
    assert predict.composition.runtime_snapshot.target_result_keys[0][1] == "cooling_power"
    assert session.result_for_case(case_id) == original
