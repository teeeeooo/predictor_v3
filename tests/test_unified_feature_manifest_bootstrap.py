"""Phase 4B canonical manifest bootstrap contract tests."""

from dataclasses import replace

from core.data_definition.contract import bootstrap_manifest, dump_manifest, load_manifest


def test_bootstrap_is_deterministic_and_round_trips(tmp_path):
    first = bootstrap_manifest()
    second = bootstrap_manifest()
    assert first == second
    assert first.generation.generation_id.startswith("bootstrap-")
    path = tmp_path / "manifest.json"
    dump_manifest(first, path)
    assert load_manifest(path) == first


def test_bootstrap_uses_opaque_unique_stable_identities():
    manifest = bootstrap_manifest()
    identities = [item.identity for item in manifest.features]
    identities += [item.identity for item in manifest.derived]
    identities += [item.identity for item in manifest.one_hot_groups]
    identities += [category.identity for group in manifest.one_hot_groups for category in group.categories]
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
