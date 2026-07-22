"""Promoted-model compatibility evidence for one Definition generation."""

from dataclasses import dataclass
from pathlib import Path

import joblib


@dataclass(frozen=True)
class ModelCompatibilityEvidence:
    status: str
    summary: str


def inspect_model_compatibility(model_file: str, snapshot) -> ModelCompatibilityEvidence:  # noqa: ANN001
    path = Path(model_file)
    if not path.is_file():
        return ModelCompatibilityEvidence("retraining-required", "Active model artifact is missing.")
    try:
        payload = joblib.load(path)
    except Exception:
        return ModelCompatibilityEvidence("reload-required", "Active model metadata could not be read safely.")
    if not isinstance(payload, dict):
        return ModelCompatibilityEvidence("retraining-required", "Active model metadata is unavailable.")
    contract = payload.get("training_contract")
    expected = {
        "registry_fingerprint": snapshot.fingerprints.target_registry,
        "ordered_ml_fingerprint": snapshot.fingerprints.ordered_ml,
        "derived_semantics_fingerprint": snapshot.fingerprints.derived_semantics,
        "one_hot_fingerprint": snapshot.fingerprints.one_hot,
    }
    if payload.get("preprocess_version") != snapshot.manifest.preprocessing_version:
        return ModelCompatibilityEvidence("retraining-required", "Preprocessing version differs.")
    if not isinstance(contract, dict):
        return ModelCompatibilityEvidence(
            "retraining-required",
            "Legacy model metadata cannot prove generation compatibility.",
        )
    mismatched = tuple(key for key, value in expected.items() if contract.get(key) != value)
    if mismatched:
        return ModelCompatibilityEvidence(
            "retraining-required", "Model contract differs: " + ", ".join(mismatched)
        )
    return ModelCompatibilityEvidence("compatible", "Active model metadata matches the generation.")
