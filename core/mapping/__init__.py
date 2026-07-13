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
from core.mapping.condenser_identity import (
    condenser_identity,
    condenser_requires_pi,
    condenser_spec_key,
)
from core.mapping.editor_model import (
    MappingEditorDraft,
    MappingEditorGroup,
    MappingEditorRow,
    MappingEditorValidationResult,
)
from core.mapping.editor_commands import (
    add_draft_row,
    delete_draft_row,
    duplicate_draft_row,
    set_draft_cell,
)
from core.mapping.editor_projection import (
    OWNED_RUNTIME_SECTIONS,
    load_runtime_mapping_editor_draft,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.editor_persistence import (
    MappingEditorSaveResult,
    runtime_mapping_from_editor_draft,
    save_mapping_editor_draft,
)
from core.mapping.editor_export import (
    MappingEditorExportResult,
    export_mapping_editor_snapshot_json,
    mapping_editor_snapshot_payload,
)
from core.mapping.editor_validation import validate_mapping_editor_draft

__all__ = [
    "MappingEditorDraft",
    "MappingEditorExportResult",
    "MappingEditorGroup",
    "MappingEditorRow",
    "MappingEditorSaveResult",
    "MappingEditorValidationResult",
    "MappingAttributeDefinition",
    "MappingEntityCatalog",
    "MappingEntityDefinition",
    "MappingEntityRow",
    "MappingValidationError",
    "OWNED_RUNTIME_SECTIONS",
    "add_draft_row",
    "adapt_runtime_mapping_data",
    "condenser_identity",
    "condenser_requires_pi",
    "condenser_spec_key",
    "delete_draft_row",
    "duplicate_draft_row",
    "export_mapping_editor_snapshot_json",
    "load_runtime_mapping_editor_draft",
    "load_runtime_mapping_catalog",
    "project_runtime_mapping_to_editor_draft",
    "runtime_mapping_source_label",
    "runtime_mapping_from_editor_draft",
    "mapping_editor_snapshot_payload",
    "save_mapping_editor_draft",
    "set_draft_cell",
    "validate_mapping_editor_draft",
    "validate_mapping_entity_catalog",
]
