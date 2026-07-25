"""Qt-free structured evidence produced by the core ML training pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CORE_EVIDENCE_VERSION = "core_training_evidence.v1"


@dataclass(frozen=True)
class CoreTrainingEvidence:
    """Core-owned evaluation semantics before application-level publication."""

    started_at: str
    finished_at: str
    duration_seconds: float
    training_data_sha256: str
    training_data_rows: int
    evaluation_context: dict[str, Any]
    targets: tuple[dict[str, Any], ...]
    preprocessing: dict[str, Any]
    status: str = "complete"
    blocking_reasons: tuple[str, ...] = ()
    schema_version: str = CORE_EVIDENCE_VERSION

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CoreTrainingEvidence":
        if payload.get("schema_version") != CORE_EVIDENCE_VERSION:
            raise ValueError("unsupported core training evidence schema version")
        return cls(
            started_at=str(payload["started_at"]),
            finished_at=str(payload["finished_at"]),
            duration_seconds=float(payload["duration_seconds"]),
            training_data_sha256=str(payload["training_data_sha256"]),
            training_data_rows=int(payload["training_data_rows"]),
            evaluation_context=dict(payload["evaluation_context"]),
            targets=tuple(dict(item) for item in payload["targets"]),
            preprocessing=dict(payload["preprocessing"]),
            status=str(payload.get("status", "complete")),
            blocking_reasons=tuple(
                str(item) for item in payload.get("blocking_reasons", ())
            ),
            schema_version=str(payload["schema_version"]),
        )


@dataclass(frozen=True)
class CoreTrainingOutput:
    """Model-training return value used by the child-process adapter."""

    summary: str
    evidence: CoreTrainingEvidence
    failed_targets: tuple[dict[str, str], ...] = field(default_factory=tuple)
