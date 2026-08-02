"""Predict QWidget adapter for an already committed runtime composition."""

from __future__ import annotations

from apps.predict.composition import PredictWorkspaceComposition
from apps.predict.ui.status_widgets import render_target_badge
from apps.predict.ui.result_review import ResultReviewTableModel
from apps.predict.ui.tables.case_table_model import CaseTableModel


def apply_runtime_composition(workspace, composition: PredictWorkspaceComposition) -> None:  # noqa: ANN001
    if composition.session is not workspace.session:
        raise ValueError("runtime composition must retain the Predict session")
    horizontal_scroll = workspace.case_table.horizontalScrollBar()
    scroll_value = horizontal_scroll.value()
    result_horizontal_scroll = workspace.result_review_table.horizontalScrollBar()
    result_scroll_value = result_horizontal_scroll.value()
    workspace.bulk_paste_ui.clear_history()
    workspace.table_edit_controller = composition.table_edit_controller
    workspace.input_edit_controller = composition.input_edit_controller
    workspace.bulk_paste_transaction = composition.bulk_paste_transaction
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
    workspace.case_table.set_paste_handler(workspace.bulk_paste_ui.apply)
    workspace.result_review_model = ResultReviewTableModel(
        composition.result_review_projection
    )
    workspace.result_review_table.setModel(workspace.result_review_model)
    workspace.model_group.rebind(workspace.case_model, workspace.result_review_model)
    workspace.case_selection.bind()
    workspace.group_header.rebind(composition.columns)
    render_target_badge(
        workspace.target_badge,
        composition.runtime_snapshot,
        composition.columns,
    )
    workspace._configure_tables()
    workspace._refresh()
    workspace._reconcile_shared_case_selection()
    workspace._show_workspace_surface()
    workspace.case_table.updateGeometries()
    workspace.result_review_table.updateGeometries()
    horizontal_scroll.setValue(min(scroll_value, horizontal_scroll.maximum()))
    result_horizontal_scroll.setValue(
        min(result_scroll_value, result_horizontal_scroll.maximum())
    )
    workspace.model_lifecycle_ui.render_current()
    workspace._refresh_prediction_command_state()
