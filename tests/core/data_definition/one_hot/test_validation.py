"""Raw-manifest One-hot whole-contract validation tests."""

from dataclasses import asdict, replace

from core.data_definition.contract import (
    OneHotSelectorRestore,
    bootstrap_manifest,
    validate_contract,
)


def _codes(manifest):
    return {item.code for item in validate_contract(manifest)}


def test_raw_manifest_rejects_identity_key_selector_policy_and_order_bypass():
    manifest = bootstrap_manifest()
    first, second = manifest.one_hot_groups
    duplicate_group = replace(second, identity=first.identity, group_key=first.group_key,
                              selector_feature_identity=first.selector_feature_identity)
    invalid = replace(manifest, one_hot_groups=(first, duplicate_group))
    codes = _codes(invalid)
    assert "stable_identity_duplicate" in codes
    assert "one_hot_group_key_duplicate" in codes
    assert "one_hot_selector_duplicate" in codes
    category = first.categories[1]
    malformed = replace(first, unknown_policy="raw", missing_policy="raw", categories=(
        first.categories[0],
        replace(category, source_value=first.categories[0].source_value, order=1),
        *first.categories[2:],
    ))
    codes = _codes(replace(manifest, one_hot_groups=(malformed, second)))
    assert {
        "one_hot_unknown_policy_invalid",
        "one_hot_missing_policy_invalid",
        "one_hot_category_source_duplicate",
        "one_hot_category_order_duplicate",
        "one_hot_category_order_invalid",
    } <= codes


def test_raw_manifest_rejects_selector_and_emitted_shape_or_identity_mismatch():
    manifest = bootstrap_manifest()
    group = manifest.one_hot_groups[0]
    selector_id = group.selector_feature_identity
    emitted_id = group.categories[0].emitted_feature_identity
    invalid = replace(manifest, features=tuple(
        replace(item, editor="number") if item.identity == selector_id
        else replace(item, visible=True, readonly=False) if item.identity == emitted_id
        else item
        for item in manifest.features
    ))
    codes = _codes(invalid)
    assert "one_hot_selector_invalid" in codes
    assert "one_hot_emitted_invalid" in codes
    orphan = replace(group, categories=(
        replace(group.categories[0], emitted_feature_identity="missing-feature"),
        *group.categories[1:],
    ))
    assert "one_hot_emitted_invalid" in _codes(
        replace(manifest, one_hot_groups=(orphan, *manifest.one_hot_groups[1:]))
    )


def test_raw_manifest_rejects_active_empty_group_external_overlay_and_binding():
    manifest = bootstrap_manifest()
    group = manifest.one_hot_groups[0]
    no_active = replace(group, categories=tuple(
        replace(item, active=False) for item in group.categories
    ))
    features = tuple(
        replace(item, active=False)
        if item.identity in {category.emitted_feature_identity for category in group.categories}
        else item for item in manifest.features
    )
    assert "one_hot_active_category_required" in _codes(replace(
        manifest, features=features,
        one_hot_groups=(no_active, *manifest.one_hot_groups[1:]),
        ordering=replace(
            manifest.ordering,
            ml=tuple(identity for identity in manifest.ordering.ml
                     if identity not in {item.emitted_feature_identity for item in group.categories}),
        ),
    ))
    external = replace(
        group,
        category_source="external",
        source_binding="",
        categories=tuple(replace(item, provider_category_identity="")
                         for item in group.categories),
    )
    codes = _codes(replace(manifest, one_hot_groups=(external, *manifest.one_hot_groups[1:])))
    assert "one_hot_source_binding_invalid" in codes
    assert "one_hot_provider_category_invalid" in codes


def test_raw_manifest_rejects_static_binding_and_category_ml_order_mismatch():
    manifest = bootstrap_manifest()
    first, second = manifest.one_hot_groups
    static = replace(first, category_source="static", source_binding="unexpected")
    first_ids = [item.emitted_feature_identity for item in first.categories]
    swapped = tuple(
        first_ids[1::-1]
        + first_ids[2:]
        + [identity for identity in manifest.ordering.ml if identity not in first_ids]
    )
    invalid = replace(
        manifest,
        one_hot_groups=(static, second),
        ordering=replace(manifest.ordering, ml=swapped),
    )
    codes = _codes(invalid)
    assert "one_hot_source_binding_invalid" in codes
    assert "one_hot_ml_order_mismatch" in codes


def test_raw_manifest_rejects_restore_mismatch_dangling_takeover_and_mapping_projection():
    manifest = bootstrap_manifest()
    group = manifest.one_hot_groups[0]
    selector = next(item for item in manifest.features
                    if item.identity == group.selector_feature_identity)
    restore = OneHotSelectorRestore(**asdict(selector))

    inactive = replace(group, active=False, selector_restore=restore)
    inactive_features = tuple(
        replace(item, active=False)
        if item.identity == selector.identity
        or item.identity in {category.emitted_feature_identity for category in group.categories}
        else item
        for item in manifest.features
    )
    inactive_order = tuple(
        identity for identity in manifest.ordering.ml
        if identity not in {item.emitted_feature_identity for item in group.categories}
    )
    codes = _codes(replace(
        manifest,
        features=inactive_features,
        one_hot_groups=(inactive, *manifest.one_hot_groups[1:]),
        ordering=replace(manifest.ordering, ml=inactive_order),
    ))
    assert "one_hot_inactive_selector_mutated" in codes

    dangling_selector = replace(selector, rule_id=f"one_hot:{group.identity}")
    dangling = replace(manifest, features=tuple(
        dangling_selector if item.identity == selector.identity else item
        for item in manifest.features
    ))
    assert "one_hot_selector_restore_missing" in _codes(dangling)

    mismatch_selector = replace(selector, mapping_entity="idu")
    mismatch = replace(manifest, features=tuple(
        mismatch_selector if item.identity == selector.identity else item
        for item in manifest.features
    ))
    assert "one_hot_selector_mapping_binding_mismatch" in _codes(mismatch)

    invalid_restore = replace(inactive, selector_restore=replace(
        restore, active=False, value_source="one_hot", one_hot_group=group.group_key
    ))
    assert "one_hot_selector_restore_invalid" in _codes(replace(
        manifest,
        features=inactive_features,
        one_hot_groups=(invalid_restore, *manifest.one_hot_groups[1:]),
        ordering=replace(manifest.ordering, ml=inactive_order),
    ))
