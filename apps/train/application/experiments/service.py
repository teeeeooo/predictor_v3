"""Shared GUI/headless Experiment Specification application service."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.train.application.experiments.contracts import (
    RUN_RECORD_VERSION,
    ExperimentContractError,
    ResolvedExperiment,
    resolve_specification,
)
from apps.train.application.experiments.store import ExperimentStore
from apps.train.application.experiments.records import (
    current_revision,
    file_sha256,
    result_payload,
    result_status,
    run_record,
    utc_now,
)
from apps.train.application.experiments.request_factory import (
    build_training_request,
    gui_specification,
)
from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.state.training_run_state import TrainingRequest, TrainingResult


class ExperimentApplicationService:
    """Resolve one declarative contract and delegate to TrainingLifecycleService."""

    def __init__(
        self,
        lifecycle: TrainingLifecycleService,
        *,
        lifecycle_root: str | Path,
        revision_provider=None,  # noqa: ANN001
        derived_snapshot_provider=None,  # noqa: ANN001
    ) -> None:
        self._lifecycle = lifecycle
        self._store = ExperimentStore(lifecycle_root)
        self._revision_provider = revision_provider or current_revision
        self._derived_snapshot_provider = derived_snapshot_provider

    @property
    def store(self) -> ExperimentStore:
        return self._store

    def validate(
        self,
        specification: dict[str, Any],
        *,
        campaign_configuration: dict[str, Any] | None = None,
    ) -> ResolvedExperiment:
        resolved = resolve_specification(
            specification, campaign=campaign_configuration
        )
        self._request_from_resolved(
            resolved, run_id="validation-only", candidate_id="validation-only"
        )
        return resolved

    def gui_specification(self, data_path: str) -> dict[str, Any]:
        return gui_specification(self._lifecycle.registry_snapshot(), data_path)

    def resolve_gui_request(
        self, data_path: str, *, run_id: str, candidate_id: str = ""
    ) -> tuple[ResolvedExperiment, TrainingRequest]:
        resolved = self.validate(self.gui_specification(data_path))
        return resolved, self._request_from_resolved(
            resolved,
            run_id=run_id,
            candidate_id=candidate_id or f"candidate-{run_id}",
            execution_owner="gui",
        )

    def run(
        self,
        specification: dict[str, Any] | ResolvedExperiment,
        *,
        run_id: str | None = None,
        candidate_id: str | None = None,
        execution_owner: str = "headless-single",
        campaign_id: str = "",
        attempt: int = 1,
        callbacks: dict[str, Any] | None = None,
    ) -> TrainingResult | None:
        resolved = (
            specification
            if isinstance(specification, ResolvedExperiment)
            else self.validate(specification)
        )
        identity = run_id or f"run-{uuid4().hex}"
        try:
            self._store.read_run(identity)
        except FileNotFoundError:
            pass
        else:
            raise ExperimentContractError(
                "run_identity_conflict",
                f"Immutable experiment run identity already exists: {identity}.",
            )
        request = self._request_from_resolved(
            resolved,
            run_id=identity,
            candidate_id=candidate_id or f"candidate-{identity}",
            execution_owner=execution_owner,
            campaign_id=campaign_id,
        )
        external = callbacks or {}
        accepted_run = False
        log_reference = None

        def accepted(_request: TrainingRequest) -> None:
            nonlocal accepted_run, log_reference
            self._store.write_run(
                identity,
                run_record(
                    request,
                    resolved,
                    status="running",
                    attempt=attempt,
                    revision=self._revision_provider(),
                ),
            )
            accepted_run = True
            log_reference = self._store.append_run_event(identity, {
                "at": utc_now(),
                "level": "info",
                "message": "Training run accepted.",
            })
            _notify(external.get("accepted_callback"), request)

        def terminal(result: TrainingResult) -> None:
            if not accepted_run:
                _notify(external.get("failed_callback"), result)
                return
            record = self._store.read_run(identity)
            record.update(
                {
                    "status": result_status(result),
                    "finished_at": utc_now(),
                    "result": result_payload(
                        result, log_reference=log_reference
                    ),
                }
            )
            self._store.update_run(identity, record)
            callback_name = {
                "complete": "finished_callback",
                "cancelled": "cancelled_callback",
            }.get(result.status, "failed_callback")
            _notify(external.get(callback_name), result)

        def log_event(event) -> None:  # noqa: ANN001
            nonlocal log_reference
            if accepted_run:
                log_reference = self._store.append_run_event(identity, {
                    "at": utc_now(),
                    "level": event.level,
                    "message": event.message,
                })
            _notify(external.get("log_callback"), event)

        return self._lifecycle.start(
            request,
            accepted_callback=accepted,
            status_callback=external.get("status_callback"),
            log_callback=log_event,
            progress_callback=external.get("progress_callback"),
            finished_callback=terminal,
            failed_callback=terminal,
            cancelled_callback=terminal,
        )

    def inspect_run(self, run_id: str) -> dict[str, Any]:
        record = self._store.read_run(run_id)
        if record.get("schema_version") != RUN_RECORD_VERSION:
            raise ExperimentContractError(
                "unsupported_run_version", "Unsupported experiment run record version."
            )
        return record

    def execution_identity(self, resolved: ResolvedExperiment) -> dict[str, str]:
        request = self._request_from_resolved(
            resolved,
            run_id="identity-only",
            candidate_id="identity-only",
        )
        return {
            "specification_fingerprint": resolved.fingerprint,
            "definition_generation": request.generation_id,
            "registry_fingerprint": request.registry_fingerprint,
            "ordered_ml_fingerprint": request.ordered_ml_fingerprint,
            "derived_semantics_fingerprint": request.derived_semantics_fingerprint,
            "one_hot_fingerprint": request.one_hot_fingerprint,
            "training_execution": "training_lifecycle.v1",
            "preprocessing": request.preprocess_version,
            "metric_contract": resolved.payload["evaluation"]["metric_contract"],
            "data_sha256": file_sha256(request.data_path),
            "build_revision": self._revision_provider(),
        }

    def training_request(
        self,
        resolved: ResolvedExperiment,
        *,
        run_id: str,
        candidate_id: str,
        execution_owner: str = "headless-single",
        campaign_id: str = "",
    ) -> TrainingRequest:
        return self._request_from_resolved(
            resolved,
            run_id=run_id,
            candidate_id=candidate_id,
            execution_owner=execution_owner,
            campaign_id=campaign_id,
        )

    def _request_from_resolved(
        self,
        resolved: ResolvedExperiment,
        *,
        run_id: str,
        candidate_id: str,
        execution_owner: str = "validation",
        campaign_id: str = "",
    ) -> TrainingRequest:
        return build_training_request(
            self._lifecycle,
            resolved,
            run_id=run_id,
            candidate_id=candidate_id,
            execution_owner=execution_owner,
            campaign_id=campaign_id,
            derived_snapshot_provider=self._derived_snapshot_provider,
        )


def _notify(callback, payload) -> None:  # noqa: ANN001
    if callback is not None:
        callback(payload)
