"""Arc 15A Data Definition projection and validator tests."""

from core.data_definition.derived_policy import load_current_derived_feature_policy
from core.data_definition.projection import (
    extract_mapping_requirements,
    load_data_definition_rows,
    project_feature_catalog_from_schema,
)
from core.data_definition.validation import build_data_definition_report
from core.ml.feature_catalog import load_feature_catalog
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2
from core.predictor_schema.catalog_v2_projection import load_projected_columns_v2
from core.predictor_schema.columns import COLUMNS

EXPECTED_DERIVED_FEATURES = (
    "Cool_Capa_per_EER",
    "Cool_Capa_per_CondArea",
    "Cool_Capa_per_EvapArea",
    "Cool_Capa_per_cc",
    "Heat_Capa_per_EER",
    "Heat_Capa_per_CondArea",
    "Heat_Capa_per_EvapArea",
    "Heat_Capa_per_cc",
)

EXPECTED_MAPPING_REQUIREMENTS = {
    ("idu", "ID Volume"),
    ("evap_index", "Evap Area"),
    ("evap_index", "Evap Volume"),
    ("odu", "OD Volume"),
    ("compressor", "Comp EER"),
    ("compressor", "Comp cc"),
    ("cond_specs", "Cond Area"),
    ("cond_specs", "Cond Volume"),
}


def test_data_definition_projection_matches_current_feature_catalog_parity():
    projected = project_feature_catalog_from_schema()
    catalog = load_feature_catalog()

    assert [row.comparison_key() for row in projected] == [
        (
            row.order,
            row.ml_name,
            row.role,
            row.ui_key,
            row.label,
            row.source,
            row.mapping_key,
            row.one_hot_group,
            row.zero_fill_policy,
            row.active,
        )
        for row in catalog.rows
    ]

    report = build_data_definition_report()
    assert report.parity_issues == ()
    assert report.ok


def test_data_definition_derived_rows_are_policy_owned_not_orphans():
    policy = load_current_derived_feature_policy()
    projected = project_feature_catalog_from_schema()
    report = build_data_definition_report()

    assert tuple(row.ml_name for row in policy) == EXPECTED_DERIVED_FEATURES
    assert tuple(row.ml_name for row in projected if row.role == "derived") == (
        EXPECTED_DERIVED_FEATURES
    )
    assert not [issue for issue in report.issues if issue.code == "catalog_orphan"]


def test_data_definition_extracts_active_mapping_lookup_requirements():
    requirements = extract_mapping_requirements(load_data_definition_rows())

    assert {
        (requirement.mapping_entity, requirement.mapping_attribute)
        for requirement in requirements
    } == EXPECTED_MAPPING_REQUIREMENTS
    assert {requirement.column_key for requirement in requirements} >= {
        "id_volume",
        "evap_area",
        "evap_volume",
        "od_volume",
        "cond_area",
        "cond_volume",
        "comp_eer",
        "comp_cc",
    }


def test_data_definition_preserves_cond_specs_semantic_and_compatibility_source():
    schema_rows = {
        row.column_key: row for row in load_predict_schema_catalog_v2().active_rows
    }
    projected = {row.ui_key: row for row in project_feature_catalog_from_schema()}
    requirements = {
        requirement.column_key: requirement
        for requirement in build_data_definition_report().mapping_requirements
    }

    assert schema_rows["cond_area"].mapping_entity == "cond_specs"
    assert schema_rows["cond_volume"].mapping_entity == "cond_specs"
    assert requirements["cond_area"].mapping_entity == "cond_specs"
    assert requirements["cond_volume"].mapping_entity == "cond_specs"
    assert projected["cond_area"].source == "odu"
    assert projected["cond_volume"].source == "odu"


def test_data_definition_validates_one_hot_selector_and_emitted_feature_parity():
    report = build_data_definition_report()
    relationships = {
        relationship.one_hot_group: relationship
        for relationship in report.one_hot_relationships
    }

    assert relationships["refrigerant"].selector_column == "ref_type"
    assert relationships["refrigerant"].emitted_ml_names == ("R410A", "R32", "R290")
    assert relationships["refrigerant"].catalog_ml_names == ("R410A", "R32", "R290")
    assert relationships["expansion_device"].selector_column == "exp_type"
    assert relationships["expansion_device"].emitted_ml_names == ("EEV", "Capi")
    assert relationships["expansion_device"].catalog_ml_names == ("EEV", "Capi")
    assert not [issue for issue in report.issues if issue.code.startswith("one_hot")]


def test_data_definition_does_not_switch_runtime_projection_owner():
    assert COLUMNS == load_projected_columns_v2()
