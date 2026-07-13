"""Fixed column layout owned by the legacy mapping bootstrap adapter."""

from __future__ import annotations

from dataclasses import dataclass

from core.mapping.editor_projection import (
    COMPRESSOR_GROUP,
    EVAP_INDEX_GROUP,
    EXPANSION_GROUP,
    IDU_GROUP,
    ODU_GROUP,
    REFRIGERANT_GROUP,
)


EXPECTED_HEADERS = (
    "Compressor",
    "EER",
    "cc",
    "",
    "Size",
    "Evap Index",
    "Evap area",
    "Evap Volume",
    "",
    "IDU",
    "Volume",
    "Size",
    "",
    "ODU",
    "Volume",
    "",
    "ODU",
    "Fin type",
    "Pi",
    "Row",
    "Cond Index",
    "Cond Area",
    "Cond Volume",
    "",
    "Ref type",
    "",
    "Exp type",
)


@dataclass(frozen=True)
class LegacyBlock:
    group_key: str
    label: str
    columns: tuple[str, ...]
    indexes: tuple[int, ...]
    numeric_columns: tuple[str, ...] = ()
    runtime_sections: tuple[str, ...] = ()


LEGACY_BLOCKS = (
    LegacyBlock(
        IDU_GROUP,
        "IDU",
        ("IDU", "ID Volume", "Size"),
        (9, 10, 11),
        ("ID Volume",),
        ("idu",),
    ),
    LegacyBlock(
        EVAP_INDEX_GROUP,
        "Evap Index",
        ("Evap Index", "Size", "Evap Area", "Evap Volume"),
        (5, 4, 6, 7),
        ("Evap Area", "Evap Volume"),
        ("evap_index",),
    ),
    LegacyBlock(
        ODU_GROUP,
        "ODU",
        ("ODU", "OD Volume"),
        (13, 14),
        ("OD Volume",),
        ("odu",),
    ),
    LegacyBlock(
        COMPRESSOR_GROUP,
        "Compressor",
        ("Compressor", "Comp EER", "Comp cc"),
        (0, 1, 2),
        ("Comp EER", "Comp cc"),
        ("compressor",),
    ),
    LegacyBlock(
        REFRIGERANT_GROUP,
        "Refrigerant",
        ("Refrigerant",),
        (24,),
        runtime_sections=("ref_type",),
    ),
    LegacyBlock(
        EXPANSION_GROUP,
        "Expansion",
        ("Expansion",),
        (26,),
        runtime_sections=("exp_type",),
    ),
)
