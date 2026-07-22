"""Versioned canonical and historical One-hot contract DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegacyOneHotCategoryDefinition:
    """Version-2 name-based One-hot category retained for historical reads."""

    identity: str
    source_value: str
    emitted_ml_name: str
    order: int
    active: bool = True


@dataclass(frozen=True)
class OneHotCategoryDefinition:
    """Stable category-to-emitted-Feature relation used by contract v3."""

    identity: str
    source_value: str
    emitted_feature_identity: str
    emitted_ml_name: str
    order: int
    active: bool = True
    provider_category_identity: str = ""


@dataclass(frozen=True)
class OneHotSelectorRestore:
    """Exact ordinary Feature shape reserved before selector takeover."""

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
class LegacyOneHotGroupDefinition:
    """Version-2 One-hot group shape retained for byte-compatible reads."""

    identity: str
    group_key: str
    selector_feature_identity: str
    category_source: str
    unknown_policy: str
    missing_policy: str
    categories: tuple[LegacyOneHotCategoryDefinition, ...]


@dataclass(frozen=True)
class OneHotGroupDefinition:
    identity: str
    group_key: str
    selector_feature_identity: str
    category_source: str
    unknown_policy: str
    missing_policy: str
    categories: tuple[OneHotCategoryDefinition | LegacyOneHotCategoryDefinition, ...]
    source_binding: str = ""
    active: bool = True
    selector_restore: OneHotSelectorRestore | None = None

    @property
    def source_mode(self) -> str:
        """Return the explicit mutation-owner mode without changing the v2 key."""
        return self.category_source
