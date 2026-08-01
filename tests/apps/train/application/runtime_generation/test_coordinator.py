"""Atomic coordinator happy-path, failure, rollback, and stale guards."""

from dataclasses import replace

from apps.common.runtime_generation import PreparedParticipant
from apps.train.adapters.data_definition_generation_repository import DataDefinitionGenerationRepository
from apps.train.application.runtime_generation import RuntimeGenerationCoordinator
from core.data_definition.contract import bootstrap_manifest


class FakeParticipant:
    def __init__(self, name, generation, *, fail_prepare=False, fail_commit=False, fail_rollback=False, fail_abort=False, mutate=None):  # noqa: ANN001
        self.name = name
        self.generation = generation
        self.revision = 0
        self.fail_prepare = fail_prepare
        self.fail_commit = fail_commit
        self.fail_rollback = fail_rollback
        self.fail_abort = fail_abort
        self.mutate = mutate
        self.aborted = 0
        self.rolled_back = 0
        self.finalized = 0

    @property
    def active_generation_id(self):  # noqa: ANN201
        return self.generation

    def revision_token(self):  # noqa: ANN201
        return f"{self.generation}:{self.revision}"

    def prepare(self, candidate):  # noqa: ANN001, ANN201
        if self.fail_prepare:
            raise RuntimeError("injected prepare failure")
        if self.mutate:
            self.mutate()
        return PreparedParticipant(self.name, candidate.generation_id, self.revision_token(), candidate.generation_id)

    def commit(self, prepared):  # noqa: ANN001, ANN201
        if self.fail_commit:
            raise RuntimeError("injected commit failure")
        prior = self.generation
        self.generation = prepared.payload
        return prior

    def rollback(self, prior):  # noqa: ANN001
        if self.fail_rollback:
            raise RuntimeError("injected rollback failure")
        self.generation = prior
        self.rolled_back += 1

    def abort(self, prepared):  # noqa: ANN001
        if self.fail_abort:
            raise RuntimeError("injected abort failure")
        self.aborted += 1

    def finalize(self, prior):  # noqa: ANN001
        self.finalized += 1


def _repository(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    second = replace(
        first,
        generation=replace(
            first.generation,
            generation_id="generation-b",
            parent_generation_id=first.generation.generation_id,
        ),
    )
    return repository, first, second


def test_all_ready_commits_every_participant_after_prepare(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = tuple(FakeParticipant(name, first.generation.generation_id) for name in ("definition", "predict", "train", "mapping"))
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)

    status = coordinator.request_cutover()

    assert status.message == "Saved and applied"
    assert {item.active_generation_id for item in participants} == {"generation-b"}
    assert status.active_generation == status.persisted_generation == "generation-b"
    assert {item.finalized for item in participants} == {1}


def test_explicit_prepare_keeps_active_state_until_commit(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = tuple(FakeParticipant(name, first.generation.generation_id) for name in ("definition", "predict", "train", "mapping"))
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)

    prepared = coordinator.prepare_all()
    assert prepared.code == "prepared"
    assert {item.active_generation_id for item in participants} == {first.generation.generation_id}
    assert {item.prepared_generation for item in prepared.participants} == {"generation-b"}

    committed = coordinator.commit_all()
    assert committed.code == "applied"


def test_prepare_failure_aborts_prepared_and_preserves_all_active_state(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = (
        FakeParticipant("definition", first.generation.generation_id),
        FakeParticipant("predict", first.generation.generation_id, fail_prepare=True),
        FakeParticipant("train", first.generation.generation_id),
        FakeParticipant("mapping", first.generation.generation_id),
    )
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)

    status = coordinator.request_cutover()

    assert status.message == "Saved; update pending"
    assert {item.active_generation_id for item in participants} == {first.generation.generation_id}
    assert participants[0].aborted == 1
    assert status.pending_generation == "generation-b"


def test_commit_failure_rolls_back_already_committed_participants(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = (
        FakeParticipant("definition", first.generation.generation_id),
        FakeParticipant("predict", first.generation.generation_id),
        FakeParticipant("train", first.generation.generation_id, fail_commit=True),
        FakeParticipant("mapping", first.generation.generation_id),
    )
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)

    status = coordinator.request_cutover()

    assert status.blocker_code == "participant_commit_failed"
    assert {item.active_generation_id for item in participants} == {first.generation.generation_id}
    assert participants[0].rolled_back == participants[1].rolled_back == 1


def test_revision_change_after_prepare_rejects_stale_candidate(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = [FakeParticipant(name, first.generation.generation_id) for name in ("definition", "predict", "train", "mapping")]
    participants[1].mutate = lambda: setattr(participants[3], "revision", 1)
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)

    status = coordinator.request_cutover()

    assert status.blocker_code == "stale_candidate"
    assert {item.active_generation_id for item in participants} == {first.generation.generation_id}


def test_newer_publication_between_prepare_and_commit_rejects_old_token(tmp_path):
    repository, first, second = _repository(tmp_path)
    participants = tuple(FakeParticipant(name, first.generation.generation_id) for name in ("definition", "predict", "train", "mapping"))
    coordinator = RuntimeGenerationCoordinator(repository, participants)
    repository.publish(second)
    assert coordinator.prepare_all().code == "prepared"
    third = replace(second, generation=replace(second.generation, generation_id="generation-c", parent_generation_id="generation-b"))
    repository.publish(third)

    status = coordinator.commit_all()

    assert status.blocker_code == "stale_candidate"
    assert {item.active_generation_id for item in participants} == {first.generation.generation_id}


def test_abort_and_rollback_failures_require_restart(tmp_path):
    repository, first, second = _repository(tmp_path)
    aborting = (
        FakeParticipant("definition", first.generation.generation_id, fail_abort=True),
        FakeParticipant("predict", first.generation.generation_id, fail_prepare=True),
    )
    coordinator = RuntimeGenerationCoordinator(repository, aborting)
    repository.publish(second)
    assert coordinator.request_cutover().blocker_code == "abort_failed"

    repository.rollback(first.generation.generation_id)
    third = replace(first, generation=replace(first.generation, generation_id="generation-d", parent_generation_id=first.generation.generation_id))
    repository.publish(third)
    committing = (
        FakeParticipant("definition", first.generation.generation_id, fail_rollback=True),
        FakeParticipant("predict", first.generation.generation_id, fail_commit=True),
    )
    coordinator = RuntimeGenerationCoordinator(repository, committing)
    assert coordinator.request_cutover().blocker_code == "rollback_failed"
