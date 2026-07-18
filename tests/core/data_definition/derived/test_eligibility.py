"""Evaluator-input eligibility and leakage regression tests."""

from dataclasses import replace

import pytest

from core.data_definition import (
    AddDerivedIntent,
    EditDerivedIntent,
    SetDerivedActiveIntent,
    apply_derived_command,
    build_data_definition_draft,
)
from core.data_definition.contract import bootstrap_manifest, validate_contract
from core.data_definition.derived_operand_policy import derived_operand_eligibility
from core.data_definition.derived.evaluator import evaluation_snapshot
from core.data_definition.draft import replace_draft_row


def _manifest_and_owners():
    manifest = bootstrap_manifest()
    return manifest, manifest.features, manifest.derived


INVALID_RUNTIME_SHAPES = (
    ("input", "formula"),
    ("input", "result"),
    ("input", "status"),
    ("auto", "manual"),
    ("auto", "formula"),
    ("auto", "result"),
    ("auto", "status"),
    ("auto", "one_hot"),
    ("one_hot_feature", "manual"),
    ("one_hot_feature", "mapping_lookup"),
    ("one_hot_feature", "formula"),
    ("one_hot_feature", "result"),
    ("one_hot_feature", "status"),
)


@pytest.mark.parametrize(
    ("ml_name", "expected_source"),
    [
        ("Cooling Capa", "manual"),
        ("Cond Area", "mapping_lookup"),
        ("R32", "one_hot"),
    ],
)
def test_runtime_pre_evaluator_numeric_features_are_eligible(ml_name, expected_source):
    manifest, features, derived = _manifest_and_owners()
    feature = next(item for item in features if item.ml_name == ml_name)

    result = derived_operand_eligibility(
        features,
        derived,
        feature.identity,
        target_feature_identities={item.feature_identity for item in manifest.targets},
    )

    assert result.eligible
    assert result.identity == feature.identity
    assert result.ml_name == ml_name
    assert result.owner_kind == "feature"
    assert result.source_kind == expected_source

    draft = build_data_definition_draft(manifest=manifest)
    command = apply_derived_command(draft, AddDerivedIntent(
        f"valid_{ml_name.replace(' ', '_')}",
        feature.identity,
        manifest.derived[0].denominator_identity,
    ))
    assert command.accepted
    first = manifest.derived[0]
    raw = replace(
        manifest,
        derived=(replace(first, numerator_identity=feature.identity), *manifest.derived[1:]),
    )
    assert validate_contract(raw) == ()


@pytest.mark.parametrize(
    ("role", "value_source"),
    INVALID_RUNTIME_SHAPES,
)
def test_role_source_mismatch_is_runtime_unavailable(role, value_source):
    manifest, features, derived = _manifest_and_owners()
    source = next(item for item in features if item.ml_name == "Cooling Capa")
    disguised = replace(source, role=role, value_source=value_source)

    result = derived_operand_eligibility((disguised,), derived, disguised.identity)

    assert not result.eligible
    assert result.identity == disguised.identity
    assert result.ml_name == "Cooling Capa"
    assert result.code == "derived_operand_runtime_unavailable"
    assert f"role={role}" in result.reason
    assert f"value_source={value_source}" in result.reason


@pytest.mark.parametrize(("role", "value_source"), INVALID_RUNTIME_SHAPES)
@pytest.mark.parametrize("operand_field", ["numerator_identity", "denominator_identity"])
def test_invalid_runtime_shape_is_blocked_atomically_by_add_and_edit(
    role,
    value_source,
    operand_field,
):
    manifest = bootstrap_manifest()
    source = next(item for item in manifest.features if item.ml_name == "Cooling Capa")
    draft = build_data_definition_draft(manifest=manifest)
    disguised = replace_draft_row(
        draft,
        ("schema_row", source.identity),
        role=role,
        value_source=value_source,
    )
    valid_operand = manifest.derived[0].denominator_identity
    operands = {
        "numerator_identity": valid_operand,
        "denominator_identity": valid_operand,
    }
    operands[operand_field] = source.identity

    added = apply_derived_command(disguised, AddDerivedIntent(
        "invalid_runtime_shape",
        operands["numerator_identity"],
        operands["denominator_identity"],
    ))
    first = next(
        item for item in disguised.rows
        if item.stable_identity == manifest.derived[0].identity
    )
    edited = apply_derived_command(disguised, EditDerivedIntent(
        first.identity,
        operands["numerator_identity"],
        operands["denominator_identity"],
    ))

    for rejected in (added, edited):
        assert not rejected.accepted
        assert rejected.draft is disguised
        assert rejected.issues[0].code == "derived_operand_runtime_unavailable"
        assert rejected.issues[0].field_name == operand_field


def test_invalid_runtime_shape_cannot_survive_until_enable():
    manifest = bootstrap_manifest()
    source = next(item for item in manifest.features if item.ml_name == "Cooling Capa")
    draft = build_data_definition_draft(manifest=manifest)
    first = next(
        item for item in draft.rows
        if item.stable_identity == manifest.derived[0].identity
    )
    invalid = replace_draft_row(
        replace_draft_row(
            draft,
            ("schema_row", source.identity),
            role="input",
            value_source="formula",
        ),
        first.identity,
        active=False,
    )
    invalid = replace(
        invalid,
        ml_order=tuple(item for item in invalid.ml_order if item != first.identity),
    )

    enabled = apply_derived_command(
        invalid,
        SetDerivedActiveIntent(first.identity, True),
    )

    assert not enabled.accepted
    assert enabled.draft is invalid
    assert enabled.issues[0].code == "derived_operand_runtime_unavailable"


def test_raw_manifest_runtime_disguise_blocks_contract_and_snapshot():
    manifest = bootstrap_manifest()
    source = next(item for item in manifest.features if item.ml_name == "Cooling Capa")
    disguised = replace(
        manifest,
        features=tuple(
            replace(item, ml_name="Calculated Later", value_source="formula")
            if item.identity == source.identity else item
            for item in manifest.features
        ),
    )

    issues = validate_contract(disguised)
    assert "derived_operand_runtime_unavailable" in {
        item.code for item in issues
    }
    with pytest.raises(ValueError, match="derived_operand_runtime_unavailable"):
        evaluation_snapshot(disguised)


@pytest.mark.parametrize(
    ("source_name", "mutate", "expected_code"),
    [
        ("Cooling Power", lambda row: row, "derived_operand_target_or_result"),
        ("Cooling Capa", lambda row: replace(row, active=False), "derived_active_dependency_unavailable"),
        ("Cooling Capa", lambda row: replace(row, data_type="string"), "derived_operand_type_invalid"),
        ("Cooling Capa", lambda row: replace(row, ml_name=""), "derived_operand_type_invalid"),
        (
            "Cooling Capa",
            lambda row: replace(
                row,
                role="helper",
                value_source="formula",
                model_input_enabled=False,
            ),
            "derived_operand_runtime_unavailable",
        ),
    ],
)
def test_ineligible_feature_reasons_are_explicit(source_name, mutate, expected_code):
    manifest, features, derived = _manifest_and_owners()
    source = next(item for item in features if item.ml_name == source_name)
    candidate = mutate(source)

    result = derived_operand_eligibility(
        (candidate,),
        derived,
        candidate.identity,
        target_feature_identities={item.feature_identity for item in manifest.targets},
    )

    assert not result.eligible
    assert result.code == expected_code
    assert result.reason


@pytest.mark.parametrize(
    ("numerator", "denominator"),
    [
        ("Heating Power", "Comp EER"),
        ("Cooling Power", "Cond Area"),
        ("Ref Qty", "Comp cc"),
        ("Cooling Hz", "Comp EER"),
    ],
)
def test_result_and_target_leakage_is_blocked_by_command_and_contract(
    numerator,
    denominator,
):
    manifest = bootstrap_manifest()
    by_name = {item.ml_name: item for item in manifest.features if item.ml_name}
    draft = build_data_definition_draft(manifest=manifest)
    command = apply_derived_command(draft, AddDerivedIntent(
        f"invalid_{numerator.replace(' ', '_')}",
        by_name[numerator].identity,
        by_name[denominator].identity,
    ))
    assert not command.accepted
    assert command.issues[0].code == "derived_operand_target_or_result"

    first = manifest.derived[0]
    raw = replace(
        manifest,
        derived=(replace(first, numerator_identity=by_name[numerator].identity), *manifest.derived[1:]),
    )
    issues = validate_contract(raw)
    assert "derived_operand_target_or_result" in {item.code for item in issues}


def test_inactive_feature_is_blocked_even_for_inactive_derived_authoring():
    manifest = bootstrap_manifest()
    source = next(item for item in manifest.features if item.ml_name == "Cond Area")
    raw = replace(
        manifest,
        features=tuple(
            replace(item, active=False) if item.identity == source.identity else item
            for item in manifest.features
        ),
    )
    first = raw.derived[0]
    raw = replace(
        raw,
        derived=(replace(first, active=False, denominator_identity=source.identity), *raw.derived[1:]),
        ordering=replace(
            raw.ordering,
            ml=tuple(item for item in raw.ordering.ml if item not in {source.identity, first.identity}),
        ),
    )

    assert "derived_active_dependency_unavailable" in {
        item.code for item in validate_contract(raw)
    }


def test_existing_eight_derived_definitions_remain_valid():
    manifest = bootstrap_manifest()
    assert len(manifest.derived) == 8
    assert validate_contract(manifest) == ()
