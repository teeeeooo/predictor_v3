"""Phase 4B canonical manifest bootstrap contract tests."""

from dataclasses import replace
from pathlib import Path

from core.data_definition.contract import (
    bootstrap_manifest,
    dump_manifest,
    load_manifest,
    semantic_generation_id,
)


def test_bootstrap_is_deterministic_and_round_trips(tmp_path):
    first = bootstrap_manifest()
    second = bootstrap_manifest()
    assert first == second
    assert first.generation.generation_id.startswith("bootstrap-")
    path = tmp_path / "manifest.json"
    dump_manifest(first, path)
    assert load_manifest(path) == first


def test_repository_bootstrap_manifest_matches_deterministic_semantic_identity():
    path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "data_definition"
        / "manifest.json"
    )
    assert load_manifest(path) == bootstrap_manifest()


def test_bootstrap_uses_opaque_unique_stable_identities():
    manifest = bootstrap_manifest()
    identities = [item.identity for item in manifest.features]
    identities += [item.identity for item in manifest.derived]
    identities += [item.identity for item in manifest.one_hot_groups]
    identities += [
        category.identity
        for group in manifest.one_hot_groups
        for category in group.categories
    ]
    identities += [item.identity for item in manifest.targets]
    identities += [item.identity for item in manifest.model_groups]
    identities += [item.identity for item in manifest.mapping_requirements]
    assert len(identities) == len(set(identities))
    assert all(identity.startswith("ufm_") for identity in identities)
    assert all("cooling_capa" not in identity for identity in identities)


def test_bootstrap_preserves_current_contract_counts_and_owner_boundaries():
    manifest = bootstrap_manifest()
    assert len(manifest.features) == 35
    assert len(manifest.derived) == 8
    assert [group.group_key for group in manifest.one_hot_groups] == [
        "refrigerant", "expansion_device"
    ]
    assert len(manifest.targets) == 5
    assert len(manifest.model_groups) == 3
    assert len(manifest.mapping_requirements) == 8
    assert manifest.preprocessing_version == "v1.0"


def test_legacy_projection_values_are_not_canonical_identity():
    manifest = bootstrap_manifest()
    feature = next(item for item in manifest.features if item.column_key == "cooling_capa")
    renamed = replace(feature, column_key="renamed", label="Renamed", ml_name="Renamed ML")
    assert renamed.identity == feature.identity


def test_bootstrap_generation_identity_covers_complete_semantic_payload():
    manifest = bootstrap_manifest()
    unchanged = replace(manifest, generation=replace(manifest.generation, source="other"))
    feature_changed = replace(
        manifest,
        features=(replace(manifest.features[0], label="Semantic label"), *manifest.features[1:]),
    )
    ordering_changed = replace(
        manifest,
        ordering=replace(
            manifest.ordering,
            predict=(
                manifest.ordering.predict[1],
                manifest.ordering.predict[0],
                *manifest.ordering.predict[2:],
            ),
        ),
    )
    derived_changed = replace(
        manifest,
        derived=(replace(manifest.derived[0], zero_value=1.0), *manifest.derived[1:]),
    )
    category = manifest.one_hot_groups[0].categories[0]
    one_hot_changed = replace(
        manifest,
        one_hot_groups=(
            replace(
                manifest.one_hot_groups[0],
                categories=(
                    replace(category, source_value="semantic"),
                    *manifest.one_hot_groups[0].categories[1:],
                ),
            ),
            *manifest.one_hot_groups[1:],
        ),
    )
    target_changed = replace(
        manifest,
        targets=(replace(manifest.targets[0], presentation_order=99), *manifest.targets[1:]),
    )
    mapping_changed = replace(
        manifest,
        mapping_requirements=(
            replace(
                manifest.mapping_requirements[0],
                required=not manifest.mapping_requirements[0].required,
            ),
            *manifest.mapping_requirements[1:],
        ),
    )
    preprocessing_changed = replace(manifest, preprocessing_version="v-next")

    expected = manifest.generation.generation_id
    assert semantic_generation_id(unchanged, prefix="bootstrap") == expected
    for changed in (
        feature_changed,
        ordering_changed,
        derived_changed,
        one_hot_changed,
        target_changed,
        mapping_changed,
        preprocessing_changed,
    ):
        assert semantic_generation_id(changed, prefix="bootstrap") != expected
