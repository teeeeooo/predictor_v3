"""Arc 15C-2 guarded schema writer tests."""

from __future__ import annotations

import hashlib

import pytest

import core.data_definition.schema_writer as schema_writer
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
    assert "schema_writer_target_not_allowed" in _issue_codes(result)
    assert not destination.exists()


def test_invalid_editable_field_value_is_blocked_before_replace(tmp_path):
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, data_type="invalid_type")
    destination = tmp_path / "schema.csv"

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "candidate_schema_validation_failed" in _issue_codes(result)
    assert not destination.exists()


def test_candidate_validation_failure_does_not_overwrite_existing_destination(tmp_path):
    destination = tmp_path / "schema.csv"
    destination.write_text("original-content\n", encoding="utf-8")
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, editor="invalid_editor")

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert "candidate_schema_validation_failed" in _issue_codes(result)
    assert destination.read_text(encoding="utf-8") == "original-content\n"
    assert not (tmp_path / "backups").exists()


def test_ml_projection_guard_does_not_overwrite_existing_schema(tmp_path):
    destination = tmp_path / "schema.csv"
    destination.write_bytes(DEFAULT_SCHEMA_PATH.read_bytes())
    original = destination.read_bytes()
    draft = build_data_definition_draft(schema_path=destination)
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")

    for field_name, value in (
        ("ml_name", "Cooling Capacity Renamed"),
        ("model_input_enabled", False),
        ("active", False),
    ):
        changed = replace_draft_row(draft, row.identity, **{field_name: value})
        result = save_data_definition_schema_draft(changed, destination)

        assert not result.success
        assert result.status == "blocked"
        assert "ml_compatibility_projection_write_required" in _issue_codes(result)
        assert destination.read_bytes() == original

    assert not (tmp_path / "backups").exists()


def test_existing_destination_is_backed_up_and_replaced(tmp_path):
    initial = tmp_path / "initial_schema.csv"
    first_draft = build_data_definition_draft()
    first_row = next(item for item in first_draft.rows if item.column_key == "cooling_capa")
    first_changed = replace_draft_row(first_draft, first_row.identity, label="First Label")
    first_result = save_data_definition_schema_draft(first_changed, initial)

    second_draft = build_data_definition_draft(schema_path=initial)
    second_row = next(item for item in second_draft.rows if item.column_key == "cooling_capa")
    second_changed = replace_draft_row(second_draft, second_row.identity, label="Second Label")
    second_result = save_data_definition_schema_draft(second_changed, initial)

    assert first_result.success
    assert second_result.success
    assert second_result.backup_path is not None
    assert second_result.backup_path.exists()
    assert load_predict_schema_catalog_v2(second_result.backup_path).rows
    loaded = load_predict_schema_catalog_v2(initial)
    assert next(item for item in loaded.rows if item.column_key == "cooling_capa").label == (
        "Second Label"
    )


def test_write_failure_cleans_tmp_without_replacing_destination(tmp_path, monkeypatch):
    destination = tmp_path / "schema.csv"
    destination.write_text("original-content\n", encoding="utf-8")
    draft = build_data_definition_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    changed = replace_draft_row(draft, row.identity, label="Cooling Capacity")

    def fail_replace(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(schema_writer.os, "replace", fail_replace)

    result = save_data_definition_schema_draft(changed, destination)

    assert not result.success
    assert result.status == "error"
    assert destination.read_text(encoding="utf-8") == "original-content\n"
    assert not list(tmp_path.glob(".schema.csv.*.tmp"))


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
