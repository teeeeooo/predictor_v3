"""Train/Model runtime-generation participant."""

import csv
import hashlib
from pathlib import Path
from typing import Callable

from apps.common.runtime_generation import GenerationCandidate, PreparedParticipant
from apps.common.runtime_generation import GenerationSnapshot
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    model_registry_snapshot,
)

from .errors import ParticipantPrepareError


class TrainRuntimeParticipant:
    name = "Train / Model"

    def __init__(
        self,
        active: GenerationSnapshot,
        *,
        selected_data_path_provider: Callable[[], str] | None = None,
    ) -> None:
        self._active = active
        self._registry = model_registry_snapshot(active.manifest)
        self._selected_data_path_provider = selected_data_path_provider
        self._selection_revision = 0
        self._execution_state_provider: Callable[[], str] = lambda: "idle"

    def set_selected_data_path_provider(self, provider: Callable[[], str]) -> None:
        """Attach the shell-owned selection without making Train depend on Qt."""
        self._selected_data_path_provider = provider
        self._selection_revision += 1

    def note_selected_data_changed(self) -> None:
        self._selection_revision += 1

    def set_execution_state_provider(self, provider: Callable[[], str]) -> None:
        self._execution_state_provider = provider

    @property
    def active_generation_id(self) -> str:
        return self._active.manifest.generation.generation_id

    @property
    def registry_snapshot(self) -> ModelRegistrySnapshot:
        return self._registry

    @property
    def derived_evaluation_snapshot(self):  # noqa: ANN201
        from core.data_definition.derived.evaluator import evaluation_snapshot

        return evaluation_snapshot(self._active.manifest)

    def revision_token(self) -> str:
        evidence = self._selected_data_evidence()
        return (
            f"{self.active_generation_id}:selection={self._selection_revision}:"
            f"data={'|'.join(str(item) for item in evidence)}:"
            f"execution={self._execution_state_provider()}"
        )

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        registry = model_registry_snapshot(candidate.snapshot.manifest)
        self._validate_selected_training_data(registry)
        return PreparedParticipant(
            self.name,
            candidate.generation_id,
            self.revision_token(),
            (candidate.snapshot, registry),
        )

    def commit(self, prepared: PreparedParticipant) -> object:
        if prepared.source_revision != self.revision_token():
            raise ParticipantPrepareError(
                "training_data_revision_stale",
                "Training selection or execution state changed after prepare.",
                "Retry Apply",
            )
        prior = self._active, self._registry
        self._active, self._registry = prepared.payload
        return prior

    def rollback(self, prior_state: object) -> None:
        self._active, self._registry = prior_state

    def abort(self, prepared: PreparedParticipant) -> None:
        return None

    def _validate_selected_training_data(self, registry: ModelRegistrySnapshot) -> None:
        if self._selected_data_path_provider is None:
            return
        selected = self._selected_data_path_provider().strip()
        path = Path(selected) if selected else None
        if path is None or not path.is_file():
            return
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as source:
                headers = {item.strip() for item in next(csv.reader(source), ()) if item.strip()}
        except (OSError, UnicodeError, csv.Error) as exc:
            raise ParticipantPrepareError(
                "training_data_header_unavailable",
                "Selected training data could not be revalidated.",
                "Select a readable training CSV and retry.",
            ) from exc
        missing = tuple(item for item in registry.training_headers if item not in headers)
        if missing:
            raise ParticipantPrepareError(
                "training_data_header_incompatible",
                "Selected training data does not satisfy the candidate generation.",
                "Update the training data selection or headers and retry.",
                missing[:12],
            )

    def _selected_data_evidence(self) -> tuple[object, ...]:
        selected = (
            self._selected_data_path_provider().strip()
            if self._selected_data_path_provider is not None else ""
        )
        if not selected:
            return ("", "unselected")
        path = Path(selected)
        if not path.is_file():
            return (selected, "missing")
        try:
            stat = path.stat()
            with path.open("rb") as source:
                header = source.readline()
        except OSError:
            return (selected, "unreadable")
        return (
            selected,
            "file",
            stat.st_size,
            stat.st_mtime_ns,
            stat.st_ctime_ns,
            hashlib.sha256(header).hexdigest(),
        )
