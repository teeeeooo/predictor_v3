"""Candidate artifact validation inside the model lifecycle owner."""

from __future__ import annotations

import hashlib
from pathlib import Path

import joblib

from .candidate_contracts import (
    CANDIDATE_SCHEMA_VERSION,
    LEGACY_CANDIDATE_SCHEMA_VERSION,
    CandidateManifest,
    canonical_analysis_artifact_path,
)
from .errors import CandidateCorruptionError
from .filesystem import LifecycleFilesystem
from .training_result_contracts import (
    TRAINING_RESULT_SCHEMA_VERSION,
    TrainingAnalysisResult,
)


REQUIRED_ANALYSIS_ARTIFACTS = {
    "training_result.json": "training_result",
    "analysis/target_metrics.csv": "target_metrics",
    "analysis/selected_features.csv": "selected_features",
    "analysis/rfecv_ranking.csv": "rfecv_ranking",
    "analysis/feature_importance.csv": "feature_importance",
    "analysis/optuna_trials.csv": "optuna_trials",
    "analysis/best_parameters.csv": "best_parameters",
    "analysis/preprocessing_summary.csv": "preprocessing_summary",
    "training_report.xlsx": "training_report",
}
OPTIONAL_ANALYSIS_ARTIFACT_CATEGORIES = {
    "core_training_evidence",
    "shap",
}


def validate_candidate_files(
    filesystem: LifecycleFilesystem,
    path: Path,
    manifest: CandidateManifest,
    *,
    require_metadata: bool = False,
) -> None:
    filesystem.require_directory(path)
    required = ["model.pkl"]
    if require_metadata:
        required.extend(("manifest.json", "result.json"))
    for name in required:
        filesystem.require_regular_file(path / name)
    _validate_analysis_contract(filesystem, path, manifest)
    for artifact in manifest.analysis_artifacts:
        canonical_path = canonical_analysis_artifact_path(artifact.path)
        artifact_path = path / canonical_path
        if artifact_path.parent != path and path not in artifact_path.parents:
            raise ValueError("Candidate analysis artifact escapes Candidate root")
        filesystem.require_regular_file(artifact_path)
        with filesystem.open_regular(artifact_path) as source:
            if _sha256_stream(source) != artifact.sha256:
                raise ValueError(
                    f"Candidate analysis artifact hash mismatch: {artifact.path}"
                )
    _model_sha256, payload = load_candidate_model(
        filesystem,
        path / "model.pkl",
        expected_sha256=manifest.model_sha256,
    )
    _validate_model_bundle(payload, manifest)


def _validate_analysis_contract(
    filesystem: LifecycleFilesystem,
    path: Path,
    manifest: CandidateManifest,
) -> None:
    if manifest.schema_version == LEGACY_CANDIDATE_SCHEMA_VERSION:
        return
    if manifest.schema_version != CANDIDATE_SCHEMA_VERSION:
        raise ValueError("unsupported Candidate manifest schema version")
    if manifest.analysis_contract_version != TRAINING_RESULT_SCHEMA_VERSION:
        raise ValueError("unsupported Candidate analysis contract version")
    references = manifest.analysis_artifacts
    paths = [canonical_analysis_artifact_path(item.path) for item in references]
    categories = [item.category for item in references]
    if len(paths) != len(set(paths)) or len(categories) != len(set(categories)):
        raise ValueError("Candidate analysis artifact path or identity is duplicated")
    by_path = {item.path: item for item in references}
    for required_path, category in REQUIRED_ANALYSIS_ARTIFACTS.items():
        reference = by_path.get(required_path)
        if reference is None:
            raise ValueError(
                f"Candidate required analysis artifact is missing: {required_path}"
            )
        if reference.category != category or not reference.required:
            raise ValueError(
                f"Candidate required analysis artifact contract is invalid: {required_path}"
            )
    unexpected_required = [
        item.path for item in references
        if item.required and item.path not in REQUIRED_ANALYSIS_ARTIFACTS
    ]
    if unexpected_required:
        raise ValueError("Candidate has an unknown required analysis artifact")
    invalid_optional = [
        item.path for item in references
        if item.path not in REQUIRED_ANALYSIS_ARTIFACTS
        and (
            item.required
            or item.category not in OPTIONAL_ANALYSIS_ARTIFACT_CATEGORIES
        )
    ]
    if invalid_optional:
        raise ValueError("Candidate optional analysis artifact contract is invalid")
    structured_payload = filesystem.read_json(path / "training_result.json")
    if not isinstance(structured_payload, dict):
        raise ValueError("training result payload must be an object")
    if structured_payload.get("schema_version") != manifest.analysis_contract_version:
        raise ValueError("Candidate analysis manifest/result version mismatch")
    structured = TrainingAnalysisResult.from_payload(structured_payload)
    payload_refs = {
        (item["path"], item["category"], item["required"])
        for item in structured.artifacts
    }
    manifest_refs = {
        (item.path, item.category, item.required) for item in references
    }
    if payload_refs != manifest_refs:
        raise ValueError("Candidate analysis artifact manifest/result mismatch")


def load_candidate_model(
    filesystem: LifecycleFilesystem,
    model_path: Path,
    *,
    expected_sha256: str = "",
) -> tuple[str, object]:
    filesystem.require_regular_file(model_path)
    with filesystem.open_regular(model_path) as source:
        model_sha256 = _sha256_stream(source)
        if expected_sha256 and model_sha256 != expected_sha256:
            raise ValueError("Candidate model hash mismatch")
        source.seek(0)
        try:
            payload = joblib.load(source)
        except Exception as exc:
            raise CandidateCorruptionError(
                f"Candidate model cannot be deserialized: {str(exc).splitlines()[0]}"
            ) from exc
    return model_sha256, payload


def _validate_model_bundle(payload: object, manifest: CandidateManifest) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Candidate model bundle is invalid")
    models, features = payload.get("models"), payload.get("features")
    if not isinstance(models, dict) or not isinstance(features, dict):
        raise ValueError("Candidate model bundle is incomplete")
    expected = tuple(item.ml_name for item in manifest.targets)
    if set(models) != set(expected) or set(features) != set(expected):
        raise ValueError("Candidate production target order is incomplete")
    for target in manifest.targets:
        if tuple(features[target.ml_name]) != target.feature_names:
            raise ValueError(f"Candidate feature order mismatch: {target.ml_name}")
    if (
        manifest.promotion_eligible
        and payload.get("preprocess_version") != manifest.preprocessing_version
    ):
        raise ValueError("Candidate preprocessing version mismatch")
    contract = payload.get("training_contract")
    expected_contract = {
        "generation_id": manifest.definition_generation_id,
        "registry_fingerprint": manifest.registry_fingerprint,
        "ordered_ml_fingerprint": manifest.ordered_ml_fingerprint,
        "derived_semantics_fingerprint": manifest.derived_semantics_fingerprint,
        "one_hot_fingerprint": manifest.one_hot_fingerprint,
    }
    if manifest.promotion_eligible and (
        not isinstance(contract, dict)
        or any(contract.get(key) != value for key, value in expected_contract.items())
    ):
        raise ValueError("Candidate runtime fingerprint metadata mismatch")


def _sha256_stream(source) -> str:  # noqa: ANN001
    digest = hashlib.sha256()
    for block in iter(lambda: source.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()
