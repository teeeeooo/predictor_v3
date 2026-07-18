"""Immutable DTOs for the canonical Unified Feature contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractGeneration:
    generation_id: str
    parent_generation_id: str = ""
    source: str = "repository_bootstrap"


@dataclass(frozen=True)
class FeatureDefinition:
    identity: str
    display_order: int
    column_key: str
    label: str
    role: str
    editor: str
    data_type: str
    visible: bool
    required: bool
    readonly: bool
    value_source: str
    mapping_entity: str = ""
    mapping_attribute: str = ""
    trigger_column: str = ""
    rule_id: str = ""
    model_input_enabled: bool = False
    ml_name: str = ""
    one_hot_group: str = ""
    active: bool = True
    notes: str = ""
    zero_fill_policy: str = "disallow"


@dataclass(frozen=True)
class LegacyDerivedDefinition:
    """Version-1 name-based DTO retained only for historical bundle reads."""

    identity: str
    ml_name: str
    operation: str
    numerator_ml_name: str
    denominator_ml_name: str
    zero_value: float = 0.0
    zero_fill_policy: str = "disallow"
    active: bool = True


@dataclass(frozen=True)
class DerivedDefinition:
    """Version-2 identity-based canonical Derived definition."""

    identity: str
    ml_name: str
    operation: str
    numerator_identity: str
    denominator_identity: str
    zero_denominator_policy: str = "constant"
    zero_value: float = 0.0
    zero_fill_policy: str = "disallow"
    active: bool = True


@dataclass(frozen=True)
class OneHotCategoryDefinition:
    identity: str
    source_value: str
    emitted_ml_name: str
    order: int
    active: bool = True


@dataclass(frozen=True)
class OneHotGroupDefinition:
    identity: str
    group_key: str
    selector_feature_identity: str
    category_source: str
    unknown_policy: str
    missing_policy: str
    categories: tuple[OneHotCategoryDefinition, ...]


@dataclass(frozen=True)
class TargetDefinition:
    identity: str
    feature_identity: str
    ml_name: str
    model_group_identity: str
    presentation_order: int
    active: bool = True


@dataclass(frozen=True)
class ModelGroupDefinition:
    identity: str
    registry_key: str
    name: str
    target_identities: tuple[str, ...]
    use_rfe: bool
    target_rules: tuple[tuple[str, str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class MappingRequirementDefinition:
    identity: str
    feature_identity: str
    mapping_entity: str
    mapping_attribute: str
    trigger_feature_identity: str
    rule_id: str
    data_type: str
    required: bool


@dataclass(frozen=True)
class OrderingContract:
    predict: tuple[str, ...]
    ml: tuple[str, ...]
    derived: tuple[str, ...]
    targets: tuple[str, ...]


@dataclass(frozen=True)
class UnifiedFeatureManifest:
    contract_version: str
    generation: ContractGeneration
    preprocessing_version: str
    features: tuple[FeatureDefinition, ...]
    derived: tuple[DerivedDefinition | LegacyDerivedDefinition, ...]
    one_hot_groups: tuple[OneHotGroupDefinition, ...]
    targets: tuple[TargetDefinition, ...]
    model_groups: tuple[ModelGroupDefinition, ...]
    mapping_requirements: tuple[MappingRequirementDefinition, ...]
    ordering: OrderingContract
