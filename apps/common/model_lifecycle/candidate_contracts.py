"""Versioned immutable Candidate manifest and result payloads."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

CANDIDATE_SCHEMA_VERSION = "model_candidate_manifest.v2"
LEGACY_CANDIDATE_SCHEMA_VERSION = "model_candidate_manifest.v1"
RESULT_SCHEMA_VERSION = "model_candidate_result.v1"
ARTIFACT_FORMAT_VERSION = "multi_target_joblib.v1"
ANALYSIS_ARTIFACT_CATEGORIES = {
    "training_result",
    "target_metrics",
    "selected_features",
    "rfecv_ranking",
    "feature_importance",
    "optuna_trials",
    "best_parameters",
    "preprocessing_summary",
    "training_report",
    "core_training_evidence",
    "shap",
}
ROOT_ANALYSIS_ARTIFACTS = {
    "core_training_evidence.json",
    "training_result.json",
    "training_report.xlsx",
}
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


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
        path, category, required = parse_analysis_artifact_descriptor(payload)
        sha256 = payload.get("sha256")
        if (
            type(sha256) is not str
            or _SHA256_PATTERN.fullmatch(sha256) is None
        ):
            raise ValueError("Candidate analysis artifact sha256 is invalid")
        return cls(
            path=path,
            sha256=sha256,
            category=category,
            required=required,
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


def parse_analysis_artifact_descriptor(
    payload: dict[str, object],
) -> tuple[str, str, bool]:
    if not isinstance(payload, dict):
        raise ValueError("Candidate analysis artifact reference must be an object")
    path = canonical_analysis_artifact_path(payload.get("path"))
    category = payload.get("category")
    if (
        type(category) is not str
        or not category
        or category not in ANALYSIS_ARTIFACT_CATEGORIES
    ):
        raise ValueError("Candidate analysis artifact category is invalid")
    required = payload.get("required")
    if type(required) is not bool:
        raise ValueError("Candidate analysis artifact required must be a boolean")
    return path, category, required


def canonical_analysis_artifact_path(value: object) -> str:
    """Accept only the persisted POSIX-relative canonical artifact spelling."""
    if type(value) is not str or not value or "\\" in value:
        raise ValueError("Candidate analysis artifact path is invalid")
    parts = value.split("/")
    if (
        value.startswith("/")
        or any(part in {"", ".", ".."} for part in parts)
        or value != "/".join(parts)
    ):
        raise ValueError("Candidate analysis artifact path is not canonical")
    if len(parts) == 1:
        if value not in ROOT_ANALYSIS_ARTIFACTS:
            raise ValueError("Candidate analysis artifact is outside its namespace")
    elif parts[0] != "analysis":
        raise ValueError("Candidate analysis artifact is outside its namespace")
    return value
