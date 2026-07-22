"""Phase 4B generated projection, validation, and fingerprint tests."""

from dataclasses import replace

from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    ml_csv_text,
    predict_csv_text,
    scoped_fingerprints,
    validate_contract,
    operand_ml_name,
)
from core.data_definition.projection import extract_mapping_requirements, load_data_definition_rows
from core.ml.feature_catalog import load_feature_catalog
from core.ml.registry import MODEL_REGISTRY
from core.predictor_schema.catalog_v2 import load_predict_schema_catalog_v2


def test_generated_predict_and_ml_projections_preserve_current_contract(tmp_path):
    manifest = bootstrap_manifest()
    projections = generate_projections(manifest)
    predict_path = tmp_path / "schema.csv"
    predict_path.write_text(predict_csv_text(projections), encoding="utf-8")
    generated_predict = load_predict_schema_catalog_v2(predict_path)
    current_predict = load_predict_schema_catalog_v2()
    assert [replace(row, line_number=0) for row in generated_predict.rows] == [
        replace(row, line_number=0) for row in current_predict.rows
    ]
    feature_by_id = {item.identity: item for item in manifest.features}
    assert [row.column_key for row in generated_predict.rows] == [
        feature_by_id[identity].column_key for identity in manifest.ordering.predict
    ]

    ml_path = tmp_path / "features.csv"
    ml_path.write_text(ml_csv_text(projections), encoding="utf-8")
    generated_ml = load_feature_catalog(ml_path)
    current_ml = load_feature_catalog()
    assert generated_ml.rows == current_ml.rows


def test_generated_runtime_projections_preserve_derived_one_hot_registry_and_mapping():
    manifest = bootstrap_manifest()
    projections = generate_projections(manifest)
    assert [
        (
            item.ml_name,
            item.operation,
            operand_ml_name(manifest, item.numerator_identity),
            operand_ml_name(manifest, item.denominator_identity),
        )
        for item in projections.derived
    ] == [
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


def test_derived_one_hot_and_target_projections_use_canonical_ordering():
    manifest = bootstrap_manifest()
    first_derived, second_derived = manifest.derived[:2]
    dependent = replace(
        second_derived,
        numerator_identity=first_derived.identity,
    )
    reversed_derived = replace(
        manifest,
        derived=(dependent, first_derived, *manifest.derived[2:]),
        ordering=replace(
            manifest.ordering,
            derived=(dependent.identity, first_derived.identity, *manifest.ordering.derived[2:]),
        ),
    )
    derived_projection = generate_projections(reversed_derived)
    assert [item.identity for item in derived_projection.derived[:2]] == [
        first_derived.identity,
        dependent.identity,
    ]

    first_group = manifest.one_hot_groups[0]
    scrambled_one_hot = replace(
        manifest,
        one_hot_groups=(
            replace(first_group, categories=tuple(reversed(first_group.categories))),
            *manifest.one_hot_groups[1:],
        ),
    )
    one_hot_projection = generate_projections(scrambled_one_hot)
    assert [item.order for item in one_hot_projection.one_hot[0].categories] == [1, 2, 3]

    reordered_targets = (
        manifest.targets[2],
        manifest.targets[0],
        manifest.targets[1],
        *manifest.targets[3:],
    )
    reordered_targets = tuple(
        replace(item, presentation_order=index)
        for index, item in enumerate(reordered_targets, 1)
    )
    target_ordered = replace(
        manifest,
        targets=reordered_targets,
        ordering=replace(
            manifest.ordering,
            targets=tuple(item.identity for item in reordered_targets),
        ),
    )
    target_projection = generate_projections(target_ordered)
    assert [key for key, _payload in target_projection.target_registry] == [
        "power_model",
        "hz_model",
        "ref_model",
    ]
    assert [
        name
        for _key, payload in target_projection.target_registry
        for name in payload["targets"]
    ] == ["Cooling Power", "Heating Power", "Cooling Hz", "Heating Hz", "Ref Qty"]


def test_one_hot_and_target_presentation_order_change_scoped_fingerprints():
    manifest = bootstrap_manifest()
    group = manifest.one_hot_groups[0]
    categories = (
        replace(group.categories[1], order=1),
        replace(group.categories[0], order=2),
        *group.categories[2:],
    )
    group_feature_ids = {
        item.emitted_feature_identity for item in group.categories
    }
    reordered_feature_ids = iter(
        item.emitted_feature_identity for item in categories
    )
    one_hot_changed = replace(
        manifest,
        one_hot_groups=(replace(group, categories=categories), *manifest.one_hot_groups[1:]),
        ordering=replace(
            manifest.ordering,
            ml=tuple(
                next(reordered_feature_ids) if identity in group_feature_ids else identity
                for identity in manifest.ordering.ml
            ),
        ),
    )
    targets = (
        replace(manifest.targets[1], presentation_order=1),
        replace(manifest.targets[0], presentation_order=2),
        *manifest.targets[2:],
    )
    target_changed = replace(
        manifest,
        targets=targets,
        ordering=replace(
            manifest.ordering,
            targets=tuple(item.identity for item in targets),
        ),
    )

    assert validate_contract(one_hot_changed) == ()
    assert validate_contract(target_changed) == ()
    assert scoped_fingerprints(one_hot_changed).one_hot != scoped_fingerprints(manifest).one_hot
    assert scoped_fingerprints(target_changed).target_registry == (
        scoped_fingerprints(manifest).target_registry
    )
    assert scoped_fingerprints(target_changed).target_presentation != (
        scoped_fingerprints(manifest).target_presentation
    )
    assert scoped_fingerprints(target_changed).model_compatibility == (
        scoped_fingerprints(manifest).model_compatibility
    )


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
    cycle_rows[0] = replace(cycle_rows[0], numerator_identity=cycle_rows[1].identity)
    cycle_rows[1] = replace(cycle_rows[1], numerator_identity=cycle_rows[0].identity)
    cycle = replace(manifest, derived=tuple(cycle_rows))
    assert "derived_dependency_cycle" in {item.code for item in validate_contract(cycle)}


def test_cross_validation_rejects_ordering_one_hot_mapping_and_target_mismatches():
    manifest = bootstrap_manifest()
    feature_order = replace(
        manifest,
        features=(
            replace(manifest.features[0], display_order=999),
            *manifest.features[1:],
        ),
    )
    assert "predict_display_order_mismatch" in {
        item.code for item in validate_contract(feature_order)
    }
    duplicate_display_order = replace(
        manifest,
        features=(
            manifest.features[0],
            replace(
                manifest.features[1],
                display_order=manifest.features[0].display_order,
                active=False,
            ),
            *manifest.features[2:],
        ),
    )
    assert "predict_display_order_duplicate" in {
        item.code for item in validate_contract(duplicate_display_order)
    }
    invalid_display_order = replace(
        manifest,
        features=(
            replace(manifest.features[0], display_order=0),
            *manifest.features[1:],
        ),
    )
    assert "predict_display_order_invalid" in {
        item.code for item in validate_contract(invalid_display_order)
    }

    group = manifest.one_hot_groups[0]
    duplicate_category = replace(
        group.categories[1],
        source_value=group.categories[0].source_value,
        emitted_ml_name=group.categories[0].emitted_ml_name,
        order=group.categories[0].order,
    )
    invalid_one_hot = replace(
        manifest,
        one_hot_groups=(
            replace(
                group,
                category_source="unsupported",
                unknown_policy="unsupported",
                missing_policy="unsupported",
                categories=(group.categories[0], duplicate_category, *group.categories[2:]),
            ),
            *manifest.one_hot_groups[1:],
        ),
    )
    one_hot_codes = {item.code for item in validate_contract(invalid_one_hot)}
    assert {
        "one_hot_category_source_invalid",
        "one_hot_unknown_policy_invalid",
        "one_hot_missing_policy_invalid",
        "one_hot_category_emitted_duplicate",
        "one_hot_category_source_duplicate",
        "one_hot_category_order_duplicate",
    } <= one_hot_codes
    orphan_one_hot = replace(
        manifest,
        one_hot_groups=(
            replace(group, categories=group.categories[1:]),
            *manifest.one_hot_groups[1:],
        ),
    )
    assert "one_hot_emitted_membership_invalid" in {
        item.code for item in validate_contract(orphan_one_hot)
    }

    requirement = manifest.mapping_requirements[0]
    mapping_mismatch = replace(
        manifest,
        mapping_requirements=(
            replace(requirement, mapping_entity="wrong"),
            *manifest.mapping_requirements[1:],
        ),
    )
    assert "mapping_requirement_feature_mismatch" in {
        item.code for item in validate_contract(mapping_mismatch)
    }
    for field_name, value in (
        ("mapping_attribute", "wrong"),
        ("rule_id", "wrong"),
        ("data_type", "string"),
        ("required", not requirement.required),
    ):
        changed_requirement = replace(requirement, **{field_name: value})
        changed_manifest = replace(
            manifest,
            mapping_requirements=(
                changed_requirement,
                *manifest.mapping_requirements[1:],
            ),
        )
        assert "mapping_requirement_feature_mismatch" in {
            item.code for item in validate_contract(changed_manifest)
        }
    duplicate_mapping = replace(
        manifest,
        mapping_requirements=(
            *manifest.mapping_requirements,
            replace(requirement, identity="duplicate-requirement"),
        ),
    )
    mapping_codes = {item.code for item in validate_contract(duplicate_mapping)}
    assert "mapping_requirement_relation_duplicate" in mapping_codes
    assert "mapping_requirement_coverage_invalid" in mapping_codes
    orphan_mapping = replace(
        manifest,
        mapping_requirements=manifest.mapping_requirements[1:],
    )
    assert "mapping_requirement_coverage_invalid" in {
        item.code for item in validate_contract(orphan_mapping)
    }

    target_order = replace(
        manifest,
        targets=(
            replace(manifest.targets[0], presentation_order=2),
            *manifest.targets[1:],
        ),
    )
    target_codes = {item.code for item in validate_contract(target_order)}
    assert "target_presentation_order_duplicate" in target_codes
    assert "target_presentation_order_mismatch" in target_codes
    target_association = replace(
        manifest,
        targets=(
            replace(
                manifest.targets[0],
                model_group_identity="unknown-group",
            ),
            *manifest.targets[1:],
        ),
    )
    assert "target_model_group_invalid" in {
        item.code for item in validate_contract(target_association)
    }


def test_current_bootstrap_passes_whole_contract_validation():
    assert validate_contract(bootstrap_manifest()) == ()
