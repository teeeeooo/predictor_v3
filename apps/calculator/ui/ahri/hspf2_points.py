"""UI-only AHRI HSPF2 point display order and labels."""

from __future__ import annotations

from types import MappingProxyType

AHRI_HSPF2_UI_POINT_ORDER = (
    "H01",
    "H11",
    "H2Int",
    "H32",
    "H42",
    "H1N",
    "H12",
    "H22",
)
AHRI_HSPF2_UI_POINT_LABELS = MappingProxyType(
    {
        "H2Int": "H2v",
        "H1N": "H1N(STD)",
    }
)


def ahri_hspf2_ui_point_label(point: str) -> str:
    return AHRI_HSPF2_UI_POINT_LABELS.get(point, point)
