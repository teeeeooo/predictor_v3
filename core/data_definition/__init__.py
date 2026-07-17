"""Qt-free Data Definition projection and validation helpers."""

from core.data_definition.model import (
    DataDefinitionRow,
    DerivedFeatureDefinition,
    MappingRequirement,
    OneHotRelationship,
    ProjectedFeatureRow,
)
from core.data_definition.report_model import (
    DataDefinitionIssue,
    DataDefinitionReport,
    ReadinessCheck,
)
from core.data_definition.draft import (
    DataDefinitionDraft,
    DataDefinitionDraftChange,
    DataDefinitionDraftIssue,
    DataDefinitionDraftRow,
    build_data_definition_draft,
)
from core.data_definition.edit_policy import FieldEditability, field_editability
from core.data_definition.save_contract import (
    DataDefinitionRestartImpact,
    DataDefinitionSaveBlocker,
    DataDefinitionSavePlan,
    DataDefinitionWriteTarget,
    build_data_definition_save_plan,
)
from core.data_definition.schema_writer import (
    DataDefinitionSchemaSaveResult,
    DataDefinitionSchemaWritePreview,
    save_data_definition_schema_draft,
    schema_csv_rows_from_draft,
)
from core.data_definition.validation import build_data_definition_report
from core.data_definition.projection import extract_mapping_requirements_from_draft
from core.data_definition.command_contract import (
    MAPPING_LOOKUP_TEMPLATES,
    MappingLookupTemplate,
    mapping_template,
    mapping_template_for_relation,
    normalize_column_key,
)
from core.data_definition.command_types import (
    AddDefinitionIntent,
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
    EditDefinitionIntent,
)
from core.data_definition.feature_command_types import (
    FeatureCommandIntent,
    DuplicateDefinitionIntent,
    MoveDefinitionIntent,
    RemoveDefinitionIntent,
    RenameDefinitionIntent,
    SetDefinitionActiveIntent,
)
from core.data_definition.commands import (
    apply_add_definition_command,
    apply_edit_definition_command,
)
from core.data_definition.mutation_commands import (
    apply_duplicate_definition_command,
    apply_remove_definition_command,
    apply_set_definition_active_command,
)
from core.data_definition.rename_command import apply_rename_definition_command
from core.data_definition.ordering_commands import apply_move_definition_command
from core.data_definition.impact_preview import (
    FeatureImpactPreview,
    build_feature_impact_preview,
)
from core.data_definition.dependency_policy import is_supported_basic_feature

__all__ = [
    "DataDefinitionDraft",
    "AddDefinitionIntent",
    "DataDefinitionCommandIssue",
    "DataDefinitionCommandResult",
    "FeatureCommandIntent",
    "FeatureImpactPreview",
    "DataDefinitionDraftChange",
    "DataDefinitionDraftIssue",
    "DataDefinitionDraftRow",
    "DataDefinitionIssue",
    "DataDefinitionReport",
    "DataDefinitionRow",
    "DataDefinitionRestartImpact",
    "DataDefinitionSaveBlocker",
    "DataDefinitionSavePlan",
    "DataDefinitionSchemaSaveResult",
    "DataDefinitionSchemaWritePreview",
    "DerivedFeatureDefinition",
    "DataDefinitionWriteTarget",
    "FieldEditability",
    "EditDefinitionIntent",
    "DuplicateDefinitionIntent",
    "MoveDefinitionIntent",
    "RemoveDefinitionIntent",
    "RenameDefinitionIntent",
    "SetDefinitionActiveIntent",
    "MAPPING_LOOKUP_TEMPLATES",
    "MappingLookupTemplate",
    "MappingRequirement",
    "OneHotRelationship",
    "ProjectedFeatureRow",
    "ReadinessCheck",
    "build_data_definition_draft",
    "build_data_definition_report",
    "build_data_definition_save_plan",
    "apply_add_definition_command",
    "apply_edit_definition_command",
    "apply_duplicate_definition_command",
    "apply_remove_definition_command",
    "apply_rename_definition_command",
    "apply_set_definition_active_command",
    "apply_move_definition_command",
    "build_feature_impact_preview",
    "is_supported_basic_feature",
    "field_editability",
    "extract_mapping_requirements_from_draft",
    "mapping_template",
    "mapping_template_for_relation",
    "normalize_column_key",
    "save_data_definition_schema_draft",
    "schema_csv_rows_from_draft",
]
