"""Test-owned setup for repository-issued generation authority."""

from tempfile import TemporaryDirectory

from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)


def repository_issued_generation(manifest):  # noqa: ANN001, ANN201
    """Publish and re-read one valid manifest through the production owner."""
    with TemporaryDirectory(prefix="predict-generation-authority-") as root:
        repository = DataDefinitionGenerationRepository(root)
        repository.publish(manifest)
        return repository.read_active()
