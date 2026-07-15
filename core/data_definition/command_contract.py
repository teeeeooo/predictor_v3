"""Supported identity and mapping contracts for Data Definition commands."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MappingLookupTemplate:
    """One current schema/mapping relation supported by controlled commands."""

    key: str
    label: str
    mapping_entity: str
    trigger_column: str
    rule_id: str = ""


MAPPING_LOOKUP_TEMPLATES = (
    MappingLookupTemplate("idu_lookup", "IDU", "idu", "idu"),
    MappingLookupTemplate("evap_index_lookup", "Evap Index", "evap_index", "evap_index"),
    MappingLookupTemplate("odu_lookup", "ODU", "odu", "odu"),
    MappingLookupTemplate("compressor_lookup", "Compressor", "compressor", "compressor"),
    MappingLookupTemplate("refrigerant_lookup", "Refrigerant", "ref_type", "ref_type"),
    MappingLookupTemplate("expansion_lookup", "Expansion", "exp_type", "exp_type"),
    MappingLookupTemplate(
        "cond_specs_lookup",
        "ODU Cond Specs",
        "cond_specs",
        "odu",
        "cond_specs_lookup",
    ),
)


def normalize_column_key(value: object) -> str:
    """Return the deterministic snake-case identity used by Add commands."""
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().casefold()).strip("_")
    return re.sub(r"_+", "_", normalized)


def mapping_template(template_key: str) -> MappingLookupTemplate | None:
    """Return a supported lookup template by stable template key."""
    return next((item for item in MAPPING_LOOKUP_TEMPLATES if item.key == template_key), None)


def mapping_template_for_relation(
    mapping_entity: str,
    trigger_column: str,
    rule_id: str,
) -> MappingLookupTemplate | None:
    """Resolve an exact current entity/trigger/rule relation."""
    relation = (mapping_entity.strip(), trigger_column.strip(), rule_id.strip())
    return next(
        (
            item
            for item in MAPPING_LOOKUP_TEMPLATES
            if (item.mapping_entity, item.trigger_column, item.rule_id) == relation
        ),
        None,
    )
