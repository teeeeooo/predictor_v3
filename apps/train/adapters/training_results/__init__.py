"""Outbound adapters for the shared training result contract."""

from .artifacts import (
    MinimalTrainingResultEvidenceWriter,
    TrainingResultArtifactWriter,
    artifact_sha256,
)
from .evidence import FilesystemTrainingEvidenceAdapter

__all__ = [
    "FilesystemTrainingEvidenceAdapter",
    "MinimalTrainingResultEvidenceWriter",
    "TrainingResultArtifactWriter",
    "artifact_sha256",
]
