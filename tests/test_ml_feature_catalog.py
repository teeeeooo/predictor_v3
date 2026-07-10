"""ML feature catalog loader and parity tests."""

from __future__ import annotations

import ast
import csv
from dataclasses import replace
from pathlib import Path

import joblib
import pandas as pd

from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
import core.ml.feature_catalog as feature_catalog_module
import core.ml.features as features_module
import core.predictor_schema.columns as predictor_columns_module
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
from core.ml.catalog_fingerprint import (
    CATALOG_FINGERPRINT_KEY,
    CATALOG_FINGERPRINT_VERSION,
    CATALOG_FINGERPRINT_VERSION_KEY,
    ML_CONTRACT_FINGERPRINT_FIELDS,
    attach_catalog_fingerprint,
    current_catalog_fingerprint,
    validate_model_catalog_fingerprint,
)
from core.ml.feature_catalog_projection import BASE_FEATURE_RESULT_EXPORT_ORDER
from core.ml.feature_catalog_projection import one_hot_group, predictor_columns_projection
from core.ml.features import BASE_FEATURES, DERIVED_FEATURES, TARGETS
from core.ml.inference import build_input_df
from core.ml.preprocessing import prepare_pipeline
from core.ml.registry import MODEL_REGISTRY, get_model_config
from core.ml.training import validate_training_input_headers
from core.predictor_schema.columns import AUTO_COLS, COLUMNS, INPUT_COLS, RESULT_COLS
from core.predictor_schema.presentation import ROLE_PRESENTATION_DEFAULTS, WIDTH_OVERRIDES
from core.predictor_schema.ui_columns import (
    DROPDOWN_INPUT_COLUMNS,
    INPUT_INSERT_AFTER,
    RESULT_INSERT_AFTER,
    RULE_RESULT_COLUMNS,
    insert_columns_after,
)


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
EXPECTED_DROPDOWN_INPUT_COLS = [
    "idu", "evap_index", "odu", "fin_type", "pi", "row",
    "compressor", "ref_type", "exp_type",
]
EXPECTED_RULE_RESULT_COLS = ["eer", "cspf", "cop", "hspf2"]


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


def test_predictor_ui_only_columns_are_owned_by_ui_columns_module():
    assert [column["key"] for column in DROPDOWN_INPUT_COLUMNS] == EXPECTED_DROPDOWN_INPUT_COLS
    assert [column["key"] for column in RULE_RESULT_COLUMNS] == EXPECTED_RULE_RESULT_COLS
    assert INPUT_INSERT_AFTER == {"heating_capa": DROPDOWN_INPUT_COLUMNS}
    assert RESULT_INSERT_AFTER == {
        "cooling_power": RULE_RESULT_COLUMNS[:2],
        "heating_power": RULE_RESULT_COLUMNS[2:],
    }

    assert not hasattr(predictor_columns_module, "LEGACY_INPUT_COLUMNS")
    assert not hasattr(predictor_columns_module, "LEGACY_RULE_RESULT_COLUMNS")
    assert not hasattr(predictor_columns_module, "LEGACY_INPUT_INSERT_AFTER")
    assert not hasattr(predictor_columns_module, "LEGACY_RESULT_INSERT_AFTER")


def test_ui_columns_insert_helper_preserves_projected_order():
    projected = [{"key": "first"}, {"key": "second"}]
    inserted = [{"key": "inserted"}]

    assert insert_columns_after(projected, {"first": inserted}) == [
        {"key": "first"},
        {"key": "inserted"},
        {"key": "second"},
    ]


def test_predictor_schema_combines_catalog_projection_with_ui_only_columns():
    catalog = load_feature_catalog()
    catalog_columns = predictor_columns_projection(
        catalog.rows,
        ROLE_PRESENTATION_DEFAULTS,
        WIDTH_OVERRIDES,
    )
    catalog_keys = {column["key"] for column in catalog_columns}
    ui_only_keys = set(EXPECTED_DROPDOWN_INPUT_COLS + EXPECTED_RULE_RESULT_COLS)

    assert catalog_keys.isdisjoint(ui_only_keys)
    assert ui_only_keys.issubset({column["key"] for column in COLUMNS})
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


def test_feature_catalog_one_hot_groups_are_adapter_projection_source():
    catalog = load_feature_catalog()

    assert catalog.one_hot_groups() == {
        "refrigerant": ("R410A", "R32", "R290"),
        "expansion_device": ("EEV", "Capi"),
    }
    assert one_hot_group(catalog.rows, "refrigerant") == ("R410A", "R32", "R290")
    assert one_hot_group(catalog.rows, "expansion_device") == ("EEV", "Capi")
    assert not hasattr(RowToMlInputAdapter, "_REFRIGERANT_FEATURES")
    assert not hasattr(RowToMlInputAdapter, "_EXPANSION_FEATURES")


def test_feature_catalog_one_hot_group_missing_error_is_clear():
    catalog = FeatureCatalog(rows=())

    try:
        one_hot_group(catalog.rows, "refrigerant")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing one-hot group ValueError")

    assert "missing one-hot group 'refrigerant' in feature catalog" in message


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


def test_feature_catalog_registry_targets_are_active_result_rows():
    catalog = load_feature_catalog()
    result_names = {
        row.ml_name
        for row in catalog.active_rows
        if row.role == "result"
    }

    for config in MODEL_REGISTRY.values():
        assert set(config["targets"]).issubset(result_names)
        assert set(config.get("target_rules", {})).issubset(result_names)


def test_model_registry_rules_still_apply_after_catalog_projection():
    df = pd.DataFrame([_complete_base_row() for _index in range(5)])

    for model_key in MODEL_REGISTRY:
        config = get_model_config(model_key)
        x_full, y_full = prepare_pipeline(df, config)
        assert y_full is not None
        assert set(config["targets"]).issubset(y_full.columns)
        assert set(TARGETS).isdisjoint(x_full.columns)

        for rules in config.get("target_rules", {}).values():
            x_target = x_full.copy()
            if "exclude" in rules:
                x_target = x_target.drop(
                    columns=[
                        column for column in rules["exclude"]
                        if column in x_target.columns
                    ]
                )
                assert set(rules["exclude"]).isdisjoint(x_target.columns)
            if "allowed" in rules:
                x_target = x_target[
                    [column for column in x_target.columns if column in rules["allowed"]]
                ]
                assert set(x_target.columns).issubset(set(rules["allowed"]))


def test_feature_catalog_registry_validator_rejects_non_result_target():
    non_result_target = FeatureCatalogRow(
        order=1,
        ml_name="Cooling Capa",
        role="input",
        ui_key="cooling_capa",
        label="Cooling Capa",
        source="",
        mapping_key="",
        one_hot_group="",
        zero_fill_policy="mode_missing_allowed",
        active=True,
    )
    catalog = FeatureCatalog(rows=(non_result_target,))

    errors = validate_registry_references(
        catalog,
        {"bad_model": {"targets": ["Cooling Capa"], "target_rules": {}}},
    )

    assert "bad_model: target 'Cooling Capa' is not an active result catalog row" in errors


def test_default_catalog_path_is_packaging_required_resource():
    assert DEFAULT_CATALOG_PATH == Path.cwd() / "config" / "ml" / "features.csv"
    assert DEFAULT_CATALOG_PATH.is_file()
    assert load_feature_catalog(DEFAULT_CATALOG_PATH).path == DEFAULT_CATALOG_PATH


def test_feature_catalog_inactive_rows_are_excluded_from_projections():
    inactive = FeatureCatalogRow(
        order=1,
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
            {
                "order": "40",
                "ml_name": "",
                "role": "hidden",
                "ui_key": "",
                "label": "",
                "source": "",
                "mapping_key": "",
                "one_hot_group": "",
                "zero_fill_policy": "disallow",
                "active": "false",
                "notes": "",
            },
        ],
    )

    errors = validate_feature_catalog(load_feature_catalog(catalog_path))

    assert "order=40: ml_name is required" in errors
    assert "ml_name=ID Volume (order=10): mode_missing_allowed is not allowed for 'ID Volume'" in errors
    assert "ml_name=ID Volume (order=10): role=auto requires source" in errors
    assert "ml_name=ID Volume (order=10): role=auto requires mapping_key" in errors
    assert "ml_name=R32 (order=20): role=one_hot requires one_hot_group" in errors
    assert "ml_name=R290 (order=30): invalid role 'unknown'" in errors
    assert "ml_name=R290 (order=30): invalid zero_fill_policy 'bad_policy'" in errors


def test_feature_catalog_header_policy_rejects_unknown_header(tmp_path):
    catalog_path = tmp_path / "unknown_header_features.csv"
    headers = list(REQUIRED_HEADERS) + ["width"]
    with catalog_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

    errors = validate_feature_catalog(load_feature_catalog(catalog_path))

    assert "unknown header(s): width" in errors


def test_feature_catalog_fingerprint_scope_fields_are_explicit():
    assert ML_CONTRACT_FINGERPRINT_FIELDS == (
        "ml_name",
        "role",
        "one_hot_group",
        "zero_fill_policy",
    )
    assert CATALOG_FINGERPRINT_VERSION == "feature_catalog.ml_contract.v2"


def test_feature_catalog_fingerprint_ignores_non_model_contract_fields():
    catalog = load_feature_catalog()
    base = current_catalog_fingerprint(catalog)

    for field, value in (
        ("label", "Display Label Only"),
        ("notes", "Operator note only"),
        ("order", catalog.rows[0].order + 999),
        ("ui_key", "ui_key_only"),
        ("source", "mapping-source-only"),
        ("mapping_key", "Mapping Key Only"),
    ):
        changed = _catalog_with_changed_active_row(catalog, **{field: value})
        assert current_catalog_fingerprint(changed) == base, field


def test_feature_catalog_fingerprint_changes_with_model_contract_fields():
    catalog = load_feature_catalog()
    base = current_catalog_fingerprint(catalog)

    for field, value in (
        ("ml_name", "Changed ML Name"),
        ("role", "hidden"),
        ("active", False),
        ("one_hot_group", "changed_group"),
        ("zero_fill_policy", "changed_policy"),
    ):
        changed = _catalog_with_changed_active_row(catalog, **{field: value})
        assert current_catalog_fingerprint(changed) != base, field


def test_feature_catalog_fingerprint_excludes_inactive_rows():
    catalog = load_feature_catalog()
    inactive_row = replace(
        catalog.rows[0],
        order=9999,
        ml_name="Inactive Feature",
        active=False,
    )
    with_inactive = FeatureCatalog(
        rows=tuple(catalog.rows) + (inactive_row,),
        headers=catalog.headers,
    )
    with_changed_inactive = FeatureCatalog(
        rows=tuple(catalog.rows) + (
            replace(
                inactive_row,
                ml_name="Inactive Changed ML Name",
                role="result",
                one_hot_group="inactive_group",
                zero_fill_policy="mode_missing_allowed",
            ),
        ),
        headers=catalog.headers,
    )

    assert current_catalog_fingerprint(with_inactive) == current_catalog_fingerprint(catalog)
    assert current_catalog_fingerprint(with_changed_inactive) == current_catalog_fingerprint(catalog)


def test_model_catalog_fingerprint_metadata_validates_current_catalog():
    model_data = attach_catalog_fingerprint({"models": {}, "features": {}})

    validate_model_catalog_fingerprint(model_data)

    assert model_data[CATALOG_FINGERPRINT_VERSION_KEY] == CATALOG_FINGERPRINT_VERSION
    assert len(model_data[CATALOG_FINGERPRINT_KEY]) == 64


def test_model_catalog_fingerprint_validation_rejects_missing_or_mismatch():
    try:
        validate_model_catalog_fingerprint({"models": {}, "features": {}})
    except ValueError as exc:
        missing_message = str(exc)
    else:
        raise AssertionError("expected missing catalog fingerprint ValueError")

    try:
        validate_model_catalog_fingerprint(
            {
                "models": {},
                "features": {},
                CATALOG_FINGERPRINT_KEY: "not-current",
            }
        )
    except ValueError as exc:
        mismatch_message = str(exc)
    else:
        raise AssertionError("expected catalog fingerprint mismatch ValueError")

    assert "missing Feature Catalog fingerprint" in missing_message
    assert "fingerprint mismatch" in mismatch_message


def test_load_model_rejects_artifact_without_catalog_fingerprint(tmp_path):
    model_path = tmp_path / "model.pkl"
    joblib.dump({"models": {}, "features": {}, "preprocess_version": "v1.0"}, model_path)

    from core.ml.inference import load_model

    try:
        load_model(model_path)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing catalog fingerprint ValueError")

    assert "missing Feature Catalog fingerprint" in message


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


def _catalog_with_changed_active_row(
    catalog: FeatureCatalog,
    **changes,
) -> FeatureCatalog:
    row_index, row = next(
        (index, row) for index, row in enumerate(catalog.rows) if row.active
    )
    changed_rows = list(catalog.rows)
    changed_rows[row_index] = replace(row, **changes)
    return FeatureCatalog(rows=tuple(changed_rows), headers=catalog.headers)


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


def test_training_input_header_guard_accepts_catalog_headers_without_derived():
    catalog = load_feature_catalog()
    headers = catalog.training_headers()

    validate_training_input_headers(pd.Index(headers))

    for derived in DERIVED_FEATURES:
        assert derived not in headers


def test_training_input_header_guard_reports_unknown_header():
    catalog = load_feature_catalog()
    headers = list(catalog.training_headers())
    headers.append("Cooling Capacity Alias")

    try:
        validate_training_input_headers(headers)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected unknown training header ValueError")

    assert "Training data header contract violation" in message
    assert "config/ml/features.csv ml_name" in message
    assert "unknown training header(s): Cooling Capacity Alias" in message


def test_training_input_header_guard_reports_missing_header():
    headers = [
        header
        for header in load_feature_catalog().training_headers()
        if header != "Cooling Capa"
    ]

    try:
        validate_training_input_headers(headers)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing training header ValueError")

    assert "Training data header contract violation" in message
    assert "missing required training header(s): Cooling Capa" in message


def test_build_input_df_allows_mode_missing_zero_fill_only_for_mode_features():
    row = _complete_base_row()
    for feature in ("Cooling Capa", "Heating Capa", "Cooling Power", "Heating Power"):
        row.pop(feature)

    df = build_input_df(row)

    assert df.loc[0, "Cooling Capa"] == 0.0
    assert df.loc[0, "Heating Capa"] == 0.0
    assert df.loc[0, "Cooling Power"] == 0.0
    assert df.loc[0, "Heating Power"] == 0.0


def test_build_input_df_rejects_missing_feature_without_zero_fill_policy():
    row = _complete_base_row()
    row.pop("ID Volume")

    try:
        build_input_df(row)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing feature ValueError")

    assert "zero_fill_policy" in message
    assert "ID Volume" in message


def test_build_input_df_required_features_do_not_require_unused_base_names():
    row = _complete_base_row()
    for feature in ("Ref Qty", "Cooling Hz", "Heating Hz"):
        row.pop(feature)

    df = build_input_df(
        row,
        required_features=["Cooling Capa", "ID Volume", "Cool_Capa_per_EER"],
    )

    assert df.loc[0, "Cooling Capa"] == 3500.0
    assert "Cool_Capa_per_EER" in df.columns


def test_build_input_df_required_derived_feature_checks_raw_dependencies():
    row = _complete_base_row()
    row.pop("Comp EER")

    try:
        build_input_df(row, required_features=["Cool_Capa_per_EER"])
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing derived dependency ValueError")

    assert "Comp EER" in message


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


def _complete_base_row() -> dict[str, float]:
    return {
        "Cooling Capa": 3500.0,
        "Heating Capa": 4000.0,
        "ID Volume": 1.0,
        "Evap Area": 2.0,
        "Evap Volume": 3.0,
        "OD Volume": 4.0,
        "Cond Area": 5.0,
        "Cond Volume": 6.0,
        "Comp EER": 7.0,
        "Comp cc": 8.0,
        "R410A": 0.0,
        "R32": 1.0,
        "R290": 0.0,
        "EEV": 1.0,
        "Capi": 0.0,
        "Ref Qty": 1.0,
        "Cooling Power": 1200.0,
        "Heating Power": 1300.0,
        "Cooling Hz": 58.0,
        "Heating Hz": 59.0,
    }
