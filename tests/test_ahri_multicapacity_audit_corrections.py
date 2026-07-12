from __future__ import annotations

import pytest

from apps.calculator.application.ahri import (
    AhriHspf2Adapter,
    AhriHspf2InputError,
    AhriHspf2Options,
    AhriSeer2Adapter,
)
from apps.calculator.ui.ahri.hspf2_batch import (
    AhriHspf2BatchActiveOptions,
    build_ahri_hspf2_batch_spec,
)
from apps.calculator.ui.ahri.hspf2_product_surface import (
    AhriHspf2ProductSurface,
)
from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2 import (
    AhriHspf2BatchSection,
)
from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section
from apps.calculator.ui.table.roles import CellRole
from core.calculators.standards._ahri.hspf2_triple_northern import (
    HSPF2TripleNorthernEngine,
)
from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator

DUAL_POINTS = {
    "AFull": (30000.0, 1.0),
    "H0Low": (22000.0, 1450.0),
    "H1Full": (25000.0, 1800.0),
    "H1Low": (18000.0, 1350.0),
    "H2Full": (21500.0, 1900.0),
    "H2Low": (14500.0, 1450.0),
    "H3Full": (19500.0, 2100.0),
    "H3Low": (10500.0, 1600.0),
}
TRIPLE_POINTS = {
    "AFull": (30000.0, 1.0),
    "H0Low": (26000.0, 1350.0),
    "H1Full": (28000.0, 1850.0),
    "H1Low": (21000.0, 1300.0),
    "H2Boost": (30000.0, 2400.0),
    "H2Full": (25500.0, 2050.0),
    "H3Boost": (28000.0, 3000.0),
    "H3Full": (22000.0, 2350.0),
    "H3Low": (14500.0, 1750.0),
    "H4Boost": (25000.0, 3400.0),
}


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


def _text_points(points):
    values = {
        "a2_capacity": str(points["AFull"][0]),
        "cut_out_c": "-40.0",
        "cut_in_c": "-40.0",
        "cd_low": "0.25",
        "cd_full": "0.25",
    }
    for point, (capacity, power) in points.items():
        if point == "AFull":
            continue
        values[f"capacity_{point}"] = str(capacity)
        values[f"power_{point}"] = str(power)
    return values


def _triple_text_values(*, low_min_c: str, include_h3: bool):
    points = dict(TRIPLE_POINTS)
    if not include_h3:
        points.pop("H3Low")
    values = _text_points(points)
    values.update(
        {
            "cd_boost": "0.25",
            "low_min_c": low_min_c,
            "low_max_c": "18.3",
            "full_min_c": "-6.7",
            "full_max_c": "10.0",
            "boost_min_c": "-28.9",
            "boost_max_c": "-1.1",
        }
    )
    return values


def test_dual_lockout_above_37f_calculates_without_h3low():
    points = dict(DUAL_POINTS)
    points.pop("H3Low")
    result = AHRIHSPF2Calculator(
        "data/region_configs/usa_hspf2.json"
    ).calculate_hspf2(
        points,
        product_classification="dual_stage",
        low_stage_lockout_enabled=True,
        low_stage_lockout_temp_f=38.0,
        defrost_mode="none",
        t_off=-40.0,
        t_on=-40.0,
    )

    metadata = result["summary"]["metadata"]
    assert metadata["h3_low_required"] is False
    assert metadata["point_sources"]["H3Low"] == (
        "not_applicable_to_low_stage_lockout"
    )
    assert "H3Low" not in metadata["resolved_points"]
    assert all(
        row["q_low"] is None and row["p_low"] is None
        for row in result["bin_details"]
        if not row["low_permitted"]
    )


@pytest.mark.parametrize(
    ("lockout_enabled", "lockout_temp_c"),
    ((True, "2.7"), (False, "4.4")),
    ids=("lockout-at-or-below-37f", "lockout-disabled"),
)
def test_dual_h3low_missing_is_a_field_error_when_required(
    lockout_enabled,
    lockout_temp_c,
):
    values = _text_points({key: value for key, value in DUAL_POINTS.items() if key != "H3Low"})
    values["low_stage_lockout_temp_c"] = lockout_temp_c

    with pytest.raises(AhriHspf2InputError) as exc_info:
        AhriHspf2Adapter().calculate(
            values,
            options=AhriHspf2Options(
                product_classification="dual_stage",
                low_stage_lockout_enabled=lockout_enabled,
                defrost_mode="none",
            ),
        )

    assert exc_info.value.field_errors == {
        "capacity_H3Low": "37°F 이하 Low-stage 운전 시 필수 시험점",
        "power_H3Low": "37°F 이하 Low-stage 운전 시 필수 시험점",
    }


def test_triple_low_min_38f_calculates_without_h3low_or_fabricated_metadata():
    points = dict(TRIPLE_POINTS)
    points.pop("H3Low")
    result = AHRIHSPF2Calculator(
        "data/region_configs/usa_hspf2.json"
    ).calculate_hspf2(
        points,
        product_classification="triple_capacity_northern",
        h3_low_tested=False,
        defrost_mode="none",
        t_off=-45.0,
        t_on=-45.0,
        stage_ranges_f={
            "low": (38.0, 65.0),
            "full": (20.0, 50.0),
            "boost": (-20.0, 30.0),
        },
    )

    metadata = result["summary"]["metadata"]
    assert metadata["h3_low_required"] is False
    assert metadata["point_sources"]["H3Low"] == (
        "not_applicable_to_permitted_range"
    )
    assert metadata["point_sources"]["H2Low"] == (
        "not_applicable_to_permitted_range"
    )
    assert "H3Low" not in metadata["resolved_points"]
    assert "H2Low" not in metadata["resolved_points"]
    assert all(
        row["q_low"] is None and row["p_low"] is None
        for row in result["bin_details"]
        if row["temp_F"] <= 37.0
    )


def test_triple_low_min_37f_requires_h3low_field():
    with pytest.raises(AhriHspf2InputError) as exc_info:
        AhriHspf2Adapter().calculate(
            _triple_text_values(low_min_c="2.7", include_h3=False),
            options=AhriHspf2Options(
                product_classification="triple_capacity_northern",
                defrost_mode="none",
            ),
        )

    assert set(exc_info.value.field_errors) == {
        "capacity_H3Low",
        "power_H3Low",
    }


def test_single_and_batch_h3low_schemas_follow_the_same_boundary(tk_root):
    dual = AhriHspf2ProductSurface(
        tk_root,
        product="dual_stage",
        on_values_changed=lambda: None,
    )
    dual.low_lockout_var.set(True)
    dual.numeric_table.set_value("low_stage_lockout_temp_c", "3.4")
    tk_root.update_idletasks()
    h3_column = tuple(key for key, _label in dual.heating_table.columns).index(
        "H3Low"
    )
    capacity_row = tuple(key for key, _label in dual.heating_table.rows).index(
        "capacity"
    )
    assert dual.heating_table.cell_role((capacity_row, h3_column)) is CellRole.READONLY
    dual_batch = build_ahri_hspf2_batch_spec(
        AhriHspf2BatchActiveOptions(
            product_classification="dual_stage",
            h3_low_enabled=False,
        )
    )
    assert "capacity_H3Low" not in dual_batch.input_keys

    triple = AhriHspf2ProductSurface(
        tk_root,
        product="triple_capacity_northern",
        on_values_changed=lambda: None,
    )
    triple.range_table.set_value("low_min_c", "2.7")
    tk_root.update_idletasks()
    low_table = triple.heating_tables[0]
    h3_column = tuple(key for key, _label in low_table.columns).index("H3Low")
    capacity_row = tuple(key for key, _label in low_table.rows).index("capacity")
    assert low_table.cell_role((capacity_row, h3_column)) is CellRole.EDITABLE
    triple_batch = build_ahri_hspf2_batch_spec(
        AhriHspf2BatchActiveOptions(
            product_classification="triple_capacity_northern",
            h3_low_enabled=True,
        )
    )
    assert "capacity_H3Low" in triple_batch.input_keys


def test_batch_dialog_derives_h3low_schema_from_common_inputs(tk_root):
    section = AhriHspf2BatchSection(tk_root)
    section.product_var.set("Dual Stage")
    section._vars["low_stage_lockout_enabled"].set("1")
    section._vars["low_stage_lockout_temp_c"].set("3.4")
    section._apply_options()
    assert "capacity_H3Low" not in section.table.spec.input_keys

    section.product_var.set("Triple Stage Northern")
    section._vars["low_min_c"].set("2.7")
    section._apply_options()
    assert "capacity_H3Low" in section.table.spec.input_keys
    section.dispose()


def test_availability_label_uses_the_stage_selected_by_the_case():
    deltas = {"low": 0.5, "full": 1.0, "boost": 1.0}
    assert HSPF2TripleNorthernEngine._selected_availability_delta(
        4,
        {"low": 0.4, "full": 0.6},
        deltas,
    ) == 0.5
    assert HSPF2TripleNorthernEngine._selected_availability_delta(
        7,
        {"full": 1.0},
        deltas,
    ) == 1.0
    assert HSPF2TripleNorthernEngine._selected_availability_delta(
        8,
        {"resistance": 1.0},
        deltas,
    ) == 0.0


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
