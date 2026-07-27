"""Freeze one Phase 5G recommendation into immutable Phase 5H meaning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from apps.common.model_lifecycle.closeout.canonical import content_sha256
from apps.common.model_lifecycle.closeout.compatibility import (
    inspect_persisted_contract,
    validate_recommendation_evidence,
)
from apps.common.model_lifecycle.closeout.contracts import build_snapshot_record
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.experiments.store import ExperimentStore

from .snapshot_evidence import (
    candidate_artifacts,
    directory_artifacts,
    preflight_data,
    selected_parameters,
    specification_fingerprint,
)


@dataclass(frozen=True)
class SnapshotFreezeOutcome:
    status: str
    snapshot_id: str = ""
    record: dict[str, Any] | None = None
    reason_code: str = ""
    message: str = ""


class SnapshotFreezeService:
    def __init__(
        self,
        lifecycle_repository: ModelLifecycleRepository,
        generation_repository: DataDefinitionGenerationRepository,
        *,
        closeout_store: LifecycleCloseoutStore | None = None,
        clock=None,  # noqa: ANN001
    ) -> None:
        self._repository = lifecycle_repository
        self._generations = generation_repository
        self._experiments = ExperimentStore(lifecycle_repository.root)
        self._store = closeout_store or LifecycleCloseoutStore(
            lifecycle_repository.root
        )
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def preflight(
        self,
        campaign_id: str,
        recommendation_id: str,
        *,
        selected_candidate_id: str,
    ) -> SnapshotFreezeOutcome:
        try:
            meaning = self._collect_meaning(
                campaign_id,
                recommendation_id,
                selected_candidate_id=selected_candidate_id,
                materialize=False,
            )
            record = build_snapshot_record(
                meaning,
                created_at=self._clock().isoformat(),
                actor_kind="user",
                status="creating",
            )
        except Exception as exc:
            return SnapshotFreezeOutcome(
                "blocked_incomplete",
                reason_code="snapshot_preflight_blocked",
                message=str(exc).splitlines()[0],
            )
        return SnapshotFreezeOutcome("creating", record=record)

    def freeze(
        self,
        campaign_id: str,
        recommendation_id: str,
        *,
        selected_candidate_id: str,
        actor_kind: str,
    ) -> SnapshotFreezeOutcome:
        try:
            meaning = self._collect_meaning(
                campaign_id,
                recommendation_id,
                selected_candidate_id=selected_candidate_id,
                materialize=True,
            )
            record = build_snapshot_record(
                meaning,
                created_at=self._clock().isoformat(),
                actor_kind=actor_kind,
            )
            self._store.write_snapshot(record)
        except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
            return SnapshotFreezeOutcome(
                "failed",
                reason_code="snapshot_freeze_failed",
                message=str(exc).splitlines()[0],
            )
        return SnapshotFreezeOutcome(
            "frozen",
            snapshot_id=record["snapshot_id"],
            record=record,
        )

    def inspect(self, snapshot_id: str) -> SnapshotFreezeOutcome:
        try:
            record = self._store.read_snapshot(snapshot_id)
        except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
            return SnapshotFreezeOutcome(
                "blocked_incomplete",
                snapshot_id=snapshot_id,
                reason_code="snapshot_unreadable",
                message=str(exc).splitlines()[0],
            )
        return SnapshotFreezeOutcome(
            record["status"], snapshot_id=snapshot_id, record=record
        )

    def _collect_meaning(
        self,
        campaign_id: str,
        recommendation_id: str,
        *,
        selected_candidate_id: str,
        materialize: bool,
    ) -> dict[str, Any]:
        campaign = self._experiments.read_campaign(campaign_id)
        recommendation = self._experiments.read_campaign_evidence(
            campaign_id,
            "recommendations",
            recommendation_id,
            "recommendation.json",
        )
        recommendation_state = validate_recommendation_evidence(
            recommendation, campaign=campaign
        )
        if not recommendation_state.executable:
            raise ValueError(
                recommendation_state.reason_code
                or "recommendation evidence is not executable"
            )
        selected = recommendation["recommended_candidate"]
        if selected["candidate_id"] != selected_candidate_id:
            raise ValueError("selected recommendation Candidate is stale")
        candidate = self._repository.read_candidate(selected_candidate_id)
        if (
            not candidate.manifest.promotion_eligible
            or candidate.manifest.blocking_reasons
            or candidate.manifest.contains_unpublished_features
        ):
            raise ValueError("selected Candidate is not production eligible")
        run = self._experiments.read_run(candidate.manifest.run_id)
        run_state = inspect_persisted_contract("run", run)
        if not run_state.executable:
            raise ValueError(
                run_state.reason_code or "selected source run is not executable"
            )
        if (
            run.get("candidate_id") != selected_candidate_id
            or run.get("result", {}).get("candidate_reference")
            != selected_candidate_id
        ):
            raise ValueError("selected Candidate/source run identity mismatch")
        specification = run["resolved_specification"]
        fingerprint = run["contract_identity"]["specification_fingerprint"]
        if specification_fingerprint(specification) != fingerprint:
            raise ValueError("resolved Experiment Specification fingerprint mismatch")
        generation_id = candidate.manifest.definition_generation_id
        generation = self._generations.read_generation(generation_id)
        artifacts = candidate_artifacts(candidate.path, candidate.manifest)
        definition_files = directory_artifacts(generation.path)
        source_path = specification["data"]["source_path"]
        training_data = (
            self._store.materialize_local_source(
                source_path,
                filtering_meaning={
                    "selection": specification["data"],
                    "preprocessing": specification["preprocessing"],
                    "row_filter_owner": "core.ml.training.load_and_preprocess",
                },
            )
            if materialize
            else preflight_data(source_path, run)
        )
        active = self._repository.read_active(optional=True)
        selected_parameters_value = selected_parameters(
            candidate.path / "training_result.json"
        )
        return {
            "recommendation": {
                "recommendation_id": recommendation_id,
                "campaign_id": campaign_id,
                "sha256": content_sha256(recommendation),
                "schema_version": recommendation["schema_version"],
            },
            "campaign": {
                "campaign_id": campaign_id,
                "schema_version": campaign["schema_version"],
                "sha256": content_sha256(campaign),
            },
            "selected_candidate": {
                "candidate_id": candidate.manifest.candidate_id,
                "manifest_sha256": artifacts["manifest.json"]["sha256"],
                "model_sha256": candidate.manifest.model_sha256,
            },
            "source_run": {
                "run_id": run["run_id"],
                "schema_version": run["schema_version"],
                "sha256": content_sha256(run),
            },
            "candidate_artifacts": artifacts,
            "resolved_specification": specification,
            "specification_fingerprint": fingerprint,
            "definition_runtime": {
                "generation_id": generation_id,
                "contract_version": generation.manifest.contract_version,
                "bundle_files": definition_files,
                "registry_fingerprint": candidate.manifest.registry_fingerprint,
                "ordered_ml_fingerprint": candidate.manifest.ordered_ml_fingerprint,
                "derived_semantics_fingerprint": (
                    candidate.manifest.derived_semantics_fingerprint
                ),
                "one_hot_fingerprint": candidate.manifest.one_hot_fingerprint,
                "confirmation_targets": [
                    {
                        "identity": target.identity,
                        "ml_name": target.ml_name,
                        "ordered_features": list(target.feature_names),
                    }
                    for target in candidate.manifest.targets
                ],
            },
            "target_roles": specification["targets"],
            "feature_contract": {
                "specification": specification["features"],
                "ordered_targets": [
                    {
                        "identity": target.identity,
                        "ml_name": target.ml_name,
                        "ordered_features": list(target.feature_names),
                    }
                    for target in candidate.manifest.targets
                ],
                "mapping_and_derived_bundle_hashes": definition_files,
                "preprocessing_version": candidate.manifest.preprocessing_version,
            },
            "evaluation_contract": {
                "evaluation": specification["evaluation"],
                "metric_direction_threshold_tolerance": campaign.get(
                    "policy", {}
                ).get("ranking", {}),
                "fold_count": specification["optuna"]["cv_folds"],
                "seed": specification["evaluation"]["seed"],
            },
            "training_configuration": {
                "rfecv": specification["rfecv"],
                "selected_parameters": selected_parameters_value,
                "search_disabled_for_confirmation": True,
            },
            "baseline": {
                "campaign_baseline": campaign.get("baseline"),
                "observed_active_candidate_id": (
                    active.candidate_id if active else None
                ),
                "observed_active_revision": active.revision if active else 0,
            },
            "build_identity": run["contract_identity"]["build_revision"],
            "training_semantic_identity": {
                key: value
                for key, value in run["contract_identity"].items()
                if key not in {"build_revision", "python", "data_request"}
            },
            "training_data": training_data,
        }
