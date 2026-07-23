"""Build and publish a versioned Candidate from one terminal training artifact."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from apps.common.model_lifecycle.candidate_contracts import (
    CandidateManifest,
    CandidateResult,
    TargetArtifactContract,
)
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.state.training_run_state import TrainingRequest, TrainingResult
from core.data_definition.target_registry.runtime import ModelRegistrySnapshot


class CandidatePublisher:
    def __init__(self, repository: ModelLifecycleRepository) -> None:
        self._repository = repository

    def publish(
        self,
        request: TrainingRequest,
        result: TrainingResult,
        staging: Path,
    ) -> TrainingResult:
        model_sha256, payload = self._repository.inspect_staged_model(staging)
        if not isinstance(payload, dict):
            raise ValueError("Candidate model bundle is invalid")
        snapshot = ModelRegistrySnapshot.from_payload(
            json.loads(request.registry_payload_json)
        )
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
            candidate_id=request.candidate_id,
            run_id=request.run_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            source="training",
            model_sha256=model_sha256,
            definition_generation_id=request.generation_id,
            registry_fingerprint=request.registry_fingerprint,
            ordered_ml_fingerprint=request.ordered_ml_fingerprint,
            derived_semantics_fingerprint=request.derived_semantics_fingerprint,
            one_hot_fingerprint=request.one_hot_fingerprint,
            preprocessing_version=request.preprocess_version,
            targets=tuple(TargetArtifactContract(
                target.identity,
                target.ml_name,
                tuple(payload["features"][target.ml_name]),
            ) for target in targets),
            promotion_eligible=True,
        )
        publication = CandidateResult(
            request.run_id, request.candidate_id, "complete", "published", True
        )
        candidate = self._repository.publish(staging, manifest, publication)
        return replace(
            result,
            model_path=str(candidate.model_path),
            candidate_id=request.candidate_id,
            publication_outcome="published",
        )
