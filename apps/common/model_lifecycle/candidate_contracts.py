"""Versioned immutable Candidate manifest and result payloads."""

from __future__ import annotations

from dataclasses import asdict, dataclass

CANDIDATE_SCHEMA_VERSION = "model_candidate_manifest.v2"
LEGACY_CANDIDATE_SCHEMA_VERSION = "model_candidate_manifest.v1"
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
class CandidateArtifactReference:
    path: str
    sha256: str
    category: str
    required: bool = True

    @classmethod
    def from_payload(
        cls, payload: dict[str, object]
    ) -> "CandidateArtifactReference":
        return cls(
            path=str(payload["path"]),
            sha256=str(payload["sha256"]),
            category=str(payload["category"]),
            required=bool(payload.get("required", True)),
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
    analysis_contract_version: str = ""
    analysis_artifacts: tuple[CandidateArtifactReference, ...] = ()
    schema_version: str = CANDIDATE_SCHEMA_VERSION
    artifact_format_version: str = ARTIFACT_FORMAT_VERSION

    def to_payload(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CandidateManifest":
        schema_version = payload.get("schema_version")
        if schema_version not in {
            LEGACY_CANDIDATE_SCHEMA_VERSION,
            CANDIDATE_SCHEMA_VERSION,
        }:
            raise ValueError("unsupported Candidate manifest schema version")
        return cls(
            **{
                key: payload[key]
                for key in cls.__dataclass_fields__
                if key in payload and key not in {
                    "targets", "blocking_reasons", "analysis_artifacts"
                }
            },
            targets=tuple(
                TargetArtifactContract.from_payload(item)
                for item in payload["targets"]
            ),
            blocking_reasons=tuple(
                str(item) for item in payload.get("blocking_reasons", ())
            ),
            analysis_artifacts=tuple(
                CandidateArtifactReference.from_payload(item)
                for item in payload.get("analysis_artifacts", ())
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

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CandidateResult":
        if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
            raise ValueError("unsupported Candidate result schema version")
        return cls(
            run_id=str(payload["run_id"]),
            candidate_id=str(payload["candidate_id"]),
            status=str(payload["status"]),
            publication_outcome=str(payload["publication_outcome"]),
            promotion_eligible=bool(payload["promotion_eligible"]),
            blocking_reasons=tuple(payload.get("blocking_reasons", ())),
        )
