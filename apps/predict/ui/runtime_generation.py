"""Predict QWidget adapter for an already committed runtime composition."""

from __future__ import annotations

from apps.predict.composition import PredictWorkspaceComposition
from apps.predict.ui.tables.case_table_model import CaseTableModel


def apply_runtime_composition(workspace, composition: PredictWorkspaceComposition) -> None:  # noqa: ANN001
    if composition.session is not workspace.session:
        raise ValueError("runtime composition must retain the Predict session")
    workspace.table_edit_controller = composition.table_edit_controller
    workspace.input_edit_controller = composition.input_edit_controller
    workspace.prediction_controller = composition.prediction_controller
    workspace.dropdown_option_adapter = composition.dropdown_option_adapter
    workspace.mapping_repository = composition.mapping_repository
    workspace.generation_id = composition.generation_id
    workspace.case_model = CaseTableModel(
        workspace.session,
        columns=composition.columns,
        edit_callback=workspace._handle_input_cell_edited,
    )
    workspace.case_table.setModel(workspace.case_model)
    workspace._configure_tables()
    workspace._refresh()
