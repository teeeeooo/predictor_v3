"""Fixtures for lifecycle repository and service tests."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime, timezone

import joblib
import pytest

from apps.common.model_lifecycle import (
    CandidateManifest,
    CandidateResult,
    ModelLifecycleRepository,
    TargetArtifactContract,
)
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tools.dev.mock_smoke.generators import build_mock_prediction_artifact


@pytest.fixture
def registry_snapshot():
    return model_registry_snapshot(bootstrap_manifest())


@pytest.fixture
def repository(tmp_path):
    return ModelLifecycleRepository(tmp_path / "lifecycle")


def artifact_for(snapshot, *, generation_id=None):  # noqa: ANN001
    artifact = build_mock_prediction_artifact(rows=8)
    artifact["preprocess_version"] = snapshot.preprocessing_version
    artifact["training_contract"] = {
        "generation_id": generation_id or snapshot.generation_id,
        "registry_fingerprint": snapshot.registry_fingerprint,
        "ordered_ml_fingerprint": snapshot.ordered_ml_fingerprint,
        "derived_semantics_fingerprint": snapshot.derived_semantics_fingerprint,
        "one_hot_fingerprint": snapshot.one_hot_fingerprint,
    }
    return artifact


def publish_candidate(repository, snapshot, candidate_id, *, artifact=None):  # noqa: ANN001
    artifact = artifact or artifact_for(snapshot)
    staging = repository.create_staging(candidate_id)
    model_path = staging / "model.pkl"
    joblib.dump(artifact, model_path)
    by_identity = {
        target.identity: target
        for group in snapshot.groups for target in group.targets
    }
    targets = tuple(
        by_identity[identity]
        for identity in snapshot.target_presentation_order
        if identity in by_identity
    )
    manifest = CandidateManifest(
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
        created_at=datetime.now(timezone.utc).isoformat(),
        source="test",
        model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),
        definition_generation_id=snapshot.generation_id,
        registry_fingerprint=snapshot.registry_fingerprint,
        ordered_ml_fingerprint=snapshot.ordered_ml_fingerprint,
        derived_semantics_fingerprint=snapshot.derived_semantics_fingerprint,
        one_hot_fingerprint=snapshot.one_hot_fingerprint,
        preprocessing_version=snapshot.preprocessing_version,
        targets=tuple(TargetArtifactContract(
            target.identity,
            target.ml_name,
            tuple(artifact["features"][target.ml_name]),
        ) for target in targets),
        promotion_eligible=True,
    )
    result = CandidateResult(
        manifest.run_id, candidate_id, "complete", "published", True
    )
    return repository.publish(staging, manifest, result)


def incompatible_snapshot(snapshot, field, value):  # noqa: ANN001
    return replace(snapshot, **{field: value})
