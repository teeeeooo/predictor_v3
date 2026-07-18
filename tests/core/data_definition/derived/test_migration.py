"""Legacy name-reference compatibility and immutable rollback tests."""

import json
from dataclasses import replace

import pytest

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from core.data_definition.contract import (
    ContractGeneration,
    LegacyDerivedDefinition,
    bootstrap_manifest,
    current_derived_definitions,
    validate_contract,
    operand_ml_name,
    scoped_fingerprints,
)
from core.data_definition.derived.evaluator import evaluation_snapshot


def _legacy_manifest():
    current = bootstrap_manifest()
    legacy = replace(
        current,
        contract_version="unified_feature_contract.v1",
        generation=ContractGeneration("bootstrap-79c660826359bdd6d2ac"),
        derived=tuple(
            LegacyDerivedDefinition(
                item.identity,
                item.ml_name,
                item.operation,
                operand_ml_name(current, item.numerator_identity),
                operand_ml_name(current, item.denominator_identity),
                item.zero_value,
                item.zero_fill_policy,
                item.active,
            )
            for item in current.derived
        ),
    )
    return current, legacy


def test_representation_only_migration_preserves_derived_and_model_fingerprints():
    current, legacy = _legacy_manifest()
    before, after = scoped_fingerprints(legacy), scoped_fingerprints(current)
    assert before.derived == after.derived
    assert before.derived_semantics == after.derived_semantics
    assert before.model_compatibility == after.model_compatibility
    assert tuple(item.numerator_identity for item in current_derived_definitions(legacy)) == tuple(
        item.numerator_identity for item in current.derived
    )


def test_legacy_missing_and_ambiguous_names_are_actionable_failures():
    _current, legacy = _legacy_manifest()
    first = legacy.derived[0]
    missing = replace(
        legacy,
        derived=(replace(first, numerator_ml_name="missing"), *legacy.derived[1:]),
    )
    with pytest.raises(ValueError, match="is missing"):
        current_derived_definitions(missing)
    duplicate_feature = replace(legacy.features[2], ml_name=first.numerator_ml_name)
    ambiguous = replace(
        legacy,
        features=(*legacy.features[:2], duplicate_feature, *legacy.features[3:]),
    )
    with pytest.raises(ValueError, match="is ambiguous"):
        current_derived_definitions(ambiguous)


def test_legacy_decode_succeeds_but_invalid_runtime_shape_cannot_execute():
    _current, legacy = _legacy_manifest()
    source_name = legacy.derived[0].numerator_ml_name
    disguised = replace(
        legacy,
        features=tuple(
            replace(item, value_source="formula")
            if item.ml_name == source_name else item
            for item in legacy.features
        ),
    )

    assert current_derived_definitions(disguised)[0].numerator_identity
    assert "derived_operand_runtime_unavailable" in {
        item.code for item in validate_contract(disguised)
    }
    with pytest.raises(ValueError, match="derived_operand_runtime_unavailable"):
        evaluation_snapshot(disguised)


def test_historical_v1_bundle_without_new_metadata_field_reads_and_rolls_back(tmp_path):
    current, legacy = _legacy_manifest()
    repository = DataDefinitionGenerationRepository(tmp_path)
    repository.publish(legacy)
    bundle_path = tmp_path / "generations" / legacy.generation.generation_id / "bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["fingerprints"].pop("derived_semantics")
    bundle_path.write_text(json.dumps(bundle, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    historical = repository.read_generation(legacy.generation.generation_id)
    assert historical.manifest.contract_version.endswith(".v1")
    candidate = replace(
        current,
        generation=replace(
            current.generation,
            parent_generation_id=legacy.generation.generation_id,
            source="migration_test",
        ),
    )
    repository.publish(candidate)
    rolled_back = repository.rollback(legacy.generation.generation_id)
    assert rolled_back.manifest.generation.generation_id == legacy.generation.generation_id
    assert current_derived_definitions(rolled_back.manifest)[0].numerator_identity == (
        current.derived[0].numerator_identity
    )
