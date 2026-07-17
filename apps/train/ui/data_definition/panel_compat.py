"""Compatibility aliases and state lookup kept outside panel composition."""

from __future__ import annotations


def publish_diagnostic_aliases(panel) -> None:  # noqa: ANN001
    for name in (
        "summary_table", "draft_table", "draft_changes_table", "save_plan_table",
        "save_blockers_table", "save_result_table", "projected_features_table",
        "mapping_requirements_table", "one_hot_table", "readiness_table", "issues_table",
    ):
        setattr(panel, name, getattr(panel.diagnostics, name))


def publish_workspace_aliases(panel) -> None:  # noqa: ANN001
    aliases = {
        "status_label": panel.task_header.status_label,
        "refresh_action": panel.task_header.refresh_action,
        "reset_action": panel.task_header.reset_action,
        "details_action": panel.task_header.details_action,
        "more_button": panel.task_header.more_button,
        "add_definition_button": panel.task_header.add_button,
        "edit_button": panel.task_header.edit_button,
        "save_button": panel.task_header.save_button,
        "review_blockers_button": panel.task_header.review_button,
        "add_manual_action": panel.task_header.add_manual_action,
        "add_mapping_predict_action": panel.task_header.add_mapping_action,
        "add_mapping_attribute_action": panel.task_header.add_attribute_action,
        "add_predict_only_action": panel.task_header.add_predict_only_action,
        "add_ml_only_action": panel.task_header.add_ml_only_action,
        "add_helper_action": panel.task_header.add_helper_action,
        "rename_action": panel.task_header.rename_action,
        "duplicate_action": panel.task_header.duplicate_action,
        "remove_action": panel.task_header.remove_action,
        "toggle_active_action": panel.task_header.toggle_active_action,
        "move_predict_up_action": panel.task_header.move_predict_up_action,
        "move_predict_down_action": panel.task_header.move_predict_down_action,
        "move_ml_up_action": panel.task_header.move_ml_up_action,
        "move_ml_down_action": panel.task_header.move_ml_down_action,
        "impact_preview_button": panel.task_header.preview_button,
        "inventory_state_label": panel.inventory_view.state_label,
        "clear_filters_button": panel.inventory_view.clear_button,
        "detail_state_label": panel.task_header.detail_label,
    }
    for name, value in aliases.items():
        setattr(panel, name, value)


def selected_values(state, identity):  # noqa: ANN001, ANN201
    if state is None or identity is None:
        return None
    try:
        index = state.draft_row_identities.index(identity)
    except ValueError:
        return None
    return {cell.field_name: cell.value for cell in state.draft_rows[index]}


def read_only_tables(panel):  # noqa: ANN001, ANN201
    return panel.diagnostics.read_only_tables()
