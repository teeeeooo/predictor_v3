"""Data Definition training/model readiness integration tests."""

from core.data_definition import build_data_definition_draft, build_data_definition_save_plan
from core.data_definition.draft import replace_draft_row
from core.data_definition.projection import project_feature_catalog_from_schema
from core.data_definition.readiness import build_readiness_checks


def test_readiness_explicit_directory_path_is_unavailable(tmp_path):
    projected = project_feature_catalog_from_schema()

    check = _readiness_by_name(build_readiness_checks(projected, tmp_path))[
        "training_headers"
    ]

    assert check.status == "unavailable"
    assert "not a file" in check.message
    assert str(tmp_path) in check.message


def test_save_plan_marks_retrain_for_model_input_name_and_source_changes():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")

    ml_name_changed = replace_draft_row(draft, row.identity, ml_name="Cooling_Capacity")
    value_source_changed = replace_draft_row(draft, row.identity, value_source="mapping_lookup")

    ml_name_plan = build_data_definition_save_plan(ml_name_changed)
    value_source_plan = build_data_definition_save_plan(value_source_changed)

    assert ml_name_plan.requires_retrain
    assert value_source_plan.requires_retrain
    assert not ml_name_plan.can_save_schema
    assert not value_source_plan.can_save_schema
    assert "retrain_required_for_new_model_input" in _blocker_codes(ml_name_plan)
    assert "retrain_required_for_new_model_input" in _blocker_codes(value_source_plan)
    assert "ml_compatibility_projection_write_required" in _blocker_codes(ml_name_plan)
    assert "ml_compatibility_projection_write_required" in _blocker_codes(value_source_plan)


def test_save_plan_marks_schema_visible_editor_data_type_restart_required():
    draft = build_data_definition_draft()
    numeric_row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    dropdown_row = next(item for item in draft.rows if item.column_key == "idu")

    for row, field_name, value in (
        (numeric_row, "visible", not numeric_row.visible),
        (dropdown_row, "editor", "number"),
        (dropdown_row, "data_type", "number"),
    ):
        changed = replace_draft_row(draft, row.identity, **{field_name: value})
        plan = build_data_definition_save_plan(changed)

        assert plan.requires_restart
        assert not plan.requires_retrain
        assert "restart-required" in plan.restart_impact.message


def _readiness_by_name(readiness):
    return {check.name: check for check in readiness}


def _blocker_codes(plan):
    return {blocker.code for blocker in plan.blocked_reasons}
