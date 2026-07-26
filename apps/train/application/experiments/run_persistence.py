"""Durable run acknowledgement and terminal-result callbacks."""

from __future__ import annotations

from typing import Any

from apps.train.application.experiments.records import (
    result_payload,
    result_status,
    run_record,
    utc_now,
)
from apps.train.application.experiments.store import ExperimentStore
from apps.train.state.training_run_state import TrainingRequest, TrainingResult


class ExperimentRunRecorder:
    def __init__(
        self,
        store: ExperimentStore,
        *,
        identity: str,
        request: TrainingRequest,
        resolved,  # noqa: ANN001
        attempt: int,
        build_identity: dict[str, Any],
        external: dict[str, Any],
    ) -> None:
        self._store = store
        self._identity = identity
        self._request = request
        self._resolved = resolved
        self._attempt = attempt
        self._build_identity = build_identity
        self._external = external
        self._accepted = False
        self._log_reference: str | None = None

    def accepted(self, _request: TrainingRequest) -> None:
        self._store.write_run(
            self._identity,
            run_record(
                self._request,
                self._resolved,
                status="starting",
                attempt=self._attempt,
                revision=self._build_identity,
            ),
        )
        self._accepted = True
        self._log_reference = self._store.append_run_event(self._identity, {
            "at": utc_now(),
            "level": "info",
            "message": "Training run accepted.",
        })
        _notify(self._external.get("accepted_callback"), self._request)

    def training_started(self, started_request: TrainingRequest) -> None:
        if not self._accepted:
            raise RuntimeError(
                "Training started before its durable run record was accepted."
            )
        record = self._store.read_run(self._identity)
        if not record.get("training_started"):
            record.update({
                "status": "running",
                "training_started": True,
                "training_started_at": utc_now(),
            })
            self._store.update_run(self._identity, record)
        _notify(self._external.get("started_callback"), started_request)

    def terminal(self, result: TrainingResult) -> None:
        if not self._accepted:
            _notify(self._external.get("failed_callback"), result)
            return
        record = self._store.read_run(self._identity)
        record.update({
            "status": result_status(result),
            "finished_at": utc_now(),
            "result": result_payload(
                result, log_reference=self._log_reference
            ),
        })
        self._store.update_run(self._identity, record)
        callback_name = {
            "complete": "finished_callback",
            "cancelled": "cancelled_callback",
        }.get(result.status, "failed_callback")
        _notify(self._external.get(callback_name), result)

    def log_event(self, event) -> None:  # noqa: ANN001
        if self._accepted:
            self._log_reference = self._store.append_run_event(self._identity, {
                "at": utc_now(),
                "level": event.level,
                "message": event.message,
            })
        _notify(self._external.get("log_callback"), event)


def _notify(callback, payload) -> None:  # noqa: ANN001
    if callback is not None:
        callback(payload)
