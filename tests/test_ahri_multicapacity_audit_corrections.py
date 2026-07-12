from __future__ import annotations

import pytest

from apps.calculator.application.ahri import AhriSeer2Adapter
from apps.calculator.ui.ahri.hspf2_batch import (
    AhriHspf2BatchActiveOptions,
    build_ahri_hspf2_batch_spec,
)
from apps.calculator.ui.ahri.hspf2_product_surface import (
    AhriHspf2ProductSurface,
)
from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section
from apps.calculator.ui.table.roles import CellRole


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
        root.destroy()


def test_triple_surface_disables_h2low_when_h3low_is_tested(tk_root):
    surface = AhriHspf2ProductSurface(
        tk_root,
        product="triple_capacity_northern",
        on_values_changed=lambda: None,
    )

    surface.h3_low_var.set(False)
    surface.h2_low_var.set(True)
    assert str(surface.h2_low_checkbutton.cget("state")) == "normal"
    assert surface.options().measured_h2_low is True

    surface.h3_low_var.set(True)
    tk_root.update_idletasks()

    assert surface.h2_low_var.get() is False
    assert str(surface.h2_low_checkbutton.cget("state")) == "disabled"
    assert surface.options().measured_h3_low is True
    assert surface.options().measured_h2_low is False
    low_table = surface.heating_tables[0]
    h2_column = tuple(key for key, _label in low_table.columns).index("H2Low")
    capacity_row = tuple(key for key, _label in low_table.rows).index("capacity")
    assert low_table.cell_role((capacity_row, h2_column)) is CellRole.READONLY


def test_triple_batch_spec_omits_h2low_when_h3low_is_tested():
    spec = build_ahri_hspf2_batch_spec(
        AhriHspf2BatchActiveOptions(
            product_classification="triple_capacity_northern",
            h2_low_enabled=True,
            h3_low_enabled=True,
        )
    )
    h2_low = next(point for point in spec.measurement_points if point.key == "H2Low")

    assert h2_low.input_key_for(spec.physical_rows[0]) is None
    assert h2_low.input_key_for(spec.physical_rows[1]) is None
    assert "capacity_H2Low" not in spec.input_keys
    assert "power_H2Low" not in spec.input_keys


def test_seer2_option_parse_error_marks_the_exact_option_cell(tk_root):
    adapter = AhriSeer2Adapter(
        capability_executor=lambda *_args, **_kwargs: pytest.fail(
            "invalid option input must fail before capability execution"
        ),
        calculator_config={"constants": {"cooling_season_hours": 1000.0}},
    )
    section = AhriSeer2Section(tk_root, adapter=adapter)
    section.product_var.set("Dual Stage")
    tk_root.update_idletasks()
    assert section._surface.options_table is not None

    section._surface.options_table.set_value("cd_full", "not-a-number")
    section.recalculate_now()

    assert section._surface.options_table.is_field_invalid("cd_full")
    assert section._surface.options_table.invalid_message("cd_full") == (
        "숫자 입력 필요"
    )
