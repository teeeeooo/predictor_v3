"""Arc 15C-1 Data Definition draft and save contract tests."""

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    build_data_definition_draft,
    build_data_definition_report,
    build_data_definition_save_plan,
    field_editability,
)
from core.data_definition.draft import replace_draft_row
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2


def test_data_definition_draft_builds_schema_and_derived_policy_rows():
    draft = build_data_definition_draft()

    schema_rows = [row for row in draft.rows if row.source_kind == "schema_row"]
    derived_rows = [row for row in draft.rows if row.source_kind == "derived_policy"]

    assert len(schema_rows) == len(load_predict_schema_catalog_v2().rows)
    assert len(derived_rows) == 8
    assert schema_rows[0].column_key == "cooling_capa"
    assert derived_rows[0].ml_name == "Cool_Capa_per_EER"
    assert not draft.is_changed


def test_data_definition_edit_policy_separates_editable_and_restricted_fields():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    derived_row = next(row for row in draft.rows if row.source_kind == "derived_policy")

    assert field_editability(schema_row, "label").editable
    assert field_editability(schema_row, "notes").editable
    assert field_editability(schema_row, "column_key").category == (
        "schema_backed_restricted"
    )
    assert field_editability(schema_row, "display_order").category == (
        "schema_backed_restricted"
    )
    assert field_editability(schema_row, "role").category == "schema_backed_restricted"
    assert field_editability(schema_row, "mapping_value").category == "mapping_value_owned"
    assert field_editability(derived_row, "ml_name").category == "derived_policy_blocked"


def test_data_definition_save_plan_for_unchanged_draft_is_noop_preview():
    draft = build_data_definition_draft()
    plan = build_data_definition_save_plan(draft)

    assert not plan.changed_fields
    assert not plan.can_save_schema
    assert not plan.can_write_features_projection
    assert not plan.can_write_derived_policy
    assert not plan.requires_restart
    assert not plan.requires_retrain
    assert _target_status(plan, "schema_csv") == "no_op"
    assert _target_status(plan, "features_csv") == "blocked"
    assert build_data_definition_report().ok


def test_data_definition_save_plan_blocks_features_csv_dual_writer_risk():
    draft = build_data_definition_draft()
    plan = build_data_definition_save_plan(draft, requested_targets=("features_csv",))

    assert not plan.can_write_features_projection
    assert _target_status(plan, "features_csv") == "blocked"
    assert _blocker_codes(plan) >= {"features_csv_dual_writer_not_resolved"}


def test_data_definition_save_plan_blocks_derived_policy_persistence():
    draft = build_data_definition_draft()
    derived_row = next(row for row in draft.rows if row.source_kind == "derived_policy")
    changed = replace_draft_row(
        draft,
        derived_row.identity,
        ml_name=f"{derived_row.ml_name}_edited",
    )

    plan = build_data_definition_save_plan(changed, requested_targets=("derived_policy",))

    assert not plan.can_save_schema
    assert not plan.can_write_derived_policy
    assert _blocker_codes(plan) >= {"derived_policy_persistence_required"}
    assert _target_status(plan, "derived_policy") == "blocked"


def test_data_definition_save_plan_blocks_mapping_value_ownership():
    draft = build_data_definition_draft()
    plan = build_data_definition_save_plan(draft, requested_targets=("mapping_json",))

    assert "mapping_json" in {target.target for target in plan.planned_targets}
    assert _target_status(plan, "mapping_json") == "blocked"
    assert _blocker_codes(plan) >= {"mapping_value_edit_not_allowed"}


def test_data_definition_save_plan_blocks_model_input_projection_change():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(
        draft,
        schema_row.identity,
        model_input_enabled=not schema_row.model_input_enabled,
    )

    plan = build_data_definition_save_plan(changed)

    blocker = _blocker(plan, "ml_compatibility_projection_write_required")

    assert not plan.can_save_schema
    assert plan.requires_restart
    assert plan.requires_retrain
    assert "retrain_required_for_new_model_input" in _blocker_codes(plan)
    assert blocker.severity == "error"
    assert blocker.target == "schema_csv"
    assert _target_status(plan, "schema_csv") == "blocked"
    assert "retrain" in plan.restart_impact.message.lower()


def test_data_definition_save_plan_blocks_ml_name_projection_change():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, ml_name="Cooling Capacity Renamed")

    plan = build_data_definition_save_plan(changed)
    blocker = _blocker(plan, "ml_compatibility_projection_write_required")

    assert not plan.can_save_schema
    assert blocker.severity == "error"
    assert blocker.target == "schema_csv"
    assert "features.csv" in blocker.message


def test_data_definition_save_plan_blocks_one_hot_group_projection_change():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.role == "one_hot_feature")
    changed = replace_draft_row(draft, row.identity, one_hot_group="changed_group")

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert _target_status(plan, "schema_csv") == "blocked"
    assert "ml_compatibility_projection_write_required" in _blocker_codes(plan)


def test_data_definition_save_plan_blocks_active_projection_change():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, active=False)

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "ml_compatibility_projection_write_required" in _blocker_codes(plan)


def test_data_definition_save_plan_marks_deferred_mapping_and_one_hot_work():
    draft = build_data_definition_draft()
    mapping_row = next(row for row in draft.rows if row.column_key == "evap_area")
    one_hot_row = next(row for row in draft.rows if row.column_key == "ref_type")
    changed = replace_draft_row(
        draft,
        mapping_row.identity,
        mapping_attribute="Evap Inner Surface Area",
    )
    changed = replace_draft_row(
        changed,
        one_hot_row.identity,
        one_hot_group="tube_type",
    )

    plan = build_data_definition_save_plan(changed)

    assert plan.can_save_schema
    assert _blocker_codes(plan) >= {
        "data_mapping_dynamic_requirement_deferred",
        "one_hot_runtime_owner_deferred",
    }


def test_data_definition_save_plan_blocks_column_key_direct_edit():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, schema_row.identity, column_key="cooling_capacity")

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "restricted_field_edit_not_allowed" in _blocker_codes(plan)


def test_data_definition_save_plan_blocks_display_order_direct_edit():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(
        draft,
        schema_row.identity,
        display_order=schema_row.display_order + 1,
    )

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "restricted_field_edit_not_allowed" in _blocker_codes(plan)


def test_data_definition_save_plan_blocks_role_direct_edit():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, schema_row.identity, role="auto")

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "restricted_field_edit_not_allowed" in _blocker_codes(plan)


def test_data_definition_save_plan_blocks_raw_row_add():
    draft = build_data_definition_draft()
    changed = DataDefinitionDraft(
        rows=(
            *draft.rows,
            DataDefinitionDraftRow(
                source_kind="schema_row",
                column_key="raw_new_feature",
                role="input",
            ),
        ),
        baseline_rows=draft.baseline_rows,
    )

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "raw_row_add_delete_not_allowed" in _blocker_codes(plan)


def test_data_definition_save_plan_blocks_raw_row_delete():
    draft = build_data_definition_draft()
    changed = DataDefinitionDraft(
        rows=draft.rows[1:],
        baseline_rows=draft.baseline_rows,
    )

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "raw_row_add_delete_not_allowed" in _blocker_codes(plan)


def test_data_definition_save_plan_allows_schema_backed_label_change():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, schema_row.identity, label="Cooling Capacity")

    plan = build_data_definition_save_plan(changed)

    assert plan.can_save_schema
    assert _target_status(plan, "schema_csv") == "planned"
    assert "restricted_field_edit_not_allowed" not in _blocker_codes(plan)
    assert "raw_row_add_delete_not_allowed" not in _blocker_codes(plan)


def test_data_definition_save_plan_allows_notes_change_without_ml_impact():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, schema_row.identity, notes="Display note only")

    plan = build_data_definition_save_plan(changed)

    assert plan.can_save_schema
    assert _target_status(plan, "schema_csv") == "planned"
    assert "ml_compatibility_projection_write_required" not in _blocker_codes(plan)


def _target_status(plan, target):
    return next(item.status for item in plan.planned_targets if item.target == target)


def _blocker_codes(plan):
    return {blocker.code for blocker in plan.blocked_reasons}


def _blocker(plan, code):
    return next(blocker for blocker in plan.blocked_reasons if blocker.code == code)
