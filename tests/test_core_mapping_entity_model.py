"""Generic mapping entity model tests."""

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)


def test_generic_fan_motor_entity_definition_is_supported():
    catalog = MappingEntityCatalog(
        entities=(
            MappingEntityDefinition(
                entity_key="fan_motor",
                label="Fan Motor",
                key_attribute="motor_code",
                attributes=(
                    MappingAttributeDefinition("motor_code", "Motor Code"),
                    MappingAttributeDefinition(
                        "motor_efficiency",
                        "Motor Efficiency",
                        data_type="number",
                        required=True,
                    ),
                    MappingAttributeDefinition(
                        "enabled",
                        "Enabled",
                        data_type="boolean",
                    ),
                ),
            ),
        ),
        rows=(
            MappingEntityRow(
                entity_key="fan_motor",
                row_key="FM-A",
                values={"motor_efficiency": 0.82, "enabled": True},
            ),
        ),
    )

    entity = catalog.entity_definition("fan_motor")

    assert entity is not None
    assert entity.label == "Fan Motor"
    assert catalog.value_for("fan_motor", "FM-A", "motor_efficiency") == 0.82
    assert catalog.value_for("fan_motor", "FM-A", "enabled") is True


def test_existing_mapping_entity_can_add_new_attribute_as_data():
    catalog = MappingEntityCatalog(
        entities=(
            MappingEntityDefinition(
                entity_key="evap_index",
                label="Evap Index",
                key_attribute="evap_index",
                attributes=(
                    MappingAttributeDefinition("evap_index", "Evap Index"),
                    MappingAttributeDefinition("Size", "Size", data_type="number"),
                    MappingAttributeDefinition(
                        "Inner Surface Area",
                        "Inner Surface Area",
                        data_type="number",
                    ),
                ),
            ),
        ),
        rows=(
            MappingEntityRow(
                entity_key="evap_index",
                row_key="S1-2",
                values={"Size": 1, "Inner Surface Area": 8.2},
            ),
        ),
    )

    attribute = catalog.attribute_definition("evap_index", "Inner Surface Area")
    row = catalog.row("evap_index", "S1-2")

    assert attribute is not None
    assert attribute.data_type == "number"
    assert row is not None
    assert row.value_for("Inner Surface Area") == 8.2


def test_entity_row_values_can_be_looked_up_by_key_and_attribute():
    catalog = MappingEntityCatalog(
        entities=(
            MappingEntityDefinition(
                entity_key="tube_geometry",
                label="Tube Geometry",
                key_attribute="tube_code",
                attributes=(
                    MappingAttributeDefinition("tube_code", "Tube Code"),
                    MappingAttributeDefinition("inner_area", "Inner Area"),
                ),
            ),
        ),
        rows=(
            MappingEntityRow(
                entity_key="tube_geometry",
                row_key="T-07",
                values={"inner_area": "14.2"},
            ),
        ),
    )

    assert catalog.rows_for_entity("tube_geometry")[0].row_key == "T-07"
    assert catalog.value_for("tube_geometry", "T-07", "inner_area") == "14.2"
    assert catalog.value_for("tube_geometry", "missing", "inner_area", "") == ""


def test_row_key_is_canonical_identity_when_key_attribute_value_is_omitted():
    catalog = MappingEntityCatalog(
        entities=(
            MappingEntityDefinition(
                entity_key="fan_motor",
                label="Fan Motor",
                key_attribute="motor_code",
                attributes=(
                    MappingAttributeDefinition("motor_code", "Motor Code"),
                    MappingAttributeDefinition("motor_power", "Motor Power"),
                ),
            ),
        ),
        rows=(
            MappingEntityRow(
                entity_key="fan_motor",
                row_key="FM-A",
                values={"motor_power": 35},
            ),
        ),
    )

    row = catalog.row("fan_motor", "FM-A")

    assert row is not None
    assert row.value_for("motor_code") is None
    assert catalog.value_for("fan_motor", "FM-A", "motor_power") == 35
