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
from core.data_definition.commands import (
    apply_add_definition_command,
    apply_edit_definition_command,
)

__all__ = [
    "DataDefinitionDraft",
    "AddDefinitionIntent",
    "DataDefinitionCommandIssue",
    "DataDefinitionCommandResult",
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
    "field_editability",
    "extract_mapping_requirements_from_draft",
    "mapping_template",
    "mapping_template_for_relation",
    "normalize_column_key",
    "save_data_definition_schema_draft",
    "schema_csv_rows_from_draft",
]
