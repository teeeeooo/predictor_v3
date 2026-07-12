import tkinter as tk

import pytest

from apps.calculator.application.ahri import (
    AHRI_HSPF2_DUAL_POINT_ORDER,
    AHRI_SEER2_DUAL_POINT_ORDER,
    AHRI_SEER2_POINT_ORDER,
)
from apps.calculator.ui.ahri.hspf2_batch import (
    AhriHspf2BatchActiveOptions,
    build_ahri_hspf2_batch_spec,
)
from apps.calculator.ui.ahri.seer2_batch import build_ahri_seer2_batch_spec
from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section
from apps.calculator.ui.sections.ahri_multicapacity_detail_schema import (
    AHRI_DUAL_SEER2_BIN_DETAIL_SCHEMA,
    AHRI_TRIPLE_HSPF2_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk is not available")
    root.withdraw()
    yield root
    root.destroy()


def _column_keys(table) -> tuple[str, ...]:
    return tuple(key for key, _label in table.columns)


def test_seer2_product_switch_restores_product_local_drafts_and_schema(tk_root):
    section = AhriSeer2Section(tk_root)
    section.input_table.set_values({"capacity_A_Full": "11111"})

    section.product_var.set("Dual Stage")
    assert _column_keys(section.input_table) == AHRI_SEER2_DUAL_POINT_ORDER
    assert section.detail_panel._schema == AHRI_DUAL_SEER2_BIN_DETAIL_SCHEMA
    section.input_table.set_values({"capacity_AFull": "48000"})

    section.product_var.set("Variable Capacity")
    assert _column_keys(section.input_table) == AHRI_SEER2_POINT_ORDER
    assert section.input_table.get_text_values()["capacity_A_Full"] == "11111"

    section.product_var.set("Dual Stage")
    assert section.input_table.get_text_values()["capacity_AFull"] == "48000"


def test_hspf2_triple_uses_stacked_stage_tables_and_restores_draft(tk_root):
    section = AhriHspf2Section(tk_root)
    section.product_var.set("Triple Stage Northern")

    surface = section._multi_surface
    assert surface is not None
    assert len(surface.heating_tables) == 3
    assert section.detail_panel._schema == AHRI_TRIPLE_HSPF2_BIN_DETAIL_SCHEMA
    low_table = surface.heating_tables[0]
    low_table.set_values({"capacity_H1Low": "21000"})

    section.product_var.set("Dual Stage")
    assert section._multi_surface is not None
    assert _column_keys(section._multi_surface.heating_table) == AHRI_HSPF2_DUAL_POINT_ORDER

    section.product_var.set("Triple Stage Northern")
    restored = section._multi_surface.heating_tables[0].get_text_values()
    assert restored["capacity_H1Low"] == "21000"


def test_batch_specs_preserve_variable_contract_and_add_product_results():
    variable_seer = build_ahri_seer2_batch_spec("variable_capacity")
    dual_seer = build_ahri_seer2_batch_spec("dual_stage")
    assert variable_seer.profile_key == "ahri_seer2"
    assert variable_seer.result_keys == ("seer2",)
    assert dual_seer.result_keys == (
        "raw_seer2",
        "published_seer2",
        "total_cooling",
        "total_energy",
    )

    variable_hspf = build_ahri_hspf2_batch_spec(AhriHspf2BatchActiveOptions())
    triple_hspf = build_ahri_hspf2_batch_spec(
        AhriHspf2BatchActiveOptions(
            product_classification="triple_capacity_northern",
            h2_low_enabled=False,
        )
    )
    assert variable_hspf.result_keys == ("hspf2",)
    assert "capacity_H2Low" not in triple_hspf.input_keys
    assert triple_hspf.result_keys[:2] == ("raw_hspf2", "published_hspf2")
