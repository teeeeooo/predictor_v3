"""Project lifecycle state into the Common read-only retention policy."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
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
        for candidate_id in loaded_candidates:
            references.append(ArtifactReference(
                "predict-runtime",
                candidate_id,
                "loaded_predict_model",
            ))
        preview = build_retention_preview(
            nodes=nodes,
            references=references,
            policy=policy,
            reference_complete=reference_complete,
            loaded_model_lease_status=lease_status,
            created_at=now.isoformat(),
        )
        self._store.write_retention_preview(preview)
        return preview

    def _inventory(
        self, now: datetime
    ) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
        nodes = []
        references = []
        reference_complete = True
        active = self._repository.read_active(optional=True)
        for candidate in self._repository.list_candidates():
            manifest = candidate.manifest
            disposition = inspect_persisted_contract(
                "candidate_manifest", manifest.to_payload()
            )
            nodes.append(ArtifactNode(
                manifest.candidate_id,
                "candidate",
                manifest.created_at,
                _directory_size(candidate.path),
                _age_days(manifest.created_at, now),
                version_disposition=disposition.status,
            ))
        if active is not None:
            references.append(ArtifactReference(
                "active-reference",
                active.candidate_id,
                "current_active",
            ))
            references.extend(
                ArtifactReference(
                    f"active-history-r{record.revision}",
                    record.candidate_id,
                    "active_history",
                )
                for record in active.history
            )
        try:
            campaigns = self._experiments.list_campaigns()
        except (FileNotFoundError, OSError, TypeError, ValueError):
            campaigns = ()
            reference_complete = False
        for campaign in campaigns:
            reference_complete = self._campaign_references(
                campaign, references
            ) and reference_complete
        closeout_nodes, closeout_references, closeout_complete = (
            self._closeout_inventory(now)
        )
        nodes.extend(closeout_nodes)
        references.extend(closeout_references)
        reference_complete = closeout_complete and reference_complete
        # Existing exports can live outside the lifecycle root and Phase 5E has
        # no workspace export index. Until every export is registered, preview
        # remains deliberately incomplete and therefore non-destructive.
        reference_complete = False
        return nodes, references, reference_complete

    @staticmethod
    def _campaign_references(
        campaign: dict[str, Any],
        references: list[ArtifactReference],
    ) -> bool:
        status = str(campaign.get("status", ""))
        source = str(campaign.get("campaign_id", "campaign"))
        reason = (
            "campaign_in_progress"
            if status in {
                "created",
                "running",
                "ready_to_execute",
                "awaiting_proposal",
            }
            else "campaign_resumable"
            if status in {
                "paused",
                "failed_resumable",
                "cancelled_resumable",
                "lock_conflict",
            }
            else ""
        )
        if reason:
            for run in campaign.get("completed_runs", ()):
                candidate_id = (
                    run.get("candidate_id") if isinstance(run, dict) else None
                )
                if candidate_id:
                    references.append(ArtifactReference(
                        source, candidate_id, reason
                    ))
        incumbent = campaign.get("incumbent_candidate_id")
        if incumbent:
            references.append(ArtifactReference(
                source, incumbent, "campaign_incumbent"
            ))
        for item in campaign.get("recommendations", ()):
            candidate = (
                item.get("recommended_candidate")
                if isinstance(item, dict)
                else None
            )
            if isinstance(candidate, dict) and candidate.get("candidate_id"):
                references.append(ArtifactReference(
                    source,
                    candidate["candidate_id"],
                    "selected_recommendation",
                ))
        return bool(campaign.get("schema_version"))

    def _closeout_inventory(
        self, now: datetime
    ) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
        nodes: list[ArtifactNode] = []
        references: list[ArtifactReference] = []
        complete = True
        try:
            snapshots = self._store.list_records(
                self._store.snapshots, "snapshot.json"
            )
            confirmations = self._store.list_records(
                self._store.confirmations, "confirmation.json"
            )
            decisions = self._store.list_records(
                self._store.decisions, "decision.json"
            )
            migration_previews = self._store.list_records(
                self._store.migration_previews, "preview.json"
            )
        except (FileNotFoundError, OSError, TypeError, ValueError):
            return nodes, references, False
        for raw in snapshots:
            try:
                value = self._store.read_snapshot(raw["snapshot_id"])
                nodes.append(_record_node(
                    value["snapshot_id"],
                    "confirmation_snapshot",
                    value,
                    self._store.snapshots / value["snapshot_id"],
                    now,
                    "snapshot",
                ))
                candidate = value["meaning"]["selected_candidate"]["candidate_id"]
                references.append(ArtifactReference(
                    value["snapshot_id"],
                    candidate,
                    "confirmation_snapshot",
                ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
        for initial in confirmations:
            try:
                value = self._store.read_confirmation(
                    initial["confirmation_id"]
                )
                nodes.append(_record_node(
                    value["confirmation_id"],
                    "confirmation",
                    value,
                    self._store.confirmations / value["confirmation_id"],
                    now,
                    "confirmation",
                ))
                references.append(ArtifactReference(
                    value["confirmation_id"],
                    value["snapshot_id"],
                    "confirmation_snapshot",
                ))
                candidate = value.get("confirmation_candidate_id")
                if candidate:
                    references.append(ArtifactReference(
                        value["confirmation_id"],
                        candidate,
                        "confirmation_candidate",
                    ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
        for decision in decisions:
            try:
                decision_id = decision["decision_id"]
                nodes.append(_record_node(
                    decision_id,
                    "final_decision",
                    decision,
                    self._store.decisions / decision_id,
                    now,
                    "final_decision",
                ))
                references.append(ArtifactReference(
                    decision_id,
                    decision["confirmation_id"],
                    "final_decision_evidence",
                ))
                references.append(ArtifactReference(
                    decision_id,
                    decision["candidate_id"],
                    "final_decision_evidence",
                ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
        for preview in migration_previews:
            try:
                preview_id = preview["preview_id"]
                nodes.append(_raw_node(
                    preview_id,
                    "migration_preview",
                    preview,
                    self._store.migration_previews / preview_id,
                    now,
                ))
                references.append(ArtifactReference(
                    preview_id,
                    preview_id,
                    "unresolved_migration",
                ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
        return nodes, references, complete


def _directory_size(path: Path) -> int:
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink()
    )


def _age_days(created_at: str, now: datetime) -> int:
    try:
        created = datetime.fromisoformat(created_at).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return 0
    return max((now - created).days, 0)


def _record_node(
    identity: str,
    artifact_class: str,
    payload: dict[str, Any],
    path: Path,
    now: datetime,
    contract_kind: str,
) -> ArtifactNode:
    disposition = inspect_persisted_contract(contract_kind, payload)
    return _raw_node(
        identity,
        artifact_class,
        payload,
        path,
        now,
        version_disposition=disposition.status,
    )


def _raw_node(
    identity: str,
    artifact_class: str,
    payload: dict[str, Any],
    path: Path,
    now: datetime,
    *,
    version_disposition: str = "current_and_executable",
) -> ArtifactNode:
    created_at = str(payload.get("created_at", now.isoformat()))
    return ArtifactNode(
        identity,
        artifact_class,
        created_at,
        _directory_size(path),
        _age_days(created_at, now),
        version_disposition=version_disposition,
    )
