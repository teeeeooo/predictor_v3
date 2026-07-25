"""Outbound adapters for the shared training result contract."""

from .artifacts import TrainingResultArtifactWriter, artifact_sha256
from .evidence import FilesystemTrainingEvidenceAdapter

__all__ = [
    "FilesystemTrainingEvidenceAdapter",
    "TrainingResultArtifactWriter",
    "artifact_sha256",
]
