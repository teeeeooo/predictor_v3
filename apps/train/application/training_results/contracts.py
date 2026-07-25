"""Versioned Qt-free contract for training results and analysis artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TRAINING_RESULT_SCHEMA_VERSION = "training_result.v1"


@dataclass(frozen=True)
class TrainingAnalysisResult:
    """One canonical result used by GUI, reports, and future headless callers."""

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
        if payload.get("schema_version") != TRAINING_RESULT_SCHEMA_VERSION:
            raise ValueError("unsupported training result schema version")
        _require_mapping(payload, "run", "training_context", "baseline")
        _require_mapping(payload, "preprocessing", "promotion_eligibility")
        targets = payload.get("targets")
        artifacts = payload.get("artifacts")
        if not isinstance(targets, list) or not isinstance(artifacts, list):
            raise ValueError("training result targets/artifacts must be arrays")
        return cls(
            run=dict(payload["run"]),
            training_context=dict(payload["training_context"]),
            targets=tuple(dict(item) for item in targets),
            baseline=dict(payload["baseline"]),
            preprocessing=dict(payload["preprocessing"]),
            artifacts=tuple(dict(item) for item in artifacts),
            promotion_eligibility=dict(payload["promotion_eligibility"]),
            blocking_reasons=tuple(
                dict(item) for item in payload.get("blocking_reasons", ())
            ),
            optional_capabilities=dict(payload.get("optional_capabilities", {})),
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
            raise ValueError(f"training result {name} must be an object")
