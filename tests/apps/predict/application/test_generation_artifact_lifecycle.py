"""Lifecycle regressions for sealed Predict generation artifacts."""

from dataclasses import replace
from uuid import uuid4

import pytest

from apps.common.runtime_generation import GenerationCandidate, PreparedParticipant
from apps.predict.application.model_compatibility import ModelCompatibilityEvidence
from apps.predict.application.runtime_generation_participant import (
    PredictRuntimeParticipant,
)
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.composition import build_predict_workspace_composition
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.runtime_generation import RuntimeGenerationCoordinator
from core.data_definition.contract import bootstrap_manifest


class _FailingParticipant:
    name = "Failing participant"

    def __init__(self, generation_id: str) -> None:
        self.generation_id = generation_id

    @property
    def active_generation_id(self) -> str:
        return self.generation_id

    def revision_token(self) -> str:
        return self.generation_id

    def prepare(self, candidate):  # noqa: ANN001, ANN201
        return PreparedParticipant(
            self.name, candidate.generation_id, self.revision_token(), None
        )

    def commit(self, prepared):  # noqa: ANN001, ANN201
        raise RuntimeError("injected commit failure")

    def rollback(self, prior):  # noqa: ANN001
        return None

    def abort(self, prepared):  # noqa: ANN001
        return None

    def finalize(self, prior):  # noqa: ANN001
        return None


def _setup(tmp_path):  # noqa: ANN001, ANN202
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    active = repository.read_active()
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        initial_empty_rows=1,
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    return repository, first, participant


def _publish(repository, manifest, generation_id):  # noqa: ANN001, ANN202
    candidate = replace(
        manifest,
        generation=replace(
            manifest.generation,
            generation_id=generation_id,
            parent_generation_id=manifest.generation.generation_id,
        ),
    )
    repository.publish(candidate)
    return candidate


def _candidate(snapshot, participant):  # noqa: ANN001, ANN202
    return GenerationCandidate(
        snapshot,
        snapshot.manifest.generation.generation_id,
        ((participant.name, participant.revision_token()),),
        uuid4().hex,
    )


def test_prepare_abort_releases_migration_artifact_and_repeats_bounded(tmp_path):
    repository, first, participant = _setup(tmp_path)
    _publish(repository, first, "generation-b")
    coordinator = RuntimeGenerationCoordinator(repository, (participant,))
    session = participant.composition.session

    for _index in range(5):
        assert coordinator.prepare_all().code == "prepared"
        assert session.issued_projection_count == 1
        assert coordinator.abort_prepared_candidate().code == "aborted"
        assert session.issued_projection_count == 0


def test_successful_cutovers_finalize_obsolete_rollback_snapshots(tmp_path):
    repository, manifest, participant = _setup(tmp_path)
    coordinator = RuntimeGenerationCoordinator(repository, (participant,))
    session = participant.composition.session

    for index in range(1, 6):
        manifest = _publish(repository, manifest, f"generation-{index}")
        assert coordinator.request_cutover().code == "applied"
        assert session.issued_projection_count == 0


def test_failed_later_commit_rolls_predict_back_and_releases_all_artifacts(tmp_path):
    repository, first, participant = _setup(tmp_path)
    _publish(repository, first, "generation-b")
    failing = _FailingParticipant(first.generation.generation_id)
    coordinator = RuntimeGenerationCoordinator(repository, (participant, failing))
    session = participant.composition.session
    before_revision = session.revision

    status = coordinator.request_cutover()

    assert status.blocker_code == "participant_commit_failed"
    assert participant.active_generation_id == first.generation.generation_id
    assert session.revision == before_revision
    assert session.issued_projection_count == 0


def test_direct_commit_keeps_rollback_snapshot_until_terminal_disposition(tmp_path):
    repository, first, participant = _setup(tmp_path)
    _publish(repository, first, "generation-b")
    snapshot = repository.read_active()
    prepared = participant.prepare(_candidate(snapshot, participant))
    session = participant.composition.session

    prior = participant.commit(prepared)

    assert session.issued_projection_count == 1
    participant.rollback(prior)
    assert session.issued_projection_count == 0
    with pytest.raises(ValueError, match="not issued"):
        participant.rollback(prior)


def test_successful_direct_commit_finalize_prevents_late_rollback_replay(tmp_path):
    repository, first, participant = _setup(tmp_path)
    _publish(repository, first, "generation-b")
    snapshot = repository.read_active()
    prepared = participant.prepare(_candidate(snapshot, participant))
    session = participant.composition.session
    prior = participant.commit(prepared)

    participant.finalize(prior)

    assert session.issued_projection_count == 0
    with pytest.raises(ValueError, match="not issued"):
        participant.rollback(prior)
