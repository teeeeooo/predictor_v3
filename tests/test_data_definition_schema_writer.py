"""Arc 15C-2 guarded schema writer tests."""

from __future__ import annotations

import hashlib

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    build_data_definition_draft,
    build_data_definition_report,
    save_data_definition_schema_draft,
    schema_csv_rows_from_draft,
)
from core.data_definition.draft import replace_draft_row
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def test_guarded_writer_writes_allowed_label_change_to_tmp_schema(tmp_path):
    before_hash = _file_hash(DEFAULT_SCHEMA_PATH)
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, label="Cooling Capacity")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert result.success
    assert result.status == "written"
    assert result.rows_written > 0
    loaded = load_predict_schema_catalog_v2(destination)
    assert next(item for item in loaded.rows if item.column_key == "cooling_capa").label == (
        "Cooling Capacity"
    )
    assert _file_hash(DEFAULT_SCHEMA_PATH) == before_hash


def test_unchanged_draft_is_noop(tmp_path):
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(build_data_definition_draft(), destination)

    assert not result.success
    assert result.status == "noop"
    assert result.rows_written == 0
    assert not destination.exists()


def test_restricted_field_change_is_blocked(tmp_path):
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, column_key="cooling_capacity")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "restricted_field_edit_not_allowed" in _issue_codes(result)
    assert not destination.exists()


def test_raw_row_add_is_blocked(tmp_path):
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
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "raw_row_add_delete_not_allowed" in _issue_codes(result)
    assert not destination.exists()


def test_raw_row_delete_is_blocked(tmp_path):
    draft = build_data_definition_draft()
    changed = DataDefinitionDraft(rows=draft.rows[1:], baseline_rows=draft.baseline_rows)
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "raw_row_add_delete_not_allowed" in _issue_codes(result)
    assert not destination.exists()


def test_derived_policy_change_is_blocked(tmp_path):
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.source_kind == "derived_policy")
    changed = replace_draft_row(draft, row.identity, ml_name=f"{row.ml_name}_edited")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "derived_policy_persistence_required" in _issue_codes(result)
    assert not destination.exists()


def test_writer_rejects_non_schema_target(tmp_path):
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, label="Cooling Capacity")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(
        changed,
        destination,
        target="mapping_json",
    )

    assert not result.success
    assert result.rows_written == 0
    assert not destination.exists()


def test_schema_rows_exclude_derived_policy_rows():
    draft = build_data_definition_draft()
    rows = schema_csv_rows_from_draft(draft)

    assert rows
    assert len(rows) == len(load_predict_schema_catalog_v2().rows)
    assert "Cool_Capa_per_EER" not in {row["ml_name"] for row in rows}


def test_round_trip_report_runs_for_allowed_schema_edit(tmp_path):
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, label="Cooling Capacity")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)
    report = build_data_definition_report(schema_path=destination)

    assert result.success
    assert report.projected_features
    assert "feature_projection_mismatch" in {issue.code for issue in report.parity_issues}


def _issue_codes(result):
    return {issue.code for issue in result.issues}


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
