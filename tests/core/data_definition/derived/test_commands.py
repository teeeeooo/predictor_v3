"""Restricted Derived command, DAG, identity, and fingerprint tests."""

from core.data_definition import (
    AddDerivedIntent,
    DuplicateDerivedIntent,
    EditDerivedIntent,
    RemoveDerivedIntent,
    RenameDefinitionIntent,
    RenameDerivedIntent,
    SetDerivedActiveIntent,
    apply_derived_command,
    apply_rename_definition_command,
    build_data_definition_draft,
)
from core.data_definition.contract import (
    bootstrap_manifest,
    candidate_manifest_from_draft,
    scoped_fingerprints,
)


def _state():
    manifest = bootstrap_manifest()
    return manifest, build_data_definition_draft(manifest=manifest)


def test_add_defaults_inactive_duplicate_gets_new_identity_and_rename_keeps_identity():
    manifest, draft = _state()
    added = apply_derived_command(draft, AddDerivedIntent(
        "Authored_ratio", manifest.features[0].identity, manifest.derived[0].denominator_identity
    ))
    assert added.accepted
    row = next(item for item in added.draft.rows if item.identity == added.identity)
    assert not row.active and row.zero_value == 0.0
    renamed = apply_derived_command(
        added.draft, RenameDerivedIntent(added.identity, "Authored_ratio_v2")
    )
    duplicate = apply_derived_command(
        renamed.draft, DuplicateDerivedIntent(renamed.identity, "Authored_ratio_copy")
    )
    assert renamed.accepted and duplicate.accepted
    assert renamed.identity == added.identity
    assert duplicate.identity != added.identity
    copied = next(item for item in duplicate.draft.rows if item.identity == duplicate.identity)
    assert not copied.active


def test_zero_value_accepts_finite_numbers_normalizes_blank_and_rejects_bool_nan_inf():
    manifest, draft = _state()
    for value, expected in (("", 0.0), (3, 3.0), ("-2.5", -2.5)):
        result = apply_derived_command(draft, AddDerivedIntent(
            f"ratio_{str(value).replace('-', 'm') or 'blank'}",
            manifest.features[0].identity,
                manifest.derived[0].denominator_identity,
            zero_value=value,
        ))
        assert result.accepted
        assert next(item for item in result.draft.rows if item.identity == result.identity).zero_value == expected
    for value in (True, float("nan"), float("inf"), float("-inf")):
        result = apply_derived_command(draft, AddDerivedIntent(
            "invalid_ratio", manifest.features[0].identity, manifest.features[2].identity,
            zero_value=value,
        ))
        assert not result.accepted and result.draft is draft
        assert result.issues[0].code == "derived_zero_value_invalid"


def test_self_direct_and_indirect_cycles_are_rejected_before_mutation():
    manifest, draft = _state()
    first = next(item for item in draft.rows if item.stable_identity == manifest.derived[0].identity)
    self_cycle = apply_derived_command(draft, EditDerivedIntent(
        first.identity, first.stable_identity, first.denominator_identity
    ))
    assert not self_cycle.accepted and self_cycle.draft is draft
    second = next(item for item in draft.rows if item.stable_identity == manifest.derived[1].identity)
    first_to_second = apply_derived_command(draft, EditDerivedIntent(
        first.identity, second.stable_identity, first.denominator_identity
    ))
    assert first_to_second.accepted
    indirect = apply_derived_command(first_to_second.draft, EditDerivedIntent(
        second.identity, first.stable_identity, second.denominator_identity
    ))
    assert not indirect.accepted and indirect.draft is first_to_second.draft
    assert indirect.issues[0].code == "derived_dependency_cycle"


def test_missing_type_inactive_dependency_and_downstream_lifecycle_are_blocked():
    manifest, draft = _state()
    string_feature = next(item for item in manifest.features if item.data_type == "string")
    invalid_type = apply_derived_command(draft, AddDerivedIntent(
        "invalid_type", string_feature.identity, manifest.features[0].identity
    ))
    missing = apply_derived_command(draft, AddDerivedIntent(
        "missing", "missing_identity", manifest.features[0].identity
    ))
    assert not invalid_type.accepted and not missing.accepted
    upstream = apply_derived_command(draft, AddDerivedIntent(
        "upstream", manifest.features[0].identity, manifest.derived[0].denominator_identity
    ))
    downstream = apply_derived_command(upstream.draft, AddDerivedIntent(
        "downstream", upstream.identity[1], manifest.derived[0].denominator_identity
    ))
    activate_downstream = apply_derived_command(
        downstream.draft, SetDerivedActiveIntent(downstream.identity, True)
    )
    remove_upstream = apply_derived_command(
        downstream.draft, RemoveDerivedIntent(upstream.identity)
    )
    assert not activate_downstream.accepted and not remove_upstream.accepted
    assert activate_downstream.issues[0].code == "derived_active_dependency_unavailable"
    assert remove_upstream.issues[0].code == "derived_downstream_dependency"


def test_feature_ml_rename_preserves_operand_identity_and_model_guard_scope():
    manifest, draft = _state()
    source = next(item for item in draft.rows if item.stable_identity == manifest.features[0].identity)
    renamed = apply_rename_definition_command(
        draft, RenameDefinitionIntent(source.identity, ml_name="Cooling Capacity Renamed")
    )
    assert renamed.accepted
    candidate = candidate_manifest_from_draft(renamed.draft, manifest)
    assert candidate.derived[0].numerator_identity == source.stable_identity
    assert scoped_fingerprints(candidate).model_compatibility != (
        scoped_fingerprints(manifest).model_compatibility
    )


def test_inactive_authoring_changes_semantics_not_model_compatibility():
    manifest, draft = _state()
    added = apply_derived_command(draft, AddDerivedIntent(
        "inactive_ratio", manifest.features[0].identity, manifest.derived[0].denominator_identity,
        zero_value=7,
    ))
    candidate = candidate_manifest_from_draft(added.draft, manifest)
    before, after = scoped_fingerprints(manifest), scoped_fingerprints(candidate)
    assert before.derived_semantics != after.derived_semantics
    assert before.model_compatibility == after.model_compatibility


def test_remove_unsaved_add_collapses_to_original_draft_without_identity_reuse():
    manifest, draft = _state()
    added = apply_derived_command(draft, AddDerivedIntent(
        "temporary_ratio",
        manifest.features[0].identity,
        manifest.derived[0].denominator_identity,
    ))
    removed = apply_derived_command(added.draft, RemoveDerivedIntent(added.identity))
    assert added.accepted and removed.accepted
    assert removed.draft.rows == draft.rows
    assert not removed.draft.is_changed
    assert added.identity not in removed.draft.controlled_row_additions
    replacement = apply_derived_command(removed.draft, AddDerivedIntent(
        "temporary_ratio",
        manifest.features[0].identity,
        manifest.derived[0].denominator_identity,
    ))
    assert replacement.accepted and replacement.identity != added.identity
