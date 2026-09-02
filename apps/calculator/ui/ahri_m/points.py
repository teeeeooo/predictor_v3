"""UI-only Appendix M cooling/heating point labels."""

from __future__ import annotations

from types import MappingProxyType

AHRI_M_SEER_UI_POINT_LABELS = MappingProxyType({"EV": "Ev"})
AHRI_M_HSPF_UI_POINT_LABELS = MappingProxyType(
    {
        "H2V": "H2v",
        "H1N": "H1N(STD)",
    }
)


def ahri_m_seer_ui_point_label(point: str) -> str:
    return AHRI_M_SEER_UI_POINT_LABELS.get(point, point)


def ahri_m_hspf_ui_point_label(point: str) -> str:
    return AHRI_M_HSPF_UI_POINT_LABELS.get(point, point)
