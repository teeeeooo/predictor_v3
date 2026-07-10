"""Concrete composition owner for the Predict desktop surface."""

from __future__ import annotations

from dataclasses import dataclass

from apps.predict.adapters.dropdown_option_adapter import DropdownOptionAdapter
from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.pyside_prediction_runner import PySidePredictionRunner
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.prediction_usecase import PredictionUseCase
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
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.predict_session import PredictSession


@dataclass(frozen=True)
class PredictWorkspaceComposition:
    """Collaborators used by one Predict workspace instance."""

    session: PredictSession
    table_edit_controller: TableEditController
    input_edit_controller: InputEditController
    prediction_controller: PredictionController
    dropdown_option_adapter: DropdownOptionAdapter
    mapping_repository: PredictMappingRepository
    columns: tuple[UnifiedCaseColumn, ...]


def build_predict_workspace_composition(
    *,
    session: PredictSession | None = None,
    initial_empty_rows: int = 3,
    mapping_repository: PredictMappingRepository | None = None,
    input_mapper: PredictionInputMapper | None = None,
    result_mapper: PredictionResultMapper | None = None,
    prediction_service: PredictionServicePort | None = None,
    runner_factory: PredictionRunnerFactory | None = None,
) -> PredictWorkspaceComposition:
    """Build the concrete Predict object graph without constructing widgets."""

    resolved_session = session or PredictSession()
    table_edit_controller = TableEditController(resolved_session)
    table_edit_controller.ensure_initial_rows(initial_empty_rows)

    resolved_repository = mapping_repository or PredictMappingRepository()
    input_edit_controller = InputEditController(
        resolved_session,
        mapping_repository=resolved_repository,
    )
    resolved_input_mapper = input_mapper or RowToMlInputAdapter()
    resolved_result_mapper = result_mapper or PredictionResultAdapter()
    usecase = PredictionUseCase(
        resolved_session,
        input_mapper=resolved_input_mapper,
        result_mapper=resolved_result_mapper,
    )
    service = prediction_service or PredictionService()
    prediction_controller = PredictionController(
        resolved_session,
        usecase=usecase,
        service=service,
        runner_factory=runner_factory or _build_pyside_runner,
    )
    columns = build_case_table_column_schema()
    dropdown_option_adapter = DropdownOptionAdapter(resolved_repository, columns)
    return PredictWorkspaceComposition(
        session=resolved_session,
        table_edit_controller=table_edit_controller,
        input_edit_controller=input_edit_controller,
        prediction_controller=prediction_controller,
        dropdown_option_adapter=dropdown_option_adapter,
        mapping_repository=resolved_repository,
        columns=columns,
    )


def _build_pyside_runner(service: PredictionServicePort) -> PredictionExecutionPort:
    return PySidePredictionRunner(service=service)


__all__ = [
    "PredictWorkspaceComposition",
    "build_predict_workspace_composition",
]
