"""Revalidate every byte and semantic identity captured by a frozen snapshot."""

from __future__ import annotations

from typing import Any

from apps.common.model_lifecycle.closeout.canonical import content_sha256
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.application.experiments.store import ExperimentStore

from .snapshot_evidence import (
    candidate_artifacts,
    directory_artifacts,
    specification_fingerprint,
)


class SnapshotIntegrityValidator:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        generations: DataDefinitionGenerationRepository,
        store: LifecycleCloseoutStore,
        *,
        build_identity_provider=None,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._generations = generations
        self._store = store
        self._experiments = ExperimentStore(repository.root)
        self._build_identity = build_identity_provider

    def validate(self, meaning: dict[str, Any]) -> None:
        selected = meaning["selected_candidate"]
        candidate = self._repository.read_candidate(selected["candidate_id"])
        current_candidate_artifacts = candidate_artifacts(
            candidate.path, candidate.manifest
        )
        if current_candidate_artifacts != meaning["candidate_artifacts"]:
            raise ValueError("captured Candidate artifacts changed")
        if (
            selected.get("manifest_sha256")
            != current_candidate_artifacts["manifest.json"]["sha256"]
            or selected.get("model_sha256") != candidate.manifest.model_sha256
        ):
            raise ValueError("selected Candidate identity changed")

        runtime = meaning["definition_runtime"]
        generation_id = runtime["generation_id"]
        if self._generations.active_generation_id() != generation_id:
            raise ValueError("Definition/runtime generation changed")
        generation = self._generations.read_generation(generation_id)
        if directory_artifacts(generation.path) != runtime["bundle_files"]:
            raise ValueError("captured Definition generation artifacts changed")

        run_identity = meaning["source_run"]
        run = self._experiments.read_run(run_identity["run_id"])
        if content_sha256(run) != run_identity["sha256"]:
            raise ValueError("captured selected run evidence changed")
        if run["contract_identity"]["data_sha256"] != meaning[
            "training_data"
        ]["content_sha256"]:
            raise ValueError("materialized data differs from selected run")
        if run["contract_identity"]["data_request"] != meaning[
            "resolved_specification"
        ]["data"]:
            raise ValueError("selected run filtering identity changed")
        if specification_fingerprint(
            meaning["resolved_specification"]
        ) != meaning["specification_fingerprint"]:
            raise ValueError("resolved specification fingerprint changed")

        campaign_identity = meaning["campaign"]
        campaign = self._experiments.read_campaign(
            campaign_identity["campaign_id"]
        )
        if content_sha256(campaign) != campaign_identity["sha256"]:
            raise ValueError("captured campaign evidence changed")
        recommendation_identity = meaning["recommendation"]
        recommendation = self._experiments.read_campaign_evidence(
            campaign_identity["campaign_id"],
            "recommendations",
            recommendation_identity["recommendation_id"],
            "recommendation.json",
        )
        if content_sha256(recommendation) != recommendation_identity["sha256"]:
            raise ValueError("captured recommendation evidence changed")

        self._store.verify_owned_materialization(meaning["training_data"])
        if (
            self._build_identity is not None
            and self._build_identity() != meaning["build_identity"]
        ):
            raise ValueError("training-semantic build identity changed")
