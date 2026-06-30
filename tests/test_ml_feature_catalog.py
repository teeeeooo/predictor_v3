"""ML feature catalog loader and parity tests."""

from __future__ import annotations

import ast
import csv
from pathlib import Path

from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
import core.ml.feature_catalog as feature_catalog_module
import core.ml.features as features_module
from core.ml.feature_catalog import (
    DEFAULT_CATALOG_PATH,
    REQUIRED_HEADERS,
    FeatureCatalog,
    FeatureCatalogRow,
    load_feature_catalog,
    validate_training_headers,
    validate_feature_catalog,
    validate_registry_references,
)
from core.ml.feature_catalog_projection import BASE_FEATURE_RESULT_EXPORT_ORDER
from core.ml.feature_catalog_projection import predictor_columns_projection
from core.ml.features import BASE_FEATURES, DERIVED_FEATURES, TARGETS
from core.ml.registry import MODEL_REGISTRY
from core.predictor_schema.columns import AUTO_COLS, COLUMNS, INPUT_COLS, RESULT_COLS
from core.predictor_schema.columns import ROLE_PRESENTATION_DEFAULTS, WIDTH_OVERRIDES


CANONICAL_TARGETS = ["Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz"]
EXPECTED_INPUT_COLS = [
    "cooling_capa", "heating_capa", "idu", "evap_index", "odu",
    "fin_type", "pi", "row", "compressor", "ref_type", "exp_type",
]
EXPECTED_AUTO_COLS = [
    "id_volume", "evap_area", "evap_volume", "od_volume", "cond_area",
    "cond_volume", "comp_eer", "comp_cc",
]
EXPECTED_RESULT_COLS = [
    "cooling_power", "eer", "cspf", "heating_power", "cop", "hspf2",
    "ref_qty", "cooling_hz", "heating_hz",
]


def test_feature_catalog_loads_default_draft_without_validation_errors():
    catalog = load_feature_catalog()

    assert catalog.headers == REQUIRED_HEADERS
    assert validate_feature_catalog(catalog) == []


def test_feature_catalog_feature_projection_matches_current_constants():
    catalog = load_feature_catalog()

    assert set(catalog.base_features()) == set(BASE_FEATURES)
    assert set(catalog.derived_features()) == set(DERIVED_FEATURES)
    assert set(catalog.targets()) == set(TARGETS)


def test_feature_catalog_exports_keep_deterministic_legacy_order():
    catalog = load_feature_catalog()

    assert catalog.base_features() == BASE_FEATURES
    assert catalog.derived_features() == DERIVED_FEATURES
    assert catalog.targets() == TARGETS


def test_feature_catalog_targets_use_stable_result_row_order():
    catalog = load_feature_catalog()
    result_row_order = [
        row.ml_name
        for row in catalog.active_rows
        if row.role == "result"
    ]

    assert result_row_order == CANONICAL_TARGETS
    assert catalog.targets() == CANONICAL_TARGETS
    assert TARGETS == CANONICAL_TARGETS


def test_target_compat_order_has_been_removed():
    assert not hasattr(feature_catalog_module, "TARGET_COMPAT_ORDER")


def test_base_feature_result_order_is_legacy_export_policy_only():
    assert BASE_FEATURE_RESULT_EXPORT_ORDER == (
        "Ref Qty",
        "Cooling Power",
        "Heating Power",
        "Cooling Hz",
        "Heating Hz",
    )
    assert list(BASE_FEATURE_RESULT_EXPORT_ORDER) != CANONICAL_TARGETS


def test_feature_catalog_predictor_input_auto_projection_matches_schema():
    catalog = load_feature_catalog()
    expected = {
        column["key"]: column["ml_feature"]
        for column in COLUMNS
        if column["key"] in INPUT_COLS + AUTO_COLS and column.get("ml_feature")
    }
    actual = {
        row.ui_key: row.ml_name
        for row in catalog.predictor_rows()
        if row.role in {"input", "auto"}
    }

    assert actual == expected


def test_feature_catalog_result_projection_matches_predictor_schema():
    catalog = load_feature_catalog()
    expected = {
        column["key"]: column["ml_target"]
        for column in COLUMNS
        if column["key"] in RESULT_COLS and column.get("ml_target")
    }
    actual = {
        row.ui_key: row.ml_name
        for row in catalog.predictor_rows()
        if row.role == "result"
    }

    assert actual == expected


def test_predictor_schema_exports_preserve_current_key_groups():
    assert INPUT_COLS == EXPECTED_INPUT_COLS
    assert AUTO_COLS == EXPECTED_AUTO_COLS
    assert RESULT_COLS == EXPECTED_RESULT_COLS
    assert [column["key"] for column in COLUMNS] == (
        EXPECTED_INPUT_COLS + EXPECTED_AUTO_COLS + EXPECTED_RESULT_COLS
    )


def test_predictor_schema_metadata_preserves_current_contract():
    by_key = {column["key"]: column for column in COLUMNS}

    assert by_key["cooling_capa"]["header"] == "냉방능력"
    assert by_key["cooling_capa"]["ml_feature"] == "Cooling Capa"
    assert by_key["id_volume"]["source"] == "idu"
    assert by_key["id_volume"]["mapping_key"] == "ID Volume"
    assert by_key["cooling_power"]["ml_target"] == "Cooling Power"
    assert by_key["ref_qty"]["ml_target"] == "Ref Qty"


def test_predictor_schema_role_presentation_defaults_preserve_width_and_color():
    by_key = {column["key"]: column for column in COLUMNS}

    assert by_key["cooling_capa"]["width"] == 90
    assert by_key["cooling_capa"]["bg_color"] == "#FFFFFF"
    assert by_key["id_volume"]["width"] == 90
    assert by_key["id_volume"]["bg_color"] == "#F2F2F2"
    assert by_key["comp_eer"]["width"] == 80
    assert by_key["cooling_power"]["width"] == 100
    assert by_key["cooling_power"]["bg_color"] == "#E6F3E6"
    assert by_key["ref_qty"]["width"] == 80


def test_predictor_columns_projection_uses_catalog_role_and_order():
    catalog = load_feature_catalog()
    projected = predictor_columns_projection(
        catalog.rows,
        ROLE_PRESENTATION_DEFAULTS,
        WIDTH_OVERRIDES,
    )

    assert [column["key"] for column in projected] == [
        "cooling_capa", "heating_capa",
        "id_volume", "evap_area", "evap_volume", "od_volume",
        "cond_area", "cond_volume", "comp_eer", "comp_cc",
        "cooling_power", "heating_power", "ref_qty", "cooling_hz", "heating_hz",
    ]
    assert all(column["group"] != "one_hot" for column in projected)
    assert "r32" not in {column["key"] for column in projected}
    assert "cool_capa_per_eer" not in {column["key"] for column in projected}


def test_feature_catalog_one_hot_groups_match_current_adapter_tuples():
    catalog = load_feature_catalog()

    assert catalog.one_hot_groups() == {
        "refrigerant": RowToMlInputAdapter._REFRIGERANT_FEATURES,
        "expansion_device": RowToMlInputAdapter._EXPANSION_FEATURES,
    }


def test_feature_catalog_zero_fill_policy_is_limited_to_mode_features():
    catalog = load_feature_catalog()
    policies = catalog.zero_fill_policies()
    allowed = {
        name
        for name, policy in policies.items()
        if policy == "mode_missing_allowed"
    }

    assert allowed == {"Cooling Capa", "Cooling Power", "Heating Capa", "Heating Power"}
    assert all(
        policy in {"disallow", "mode_missing_allowed"}
        for policy in policies.values()
    )


def test_feature_catalog_registry_references_exist_in_catalog():
    catalog = load_feature_catalog()

    assert validate_registry_references(catalog, MODEL_REGISTRY) == []


def test_feature_catalog_inactive_rows_are_excluded_from_projections():
    inactive = FeatureCatalogRow(
        order=1,
        feature_id="inactive_feature",
        ml_name="Inactive Feature",
        role="input",
        ui_key="inactive_feature",
        label="Inactive",
        source="",
        mapping_key="",
        one_hot_group="",
        zero_fill_policy="disallow",
        active=False,
    )
    catalog = FeatureCatalog(rows=(inactive,))

    assert catalog.base_features() == []
    assert catalog.predictor_rows() == ()
    assert catalog.zero_fill_policies() == {}
    assert catalog.training_headers() == []


def test_feature_catalog_invalid_examples_fail_validation(tmp_path):
    catalog_path = tmp_path / "invalid_features.csv"
    _write_catalog(
        catalog_path,
        [
            {
                "order": "10",
                "feature_id": "bad_zero",
                "ml_name": "ID Volume",
                "role": "auto",
                "ui_key": "id_volume",
                "label": "ID Volume",
                "source": "",
                "mapping_key": "",
                "one_hot_group": "",
                "zero_fill_policy": "mode_missing_allowed",
                "active": "true",
                "notes": "",
            },
            {
                "order": "20",
                "feature_id": "bad_one_hot",
                "ml_name": "R32",
                "role": "one_hot",
                "ui_key": "",
                "label": "R32",
                "source": "",
                "mapping_key": "",
                "one_hot_group": "",
                "zero_fill_policy": "disallow",
                "active": "true",
                "notes": "",
            },
            {
                "order": "30",
                "feature_id": "bad_one_hot",
                "ml_name": "R290",
                "role": "unknown",
                "ui_key": "",
                "label": "R290",
                "source": "",
                "mapping_key": "",
                "one_hot_group": "refrigerant",
                "zero_fill_policy": "bad_policy",
                "active": "true",
                "notes": "",
            },
        ],
    )

    errors = validate_feature_catalog(load_feature_catalog(catalog_path))

    assert "duplicate feature_id: bad_one_hot" in errors
    assert "feature_id=bad_zero: mode_missing_allowed is not allowed for 'ID Volume'" in errors
    assert "feature_id=bad_zero: role=auto requires source" in errors
    assert "feature_id=bad_zero: role=auto requires mapping_key" in errors
    assert "feature_id=bad_one_hot: role=one_hot requires one_hot_group" in errors
    assert "feature_id=bad_one_hot: invalid role 'unknown'" in errors
    assert "feature_id=bad_one_hot: invalid zero_fill_policy 'bad_policy'" in errors


def test_feature_catalog_header_policy_rejects_unknown_header(tmp_path):
    catalog_path = tmp_path / "unknown_header_features.csv"
    headers = list(REQUIRED_HEADERS) + ["width"]
    with catalog_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

    errors = validate_feature_catalog(load_feature_catalog(catalog_path))

    assert "unknown header(s): width" in errors


def test_feature_catalog_training_headers_match_raw_ml_name_contract():
    catalog = load_feature_catalog()
    expected = [
        row.ml_name
        for row in catalog.active_rows
        if row.role in {"input", "auto", "one_hot", "result"}
    ]

    assert catalog.training_headers() == expected
    assert "Cool_Capa_per_EER" not in catalog.training_headers()
    assert set(catalog.training_headers()) == set(BASE_FEATURES)


def test_validate_training_headers_accepts_catalog_headers_without_aliases():
    catalog = load_feature_catalog()

    assert validate_training_headers(catalog.training_headers(), catalog) == []
    assert catalog.validate_training_headers(catalog.training_headers()) == []


def test_validate_training_headers_reports_unknown_and_missing_names():
    catalog = load_feature_catalog()
    headers = [
        header
        for header in catalog.training_headers()
        if header != "Cooling Capa"
    ]
    headers.append("Cooling Capacity Alias")

    errors = validate_training_headers(headers, catalog)

    assert "unknown training header(s): Cooling Capacity Alias" in errors
    assert "missing required training header(s): Cooling Capa" in errors


def test_default_catalog_path_exists_for_runtime_import():
    assert DEFAULT_CATALOG_PATH.exists()


def test_features_import_error_for_missing_catalog_includes_path(tmp_path):
    missing = tmp_path / "missing_features.csv"

    try:
        features_module._load_validated_catalog(missing)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing catalog RuntimeError")

    assert str(missing) in message
    assert "ML feature catalog not found" in message


def test_features_import_error_for_invalid_catalog_includes_validation_message(tmp_path):
    catalog_path = tmp_path / "invalid_features.csv"
    _write_catalog(
        catalog_path,
        [
            {
                "order": "10",
                "feature_id": "bad_zero",
                "ml_name": "ID Volume",
                "role": "auto",
                "ui_key": "id_volume",
                "label": "ID Volume",
                "source": "",
                "mapping_key": "",
                "one_hot_group": "",
                "zero_fill_policy": "mode_missing_allowed",
                "active": "true",
                "notes": "",
            }
        ],
    )

    try:
        features_module._load_validated_catalog(catalog_path)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected invalid catalog RuntimeError")

    assert "invalid ML feature catalog" in message
    assert "mode_missing_allowed is not allowed for 'ID Volume'" in message


def test_train_panel_target_tuple_matches_catalog_targets_without_importing_ui():
    source = Path("apps/train/ui/train_model_panel.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    target_tuple = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "TARGETS" for target in node.targets):
                target_tuple = ast.literal_eval(node.value)
                break

    assert tuple(load_feature_catalog().targets()) == target_tuple


def _write_catalog(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REQUIRED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
