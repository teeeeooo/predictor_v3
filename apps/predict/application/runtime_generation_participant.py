"""Staged Predict runtime generation and stable-identity case migration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from apps.common.runtime_generation import (
    GenerationCandidate,
    ParticipantPrepareError,
    PreparedParticipant,
)
from apps.predict.application.model_compatibility import (
    ModelCompatibilityEvidence,
    inspect_model_compatibility,
)
from apps.predict.composition import (
    PredictWorkspaceComposition,
    build_predict_workspace_composition,
)
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.state.predict_session import (
    PredictSession,
    PredictSessionProjection,
)
from apps.predict.state.result_row import ResultRow


@dataclass(frozen=True)
class _PredictPrepared:
    snapshot: object
    composition: PredictWorkspaceComposition
    session_projection: PredictSessionProjection
    compatibility: ModelCompatibilityEvidence
    session_revision: int


class PredictRuntimeParticipant:
    name = "Predict"

    def __init__(
        self,
        active,
        composition: PredictWorkspaceComposition,
        *,
        model_file: str,
        compatibility_inspector: Callable[[str, object], ModelCompatibilityEvidence] = inspect_model_compatibility,
    ) -> None:
        self._active = active
        self._composition = composition
        self._model_file = model_file
        self._compatibility_inspector = compatibility_inspector

    @property
    def active_generation_id(self) -> str:
        return self._active.manifest.generation.generation_id

    @property
    def composition(self) -> PredictWorkspaceComposition:
        return self._composition

    @property
    def model_compatibility(self) -> ModelCompatibilityEvidence:
        return self._compatibility_inspector(self._model_file, self._active)

    def revision_token(self) -> str:
        path = Path(self._model_file)
        artifact = (
            f"{path.stat().st_mtime_ns}:{path.stat().st_size}"
            if path.exists() else "missing"
        )
        running = self._composition.prediction_controller.is_running
        return (
            f"{self.active_generation_id}:{artifact}:"
            f"session={self._composition.session.revision}:running={int(running)}"
        )

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        if self._composition.prediction_controller.is_running:
            raise ParticipantPrepareError(
                "prediction_in_progress",
                "Prediction is running on the active generation.",
                "Wait for prediction to finish, then Retry Apply.",
            )
        compatibility = self._compatibility_inspector(
            self._model_file, candidate.snapshot
        )
        migrated_cases = _migrated_case_rows(
            self._composition.session, self._active, candidate.snapshot
        )
        migrated_results = _migrated_result_rows(
            self._composition.session, self._active, candidate.snapshot
        )
        controller = self._composition.prediction_controller
        _prediction_service, runner_factory = controller.runtime_dependencies()
        runtime = build_predict_runtime_snapshot(candidate.snapshot)
        composition = build_predict_workspace_composition(
            session=self._composition.session,
            initial_empty_rows=0,
            mapping_repository=self._composition.mapping_repository,
            runner_factory=runner_factory,
            runtime_snapshot=runtime,
            model_file=self._model_file,
            model_lifecycle=controller.model_lifecycle,
        )
        payload = _PredictPrepared(
            candidate.snapshot,
            composition,
            PredictSessionProjection(
                self._composition.session.case_order,
                migrated_cases,
                migrated_results,
            ),
            compatibility,
            self._composition.session.revision,
        )
        return PreparedParticipant(
            self.name,
            candidate.generation_id,
            self.revision_token(),
            payload,
            compatibility=compatibility.status,
        )

    def commit(self, prepared: PreparedParticipant) -> object:
        if prepared.source_revision != self.revision_token():
            raise ParticipantPrepareError(
                "predict_revision_stale",
                "Predict cases, model, or execution state changed after prepare.",
                "Retry Apply",
            )
        prior = (
            self._active,
            self._composition,
            self._composition.session.snapshot_runtime_projection(),
        )
        payload: _PredictPrepared = prepared.payload
        runtime_generation = payload.composition.runtime_snapshot.generation_id
        semantic_generations = {
            runtime_generation,
            payload.composition.generation_id,
            payload.composition.input_mapper.generation_id,
            payload.composition.result_mapper.generation_id,
            payload.composition.prediction_service.generation_id,
            payload.composition.runtime_snapshot.derived.generation_id,
            payload.composition.runtime_snapshot.one_hot.generation_id,
        }
        if semantic_generations != {prepared.generation_id}:
            raise ParticipantPrepareError(
                "predict_runtime_generation_mismatch",
                "Prepared Predict execution semantics do not share one generation.",
                "Restart Required",
            )
        self._composition.session.apply_runtime_projection(
            payload.session_projection,
            expected_revision=payload.session_revision,
        )
        self._composition = payload.composition
        self._active = payload.snapshot
        lifecycle = self._composition.prediction_controller.model_lifecycle
        if lifecycle is not None:
            lifecycle.set_runtime_snapshot(payload.composition.runtime_snapshot)
        return prior

    def rollback(self, prior_state: object) -> None:
        active, composition, session_state = prior_state
        self._active = active
        self._composition = composition
        lifecycle = composition.prediction_controller.model_lifecycle
        if lifecycle is not None:
            lifecycle.set_runtime_snapshot(composition.runtime_snapshot)
        composition.session.restore_runtime_projection(session_state)

    def abort(self, prepared: PreparedParticipant) -> None:
        return None


def _migrated_case_rows(
    session: PredictSession,
    active,
    candidate,
) -> tuple[tuple[str, dict, dict, set], ...]:  # noqa: ANN001
    old_by_id = {item.identity: item for item in active.manifest.features}
    new_by_id = {item.identity: item for item in candidate.manifest.features}
    migrated = []
    for case_id in session.case_order:
        case = session.case_store.get_case(case_id)
        inputs, autofill, dirty = {}, {}, set()
        for identity in old_by_id.keys() & new_by_id.keys():
            before, after = old_by_id[identity], new_by_id[identity]
            old_values = (
                case.input_values if before.role == "input" else case.autofill_values
            )
            if before.column_key not in old_values:
                continue
            value = old_values[before.column_key]
            if before.data_type != after.data_type and value != "" and value is not None:
                raise ParticipantPrepareError(
                    "predict_case_type_incompatible",
                    f"Case value cannot migrate for Feature identity {identity}.",
                )
            target = (
                inputs if after.role == "input"
                else autofill if after.role == "auto"
                else None
            )
            if target is not None:
                target[after.column_key] = value
                if before.column_key in case.dirty_fields:
                    dirty.add(after.column_key)
        migrated.append((case_id, inputs, autofill, dirty))
    return tuple(migrated)


def _migrated_result_rows(
    session: PredictSession,
    active,
    candidate,
) -> tuple[ResultRow, ...]:  # noqa: ANN001
    active_keys = _active_result_keys_by_identity(active)
    candidate_keys = _active_result_keys_by_identity(candidate)
    shared_identities = active_keys.keys() & candidate_keys.keys()
    migrated = []
    for case_id in session.case_order:
        existing = session.results_by_case_id.get(case_id)
        if existing is None:
            continue
        values = {
            candidate_keys[identity]: existing.result_values[active_keys[identity]]
            for identity in shared_identities
            if active_keys[identity] in existing.result_values
        }
        migrated.append(ResultRow(
            case_id=case_id,
            status=existing.status,
            result_values=values,
            message=existing.message,
        ))
    return tuple(migrated)


def _active_result_keys_by_identity(snapshot) -> dict[str, str]:  # noqa: ANN001
    features = {item.identity: item for item in snapshot.manifest.features}
    return {
        target.feature_identity: features[target.feature_identity].column_key
        for target in snapshot.manifest.targets
        if target.active and target.feature_identity in features
    }
