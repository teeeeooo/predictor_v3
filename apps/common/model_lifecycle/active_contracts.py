"""Versioned Active reference and controlled resolution payloads."""

from collections.abc import Mapping
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


def active_reference_from_payload(
    payload: Mapping[str, object],
) -> ActiveModelReference:
    """Deserialize and validate one atomic Active revision/history unit."""
    if not isinstance(payload, Mapping):
        raise ValueError("Active reference payload must be an object")
    if payload.get("schema_version") != ACTIVE_REFERENCE_SCHEMA_VERSION:
        raise ValueError("unsupported Active reference schema version")
    history = tuple(
        ActivationRecord(**item) for item in payload["history"]
    )
    reference = ActiveModelReference(
        candidate_id=payload["candidate_id"],
        revision=payload["revision"],
        activated_at=payload["activated_at"],
        history=history,
    )
    validate_active_reference(reference)
    return reference


def validate_active_reference(reference: ActiveModelReference) -> None:
    """Reject semantic disagreement inside the revisioned Active contract."""
    if (
        not _is_safe_candidate_identity(reference.candidate_id)
        or type(reference.revision) is not int
        or reference.revision < 1
        or not isinstance(reference.activated_at, str)
        or not reference.activated_at
        or not reference.history
    ):
        raise ValueError("Active reference metadata is invalid")
    for expected_revision, record in enumerate(reference.history, start=1):
        if (
            type(record.revision) is not int
            or record.revision != expected_revision
            or not _is_safe_candidate_identity(record.candidate_id)
            or not isinstance(record.activated_at, str)
            or not record.activated_at
            or not isinstance(record.source, str)
            or not record.source
        ):
            raise ValueError("Active reference history is invalid")
    latest = reference.history[-1]
    if (
        reference.candidate_id != latest.candidate_id
        or reference.revision != latest.revision
        or reference.activated_at != latest.activated_at
    ):
        raise ValueError(
            "Active reference current state and latest history are inconsistent"
        )


def _is_safe_candidate_identity(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not value.startswith(".")
        and "/" not in value
        and "\\" not in value
    )


@dataclass(frozen=True)
class ModelResolution:
    status: str
    model_path: str = ""
    candidate_id: str = ""
    revision: int = 0
    message: str = ""
