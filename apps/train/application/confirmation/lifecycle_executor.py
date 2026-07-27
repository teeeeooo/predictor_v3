"""Existing TrainingLifecycle/CandidatePublisher adapter for fixed confirmation."""

from __future__ import annotations

import json
from dataclasses import replace

from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.application.experiments.contracts import ResolvedExperiment
from apps.train.application.experiments.service import ExperimentApplicationService

from .execution_contracts import (
    ConfirmationExecutionResult,
    FrozenConfirmationRequest,
)


class TrainingLifecycleConfirmationExecutor:
    """Synchronous/headless adapter; Core receives fixed parameters/features."""

    def __init__(
        self,
        experiments: ExperimentApplicationService,
        repository: ModelLifecycleRepository,
        *,
        closeout_store: LifecycleCloseoutStore | None = None,
    ) -> None:
        self._experiments = experiments
        self._repository = repository
        self._store = closeout_store or LifecycleCloseoutStore(repository.root)

    def execute(
        self, request: FrozenConfirmationRequest
    ) -> ConfirmationExecutionResult:
        resolved = ResolvedExperiment(
            request.resolved_specification,
            _specification_fingerprint(request.resolved_specification),
        )
        run_id = f"confirmation-run-{request.confirmation_id}"
        candidate_id = f"candidate-{request.confirmation_id}"
        blob_path = self._store.owned_materialization_path(
            request.training_data["materialized_identity"]
        )
        training = self._experiments.training_request(
            resolved,
            run_id=run_id,
            candidate_id=candidate_id,
            execution_owner="confirmation",
            data_path_override=str(blob_path),
        )
        fixed_features = {
            item["identity"]: item["ordered_features"]
            for item in request.definition_runtime["confirmation_targets"]
        }
        training = replace(
            training,
            data_path=str(blob_path),
            production_required_target_ids_json=json.dumps(
                request.production_required_targets
            ),
            target_scoped_exploratory=False,
            exploratory_feature_policy=False,
            contains_unpublished_features=False,
            publication_source="confirmation",
            confirmation_fixed_parameters_json=json.dumps(
                request.selected_parameters, sort_keys=True
            ),
            confirmation_fixed_features_json=json.dumps(
                fixed_features, sort_keys=True
            ),
        )
        immediate = self._experiments.run_resolved_request(resolved, training)
        record = self._experiments.inspect_run(run_id)
        if record["status"] != "success":
            result = record.get("result") or {}
            return ConfirmationExecutionResult(
                "failed",
                message=str(
                    result.get("message")
                    or getattr(immediate, "message", "")
                    or "Confirmation training failed."
                ),
                reason_code="confirmation_training_failed",
            )
        candidate = self._repository.read_candidate(candidate_id)
        analysis = self._repository.read_training_analysis(candidate_id)
        targets = tuple(
            dict(item) for item in getattr(analysis, "targets", ())
        )
        return ConfirmationExecutionResult(
            "succeeded",
            target_results=targets,
            confirmation_candidate_id=candidate.manifest.candidate_id,
        )


def _specification_fingerprint(payload: dict) -> str:
    import hashlib

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
