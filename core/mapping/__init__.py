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
from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorRow,
    MappingEditorValidationResult,
)
from core.mapping.editor_projection import (
    OWNED_RUNTIME_SECTIONS,
    load_runtime_mapping_editor_draft,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.editor_validation import validate_mapping_editor_draft

__all__ = [
    "MappingEditorDraft",
    "MappingEditorGroup",
    "MappingEditorRow",
    "MappingEditorValidationResult",
    "MappingAttributeDefinition",
    "MappingEntityCatalog",
    "MappingEntityDefinition",
    "MappingEntityRow",
    "MappingValidationError",
    "OWNED_RUNTIME_SECTIONS",
    "adapt_runtime_mapping_data",
    "load_runtime_mapping_editor_draft",
    "load_runtime_mapping_catalog",
    "project_runtime_mapping_to_editor_draft",
    "runtime_mapping_source_label",
    "validate_mapping_editor_draft",
    "validate_mapping_entity_catalog",
]
