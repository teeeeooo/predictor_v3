"""Predict Schema Catalog v2 draft projection parity tests."""

from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from core.ml.feature_catalog import load_feature_catalog
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2
from core.predictor_schema.catalog_v2_projection import (
    load_projected_columns_v2,
    one_hot_feature_groups,
    one_hot_selector_groups,
    project_schema_v2_columns,
    status_schema_rows,
)
from core.predictor_schema.columns import (
    AUTO_COLS,
    COLUMNS,
    DROPDOWN_COLS,
    DROPDOWN_TARGET,
    INPUT_COLS,
    RESULT_COLS,
)


def test_predict_schema_catalog_v2_projection_matches_current_core_column_order():
    projected = load_projected_columns_v2()

    assert len(projected) == len(COLUMNS) == 28
    assert [column["key"] for column in projected] == [
        column["key"] for column in COLUMNS
    ]


def test_predict_schema_catalog_v2_projection_is_current_runtime_owner():
    assert COLUMNS == load_projected_columns_v2()


def test_predict_schema_catalog_v2_projection_matches_current_core_metadata():
    projected = load_projected_columns_v2()

    for current, draft in zip(COLUMNS, projected, strict=True):
        assert draft["key"] == current["key"]
        assert draft["header"] == current["header"]
        assert draft["group"] == current["group"]
        assert draft.get("type", "") == current.get("type", "")
        assert draft.get("readonly", False) == current.get("readonly", False)
        assert draft.get("mapping", "") == current.get("mapping", "")
        assert draft.get("source", "") == current.get("source", "")
        assert draft.get("mapping_key", "") == current.get("mapping_key", "")
        assert draft.get("ml_feature", "") == current.get("ml_feature", "")
        assert draft.get("ml_target", "") == current.get("ml_target", "")
        assert draft["width"] == current["width"]
        assert draft["bg_color"] == current["bg_color"]


def test_predict_schema_catalog_v2_projection_matches_dropdown_columns():
    projected = load_projected_columns_v2()
    dropdown_keys = [
        column["key"] for column in projected if column.get("type") == "dropdown"
    ]

    assert dropdown_keys == DROPDOWN_COLS
    assert DROPDOWN_TARGET == {key: key for key in dropdown_keys}


def test_predict_schema_catalog_v2_projection_preserves_current_column_groups():
    assert INPUT_COLS == [
        "cooling_capa",
        "heating_capa",
        "idu",
        "evap_index",
        "odu",
        "fin_type",
        "pi",
        "row",
        "compressor",
        "ref_type",
        "exp_type",
    ]
    assert AUTO_COLS == [
        "id_volume",
        "evap_area",
        "evap_volume",
        "od_volume",
        "cond_area",
        "cond_volume",
        "comp_eer",
        "comp_cc",
    ]
    assert RESULT_COLS == [
        "cooling_power",
        "eer",
        "cspf",
        "heating_power",
        "cop",
        "hspf2",
        "ref_qty",
        "cooling_hz",
        "heating_hz",
    ]


def test_predict_schema_catalog_v2_one_hot_selector_mapping_matches_current_adapter():
    catalog = load_predict_schema_catalog_v2()

    assert one_hot_selector_groups(catalog) == RowToMlInputAdapter._ONE_HOT_INPUT_GROUPS


def test_predict_schema_catalog_v2_one_hot_feature_rows_match_feature_catalog():
    catalog = load_predict_schema_catalog_v2()

    assert one_hot_feature_groups(catalog) == load_feature_catalog().one_hot_groups()


def test_predict_schema_catalog_v2_status_rows_are_not_core_projected():
    catalog = load_predict_schema_catalog_v2()
    projected = project_schema_v2_columns(catalog)

    assert [row.column_key for row in status_schema_rows(catalog)] == [
        "status",
        "message",
    ]
    assert "status" not in {column["key"] for column in projected}
    assert "message" not in {column["key"] for column in projected}


def test_predict_schema_catalog_v2_preserves_cond_current_compatibility_metadata():
    projected = {column["key"]: column for column in load_projected_columns_v2()}

    assert projected["cond_area"]["source"] == "odu"
    assert projected["cond_area"]["mapping_key"] == "Cond Area"
    assert projected["cond_volume"]["source"] == "odu"
    assert projected["cond_volume"]["mapping_key"] == "Cond Volume"


def test_predict_schema_catalog_v2_separates_semantic_and_legacy_mapping_fields():
    catalog = load_predict_schema_catalog_v2()
    rows = {row.column_key: row for row in catalog.active_rows}
    projected = {column["key"]: column for column in load_projected_columns_v2()}

    assert rows["fin_type"].mapping_entity == "odu_cascade"
    assert projected["fin_type"]["mapping"] == "fin_type"
    assert rows["cond_area"].mapping_entity == "cond_specs"
    assert projected["cond_area"]["source"] == "odu"
