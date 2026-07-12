"""Regression guards for Calculator table presentation tone corrections."""

from __future__ import annotations

import csv
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
    assert surface._status_label.semantic_tone == "pending"
    assert surface._status_cell.semantic_tone == "pending"
    assert surface._status_cell.cget("background") == surface._status_label.cget(
        "background"
    )
    assert surface._status_cell.semantic_background == surface._status_cell.cget(
        "background"
    )
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


def _scop_section(tk_root):
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection

    section = En14825ScopSection(tk_root)
    section._auto_calc.cancel()
    return section


def _complete_scop_summary():
    from apps.calculator.application.en14825.scop_models import ScopResultSummary

    return ScopResultSummary(
        declared_scop=3.2,
        declared_qh_kwh=1000.0,
        declared_total_kwh=312.5,
        tested_scop=3.1,
        tested_qh_kwh=1000.0,
        tested_total_kwh=322.6,
        scop_percent=96.9,
        status_code="complete",
    )


def test_scop_result_actions_export_single_visible_climate_from_surface(
    tk_root, monkeypatch, tmp_path
) -> None:
    section = _scop_section(tk_root)
    section._result_surfaces["average"].update(_complete_scop_summary())

    section.copy_button.invoke()
    copied = tk_root.clipboard_get()
    assert copied.startswith("Average\n구분\tSCOP\tQH [kWh]\tTotal [kWh]\tSCOP %")
    assert "Declared\t3.20\t1000.0\t312.5\t-" in copied
    assert "Status\t자동 계산 완료" in copied
    assert "Warmer" not in copied and "Colder" not in copied
    assert "Bin No." not in copied

    path = tmp_path / "scop.csv"

    def choose_path(**kwargs):
        assert kwargs["initialfile"] == "en14825_scop_result.csv"
        return str(path)

    monkeypatch.setattr(
        "apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",
        choose_path,
    )
    section.export_button.invoke()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["Average"]
    assert rows[1] == ["구분", "SCOP", "QH [kWh]", "Total [kWh]", "SCOP %"]
    assert rows[-1] == ["Status", "자동 계산 완료"]


def test_scop_invalid_transition_exports_visible_status_without_stale_values(
    tk_root,
) -> None:
    section = _scop_section(tk_root)
    surface = section._result_surfaces["average"]
    surface.update(_complete_scop_summary())
    surface.show_invalid("입력 오류: 숫자 입력을 확인하세요.")

    rows = section.sectioned_csv_rows()
    assert rows == (
        ("Average",),
        ("Status", "입력 오류: 숫자 입력을 확인하세요."),
    )
    section.copy_button.invoke()
    copied = tk_root.clipboard_get()
    assert "No results" not in copied
    assert "3.20" not in copied
    assert "입력 오류: 숫자 입력을 확인하세요." in copied

    surface.update(_complete_scop_summary())
    assert "3.20" in "\n".join("\t".join(row) for row in section.sectioned_csv_rows())


def test_scop_mixed_active_climates_preserve_visible_order_and_status(tk_root) -> None:
    section = _scop_section(tk_root)
    section._result_surfaces["average"].update(_complete_scop_summary())
    section.climate_active_vars["warmer"].set(True)
    section._result_surfaces["warmer"].show_invalid("입력 오류")

    rows = section.sectioned_csv_rows()
    assert rows[0] == ("Average",)
    assert ("Warmer",) in rows
    assert rows.index(("Average",)) < rows.index(("Warmer",))
    assert ("Status", "입력 오류") in rows
    assert ("Colder",) not in rows


def test_scop_warning_pending_and_active_transitions_use_current_surface(tk_root) -> None:
    section = _scop_section(tk_root)
    section._result_surfaces["average"].update(_complete_scop_summary())
    section._result_surfaces["average"].show_error("surface failure")
    section.climate_active_vars["warmer"].set(True)
    section._result_surfaces["warmer"].clear()

    rows = section.sectioned_csv_rows()
    assert ("Status", "기류/설정 오류: surface failure") in rows
    assert ("Status", "대기 중") in rows
    assert "3.20" not in str(rows)
    assert "PASS" not in str(rows) and "FAIL" not in str(rows)

    section.climate_active_vars["average"].set(False)
    section._on_climate_toggle()
    section._auto_calc.cancel()
    rows = section.sectioned_csv_rows()
    assert ("Average",) not in rows and rows[0] == ("Warmer",)

    section.climate_active_vars["average"].set(True)
    section._on_climate_toggle()
    section._auto_calc.cancel()
    rows = section.sectioned_csv_rows()
    assert rows[0] == ("Average",)
    assert ("Status", "대기 중") in rows
    assert ("Status", "기류/설정 오류: surface failure") not in rows

    section._result_surfaces["average"].show_invalid("입력 오류")
    rows = section.sectioned_csv_rows()
    assert ("Status", "입력 오류") in rows
    assert ("Status", "대기 중") in rows


def test_scop_complete_deactivate_reactivate_clears_only_target_climate(
    tk_root,
) -> None:
    section = _scop_section(tk_root)
    average = section._result_surfaces["average"]
    warmer = section._result_surfaces["warmer"]
    average.update(_complete_scop_summary())
    section.climate_active_vars["warmer"].set(True)
    warmer.update(_complete_scop_summary())
    section.input_tables["warmer"].set_value("declared_capacity_B", "4321")

    assert "3.20" in str(section.sectioned_csv_rows())
    section.climate_active_vars["warmer"].set(False)
    section._on_climate_toggle()
    section._auto_calc.cancel()
    assert ("Warmer",) not in section.sectioned_csv_rows()
    assert section.input_tables["warmer"].get_text_values()[
        "declared_capacity_B"
    ] == "4321"

    section.climate_active_vars["warmer"].set(True)
    section._on_climate_toggle()
    section._auto_calc.cancel()
    rows = section.sectioned_csv_rows()
    assert rows[0] == ("Average",)
    assert rows.index(("Average",)) < rows.index(("Warmer",))
    warmer_index = rows.index(("Warmer",))
    assert rows[warmer_index + 1] == ("Status", "대기 중")
    assert rows.count(("Status", "자동 계산 완료")) == 1
    assert warmer.visible_snapshot().has_result_values is False

    latest = _complete_scop_summary()
    latest.tested_scop = 2.9
    warmer.update(latest)
    rows = section.sectioned_csv_rows()
    assert any(row[:2] == ("Tested", "2.90") for row in rows)


@pytest.mark.parametrize(
    "show_stale,stale_text",
    [
        (lambda surface: surface.show_invalid("입력 오류"), "입력 오류"),
        (
            lambda surface: surface.show_error("surface failure"),
            "기류/설정 오류: surface failure",
        ),
    ],
)
def test_scop_error_deactivate_reactivate_resets_to_pending(
    tk_root, show_stale, stale_text
) -> None:
    section = _scop_section(tk_root)
    section.climate_active_vars["warmer"].set(True)
    surface = section._result_surfaces["warmer"]
    show_stale(surface)

    section.climate_active_vars["warmer"].set(False)
    section._on_climate_toggle()
    section.climate_active_vars["warmer"].set(True)
    section._on_climate_toggle()
    section._auto_calc.cancel()

    rows = section.sectioned_csv_rows()
    assert ("Status", "대기 중") in rows
    assert stale_text not in str(rows)
    assert surface.visible_snapshot().has_result_values is False


def test_scop_result_csv_cancel_is_noop(tk_root, monkeypatch) -> None:
    section = _scop_section(tk_root)
    monkeypatch.setattr(
        "apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",
        lambda **_kwargs: "",
    )

    assert section.export_button.invoke() == 0
