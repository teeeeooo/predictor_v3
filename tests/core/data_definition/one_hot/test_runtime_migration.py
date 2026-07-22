"""One-hot runtime parity and v2 compatibility tests."""

import json
from dataclasses import replace

import pytest

from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.state.case_row import CaseRow
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from core.data_definition.contract import (
    ContractGeneration,
    LegacyOneHotCategoryDefinition,
    LegacyOneHotGroupDefinition,
    bootstrap_manifest,
    current_one_hot_definitions,
    generate_projections,
    legacy_bundle_fingerprint_payload,
    migrate_manifest,
    scoped_fingerprints,
)
from core.data_definition.one_hot.runtime import (
    encode_one_hot_values,
    one_hot_runtime_snapshot,
)


def _v2_manifest():
    current = bootstrap_manifest()
    groups = tuple(LegacyOneHotGroupDefinition(
        group.identity,
        group.group_key,
        group.selector_feature_identity,
        group.category_source,
        group.unknown_policy,
        group.missing_policy,
        tuple(LegacyOneHotCategoryDefinition(
            item.identity,
            item.source_value,
            item.emitted_ml_name,
            item.order,
            item.active,
        ) for item in group.categories),
    ) for group in current.one_hot_groups)
    return replace(
        current,
        contract_version="unified_feature_contract.v2",
        generation=ContractGeneration("historical-v2-one-hot"),
        one_hot_groups=groups,
    )


def test_golden_runtime_parity_missing_unknown_order_and_input_immutability():
    snapshot = one_hot_runtime_snapshot(bootstrap_manifest())
    values = {"ref_type": "R32", "exp_type": "Capi"}
    original = dict(values)
    encoded = encode_one_hot_values(snapshot, values)
    assert encoded.values == (
        ("R410A", 0.0), ("R32", 1.0), ("R290", 0.0),
        ("EEV", 0.0), ("Capi", 1.0),
    )
    assert values == original
    missing = encode_one_hot_values(snapshot, {})
    assert all(value == 0.0 for _name, value in missing.values)
    assert missing.warnings == ()
    unknown = encode_one_hot_values(
        snapshot, {"ref_type": "unknown", "exp_type": "unknown-2"}
    )
    assert all(value == 0.0 for _name, value in unknown.values)
    assert unknown.warnings == (
        "Unsupported option ignored: unknown",
        "Unsupported option ignored: unknown-2",
    )
    assert all(isinstance(value, float) for _name, value in encoded.values)
    projections = generate_projections(bootstrap_manifest())
    runtime_headers = tuple(name for name, _value in encoded.values)
    train_one_hot_headers = tuple(
        item.ml_name for item in projections.ml if item.role == "one_hot" and item.active
    )
    assert train_one_hot_headers == runtime_headers


def test_runtime_uses_selector_identity_and_supports_source_name_difference():
    manifest = bootstrap_manifest()
    group = manifest.one_hot_groups[0]
    category = group.categories[0]
    emitted = next(item for item in manifest.features
                   if item.identity == category.emitted_feature_identity)
    changed = replace(
        manifest,
        features=tuple(
            replace(item, ml_name="Refrigerant_R410A")
            if item.identity == emitted.identity else item
            for item in manifest.features
        ),
        one_hot_groups=(
            replace(group, group_key="coolant", categories=(
                replace(category, emitted_ml_name="Refrigerant_R410A"),
                *group.categories[1:],
            )),
            *manifest.one_hot_groups[1:],
        ),
    )
    selector = next(item for item in changed.features
                    if item.identity == group.selector_feature_identity)
    changed = replace(changed, features=tuple(
        replace(item, one_hot_group="coolant")
        if item.identity == selector.identity or item.one_hot_group == group.group_key
        else item for item in changed.features
    ))
    snapshot = one_hot_runtime_snapshot(changed)
    encoded = dict(encode_one_hot_values(snapshot, {selector.column_key: "R410A"}).values)
    assert encoded["Refrigerant_R410A"] == 1.0
    case = CaseRow(
        case_id="case-1",
        input_values={"cooling_capa": "3500", selector.column_key: "R410A"},
    )
    outcome = RowToMlInputAdapter(one_hot_snapshot=snapshot).build_request(case)
    assert outcome.request.row_input["Refrigerant_R410A"] == 1.0


def test_v2_relation_migration_is_identity_based_and_fingerprint_neutral():
    legacy = _v2_manifest()
    migrated = migrate_manifest(legacy)
    resolved = current_one_hot_definitions(legacy)
    assert migrated.contract_version.endswith(".v3")
    assert [item.identity for item in resolved] == [
        item.identity for item in migrated.one_hot_groups
    ]
    assert scoped_fingerprints(legacy).model_compatibility == (
        scoped_fingerprints(migrated).model_compatibility
    )
    assert scoped_fingerprints(legacy).one_hot == scoped_fingerprints(migrated).one_hot


def test_v2_missing_and_ambiguous_emitted_names_are_actionable():
    legacy = _v2_manifest()
    group = legacy.one_hot_groups[0]
    missing = replace(legacy, one_hot_groups=(replace(
        group,
        categories=(replace(group.categories[0], emitted_ml_name="missing"),
                    *group.categories[1:]),
    ), *legacy.one_hot_groups[1:]))
    with pytest.raises(ValueError, match="is missing"):
        current_one_hot_definitions(missing)
    duplicate = replace(legacy.features[0], ml_name=group.categories[0].emitted_ml_name)
    ambiguous = replace(legacy, features=(duplicate, *legacy.features[1:]))
    with pytest.raises(ValueError, match="is ambiguous"):
        current_one_hot_definitions(ambiguous)


def test_historical_v2_old_fingerprints_read_and_rollback(tmp_path):
    legacy = _v2_manifest()
    repository = DataDefinitionGenerationRepository(tmp_path)
    repository.publish(legacy)
    bundle_path = tmp_path / "generations" / legacy.generation.generation_id / "bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["fingerprints"] = legacy_bundle_fingerprint_payload(legacy)
    bundle_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    assert repository.read_generation(legacy.generation.generation_id).manifest == legacy
    current = bootstrap_manifest()
    current = replace(
        current,
        generation=replace(current.generation,
                           parent_generation_id=legacy.generation.generation_id),
    )
    repository.publish(current)
    rolled_back = repository.rollback(legacy.generation.generation_id)
    assert rolled_back.manifest.contract_version.endswith(".v2")
    assert current_one_hot_definitions(rolled_back.manifest)[0].categories[0].emitted_feature_identity
