"""Phase 4B generated projection, validation, and fingerprint tests."""

from dataclasses import replace

from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    ml_csv_text,
    predict_csv_text,
    scoped_fingerprints,
    validate_contract,
)
from core.data_definition.projection import extract_mapping_requirements, load_data_definition_rows
from core.ml.feature_catalog import load_feature_catalog
from core.ml.registry import MODEL_REGISTRY
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2


def test_generated_predict_and_ml_projections_preserve_current_contract(tmp_path):
    projections = generate_projections(bootstrap_manifest())
    predict_path = tmp_path / "schema.csv"
    predict_path.write_text(predict_csv_text(projections), encoding="utf-8")
    generated_predict = load_predict_schema_catalog_v2(predict_path)
    current_predict = load_predict_schema_catalog_v2()
    assert [replace(row, line_number=0) for row in generated_predict.rows] == [
        replace(row, line_number=0) for row in current_predict.rows
    ]

    ml_path = tmp_path / "features.csv"
    ml_path.write_text(ml_csv_text(projections), encoding="utf-8")
    generated_ml = load_feature_catalog(ml_path)
    current_ml = load_feature_catalog()
    assert generated_ml.rows == current_ml.rows


def test_generated_runtime_projections_preserve_derived_one_hot_registry_and_mapping():
    manifest = bootstrap_manifest()
    projections = generate_projections(manifest)
    assert [(item.ml_name, item.operation, item.numerator_ml_name, item.denominator_ml_name) for item in projections.derived] == [
        ("Cool_Capa_per_EER", "safe_ratio", "Cooling Capa", "Comp EER"),
        ("Cool_Capa_per_CondArea", "safe_ratio", "Cooling Capa", "Cond Area"),
        ("Cool_Capa_per_EvapArea", "safe_ratio", "Cooling Capa", "Evap Area"),
        ("Cool_Capa_per_cc", "safe_ratio", "Cooling Capa", "Comp cc"),
        ("Heat_Capa_per_EER", "safe_ratio", "Heating Capa", "Comp EER"),
        ("Heat_Capa_per_CondArea", "safe_ratio", "Heating Capa", "Cond Area"),
        ("Heat_Capa_per_EvapArea", "safe_ratio", "Heating Capa", "Evap Area"),
        ("Heat_Capa_per_cc", "safe_ratio", "Heating Capa", "Comp cc"),
    ]
    assert {
        group.group_key: tuple(item.emitted_ml_name for item in group.categories)
        for group in projections.one_hot
    } == {"refrigerant": ("R410A", "R32", "R290"), "expansion_device": ("EEV", "Capi")}
    assert dict(projections.target_registry) == MODEL_REGISTRY
    assert projections.mapping_requirements == extract_mapping_requirements(load_data_definition_rows())
    assert projections.generation_id == manifest.generation.generation_id


def test_ml_order_changes_only_order_sensitive_model_fingerprint():
    manifest = bootstrap_manifest()
    changed = replace(
        manifest,
        ordering=replace(
            manifest.ordering,
            ml=(manifest.ordering.ml[1], manifest.ordering.ml[0], *manifest.ordering.ml[2:]),
        ),
    )
    before = scoped_fingerprints(manifest)
    after = scoped_fingerprints(changed)
    assert before.ordered_ml != after.ordered_ml
    assert before.model_compatibility != after.model_compatibility
    assert before.predict == after.predict


def test_predict_presentation_change_does_not_break_model_compatibility():
    manifest = bootstrap_manifest()
    features = list(manifest.features)
    features[0] = replace(features[0], label="Presentation only")
    changed = replace(manifest, features=tuple(features))
    before = scoped_fingerprints(manifest)
    after = scoped_fingerprints(changed)
    assert before.predict != after.predict
    assert before.combined != after.combined
    assert before.model_compatibility == after.model_compatibility


def test_cross_validation_rejects_duplicate_identity_incomplete_order_and_cycle():
    manifest = bootstrap_manifest()
    duplicate = replace(
        manifest,
        derived=(replace(manifest.derived[0], identity=manifest.features[0].identity), *manifest.derived[1:]),
    )
    assert "stable_identity_duplicate" in {item.code for item in validate_contract(duplicate)}
    incomplete = replace(manifest, ordering=replace(manifest.ordering, ml=manifest.ordering.ml[:-1]))
    assert "ml_order_incomplete" in {item.code for item in validate_contract(incomplete)}
    cycle_rows = list(manifest.derived)
    cycle_rows[0] = replace(cycle_rows[0], numerator_ml_name=cycle_rows[1].ml_name)
    cycle_rows[1] = replace(cycle_rows[1], numerator_ml_name=cycle_rows[0].ml_name)
    cycle = replace(manifest, derived=tuple(cycle_rows))
    assert "derived_dependency_cycle" in {item.code for item in validate_contract(cycle)}


def test_current_bootstrap_passes_whole_contract_validation():
    assert validate_contract(bootstrap_manifest()) == ()
