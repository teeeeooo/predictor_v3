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
from core.mapping.entity_validation import validate_mapping_entity_catalog

__all__ = [
    "MappingAttributeDefinition",
    "MappingEntityCatalog",
    "MappingEntityDefinition",
    "MappingEntityRow",
    "MappingValidationError",
    "validate_mapping_entity_catalog",
]
