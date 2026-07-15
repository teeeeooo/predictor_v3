"""Saved Data Definition Mapping Requirement handoff lifecycle tests."""

import shutil

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import AddDefinitionIntent
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def test_successful_mapping_requirement_save_creates_canonical_handoff(tmp_path):
    controller = _controller(tmp_path)
    before = controller.refresh()
    added = controller.add_definition(_cond_intent())
    saved = controller.save_schema()

    assert added.last_action_ok
    assert before.projected_feature_rows == added.projected_feature_rows
    assert not saved.draft_changed
    assert len(saved.saved_mapping_handoffs) == 1
    request = saved.saved_mapping_handoffs[0]
    assert request.definition_identity == ("schema_row", "cond_inner_area")
    assert request.definition_label == "Cond Inner Area"
    assert request.mapping_entity == "cond_specs"
    assert request.resolved_group_key == "odu_cond_specs"
    assert request.mapping_attribute == "Cond Inner Area"
    assert request.required and request.saved


def test_handoff_survives_refresh_reset_and_blocked_save_then_success_replaces_it(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    controller.add_definition(_cond_intent())
    saved = controller.save_schema()

    refreshed = controller.refresh()
    reset = controller.reset_draft()
    controller.edit_cell(("schema_row", "cooling_capa"), "data_type", "invalid")
    blocked = controller.save_schema()
    controller.edit_cell(("schema_row", "cooling_capa"), "data_type", "number")
    controller.edit_cell(("schema_row", "idu"), "label", "Indoor Unit")
    unrelated_saved = controller.save_schema()

    expected = saved.saved_mapping_handoffs
    assert refreshed.saved_mapping_handoffs == expected
    assert reset.saved_mapping_handoffs == expected
    assert blocked.status == "blocked"
    assert blocked.saved_mapping_handoffs == expected
    assert unrelated_saved.status == "saved"
    assert unrelated_saved.saved_mapping_handoffs == ()


def test_multiple_saved_requirements_keep_schema_order_and_independent_targets(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    controller.add_definition(_cond_intent())
    controller.add_definition(
        AddDefinitionIntent(
            kind="mapping_attribute",
            label="Fan Diameter",
            column_key="fan_diameter",
            data_type="number",
            required=False,
            mapping_entity="idu",
            mapping_attribute="Fan Diameter",
            trigger_column="idu",
        )
    )

    saved = controller.save_schema()

    assert [item.definition_column_key for item in saved.saved_mapping_handoffs] == [
        "cond_inner_area",
        "fan_diameter",
    ]
    assert [item.resolved_group_key for item in saved.saved_mapping_handoffs] == [
        "odu_cond_specs",
        "idu",
    ]
    assert [item.required for item in saved.saved_mapping_handoffs] == [True, False]


def _controller(tmp_path):  # noqa: ANN001, ANN201
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return DataDefinitionController(DataDefinitionService(schema_path=schema_path))


def _cond_intent() -> AddDefinitionIntent:
    return AddDefinitionIntent(
        kind="mapping_attribute",
        label="Cond Inner Area",
        column_key="cond_inner_area",
        data_type="number",
        required=True,
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        trigger_column="odu",
        rule_id="cond_specs_lookup",
        notes="Supported condenser lookup",
    )
