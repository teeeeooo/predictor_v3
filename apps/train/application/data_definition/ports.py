"""Outbound port for canonical Data Definition generation persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.data_definition.contract import (
    ContractProjections,
    ScopedFingerprints,
    UnifiedFeatureManifest,
)


@dataclass(frozen=True)
class GenerationSnapshot:
    """Validated immutable generation and its active projection location."""

    manifest: UnifiedFeatureManifest
    projections: ContractProjections
    fingerprints: ScopedFingerprints
    path: Path


@dataclass(frozen=True)
class GenerationPublishResult:
    """Publication result returned without exposing filesystem operations."""

    generation_id: str
    previous_generation_id: str
    generation_path: Path


class DataDefinitionGenerationRepositoryPort(Protocol):
    """Minimal persistence operations required by the Definition use case."""

    def read_active(self) -> GenerationSnapshot:
        """Return the currently active validated generation snapshot."""

    def read_generation(self, generation_id: str) -> GenerationSnapshot:
        """Return one validated immutable historical generation."""

    def publish(self, manifest: UnifiedFeatureManifest) -> GenerationPublishResult:
        """Publish a candidate and make it active as one repository operation."""

    def rollback(self, generation_id: str) -> GenerationSnapshot:
        """Repoint active state to a validated historical generation."""
