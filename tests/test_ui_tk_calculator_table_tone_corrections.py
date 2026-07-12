"""Regression guards for Calculator table presentation tone corrections."""

from __future__ import annotations

import pytest

from tests.helpers.tk import destroy_tk_root


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        destroy_tk_root(root)


def _tones(surface) -> dict[tuple[str, str], str]:
    return {
        position: label.semantic_tone
        for position, label in surface.value_labels.items()
    }


def test_scop_compact_result_uses_per_cell_tones_and_preserves_values(tk_root) -> None:
    from apps.calculator.application.en14825.scop_models import ScopResultSummary
    from apps.calculator.ui.sections.en14825_scop_result_surface import (
        ScopResultSurface,
    )

    surface = ScopResultSurface(tk_root)
    assert {label.semantic_tone for label in surface.row_header_labels.values()} == {
        "default"
    }
    assert set(_tones(surface).values()) == {"pending"}
    assert surface._status_label.semantic_tone == "pending"

    surface.update(
        ScopResultSummary(
            declared_scop=3.21,
            declared_qh_kwh=123.45,
            declared_total_kwh=45.67,
            status_code="complete",
        )
    )
    tones = _tones(surface)
    assert tones[("Declared", "SCOP")] == "calculated"
    assert tones[("Declared", "QH [kWh]")] == "calculated"
    assert tones[("Tested", "SCOP")] == "pending"
    assert surface._status_label.semantic_tone == "default"

    surface.update(
        ScopResultSummary(
            tested_scop=3.11,
            tested_qh_kwh=111.14,
            tested_total_kwh=35.62,
            status_code="complete",
        )
    )
    tones = _tones(surface)
    assert tones[("Declared", "SCOP")] == "pending"
    assert tones[("Tested", "SCOP")] == "calculated"

    surface.update(
        ScopResultSummary(
            declared_scop=3.21,
            declared_qh_kwh=123.45,
            declared_total_kwh=45.67,
            tested_scop=3.11,
            tested_qh_kwh=111.14,
            tested_total_kwh=35.62,
            scop_percent=None,
            status_code="complete",
        )
    )
    assert surface.value_labels[("Declared", "SCOP")].cget("text") == "3.21"
    assert surface.value_labels[("Tested", "QH [kWh]")].cget("text") == "111.1"
    assert _tones(surface)[("Tested", "SCOP %")] == "pending"
    assert {label.semantic_tone for label in surface.row_header_labels.values()} == {
        "default"
    }


def test_scop_status_tone_updates_container_and_label_and_clears_stale_values(
    tk_root,
) -> None:
    from apps.calculator.application.en14825.scop_models import ScopResultSummary
    from apps.calculator.ui.sections.en14825_scop_result_surface import (
        ScopResultSurface,
    )

    surface = ScopResultSurface(tk_root)
    surface.update(ScopResultSummary(declared_scop=3.2, status_code="complete"))
    surface.update(ScopResultSummary(status_code="invalid_climate"))
    assert surface._status_label.semantic_tone == "invalid"
    assert surface._status_cell.semantic_tone == "invalid"
    assert surface._status_cell.cget("background") == surface._status_label.cget(
        "background"
    )

    surface.show_invalid("입력 오류")
    assert surface._status_label.semantic_tone == "invalid"
    surface.update(ScopResultSummary(status_code="declared_error"))
    assert surface._status_label.semantic_tone == "warning"
    surface.show_error("surface failure")
    assert surface._status_label.semantic_tone == "warning"
    assert set(_tones(surface).values()) == {"pending"}


@pytest.mark.parametrize("status,tone", [
    ("입력 대기", "pending"),
    ("입력 오류: 숫자 입력을 확인하세요.", "invalid"),
    ("guide 계산 오류", "warning"),
])
def test_korea_midpoint_status_tone_is_explicit(tk_root, status: str, tone: str) -> None:
    from apps.calculator.ui.sections.korea_midpoint_guide_table import (
        KoreaMidpointGuideTable,
    )
    from apps.calculator.ui.table.visual_policy import SemanticTone

    guide = KoreaMidpointGuideTable(tk_root)
    guide.set_status(status, tone=SemanticTone(tone))
    assert guide.table.text_at_address(("current_tc", "value")) == status
    assert guide.table.value_labels[(0, 0)].semantic_tone == "default"
    assert guide.table.value_labels[(0, 1)].semantic_tone == tone
    assert guide.table.value_labels[(1, 1)].semantic_tone == "pending"
    assert guide.table.value_labels[(2, 1)].semantic_tone == "pending"


def test_korea_midpoint_normal_values_are_calculated_and_missing_is_pending(
    tk_root,
) -> None:
    from apps.calculator.ui.sections.korea_midpoint_guide_table import (
        KoreaMidpointGuideTable,
    )

    guide = KoreaMidpointGuideTable(tk_root)
    guide.set_values((("current_tc", "0.50"), ("recommended_tc", "-")))
    assert guide.table.value_labels[(0, 0)].semantic_tone == "default"
    assert guide.table.value_labels[(0, 1)].semantic_tone == "calculated"
    assert guide.table.value_labels[(1, 1)].semantic_tone == "pending"
    assert guide.table.text_at_address(("current_tc", "value")) == "0.50"


def test_treeview_style_resolves_custom_shared_policy_without_global_style_name(
    tk_root,
) -> None:
    from tkinter import ttk

    from apps.calculator.ui.table.treeview_style import apply_treeview_style
    from apps.calculator.ui.table.visual_policy import TkTableVisualPolicy

    tree = ttk.Treeview(tk_root)
    style_name = "ToneCorrectionCustom.Treeview"
    policy = TkTableVisualPolicy(
        body_background="#101112",
        header_background="#202122",
        header_foreground="#f1f2f3",
        divider_color="#303132",
        selected_background="#404142",
        body_font=("TkDefaultFont", 9),
        header_font=("TkDefaultFont", 10, "bold"),
        cell_padx=7,
        cell_pady=3,
        header_pady=5,
    )
    binding = apply_treeview_style(tree, style_name=style_name, policy=policy)
    style = ttk.Style(tk_root)

    assert style.lookup(style_name, "background") == "#101112"
    assert style.lookup(binding.heading_style_name, "background") == "#202122"
    assert style.lookup(style_name, "bordercolor") == "#303132"
    assert ("selected", "#404142") in style.map(style_name, "background")
    assert tree.outer_edge_policy == "flat_low_contrast"
