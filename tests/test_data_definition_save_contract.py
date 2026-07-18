"""Arc 15C-1 Data Definition draft and save contract tests."""

from dataclasses import replace

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    EditDefinitionIntent,
    RenameDefinitionIntent,
    apply_edit_definition_command,
    apply_rename_definition_command,
    build_data_definition_draft,
    build_data_definition_report,
    build_data_definition_save_plan,
    field_editability,
)
from core.data_definition.draft import replace_draft_row
from core.data_definition.projection import (
    project_feature_catalog_from_draft,
    projected_feature_catalog_fingerprint,
)
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


def test_raw_derived_edit_is_blocked_without_controlled_command():
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
    assert _blocker_codes(plan) >= {"raw_row_add_delete_not_allowed"}
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
    assert blocker.row_identity == row.identity
    assert blocker.field_name == "ml_name"
    assert len(_blockers(plan, "ml_compatibility_projection_write_required")) == 1
    assert "features.csv" in blocker.message


def test_data_definition_save_plan_excludes_notes_from_single_projection_context():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(
        draft,
        row.identity,
        ml_name="Cooling Capacity Renamed",
        notes="description changed",
    )

    plan = build_data_definition_save_plan(changed)
    blockers = _blockers(plan, "ml_compatibility_projection_write_required")

    assert [(item.row_identity, item.field_name) for item in blockers] == [
        (row.identity, "ml_name"),
    ]
    assert blockers[0].target == "schema_csv"
    assert "features.csv projection writer" in blockers[0].message


def test_data_definition_save_plan_attributes_compound_projection_change_by_definition():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    changed = replace_draft_row(
        draft,
        row.identity,
        model_input_enabled=True,
        ml_name="IDU",
        notes="description changed",
    )
    before = (changed.rows, changed.baseline_rows, changed.changes())

    plan = build_data_definition_save_plan(changed)
    blockers = _blockers(plan, "ml_compatibility_projection_write_required")

    assert not plan.can_save_schema
    assert [blocker.row_identity for blocker in blockers] == [row.identity, row.identity]
    assert [blocker.field_name for blocker in blockers] == [
        "model_input_enabled",
        "ml_name",
    ]
    assert all(blocker.target == "schema_csv" for blocker in blockers)
    assert (changed.rows, changed.baseline_rows, changed.changes()) == before


def test_data_definition_save_plan_attributes_compound_changes_for_each_definition():
    draft = build_data_definition_draft()
    first = next(item for item in draft.rows if item.column_key == "idu")
    second = next(item for item in draft.rows if item.column_key == "evap_index")
    changed = replace_draft_row(
        draft,
        first.identity,
        model_input_enabled=True,
        ml_name="IDU",
    )
    changed = replace_draft_row(
        changed,
        second.identity,
        model_input_enabled=True,
        ml_name="Evap Index",
    )

    plan = build_data_definition_save_plan(changed)
    blockers = _blockers(plan, "ml_compatibility_projection_write_required")

    assert [(item.row_identity, item.field_name) for item in blockers] == [
        (first.identity, "model_input_enabled"),
        (first.identity, "ml_name"),
        (second.identity, "model_input_enabled"),
        (second.identity, "ml_name"),
    ]


def test_data_definition_save_plan_removes_compound_attribution_after_partial_revert():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    compound = replace_draft_row(
        draft,
        row.identity,
        model_input_enabled=True,
        ml_name="IDU",
        notes="description changed",
    )
    partial = replace_draft_row(compound, row.identity, model_input_enabled=False)

    blocked = build_data_definition_save_plan(compound)
    recovered = build_data_definition_save_plan(partial)

    assert _blockers(blocked, "ml_compatibility_projection_write_required")
    assert not _blockers(recovered, "ml_compatibility_projection_write_required")
    assert not recovered.can_save_schema
    assert any(
        item.code == "restricted_field_edit_not_allowed"
        and item.field_name == "ml_name"
        for item in recovered.blocked_reasons
    )
    assert [change.field_name for change in recovered.changed_fields] == [
        "ml_name",
        "notes",
    ]


def test_data_definition_save_plan_keeps_context_after_unrelated_field_revert():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    changed = replace_draft_row(
        draft,
        row.identity,
        model_input_enabled=True,
        ml_name="IDU",
        notes="description changed",
    )
    reverted = replace_draft_row(changed, row.identity, notes=row.notes)

    changed_plan = build_data_definition_save_plan(changed)
    before = _blockers(changed_plan, "ml_compatibility_projection_write_required")
    after = _blockers(
        build_data_definition_save_plan(reverted),
        "ml_compatibility_projection_write_required",
    )

    assert [(item.row_identity, item.field_name) for item in before] == [
        (row.identity, "model_input_enabled"),
        (row.identity, "ml_name"),
    ]
    assert [(item.row_identity, item.field_name) for item in after] == [
        (row.identity, "model_input_enabled"),
        (row.identity, "ml_name"),
    ]
    assert not changed_plan.can_save_schema


def test_data_definition_save_plan_keeps_independent_singleton_impacts():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    model_only = replace_draft_row(
        draft,
        row.identity,
        model_input_enabled=False,
    )
    active_only = replace_draft_row(draft, row.identity, active=False)
    changed = replace_draft_row(
        draft,
        row.identity,
        model_input_enabled=False,
        active=False,
    )

    assert (
        _fingerprint(model_only)
        == _fingerprint(active_only)
        == _fingerprint(changed)
    )
    blockers = _blockers(
        build_data_definition_save_plan(changed),
        "ml_compatibility_projection_write_required",
    )

    assert [item.field_name for item in blockers] == [
        "model_input_enabled",
        "active",
    ]


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

    assert not plan.can_save_schema
    assert _blocker_codes(plan) >= {
        "data_mapping_dynamic_requirement_deferred",
        "one_hot_runtime_owner_deferred",
        "candidate_feature_projection_mismatch",
        "candidate_one_hot_selector_relation_unsupported",
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


def test_data_definition_save_plan_blocks_direct_stable_identity_replacement():
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    forged = replace(row, stable_identity="forged_identity")
    changed = replace(
        draft,
        rows=tuple(forged if item.identity == row.identity else item for item in draft.rows),
    )

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert any(
        item.code == "restricted_field_edit_not_allowed"
        and item.field_name == "stable_identity"
        for item in plan.blocked_reasons
    )


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


def test_independent_parity_blocker_is_present_before_and_after_ml_revert():
    draft = build_data_definition_draft()
    combined = _controlled_edit(
        draft,
        "cooling_capa",
        (("ml_name", "Cooling Capacity Renamed"),),
    )
    combined = _mapping_relation_edit(combined, "id_volume", "evap_index")

    combined_plan = build_data_definition_save_plan(combined)
    parity_before = _blocker_evidence(
        _blocker(combined_plan, "candidate_feature_projection_mismatch")
    )
    reverted = _controlled_edit(
        combined,
        "cooling_capa",
        (("ml_name", "Cooling Capa"),),
    )
    reverted_plan = build_data_definition_save_plan(reverted)
    parity_after = _blocker_evidence(
        _blocker(reverted_plan, "candidate_feature_projection_mismatch")
    )

    assert _blocker_codes(combined_plan) >= {
        "ml_compatibility_projection_write_required",
        "candidate_feature_projection_mismatch",
    }
    assert parity_before == parity_after
    assert parity_before[1:3] == (("schema_row", "id_volume"), "trigger_column")
    assert "ml_compatibility_projection_write_required" not in _blocker_codes(
        reverted_plan
    )
    assert not reverted_plan.can_save_schema


def test_same_row_field_ml_parity_duplicate_is_suppressed_deterministically():
    draft = build_data_definition_draft()
    changed = _controlled_edit(
        draft,
        "cooling_capa",
        (("ml_name", "Cooling Capacity Renamed"),),
    )

    first = build_data_definition_save_plan(changed)
    second = build_data_definition_save_plan(changed)
    projection_blockers = tuple(
        blocker
        for blocker in first.blocked_reasons
        if blocker.code == "ml_compatibility_projection_write_required"
        or blocker.code.startswith("candidate_feature_projection")
    )

    assert [(item.code, item.row_identity, item.field_name) for item in projection_blockers] == [
        (
            "ml_compatibility_projection_write_required",
            ("schema_row", "cooling_capa"),
            "ml_name",
        ),
    ]
    assert first.blocked_reasons == second.blocked_reasons


def test_ml_blocker_preserves_multiple_independent_parity_issues():
    draft = build_data_definition_draft()
    changed = _controlled_edit(
        draft,
        "cooling_capa",
        (("ml_name", "Cooling Capacity Renamed"),),
    )
    changed = _mapping_relation_edit(changed, "id_volume", "evap_index")
    changed = _mapping_relation_edit(changed, "evap_area", "idu")

    plan = build_data_definition_save_plan(changed)
    parity = _blockers(plan, "candidate_feature_projection_mismatch")

    assert [(item.row_identity, item.field_name) for item in parity] == [
        (("schema_row", "id_volume"), "trigger_column"),
        (("schema_row", "evap_area"), "trigger_column"),
    ]
    assert len(_blockers(plan, "ml_compatibility_projection_write_required")) == 1
    assert not plan.can_save_schema


def test_data_definition_save_plan_allows_schema_backed_label_change():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "idu")
    changed = replace_draft_row(draft, schema_row.identity, label="Indoor Unit")

    plan = build_data_definition_save_plan(changed)

    assert plan.can_save_schema
    assert _target_status(plan, "schema_csv") == "planned"
    assert "restricted_field_edit_not_allowed" not in _blocker_codes(plan)
    assert "raw_row_add_delete_not_allowed" not in _blocker_codes(plan)


def test_full_parity_blocks_projected_label_without_expanding_ml_fingerprint():
    draft = build_data_definition_draft()
    schema_row = next(row for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, schema_row.identity, label="Cooling Capacity")

    plan = build_data_definition_save_plan(changed)

    assert not plan.can_save_schema
    assert "candidate_feature_projection_mismatch" in _blocker_codes(plan)
    assert "ml_compatibility_projection_write_required" not in _blocker_codes(plan)
    blocker = _blocker(plan, "candidate_feature_projection_mismatch")
    assert (blocker.row_identity, blocker.field_name) == (
        schema_row.identity,
        "label",
    )


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


def _blockers(plan, code):
    return tuple(blocker for blocker in plan.blocked_reasons if blocker.code == code)


def _blocker(plan, code):
    return next(blocker for blocker in plan.blocked_reasons if blocker.code == code)


def _fingerprint(draft):
    return projected_feature_catalog_fingerprint(
        project_feature_catalog_from_draft(draft)
    )


def _controlled_edit(draft, column_key, updates):
    ml_name = next((value for field, value in updates if field == "ml_name"), None)
    remaining = tuple(item for item in updates if item[0] != "ml_name")
    if ml_name is not None:
        renamed = apply_rename_definition_command(
            draft,
            RenameDefinitionIntent(("schema_row", column_key), ml_name=str(ml_name)),
        )
        assert renamed.accepted, renamed.issues
        draft = renamed.draft
    if not remaining:
        return draft
    result = apply_edit_definition_command(
        draft,
        EditDefinitionIntent(("schema_row", column_key), remaining),
    )
    assert result.accepted, result.issues
    return result.draft


def _mapping_relation_edit(draft, column_key, mapping_entity):
    row = next(item for item in draft.rows if item.column_key == column_key)
    return _controlled_edit(draft, column_key, (
        ("value_source", "mapping_lookup"),
        ("mapping_entity", mapping_entity),
        ("mapping_attribute", row.mapping_attribute),
        ("trigger_column", mapping_entity),
        ("rule_id", ""),
    ))


def _blocker_evidence(blocker):
    return (
        blocker.code,
        blocker.row_identity,
        blocker.field_name,
        blocker.target,
        blocker.message,
    )
