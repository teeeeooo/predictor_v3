"""Shared read/publish contract for immutable Definition generations."""

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
    manifest: UnifiedFeatureManifest
    projections: ContractProjections
    fingerprints: ScopedFingerprints
    path: Path


@dataclass(frozen=True)
class GenerationPublishResult:
    generation_id: str
    previous_generation_id: str
    generation_path: Path


class DataDefinitionGenerationRepositoryPort(Protocol):
    def read_active(self) -> GenerationSnapshot: ...

    def read_generation(self, generation_id: str) -> GenerationSnapshot: ...

    def publish(self, manifest: UnifiedFeatureManifest) -> GenerationPublishResult: ...

    def rollback(self, generation_id: str) -> GenerationSnapshot: ...
