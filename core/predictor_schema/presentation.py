"""Presentation metadata shared by predictor schema projections."""

from __future__ import annotations


ROLE_PRESENTATION_DEFAULTS = {
    "input": {"width": 90, "bg_color": "#FFFFFF"},
    "auto": {"width": 90, "bg_color": "#F2F2F2"},
    "result": {"width": 100, "bg_color": "#E6F3E6"},
}

WIDTH_OVERRIDES = {
    "idu": 120,
    "evap_index": 100,
    "odu": 120,
    "fin_type": 80,
    "pi": 60,
    "row": 60,
    "compressor": 120,
    "ref_type": 80,
    "exp_type": 80,
    "comp_eer": 80,
    "comp_cc": 80,
    "ref_qty": 80,
    "cspf": 110,
    "hspf2": 110,
}


def presentation_metadata(column_key: str, role: str) -> dict[str, object]:
    """Return current predictor table presentation metadata for one column."""
    metadata = dict(ROLE_PRESENTATION_DEFAULTS[role])
    if column_key in WIDTH_OVERRIDES:
        metadata["width"] = WIDTH_OVERRIDES[column_key]
    return metadata
