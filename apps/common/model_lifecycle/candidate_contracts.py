"""Versioned immutable Candidate manifest and result payloads."""

from __future__ import annotations

from dataclasses import asdict, dataclass

CANDIDATE_SCHEMA_VERSION = "model_candidate_manifest.v1"
RESULT_SCHEMA_VERSION = "model_candidate_result.v1"
ARTIFACT_FORMAT_VERSION = "multi_target_joblib.v1"


@dataclass(frozen=True)
class TargetArtifactContract:
    identity: str
    ml_name: str
    feature_names: tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "TargetArtifactContract":
        return cls(
            identity=str(payload["identity"]),
            ml_name=str(payload["ml_name"]),
            feature_names=tuple(str(item) for item in payload["feature_names"]),
        )


@dataclass(frozen=True)
class CandidateManifest:
    candidate_id: str
    run_id: str
    created_at: str
    source: str
    model_sha256: str
    definition_generation_id: str
    registry_fingerprint: str
    ordered_ml_fingerprint: str
    derived_semantics_fingerprint: str
    one_hot_fingerprint: str
    preprocessing_version: str
    targets: tuple[TargetArtifactContract, ...]
    promotion_eligible: bool
    blocking_reasons: tuple[str, ...] = ()
    contains_unpublished_features: bool = False
    original_model_sha256: str = ""
    schema_version: str = CANDIDATE_SCHEMA_VERSION
    artifact_format_version: str = ARTIFACT_FORMAT_VERSION

    def to_payload(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CandidateManifest":
        if payload.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
            raise ValueError("unsupported Candidate manifest schema version")
        return cls(
            **{
                key: payload[key]
                for key in cls.__dataclass_fields__
                if key not in {"targets", "blocking_reasons"}
            },
            targets=tuple(
                TargetArtifactContract.from_payload(item)
                for item in payload["targets"]
            ),
            blocking_reasons=tuple(
                str(item) for item in payload.get("blocking_reasons", ())
            ),
        )


@dataclass(frozen=True)
class CandidateResult:
    run_id: str
    candidate_id: str
    status: str
    publication_outcome: str
    promotion_eligible: bool
    blocking_reasons: tuple[str, ...] = ()
    schema_version: str = RESULT_SCHEMA_VERSION

    def to_payload(self) -> dict[str, object]:
        return asdict(self)
