"""Concrete composition owner for the Predict desktop surface."""

from __future__ import annotations

from dataclasses import dataclass

from apps.common.model_lifecycle import ModelLifecycleRepository, ModelResolution
from apps.predict.adapters.dropdown_option_adapter import DropdownOptionAdapter
from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.pyside_prediction_runner import PySidePredictionRunner
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.model_lifecycle import PredictModelLifecycleService
from apps.predict.application.bulk_paste import BulkPasteTransaction
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.application.result_review import ResultReviewProjection
from apps.predict.application.workspace_state import PredictWorkspaceState
from apps.predict.application.result_contract import (
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import (
    PredictRuntimeSnapshot,
    compatibility_predict_runtime_snapshot,
    validate_runtime_target_contract,
)
from apps.predict.controllers.input_edit_controller import InputEditController
from apps.predict.controllers.prediction_controller import (
    PredictionController,
    PredictionRunnerFactory,
)
from apps.predict.controllers.table_edit_controller import TableEditController
from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.ports.prediction_execution_port import PredictionExecutionPort
from apps.predict.ports.prediction_workflow_ports import (
    PredictionInputMapper,
    PredictionResultMapper,
    PredictionServicePort,
)
from apps.predict.schema.case_table_schema_adapter import (
    UnifiedCaseColumn,
    build_case_table_column_schema,
)
from apps.predict.schema.column_schema_adapter import (
    build_predict_column_schema,
    build_result_column_schema,
)
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.predict_session import PredictSession
from core.predictor_schema.catalog_v2 import PredictSchemaV2Row
from core.data_definition.one_hot import OneHotRuntimeSnapshot
from core.ml.artifacts import MODEL_FILE


@dataclass(frozen=True)
class PredictWorkspaceComposition:
    """Collaborators used by one Predict workspace instance."""

    session: PredictSession
    table_edit_controller: TableEditController
    input_edit_controller: InputEditController
    bulk_paste_transaction: BulkPasteTransaction
    prediction_controller: PredictionController
    input_mapper: PredictionInputMapper
    result_mapper: PredictionResultMapper
    prediction_service: PredictionServicePort
    dropdown_option_adapter: DropdownOptionAdapter
    mapping_repository: PredictMappingRepository
    columns: tuple[UnifiedCaseColumn, ...]
    generation_id: str
    runtime_snapshot: PredictRuntimeSnapshot
    result_review_projection: ResultReviewProjection
    workspace_state: PredictWorkspaceState


def build_predict_workspace_composition(
    *,
    session: PredictSession | None = None,
    initial_empty_rows: int = 3,
    mapping_repository: PredictMappingRepository | None = None,
    input_mapper: PredictionInputMapper | None = None,
    result_mapper: PredictionResultMapper | None = None,
    prediction_service: PredictionServicePort | None = None,
    runner_factory: PredictionRunnerFactory | None = None,
    one_hot_snapshot: OneHotRuntimeSnapshot | None = None,
    predict_projection: tuple[PredictSchemaV2Row, ...] | None = None,
    runtime_snapshot: PredictRuntimeSnapshot | None = None,
    model_file: str = MODEL_FILE,
    lifecycle_repository: ModelLifecycleRepository | None = None,
    model_resolution: ModelResolution | None = None,
    model_lifecycle: PredictModelLifecycleService | None = None,
    model_identity: PredictionModelIdentity | None = None,
    workspace_state: PredictWorkspaceState | None = None,
) -> PredictWorkspaceComposition:
    """Build the concrete Predict object graph without constructing widgets."""

    resolved_session = session or PredictSession()
    table_edit_controller = TableEditController(resolved_session)
    table_edit_controller.ensure_initial_rows(initial_empty_rows)

    resolved_repository = mapping_repository or PredictMappingRepository()
    runtime = runtime_snapshot or compatibility_predict_runtime_snapshot()
    if (
        predict_projection is not None
        and predict_projection != runtime.predict_projection
    ):
        raise ValueError(
            "predict_projection cannot establish canonical Feature identity; "
            "provide a complete runtime_snapshot"
        )
    if one_hot_snapshot is not None and one_hot_snapshot != runtime.one_hot:
        raise ValueError(
            "one_hot_snapshot cannot establish canonical generation authority; "
            "provide a repository-issued runtime_snapshot"
        )
    validate_runtime_target_contract(runtime)
    resolved_one_hot_snapshot = runtime.one_hot
    column_descriptors = runtime.column_descriptors
    predict_columns = build_predict_column_schema(column_descriptors)
    input_edit_controller = InputEditController(
        resolved_session,
        mapping_repository=resolved_repository,
        columns=predict_columns,
    )
    resolved_input_mapper = input_mapper or RowToMlInputAdapter(
        columns=tuple(item for item in predict_columns if item.group in {"input", "auto"}),
        one_hot_snapshot=resolved_one_hot_snapshot
    )
    resolved_result_mapper = result_mapper or PredictionResultAdapter(
        build_result_column_schema(column_descriptors),
        input_columns=tuple(
            item for item in predict_columns if item.group in {"input", "auto"}
        ),
        active_targets=runtime.active_targets,
        target_result_keys=runtime.target_result_keys,
        target_descriptors=runtime.target_descriptors,
        generation_id=runtime.generation_id,
    )
    service = prediction_service or PredictionService(
        model_file=model_file,
        runtime_snapshot=runtime,
    )
    lifecycle = model_lifecycle
    if lifecycle is None and lifecycle_repository is not None:
        lifecycle = PredictModelLifecycleService(
            lifecycle_repository,
            runtime,
            lambda path, snapshot: PredictionService(
                model_file=path,
                runtime_snapshot=snapshot,
            ),
        )
        if model_resolution is not None and model_resolution.status == "resolved":
            try:
                lifecycle.initialize_loaded(
                    service,
                    candidate_id=model_resolution.candidate_id,
                    active_revision=model_resolution.revision,
                )
            except Exception as exc:
                lifecycle.record_startup_failure(
                    f"{type(exc).__name__}: {str(exc)}"
                )
    loaded = lifecycle.loaded if lifecycle is not None else None
    resolved_model_identity = model_identity or PredictionModelIdentity(
        candidate_id=loaded.candidate_id if loaded is not None else f"unmanaged:{model_file}",
        active_revision=loaded.active_revision if loaded is not None else 0,
        generation_id=loaded.generation_id if loaded is not None else runtime.generation_id,
    )
    usecase = PredictionUseCase(
        resolved_session,
        input_mapper=resolved_input_mapper,
        result_mapper=resolved_result_mapper,
        execution_semantics=execution_semantics_from_runtime(runtime),
        model_identity=resolved_model_identity,
    )
    prediction_controller = PredictionController(
        resolved_session,
        usecase=usecase,
        service=service,
        runner_factory=runner_factory or _build_pyside_runner,
        model_lifecycle=lifecycle,
    )
    columns = build_case_table_column_schema(column_descriptors)
    dropdown_option_adapter = DropdownOptionAdapter(
        resolved_repository, columns, one_hot_snapshot=resolved_one_hot_snapshot
    )
    bulk_paste_transaction = BulkPasteTransaction(
        resolved_session,
        predict_columns,
        resolved_repository.load,
        dropdown_option_adapter.base_options_for_key_from_mapping,
    )
    return PredictWorkspaceComposition(
        session=resolved_session,
        table_edit_controller=table_edit_controller,
        input_edit_controller=input_edit_controller,
        bulk_paste_transaction=bulk_paste_transaction,
        prediction_controller=prediction_controller,
        input_mapper=resolved_input_mapper,
        result_mapper=resolved_result_mapper,
        prediction_service=service,
        dropdown_option_adapter=dropdown_option_adapter,
        mapping_repository=resolved_repository,
        columns=columns,
        generation_id=runtime.generation_id,
        runtime_snapshot=runtime,
        result_review_projection=ResultReviewProjection(
            resolved_session, runtime.column_descriptors
        ),
        workspace_state=workspace_state or PredictWorkspaceState(),
    )


def _build_pyside_runner(service: PredictionServicePort) -> PredictionExecutionPort:
    return PySidePredictionRunner(service=service)


__all__ = [
    "PredictWorkspaceComposition",
    "build_predict_workspace_composition",
]
