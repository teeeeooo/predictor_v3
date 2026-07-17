"""Predict Schema Catalog v2 draft loader and validation tests."""

import csv

from core.ml.feature_catalog import load_feature_catalog
from core.predictor_schema.catalog_v2 import (
    MAX_DISPLAY_ORDER,
    REQUIRED_HEADERS,
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)
from core.predictor_schema.catalog_v2_projection import (
    one_hot_feature_groups,
    one_hot_selector_groups,
    status_schema_rows,
)


def test_predict_schema_catalog_v2_loads_default_draft_without_validation_errors():
    catalog = load_predict_schema_catalog_v2()

    assert catalog.headers == REQUIRED_HEADERS
    assert validate_predict_schema_catalog_v2(catalog) == []
    assert len(catalog.rows) == 35


def test_predict_schema_catalog_v2_represents_one_hot_selectors_and_features():
    catalog = load_predict_schema_catalog_v2()

    assert one_hot_selector_groups(catalog) == {
        "ref_type": "refrigerant",
        "exp_type": "expansion_device",
    }
    assert one_hot_feature_groups(catalog) == load_feature_catalog().one_hot_groups()


def test_predict_schema_catalog_v2_represents_status_rows_as_projection_excluded():
    catalog = load_predict_schema_catalog_v2()
    status_rows = status_schema_rows(catalog)

    assert [row.column_key for row in status_rows] == ["status", "message"]
    assert all(row.visible for row in status_rows)
    assert all(row.readonly for row in status_rows)
    assert all(not row.model_input_enabled for row in status_rows)


def test_predict_schema_catalog_v2_validation_rejects_duplicate_active_keys(tmp_path):
    source = load_predict_schema_catalog_v2()
    path = tmp_path / "schema.csv"
    rows = [row_to_csv_dict(row) for row in source.rows[:2]]
    rows[1]["column_key"] = rows[0]["column_key"]
    write_schema(path, rows)

    errors = validate_predict_schema_catalog_v2(load_predict_schema_catalog_v2(path))

    assert any("duplicate active column_key 'cooling_capa'" in error for error in errors)


def test_predict_schema_validation_rejects_duplicate_order_including_inactive_rows(
    tmp_path,
):
    source = load_predict_schema_catalog_v2()
    path = tmp_path / "schema.csv"
    rows = [row_to_csv_dict(row) for row in source.rows[:2]]
    rows[1]["display_order"] = rows[0]["display_order"]
    rows[1]["active"] = "false"
    write_schema(path, rows)

    errors = validate_predict_schema_catalog_v2(load_predict_schema_catalog_v2(path))

    assert any("duplicate display_order '10'" in error for error in errors)


def test_predict_schema_validation_rejects_display_order_outside_supported_range(
    tmp_path,
):
    source = load_predict_schema_catalog_v2()
    for value in ("0", str(MAX_DISPLAY_ORDER + 1)):
        path = tmp_path / f"schema-{value}.csv"
        rows = [row_to_csv_dict(source.rows[0])]
        rows[0]["display_order"] = value
        write_schema(path, rows)

        errors = validate_predict_schema_catalog_v2(
            load_predict_schema_catalog_v2(path)
        )

        assert any("display_order must be between" in error for error in errors)


def test_predict_schema_catalog_v2_validation_rejects_invalid_enums_and_booleans(tmp_path):
    source = load_predict_schema_catalog_v2()
    path = tmp_path / "schema.csv"
    rows = [row_to_csv_dict(source.rows[0])]
    rows[0]["role"] = "bad_role"
    rows[0]["visible"] = "maybe"
    write_schema(path, rows)

    errors = validate_predict_schema_catalog_v2(load_predict_schema_catalog_v2(path))

    assert "line 2: visible must be a boolean" in errors
    assert any("invalid role 'bad_role'" in error for error in errors)


def test_predict_schema_catalog_v2_validation_requires_mapping_lookup_contract(tmp_path):
    source = load_predict_schema_catalog_v2()
    path = tmp_path / "schema.csv"
    rows = [row_to_csv_dict(source.rows[12])]
    rows[0]["mapping_entity"] = ""
    rows[0]["mapping_attribute"] = ""
    rows[0]["trigger_column"] = ""
    rows[0]["rule_id"] = ""
    write_schema(path, rows)

    errors = validate_predict_schema_catalog_v2(load_predict_schema_catalog_v2(path))

    assert any("mapping_lookup requires mapping_entity" in error for error in errors)
    assert any("mapping_lookup requires mapping_attribute" in error for error in errors)
    assert any("mapping_lookup requires trigger_column" in error for error in errors)


def row_to_csv_dict(row):
    return {
        "display_order": str(row.display_order),
        "column_key": row.column_key,
        "label": row.label,
        "role": row.role,
        "editor": row.editor,
        "data_type": row.data_type,
        "visible": str(row.visible).lower(),
        "required": str(row.required).lower(),
        "readonly": str(row.readonly).lower(),
        "value_source": row.value_source,
        "mapping_entity": row.mapping_entity,
        "mapping_attribute": row.mapping_attribute,
        "trigger_column": row.trigger_column,
        "rule_id": row.rule_id,
        "model_input_enabled": str(row.model_input_enabled).lower(),
        "ml_name": row.ml_name,
        "one_hot_group": row.one_hot_group,
        "active": str(row.active).lower(),
        "notes": row.notes,
    }


def write_schema(path, rows):
    with path.open("w", encoding="utf-8", newline="") as schema_file:
        writer = csv.DictWriter(schema_file, fieldnames=REQUIRED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
