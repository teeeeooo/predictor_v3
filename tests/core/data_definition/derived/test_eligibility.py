"""Evaluator-input eligibility and leakage regression tests."""

from dataclasses import replace

import pytest

from core.data_definition import (
    AddDerivedIntent,
    apply_derived_command,
    build_data_definition_draft,
)
from core.data_definition.contract import bootstrap_manifest, validate_contract
from core.data_definition.derived_operand_policy import derived_operand_eligibility


def _manifest_and_owners():
    manifest = bootstrap_manifest()
    return manifest, manifest.features, manifest.derived


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
