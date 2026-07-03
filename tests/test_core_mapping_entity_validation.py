"""Generic mapping entity validation tests."""

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)
from core.mapping.entity_validation import validate_mapping_entity_catalog


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
