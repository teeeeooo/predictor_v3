"""Runtime mapping repository to entity catalog adapter tests."""

import json

import pytest

from core.mapping.entity_runtime_adapter import (
    adapt_runtime_mapping_data,
    load_runtime_mapping_catalog,
    runtime_mapping_source_label,
)
from core.mapping.entity_validation import validate_mapping_entity_catalog


SAMPLE_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
        }
    },
}


def test_adapt_runtime_mapping_data_builds_deterministic_catalog():
    catalog = adapt_runtime_mapping_data(SAMPLE_MAPPING, source_label="/tmp/mapping.json")

    assert [entity.entity_key for entity in catalog.entities] == [
        "cond_specs",
        "idu",
        "odu",
        "odu_cascade",
    ]
    idu = catalog.entity_definition("idu")
    assert idu is not None
    assert idu.label == "Idu"
    assert idu.key_attribute == "idu_key"
    assert [attribute.attribute_key for attribute in idu.attributes] == [
        "idu_key",
        "ID Volume",
    ]
    assert idu.attributes[1].data_type == "number"
    assert catalog.value_for("idu", "IDU-A", "ID Volume") == 1.25
    assert validate_mapping_entity_catalog(catalog) == ()


def test_adapter_preserves_composite_and_list_runtime_values():
    catalog = adapt_runtime_mapping_data(SAMPLE_MAPPING)

    cond_row = catalog.row("cond_specs", "ODU-A F&T 7 1")
    cascade_row = catalog.row("odu_cascade", "ODU-A")

    assert cond_row is not None
    assert cond_row.value_for("Cond Area") == 3.5
    assert cascade_row is not None
    assert cascade_row.value_for("Available_Fins") == ["F&T"]
    assert catalog.attribute_definition("odu_cascade", "Available_Fins").data_type == "string"


def test_adapter_records_nested_values_without_flattening():
    catalog = adapt_runtime_mapping_data(
        {
            "nested_section": {
                "ROW-1": {
                    "Visible": "yes",
                    "Nested": {"inner": 1},
                }
            }
        }
    )

    row = catalog.row("nested_section", "ROW-1")

    assert row is not None
    assert row.value_for("Visible") == "yes"
    assert "Nested values not flattened: Nested" == row.notes
    assert catalog.attribute_definition("nested_section", "Nested") is None
    assert validate_mapping_entity_catalog(catalog) == ()


def test_load_runtime_mapping_catalog_uses_repository_loader_path(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps(SAMPLE_MAPPING), encoding="utf-8")

    catalog = load_runtime_mapping_catalog(str(mapping_file))

    assert catalog.rows_for_entity("cond_specs")[0].row_key == "ODU-A F&T 7 1"
    assert str(mapping_file) in catalog.notes
    assert runtime_mapping_source_label(str(mapping_file)).endswith(str(mapping_file))


def test_load_runtime_mapping_catalog_rejects_missing_or_empty_data(tmp_path):
    with pytest.raises(ValueError, match="empty or unavailable"):
        load_runtime_mapping_catalog(str(tmp_path / "missing.json"))
