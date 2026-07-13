"""Read-only models for Arc 15A Data Definition reports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataDefinitionRow:
    """Normalized view of one active Predict Schema v2 row."""

    column_key: str
    label: str
    role: str
    value_source: str
    mapping_entity: str = ""
    mapping_attribute: str = ""
    trigger_column: str = ""
    rule_id: str = ""
    model_input_enabled: bool = False
    ml_name: str = ""
    one_hot_group: str = ""
    display_order: int = 0
    data_type: str = "string"
    required: bool = False


@dataclass(frozen=True)
class ProjectedFeatureRow:
    """Feature Catalog-compatible row projected from Data Definition state."""

    order: int
    ml_name: str
    role: str
    ui_key: str = ""
    label: str = ""
    source: str = ""
    mapping_key: str = ""
    one_hot_group: str = ""
    zero_fill_policy: str = "disallow"
    active: bool = True

    def comparison_key(self) -> tuple[object, ...]:
        """Return fields that participate in Arc 15A parity checks."""
        return (
            self.order,
            self.ml_name,
            self.role,
            self.ui_key,
            self.label,
            self.source,
            self.mapping_key,
            self.one_hot_group,
            self.zero_fill_policy,
            self.active,
        )


@dataclass(frozen=True)
class DerivedFeatureDefinition:
    """Explicit policy row for a derived ML feature."""

    ml_name: str
    zero_fill_policy: str = "disallow"
    active: bool = True


@dataclass(frozen=True)
class MappingRequirement:
    """Mapping lookup requirement declared by Data Definition."""

    column_key: str
    ml_name: str
    mapping_entity: str
    mapping_attribute: str
    trigger_column: str
    rule_id: str = ""
    data_type: str = "string"
    required: bool = True


@dataclass(frozen=True)
class OneHotRelationship:
    """Relationship between one selector and emitted ML feature names."""

    selector_column: str
    one_hot_group: str
    emitted_ml_names: tuple[str, ...]
    catalog_ml_names: tuple[str, ...] = ()
