"""Calculator profile empty-state contracts after sample-prefill removal."""

from __future__ import annotations

import pytest

from tests.helpers.tk import destroy_tk_root, make_hidden_root


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = make_hidden_root()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    try:
        yield root
    finally:
        destroy_tk_root(root)


def _assert_blank(values: dict[str, str]) -> None:
    assert values
    assert all(not value.strip() for value in values.values())


def test_en14825_profiles_keep_options_but_start_without_performance_data(
    tk_root,
) -> None:
    from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection
    from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection

    seer = En14825SeerSection(tk_root)
    assert seer.design_table.get_text_values() == {
        "p_design_c": "",
        "t_design_c": "35.0",
        "cd": "0.25",
    }
    _assert_blank(seer.input_table.get_text_values())
    assert seer._detail_status.startswith("\uc785\ub825 \ub300\uae30")
    assert not seer.result_panel.summary_tables

    scop = En14825ScopSection(tk_root)
    assert scop.cd_table.get_text_values() == {"cd": "0.25"}
    assert scop._appliance_type_var.get() == "reversible"
    assert scop.climate_active_vars["average"].get() is True
    for climate in scop.climates:
        assert scop.p_design_h_vars[climate].get() == ""
        _assert_blank(scop.input_tables[climate].get_text_values())
    assert scop._detail_status.startswith("\uc785\ub825 \ub300\uae30")
    assert not scop.result_panel.summary_tables


def test_ahri_profiles_keep_options_but_start_without_performance_data(
    tk_root,
) -> None:
    from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section
    from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section

    seer2 = AhriSeer2Section(tk_root)
    assert seer2.type_var.get() == "HP"
    _assert_blank(seer2.input_table.get_text_values())
    assert seer2._detail_status == "\uc785\ub825 \ub300\uae30"
    assert not seer2.result_panel.summary_tables

    hspf2 = AhriHspf2Section(tk_root)
    assert hspf2.region_var.get() == "IV"
    assert hspf2.h42_var.get() is True
    assert hspf2.h12_var.get() is False
    assert hspf2.h22_var.get() is False
    assert hspf2.minimum_speed_var.get() is True
    assert hspf2.numeric_table.get_text_values() == {
        "cd": "0.25",
        "defrost_credit": "1.0",
        "cut_out_c": "-40.0",
        "cut_in_c": "-40.0",
    }
    _assert_blank(hspf2.a2_table.get_text_values())
    _assert_blank(hspf2.heating_table.get_text_values())
    assert hspf2._detail_status == "\uc785\ub825 \ub300\uae30"
    assert not hspf2.result_panel.summary_tables


def test_iso_hong_kong_and_saso_profiles_start_in_input_waiting_state(
    tk_root,
) -> None:
    from apps.calculator.ui.sections.hong_kong_cspf_section import HongKongCspfSection
    from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection
    from apps.calculator.ui.sections.iso_iseer_2point_section import (
        IsoIseer2PointSection,
    )
    from apps.calculator.ui.sections.iso_saso_t3_section import IsoSasoT3Section

    two_point = IsoIseer2PointSection(tk_root)
    _assert_blank(two_point.input_table.get_text_values())
    assert two_point.result_table.status_label.cget("text") == "\uc785\ub825 \ub300\uae30"
    assert two_point._trace_status == "\uc785\ub825 \ub300\uae30"

    cspf = HongKongCspfSection(tk_root, "Hong Kong")
    _assert_blank(cspf.rated_table.get_text_values())
    _assert_blank(cspf.input_table.get_text_values())
    assert cspf.result_panel.summary_status_labels["CSPF"].cget("text") == "\uc785\ub825 \ub300\uae30"
    assert cspf._trace_status == "\uc785\ub825 \ub300\uae30"

    hspf = HongKongHspfSection(tk_root, "Hong Kong")
    _assert_blank(hspf.input_table.get_text_values())
    assert hspf.result_panel.summary_status_labels["HSPF"].cget("text") == "\uc785\ub825 \ub300\uae30"
    assert hspf._trace_status == "\uc785\ub825 \ub300\uae30"

    saso = IsoSasoT3Section(tk_root)
    _assert_blank(saso.input_table.get_text_values())
    assert saso.optional_min_enabled.get() is True
    assert saso.result_table.status_label.cget("text") == "\uc785\ub825 \ub300\uae30"
    assert saso._trace_status == "\uc785\ub825 \ub300\uae30"
