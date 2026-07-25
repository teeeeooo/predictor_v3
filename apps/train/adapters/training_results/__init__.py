"""Outbound adapters for the shared training result contract."""

from .artifacts import TrainingResultArtifactWriter, artifact_sha256

__all__ = ["TrainingResultArtifactWriter", "artifact_sha256"]
