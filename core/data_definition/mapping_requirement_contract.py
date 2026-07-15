"""Resolve Data Definition requirements into stable mapping-cell contracts."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.model import MappingRequirement

MAPPING_ENTITY_GROUP_ALIASES = {
    "cond_specs": "odu_cond_specs",
    "ref_type": "refrigerant",
    "exp_type": "expansion",
}
SUPPORTED_MAPPING_DATA_TYPES = frozenset({"string", "number", "boolean"})


@dataclass(frozen=True)
class EffectiveMappingRequirement:
    """One compatible contract shared by every definition for a mapping cell."""

    resolved_group_key: str
    mapping_attribute: str
    mapping_entity: str
    trigger_column: str
    rule_id: str
    data_type: str
    required: bool
    definition_column_keys: tuple[str, ...]
    ml_names: tuple[str, ...] = ()
    model_input_enabled: bool = False

    @property
    def column_key(self) -> str:
        """Return the deterministic primary definition identity."""
        return self.definition_column_keys[0] if self.definition_column_keys else ""


@dataclass(frozen=True)
class MappingRequirementConflict:
    """Incompatible source definitions that claim one resolved mapping cell."""

    resolved_group_key: str
    mapping_attribute: str
    definition_column_keys: tuple[str, ...]
    mapping_entities: tuple[str, ...]
    data_types: tuple[str, ...]
    relation_signatures: tuple[tuple[str, str], ...]
    reasons: tuple[str, ...]

    @property
    def message(self) -> str:
        """Return a deterministic concise conflict explanation."""
        definitions = ", ".join(self.definition_column_keys) or "<unknown>"
        details: list[str] = []
        if "data_type" in self.reasons:
            details.append(f"data types [{', '.join(self.data_types)}]")
        if "unsupported_data_type" in self.reasons:
            details.append(f"unsupported data types [{', '.join(self.data_types)}]")
        if "relation" in self.reasons:
            relations = ", ".join(
                f"{trigger or '<blank>'}/{rule or '<blank>'}"
                for trigger, rule in self.relation_signatures
            )
            details.append(f"relations [{relations}]")
        detail = "; ".join(details) or "incompatible declarations"
        return (
            "Mapping Requirement contract conflict for "
            f"{self.resolved_group_key}.{self.mapping_attribute} across definitions "
            f"[{definitions}]: {detail}."
        )


@dataclass(frozen=True)
class MappingRequirementContractResolution:
    """Compatible effective contracts plus conflicts excluded from projection."""

    contracts: tuple[EffectiveMappingRequirement, ...] = ()
    conflicts: tuple[MappingRequirementConflict, ...] = ()


def mapping_group_key_for_requirement(requirement: object) -> str:
    """Return the canonical editor group for one mapping requirement."""
    entity = _text(getattr(requirement, "mapping_entity", ""))
    return MAPPING_ENTITY_GROUP_ALIASES.get(entity, entity)


def resolve_mapping_requirement_contracts(
    requirements: tuple[MappingRequirement, ...] | tuple[object, ...],
) -> MappingRequirementContractResolution:
    """Aggregate compatible definitions by resolved group and attribute."""
    grouped: dict[tuple[str, str], list[object]] = {}
    for requirement in requirements:
        group_key = mapping_group_key_for_requirement(requirement)
        attribute = _text(getattr(requirement, "mapping_attribute", ""))
        if group_key and attribute:
            grouped.setdefault((group_key, attribute), []).append(requirement)

    contracts: list[EffectiveMappingRequirement] = []
    conflicts: list[MappingRequirementConflict] = []
    for (group_key, attribute), sources in grouped.items():
        ordered = tuple(sorted(sources, key=_requirement_sort_key))
        definition_keys = tuple(
            dict.fromkeys(_text(getattr(item, "column_key", "")) for item in ordered)
        )
        entities = tuple(
            sorted({_text(getattr(item, "mapping_entity", "")) for item in ordered})
        )
        data_types = tuple(
            sorted(
                {
                    _text(getattr(item, "data_type", "string")) or "string"
                    for item in ordered
                }
            )
        )
        relations = tuple(
            sorted(
                {
                    (
                        _text(getattr(item, "trigger_column", "")),
                        _text(getattr(item, "rule_id", "")),
                    )
                    for item in ordered
                }
            )
        )
        reasons: list[str] = []
        if len(data_types) > 1:
            reasons.append("data_type")
        if any(data_type not in SUPPORTED_MAPPING_DATA_TYPES for data_type in data_types):
            reasons.append("unsupported_data_type")
        if len(relations) > 1:
            reasons.append("relation")
        if reasons:
            conflicts.append(
                MappingRequirementConflict(
                    resolved_group_key=group_key,
                    mapping_attribute=attribute,
                    definition_column_keys=definition_keys,
                    mapping_entities=entities,
                    data_types=data_types,
                    relation_signatures=relations,
                    reasons=tuple(reasons),
                )
            )
            continue
        contracts.append(
            EffectiveMappingRequirement(
                resolved_group_key=group_key,
                mapping_attribute=attribute,
                mapping_entity=entities[0] if entities else group_key,
                trigger_column=relations[0][0],
                rule_id=relations[0][1],
                data_type=data_types[0],
                required=any(bool(getattr(item, "required", True)) for item in ordered),
                definition_column_keys=definition_keys,
                ml_names=tuple(
                    sorted(
                        {
                            _text(getattr(item, "ml_name", ""))
                            for item in ordered
                            if _text(getattr(item, "ml_name", ""))
                        }
                    )
                ),
                model_input_enabled=any(
                    bool(getattr(item, "model_input_enabled", False))
                    for item in ordered
                ),
            )
        )
    return MappingRequirementContractResolution(tuple(contracts), tuple(conflicts))


def _requirement_sort_key(requirement: object) -> tuple[str, ...]:
    return (
        _text(getattr(requirement, "column_key", "")),
        _text(getattr(requirement, "mapping_entity", "")),
        _text(getattr(requirement, "trigger_column", "")),
        _text(getattr(requirement, "rule_id", "")),
        _text(getattr(requirement, "data_type", "string")) or "string",
    )


def _text(value: object) -> str:
    return str(value or "").strip()
