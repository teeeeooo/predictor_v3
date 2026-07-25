"""Build and publish a versioned Candidate from one terminal training artifact."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from apps.common.model_lifecycle.candidate_contracts import (
    CANDIDATE_SCHEMA_VERSION,
    CandidateArtifactReference,
    CandidateManifest,
    CandidateResult,
    TargetArtifactContract,
)
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.adapters.training_results import (
    TrainingResultArtifactWriter,
    artifact_sha256,
)
from apps.train.application.training_results import (
    TRAINING_RESULT_SCHEMA_VERSION,
    TrainingResultService,
)
from apps.train.application.training_results.evidence import (
    load_active_baseline,
    load_candidate_evidence,
    load_terminal_evidence,
)
from apps.train.state.training_run_state import TrainingRequest, TrainingResult
from core.data_definition.target_registry.runtime import ModelRegistrySnapshot


class CandidateArtifactGenerationError(RuntimeError):
    """Required result artifacts could not be completed and verified."""


class CandidatePublisher:
    def __init__(self, repository: ModelLifecycleRepository) -> None:
        self._repository = repository
        self._result_service = TrainingResultService()
        self._artifact_writer = TrainingResultArtifactWriter()

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
        evidence = load_candidate_evidence(staging, targets)
        (staging / "core_training_evidence.json").unlink(missing_ok=True)
        if evidence.status != "complete":
            raise ValueError("partial or failed training cannot publish a Candidate")
        baseline, baseline_identity, baseline_reason = load_active_baseline(
            self._repository
        )
        analysis = self._result_service.build(
            run_id=request.run_id,
            candidate_id=request.candidate_id,
            evidence=evidence,
            required_target_identities=tuple(
                target.identity for target in targets
            ),
            baseline=baseline,
            baseline_identity=baseline_identity,
            baseline_unavailable_reason=baseline_reason,
            publication_outcome="published",
        )
        try:
            self._artifact_writer.write(staging, analysis)
        except Exception as exc:
            raise CandidateArtifactGenerationError(
                str(exc).splitlines()[0]
            ) from exc
        artifact_references = tuple(
            CandidateArtifactReference(
                path=str(item["path"]),
                sha256=artifact_sha256(staging / str(item["path"])),
                category=str(item["category"]),
                required=bool(item["required"]),
            )
            for item in analysis.artifacts
        )
        promotion_eligible = bool(
            analysis.promotion_eligibility.get("eligible", False)
        )
        blocking_reasons = tuple(
            item["code"] for item in analysis.blocking_reasons
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
            promotion_eligible=promotion_eligible,
            blocking_reasons=blocking_reasons,
            analysis_contract_version=TRAINING_RESULT_SCHEMA_VERSION,
            analysis_artifacts=artifact_references,
            schema_version=CANDIDATE_SCHEMA_VERSION,
        )
        publication = CandidateResult(
            request.run_id,
            request.candidate_id,
            "complete",
            "published",
            promotion_eligible,
            blocking_reasons,
        )
        candidate = self._repository.publish(staging, manifest, publication)
        return replace(
            result,
            model_path=str(candidate.model_path),
            candidate_id=request.candidate_id,
            publication_outcome="published",
        )

    def preserve_terminal_evidence(
        self,
        request: TrainingRequest,
        result: TrainingResult,
        staging: Path,
        *,
        publication_outcome: str,
    ) -> TrainingResult:
        snapshot = ModelRegistrySnapshot.from_payload(
            json.loads(request.registry_payload_json)
        )
        targets = tuple(
            target
            for identity in snapshot.target_presentation_order
            for group in snapshot.groups
            for target in group.targets
            if target.identity == identity
        )
        evidence = load_terminal_evidence(staging, result)
        analysis = self._result_service.build(
            run_id=request.run_id,
            candidate_id=request.candidate_id,
            evidence=evidence,
            required_target_identities=tuple(
                target.identity for target in targets
            ),
            publication_outcome=publication_outcome,
        )
        (staging / "model.pkl").unlink(missing_ok=True)
        (staging / "core_training_evidence.json").unlink(missing_ok=True)
        self._artifact_writer.write(staging, analysis)
        evidence_path = self._repository.preserve_run_evidence(
            staging, request.run_id
        )
        return replace(
            result,
            candidate_id=request.candidate_id,
            publication_outcome=publication_outcome,
            evidence_path=str(evidence_path / "training_result.json"),
        )
