"""Mapping package owner boundary.

Arc 7 moves mapping paths, repository loading, autofill policy, and pure update
logic here while preserving existing root/script compatibility.
"""

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
    MappingValidationError,
)
from core.mapping.entity_runtime_adapter import (
    adapt_runtime_mapping_data,
    load_runtime_mapping_catalog,
    runtime_mapping_source_label,
)
from core.mapping.entity_validation import validate_mapping_entity_catalog

__all__ = [
    "MappingAttributeDefinition",
    "MappingEntityCatalog",
    "MappingEntityDefinition",
    "MappingEntityRow",
    "MappingValidationError",
    "adapt_runtime_mapping_data",
    "load_runtime_mapping_catalog",
    "runtime_mapping_source_label",
    "validate_mapping_entity_catalog",
]
