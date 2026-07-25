"""Lifecycle-readable, versioned training analysis contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .candidate_contracts import (
    CandidateArtifactContractError,
    parse_analysis_artifact_descriptor,
)

TRAINING_RESULT_SCHEMA_VERSION = "training_result.v1"


@dataclass(frozen=True)
class TrainingAnalysisResult:
    """Canonical Qt-free result shared by publication and lifecycle validation."""

    run: dict[str, Any]
    training_context: dict[str, Any]
    targets: tuple[dict[str, Any], ...]
    baseline: dict[str, Any]
    preprocessing: dict[str, Any]
    artifacts: tuple[dict[str, Any], ...]
    promotion_eligibility: dict[str, Any]
    blocking_reasons: tuple[dict[str, str], ...] = ()
    optional_capabilities: dict[str, Any] | None = None
    schema_version: str = TRAINING_RESULT_SCHEMA_VERSION

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["optional_capabilities"] = self.optional_capabilities or {
            "shap": {
                "status": "not_used",
                "reason": "SHAP was not requested for this run.",
            }
        }
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TrainingAnalysisResult":
        if not isinstance(payload, dict):
            raise CandidateArtifactContractError(
                "training result payload must be an object"
            )
        if payload.get("schema_version") != TRAINING_RESULT_SCHEMA_VERSION:
            raise CandidateArtifactContractError(
                "unsupported training result schema version"
            )
        _require_mapping(payload, "run", "training_context", "baseline")
        _require_mapping(payload, "preprocessing", "promotion_eligibility")
        targets = _mapping_array(payload, "targets")
        artifacts = _mapping_array(payload, "artifacts")
        blocking = _mapping_array(payload, "blocking_reasons", default=())
        parsed_artifacts = tuple(
            {
                "path": path,
                "category": category,
                "required": required,
            }
            for path, category, required in (
                parse_analysis_artifact_descriptor(item)
                for item in artifacts
            )
        )
        artifact_paths = [item["path"] for item in parsed_artifacts]
        artifact_categories = [item["category"] for item in parsed_artifacts]
        if (
            "" in artifact_paths
            or "" in artifact_categories
            or len(artifact_paths) != len(set(artifact_paths))
            or len(artifact_categories) != len(set(artifact_categories))
        ):
            raise CandidateArtifactContractError(
                "training result artifact identity is invalid"
            )
        optional = payload.get("optional_capabilities", {})
        if not isinstance(optional, dict):
            raise CandidateArtifactContractError(
                "training result optional_capabilities must be an object"
            )
        return cls(
            run=dict(payload["run"]),
            training_context=dict(payload["training_context"]),
            targets=targets,
            baseline=dict(payload["baseline"]),
            preprocessing=dict(payload["preprocessing"]),
            artifacts=parsed_artifacts,
            promotion_eligibility=dict(payload["promotion_eligibility"]),
            blocking_reasons=blocking,
            optional_capabilities=dict(optional),
            schema_version=str(payload["schema_version"]),
        )


def load_training_analysis_payload(
    payload: dict[str, Any] | None,
) -> TrainingAnalysisResult | dict[str, str]:
    """Read supported results and project legacy absence without mutation."""
    if payload is None:
        return {
            "status": "unavailable",
            "reason": "Candidate predates the training analysis contract.",
        }
    return TrainingAnalysisResult.from_payload(payload)


def _require_mapping(payload: dict[str, Any], *names: str) -> None:
    for name in names:
        if not isinstance(payload.get(name), dict):
            raise CandidateArtifactContractError(
                f"training result {name} must be an object"
            )


def _mapping_array(
    payload: dict[str, Any],
    name: str,
    *,
    default: object = None,
) -> tuple[dict[str, Any], ...]:
    value = payload.get(name, default)
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, dict) for item in value
    ):
        raise CandidateArtifactContractError(
            f"training result {name} must be an array of objects"
        )
    return tuple(dict(item) for item in value)
