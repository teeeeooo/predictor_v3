"""Composition boundary for training evidence, reports, and publication."""

from __future__ import annotations

from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.adapters.training_results import (
    FilesystemTrainingEvidenceAdapter,
    TrainingResultArtifactWriter,
)
from apps.train.application.candidate_publication import CandidatePublisher


def build_candidate_publisher(
    repository: ModelLifecycleRepository,
) -> CandidatePublisher:
    return CandidatePublisher(
        repository,
        evidence=FilesystemTrainingEvidenceAdapter(repository),
        artifacts=TrainingResultArtifactWriter(),
    )
