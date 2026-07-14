"""Generic mapping entity validation tests."""

import pytest

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)
from core.mapping.entity_validation import validate_mapping_entity_catalog
from core.mapping.value_policy import coerce_mapping_boolean


def _fan_motor_entity(
    *,
    entity_key: str = "fan_motor",
    attributes: tuple[MappingAttributeDefinition, ...] | None = None,
    key_attribute: str = "motor_code",
) -> MappingEntityDefinition:
    return MappingEntityDefinition(
        entity_key=entity_key,
        label="Fan Motor",
        key_attribute=key_attribute,
        attributes=attributes
        or (
            MappingAttributeDefinition("motor_code", "Motor Code"),
            MappingAttributeDefinition(
                "motor_efficiency",
                "Motor Efficiency",
                data_type="number",
                required=True,
            ),
            MappingAttributeDefinition("enabled", "Enabled", data_type="boolean"),
        ),
    )


def _codes(catalog: MappingEntityCatalog) -> set[str]:
    return {error.code for error in validate_mapping_entity_catalog(catalog)}


def test_valid_catalog_has_no_validation_errors():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_efficiency": "0.82", "enabled": "true"},
            ),
        ),
    )

    assert validate_mapping_entity_catalog(catalog) == ()


def test_duplicate_entity_key_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(), _fan_motor_entity()),
    )

    assert "duplicate_entity_key" in _codes(catalog)


def test_blank_entity_key_is_rejected():
    catalog = MappingEntityCatalog(entities=(_fan_motor_entity(entity_key=" "),))

    assert "blank_entity_key" in _codes(catalog)


def test_duplicate_attribute_key_is_rejected_within_entity():
    duplicate_attributes = (
        MappingAttributeDefinition("motor_code", "Motor Code"),
        MappingAttributeDefinition("motor_efficiency", "Motor Efficiency"),
        MappingAttributeDefinition("motor_efficiency", "Motor Efficiency Copy"),
    )
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(attributes=duplicate_attributes),),
    )

    assert "duplicate_attribute_key" in _codes(catalog)


def test_missing_key_attribute_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(key_attribute="missing_code"),),
    )

    assert "missing_key_attribute" in _codes(catalog)


def test_unknown_row_entity_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(MappingEntityRow("unknown_entity", "FM-A", {}),),
    )

    assert "unknown_row_entity" in _codes(catalog)


def test_blank_row_key_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(MappingEntityRow("fan_motor", " ", {"motor_efficiency": 0.82}),),
    )

    assert "blank_row_key" in _codes(catalog)


def test_duplicate_row_key_is_rejected_within_entity():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow("fan_motor", "FM-A", {"motor_efficiency": 0.82}),
            MappingEntityRow("fan_motor", "FM-A", {"motor_efficiency": 0.86}),
        ),
    )

    assert "duplicate_row_key" in _codes(catalog)


def test_required_attribute_missing_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(MappingEntityRow("fan_motor", "FM-A", {"enabled": True}),),
    )

    assert "missing_required_value" in _codes(catalog)


def test_unknown_attribute_value_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_efficiency": 0.82, "unexpected": "value"},
            ),
        ),
    )

    assert "unknown_attribute_value" in _codes(catalog)


def test_number_and_boolean_data_types_are_validated():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_efficiency": "not-a-number", "enabled": "not-a-boolean"},
            ),
        ),
    )

    errors = validate_mapping_entity_catalog(catalog)

    assert [error.code for error in errors] == [
        "invalid_value_type",
        "invalid_value_type",
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        ("TRUE", True),
        ("false", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("NO", False),
    ],
)
def test_boolean_policy_uses_explicit_repository_conventions(value, expected):
    assert coerce_mapping_boolean(value) is expected


@pytest.mark.parametrize("value", ["not-a-boolean", 2, object()])
def test_boolean_policy_rejects_ambiguous_values(value):
    with pytest.raises(ValueError, match="boolean"):
        coerce_mapping_boolean(value)


def test_inactive_attribute_skips_required_and_type_value_validation():
    attributes = (
        MappingAttributeDefinition("motor_code", "Motor Code"),
        MappingAttributeDefinition(
            "legacy_efficiency",
            "Legacy Efficiency",
            data_type="number",
            required=True,
            active=False,
        ),
    )
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(attributes=attributes),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"legacy_efficiency": "not-a-number"},
            ),
        ),
    )

    assert validate_mapping_entity_catalog(catalog) == ()


def test_inactive_row_skips_required_and_type_value_validation():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_efficiency": "not-a-number", "enabled": "not-a-boolean"},
                active=False,
            ),
        ),
    )

    assert validate_mapping_entity_catalog(catalog) == ()


def test_inactive_entity_still_participates_in_structural_validation():
    catalog = MappingEntityCatalog(
        entities=(
            _fan_motor_entity(entity_key="fan_motor"),
            MappingEntityDefinition(
                entity_key="fan_motor",
                label="Inactive duplicate",
                key_attribute="motor_code",
                attributes=(MappingAttributeDefinition("motor_code", "Motor Code"),),
                active=False,
            ),
        ),
    )

    assert "duplicate_entity_key" in _codes(catalog)


def test_key_attribute_value_may_be_omitted_from_row_values():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_efficiency": 0.82, "enabled": True},
            ),
        ),
    )

    assert validate_mapping_entity_catalog(catalog) == ()


def test_key_attribute_value_matches_row_key_after_trim():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_code": " FM-A ", "motor_efficiency": 0.82},
            ),
        ),
    )

    assert validate_mapping_entity_catalog(catalog) == ()


def test_key_attribute_value_mismatch_is_rejected():
    catalog = MappingEntityCatalog(
        entities=(_fan_motor_entity(),),
        rows=(
            MappingEntityRow(
                "fan_motor",
                "FM-A",
                {"motor_code": "FM-B", "motor_efficiency": 0.82},
            ),
        ),
    )

    assert "row_key_attribute_mismatch" in _codes(catalog)
