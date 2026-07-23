"""Versioned Active reference and controlled resolution payloads."""

from dataclasses import asdict, dataclass

ACTIVE_REFERENCE_SCHEMA_VERSION = "active_model_reference.v1"


@dataclass(frozen=True)
class ActivationRecord:
    revision: int
    candidate_id: str
    activated_at: str
    source: str


@dataclass(frozen=True)
class ActiveModelReference:
    candidate_id: str
    revision: int
    activated_at: str
    history: tuple[ActivationRecord, ...]
    schema_version: str = ACTIVE_REFERENCE_SCHEMA_VERSION

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ModelResolution:
    status: str
    model_path: str = ""
    candidate_id: str = ""
    revision: int = 0
    message: str = ""
