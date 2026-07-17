"""Canonical Unified Feature contract models and bootstrap helpers."""

from core.data_definition.contract.bootstrap import bootstrap_manifest
from core.data_definition.contract.codec import dump_manifest, load_manifest, manifest_payload
from core.data_definition.contract.model import (
    ContractGeneration,
    DerivedDefinition,
    FeatureDefinition,
    MappingRequirementDefinition,
    ModelGroupDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    OrderingContract,
    TargetDefinition,
    UnifiedFeatureManifest,
)

__all__ = [
    "ContractGeneration",
    "DerivedDefinition",
    "FeatureDefinition",
    "MappingRequirementDefinition",
    "ModelGroupDefinition",
    "OneHotCategoryDefinition",
    "OneHotGroupDefinition",
    "OrderingContract",
    "TargetDefinition",
    "UnifiedFeatureManifest",
    "bootstrap_manifest",
    "dump_manifest",
    "load_manifest",
    "manifest_payload",
]
