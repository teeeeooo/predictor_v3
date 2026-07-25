"""Candidate artifact validation inside the model lifecycle owner."""

from __future__ import annotations

import hashlib
from pathlib import Path

import joblib

from .candidate_contracts import CandidateManifest
from .errors import CandidateCorruptionError
from .filesystem import LifecycleFilesystem


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
    for artifact in manifest.analysis_artifacts:
        relative = Path(artifact.path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Candidate analysis artifact reference is unsafe")
        artifact_path = path / artifact.path
        if artifact_path.parent != path and path not in artifact_path.parents:
            raise ValueError("Candidate analysis artifact escapes Candidate root")
        filesystem.require_regular_file(artifact_path)
        with filesystem.open_regular(artifact_path) as source:
            if _sha256_stream(source) != artifact.sha256:
                raise ValueError(
                    f"Candidate analysis artifact hash mismatch: {artifact.path}"
                )
    if (
        manifest.schema_version != "model_candidate_manifest.v1"
        and not manifest.analysis_artifacts
    ):
        raise ValueError("Candidate required analysis artifacts are incomplete")
    _model_sha256, payload = load_candidate_model(
        filesystem,
        path / "model.pkl",
        expected_sha256=manifest.model_sha256,
    )
    _validate_model_bundle(payload, manifest)


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
