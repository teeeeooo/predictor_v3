"""Canonical Unified Feature contract models and bootstrap helpers."""

from core.data_definition.contract.bootstrap import bootstrap_manifest
from core.data_definition.contract.candidate import candidate_manifest_from_draft
from core.data_definition.contract.codec import dump_manifest, load_manifest, manifest_payload
from core.data_definition.contract.fingerprints import (
    ScopedFingerprints,
    scoped_fingerprints,
    semantic_generation_id,
    semantic_manifest_fingerprint,
    legacy_bundle_fingerprint_payload,
)
from core.data_definition.contract.model import (
    ContractGeneration,
    DerivedDefinition,
    FeatureDefinition,
    MappingRequirementDefinition,
    ModelGroupDefinition,
    LegacyOneHotCategoryDefinition,
    LegacyOneHotGroupDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    OrderingContract,
    TargetDefinition,
    UnifiedFeatureManifest,
    LegacyDerivedDefinition,
)
from core.data_definition.contract.compatibility import (
    CURRENT_CONTRACT_VERSION,
    LEGACY_CONTRACT_VERSION,
    ONE_HOT_LEGACY_CONTRACT_VERSION,
    current_derived_definitions,
    current_one_hot_definitions,
    migrate_manifest,
    operand_ml_name,
)
from core.data_definition.contract.projections import (
    ContractProjections,
    generate_projections,
    ml_csv_text,
    predict_csv_text,
    topological_derived_identities,
)
from core.data_definition.contract.validation import (
    ContractValidationIssue,
    require_valid_contract,
    validate_contract,
)

__all__ = [
    "ContractGeneration",
    "ContractProjections",
    "ContractValidationIssue",
    "DerivedDefinition",
    "LegacyDerivedDefinition",
    "LegacyOneHotCategoryDefinition",
    "LegacyOneHotGroupDefinition",
    "CURRENT_CONTRACT_VERSION",
    "LEGACY_CONTRACT_VERSION",
    "ONE_HOT_LEGACY_CONTRACT_VERSION",
    "FeatureDefinition",
    "MappingRequirementDefinition",
    "ModelGroupDefinition",
    "OneHotCategoryDefinition",
    "OneHotGroupDefinition",
    "OrderingContract",
    "ScopedFingerprints",
    "TargetDefinition",
    "UnifiedFeatureManifest",
    "bootstrap_manifest",
    "candidate_manifest_from_draft",
    "dump_manifest",
    "generate_projections",
    "load_manifest",
    "manifest_payload",
    "ml_csv_text",
    "predict_csv_text",
    "require_valid_contract",
    "scoped_fingerprints",
    "semantic_generation_id",
    "semantic_manifest_fingerprint",
    "legacy_bundle_fingerprint_payload",
    "topological_derived_identities",
    "validate_contract",
    "current_derived_definitions",
    "current_one_hot_definitions",
    "migrate_manifest",
    "operand_ml_name",
]
