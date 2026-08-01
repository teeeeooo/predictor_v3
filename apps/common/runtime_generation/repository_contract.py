"""Shared read/publish contract for immutable Definition generations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from weakref import ref

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


_ISSUED_GENERATIONS: dict[
    int,
    tuple[ref[GenerationSnapshot], tuple[object, ...]],
] = {}


def _issue_generation_snapshot(
    manifest: UnifiedFeatureManifest,
    projections: ContractProjections,
    fingerprints: ScopedFingerprints,
    path: Path,
) -> GenerationSnapshot:
    """Issue one exact snapshot after its trusted owner validates the bundle."""
    snapshot = GenerationSnapshot(manifest, projections, fingerprints, path)
    identity = id(snapshot)

    def release(reference: ref[GenerationSnapshot]) -> None:
        current = _ISSUED_GENERATIONS.get(identity)
        if current is not None and current[0] is reference:
            _ISSUED_GENERATIONS.pop(identity, None)

    reference = ref(snapshot, release)
    _ISSUED_GENERATIONS[identity] = (reference, _generation_payload(snapshot))
    return snapshot


def require_issued_generation_snapshot(snapshot: GenerationSnapshot) -> None:
    """Reject caller-assembled or replaced snapshots as generation authority."""
    issued = _ISSUED_GENERATIONS.get(id(snapshot))
    if (
        issued is None
        or issued[0]() is not snapshot
        or issued[1] != _generation_payload(snapshot)
    ):
        raise ValueError(
            "Predict runtime requires a repository-issued generation snapshot"
        )


def _generation_payload(snapshot: GenerationSnapshot) -> tuple[object, ...]:
    return (
        snapshot.manifest,
        snapshot.projections,
        snapshot.fingerprints,
        snapshot.path,
    )


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
