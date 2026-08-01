"""Standalone Predict reload and stale-prediction blocking."""

from dataclasses import replace

from apps.common.runtime_generation import PreparedParticipant
from apps.predict.application.runtime_generation import StandalonePredictGenerationGuard
from apps.train.adapters.data_definition_generation_repository import DataDefinitionGenerationRepository
from core.data_definition.contract import bootstrap_manifest


class Participant:
    name = "Predict"

    def __init__(self, generation):  # noqa: ANN001
        self.generation = generation
        self.fail = False
        self.model_compatibility = type("Evidence", (), {"status": "compatible"})()

    @property
    def active_generation_id(self):  # noqa: ANN201
        return self.generation

    def revision_token(self):  # noqa: ANN201
        return self.generation

    def prepare(self, candidate):  # noqa: ANN001, ANN201
        if self.fail:
            raise RuntimeError("reload failed")
        return PreparedParticipant(self.name, candidate.generation_id, self.generation, candidate.generation_id)

    def commit(self, prepared):  # noqa: ANN001, ANN201
        prior = self.generation
        self.generation = prepared.payload
        return prior

    def rollback(self, prior):  # noqa: ANN001
        self.generation = prior

    def abort(self, prepared):  # noqa: ANN001
        return None

    def finalize(self, prior):  # noqa: ANN001
        return None


def test_prediction_boundary_reloads_latest_or_blocks_without_changing_active(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    first = bootstrap_manifest()
    repository.publish(first)
    participant = Participant(first.generation.generation_id)
    guard = StandalonePredictGenerationGuard(repository, participant)
    second = replace(first, generation=replace(first.generation, generation_id="b", parent_generation_id=first.generation.generation_id))
    repository.publish(second)

    assert guard.ensure_current()
    assert participant.active_generation_id == "b"

    third = replace(second, generation=replace(second.generation, generation_id="c", parent_generation_id="b"))
    repository.publish(third)
    participant.fail = True
    assert not guard.ensure_current()
    assert participant.active_generation_id == "b"
    assert guard.status == "Reload failed"
