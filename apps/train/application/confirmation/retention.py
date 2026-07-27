"""Project lifecycle state into the Common read-only retention policy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.common.model_lifecycle.closeout.compatibility import (
    inspect_persisted_contract,
)
from apps.common.model_lifecycle.closeout.loaded_model_lease import (
    inspect_loaded_model_leases,
)
from apps.common.model_lifecycle.closeout.retention import (
    ArtifactNode,
    ArtifactReference,
    RetentionPolicy,
    build_retention_preview,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.application.experiments.store import ExperimentStore

from .retention_closeout import closeout_inventory
from .retention_experiments import experiment_inventory
from .retention_nodes import age_days, directory_size


class LifecycleRetentionApplicationService:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        *,
        closeout_store: LifecycleCloseoutStore | None = None,
        clock=None,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._experiments = ExperimentStore(repository.root)
        self._store = closeout_store or LifecycleCloseoutStore(repository.root)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def preview(self, policy: RetentionPolicy) -> dict[str, Any]:
        now = self._clock()
        nodes, references, reference_complete = self._inventory(now)
        leases = list(self._store.list_loaded_model_leases())
        lease_status, loaded_candidates = inspect_loaded_model_leases(
            leases, now=now.isoformat()
        )
        self._lease_nodes(
            leases, loaded_candidates, nodes, references, now
        )
        preview = build_retention_preview(
            nodes=nodes,
            references=references,
            policy=policy,
            reference_complete=reference_complete,
            loaded_model_lease_status=lease_status,
        )
        self._store.write_retention_preview(preview)
        return preview

    def _inventory(
        self, now: datetime
    ) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
        nodes, references = self._candidate_active_inventory(now)
        try:
            campaigns = self._experiments.list_campaigns()
        except (FileNotFoundError, OSError, TypeError, ValueError):
            campaigns = ()
        experiment_nodes, experiment_references, _experiment_complete = (
            experiment_inventory(self._experiments, campaigns, now)
        )
        closeout_nodes, closeout_references, _closeout_complete = (
            closeout_inventory(self._store, now)
        )
        nodes.extend(experiment_nodes)
        nodes.extend(closeout_nodes)
        references.extend(experiment_references)
        references.extend(closeout_references)
        # Phase 5E exports have no lifecycle-root index. Keep the class visible
        # and the graph incomplete rather than omitting unknown deployments.
        nodes.append(ArtifactNode(
            "deployment-export-index",
            "deployment_export",
            now.isoformat(),
            0,
            version_disposition="corrupt_or_incomplete",
            source_artifact_identity="missing:deployment-export-index",
        ))
        return nodes, references, False

    def _candidate_active_inventory(
        self, now: datetime
    ) -> tuple[list[ArtifactNode], list[ArtifactReference]]:
        nodes: list[ArtifactNode] = []
        references: list[ArtifactReference] = []
        for candidate in self._repository.list_candidates():
            manifest = candidate.manifest
            disposition = inspect_persisted_contract(
                "candidate_manifest", manifest.to_payload()
            )
            nodes.append(ArtifactNode(
                manifest.candidate_id,
                "candidate",
                manifest.created_at,
                directory_size(candidate.path),
                age_days(manifest.created_at, now),
                version_disposition=disposition.status,
                source_artifact_identity=str(candidate.path),
            ))
        active = self._repository.read_active(optional=True)
        if active is None:
            return nodes, references
        nodes.append(ArtifactNode(
            "active-reference",
            "active",
            active.activated_at,
            self._repository.active_reference_path.stat().st_size,
            age_days(active.activated_at, now),
            source_artifact_identity=str(
                self._repository.active_reference_path
            ),
        ))
        references.append(ArtifactReference(
            "active-reference", active.candidate_id, "current_active"
        ))
        for record in active.history:
            identity = f"active-history-r{record.revision}"
            nodes.append(ArtifactNode(
                identity,
                "active_history",
                record.activated_at,
                0,
                age_days(record.activated_at, now),
                source_artifact_identity=(
                    f"{self._repository.active_reference_path}"
                    f"#history[{record.revision}]"
                ),
            ))
            references.append(ArtifactReference(
                identity, record.candidate_id, "active_history"
            ))
        return nodes, references

    def _lease_nodes(
        self,
        leases: list[dict[str, Any]],
        loaded_candidates: set[str],
        nodes: list[ArtifactNode],
        references: list[ArtifactReference],
        now: datetime,
    ) -> None:
        for index, lease in enumerate(leases, 1):
            identity = (
                f"loaded-model-lease-{lease.get('lease_id', 'unknown')}-{index}"
            )
            nodes.append(ArtifactNode(
                identity,
                "loaded_model_lease",
                str(lease.get("observed_at", now.isoformat())),
                0,
                source_artifact_identity=(
                    f"{self._store.loaded_model_leases}/"
                    f"{lease.get('lease_id', 'unknown')}"
                ),
            ))
            if lease.get("candidate_id") in loaded_candidates:
                references.append(ArtifactReference(
                    identity,
                    lease["candidate_id"],
                    "loaded_predict_model",
                ))
