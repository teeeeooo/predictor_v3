"""Train Data Definition readiness preview integration tests."""

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _controller() -> DataDefinitionController:
    return DataDefinitionController(
        DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    )


def test_controller_surfaces_retrain_required_preview_for_model_input_change():
    controller = _controller()
    state = controller.refresh()

    edited = controller.edit_cell(
        state.draft_row_identities[0],
        "ml_name",
        "Cooling_Capacity",
    )

    assert edited.draft_changed
    assert not edited.can_save_schema
    assert ("Impact", "Schema restart and model retrain are required before activation.") in (
        edited.summary_rows
    )
    assert any(row[1] == "retrain_required_for_new_model_input" for row in edited.save_blocker_rows)
    assert any(
        row[:3]
        == ("error", "ml_compatibility_projection_write_required", "schema_csv")
        for row in edited.save_blocker_rows
    )


def test_controller_surfaces_restart_only_preview_for_visible_change():
    controller = _controller()
    state = controller.refresh()
    visible_col = next(
        index for index, cell in enumerate(state.draft_rows[0])
        if cell.field_name == "visible"
    )
    new_value = "false" if state.draft_rows[0][visible_col].value == "true" else "true"

    edited = controller.edit_cell(state.draft_row_identities[0], "visible", new_value)

    assert edited.draft_changed
    assert edited.can_save_schema
    assert ("Impact", "Schema change is restart-required.") in edited.summary_rows
    assert not any(
        row[1] == "retrain_required_for_new_model_input"
        for row in edited.save_blocker_rows
    )
