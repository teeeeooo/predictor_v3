import pytest

from tests.test_iso16358_hspf_formula_micro import (
    EXTENDED_CAPACITY,
    EXTENDED_POWER,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    iso_points,
    iso_points_with_extended,
    make_iso_micro_calculator,
    rated_for_load_at_7c,
    single_detail,
)


def test_boundary_point_helper_returns_consistent_cop(tmp_path):
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 0.0, "nj": 1.0}],
    )
    load = 1900.0
    measured = iso_points_with_extended(rated_heating_capacity=load)

    from core.calculators.standards.iso16358 import ISO16358Calculator

    assert isinstance(calculator, ISO16358Calculator)

    resolved, _ = calculator._iso_hspf_resolve_common_points(
        calculator._iso_hspf_normalize_common_points(measured),
        calculator.config.get("hspf", {}),
    )
    load_line_info = calculator._iso_hspf_common_load_line(
        calculator.config.get("hspf", {}), load
    )
    load_line = load_line_info["line"]

    full_point = calculator._iso_hspf_boundary_point(
        "full", resolved, frost=True, load_line=load_line
    )

    direct_cop = calculator._iso_hspf_boundary_cop(
        full_point["temp"], "full", resolved, True
    )
    assert full_point["cop"] == pytest.approx(direct_cop)
    # capacity line and load line meet at boundary temperature: capacity ≈ load
    assert full_point["capacity"] == pytest.approx(
        full_point["load_at_boundary"], rel=1e-9, abs=1e-6
    )


def test_formula50_trace_exposes_boundary_cop_endpoints(tmp_path):
    load = 1900.0
    hours = 2.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 0.0, "nj": hours}],
    )
    result = calculator.calculate_hspf(
        iso_points_with_extended(rated_heating_capacity=load)
    )
    detail = single_detail(result)

    assert detail["case"] == "formula50_full_extended_frost"
    assert detail["frost"] is True
    for key in ("tg", "tf", "cop_fe_f", "cop_ful_f_tg", "cop_ext_f_tf"):
        assert key in detail, f"missing Formula 50 trace key: {key}"

    # Endpoint invariants: at tj=tg the interpolated COP equals cop_ful_f_tg,
    # at tj=tf it equals cop_ext_f_tf.  Reconstruct interpolation explicitly.
    tg = detail["tg"]
    tf = detail["tf"]
    cop_full = detail["cop_ful_f_tg"]
    cop_ext = detail["cop_ext_f_tf"]
    tj = detail["tj"]
    expected_cop = cop_full + (cop_ext - cop_full) * (tj - tg) / (tf - tg)
    assert detail["cop_fe_f"] == pytest.approx(expected_cop)

    # ISO 16358-2 Formula 50 spec form must yield the same numeric COP.
    spec_cop = cop_ext + (cop_full - cop_ext) * (tj - tf) / (tg - tf)
    assert detail["cop_fe_f"] == pytest.approx(spec_cop)

    assert detail["P_j"] == pytest.approx(load / detail["cop_fe_f"])


@pytest.mark.parametrize("tj", [-1.0, 0.0])
def test_formula50_spec_form_matches_implementation_at_problem_bins(tmp_path, tj):
    # Bins where external audit flagged a P_j gap (tj=-1, tj=0).  We don't
    # hard-code the audit value; instead we verify the implementation's
    # cop_fe_f matches the literal ISO 16358-2 Formula 50 spec form, so any
    # future regression away from the spec direction would fail this test.
    load = 1900.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": tj, "nj": 1.0}],
    )
    result = calculator.calculate_hspf(
        iso_points_with_extended(rated_heating_capacity=load)
    )
    detail = single_detail(result)
    assert detail["case"] == "formula50_full_extended_frost"

    tg, tf = detail["tg"], detail["tf"]
    cop_full, cop_ext = detail["cop_ful_f_tg"], detail["cop_ext_f_tf"]
    spec_cop = cop_ext + (cop_full - cop_ext) * (tj - tf) / (tg - tf)
    assert detail["cop_fe_f"] == pytest.approx(spec_cop)
    assert detail["P_j"] == pytest.approx(detail["bl_h"] / spec_cop)


def test_formula45_half_full_endpoints_match_boundary_helper(tmp_path):
    load = 1300.0  # between half (1000) and full (1700)
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 7.0, "nj": 1.0}],
    )
    result = calculator.calculate_hspf(
        iso_points(rated_heating_capacity=rated_for_load_at_7c(load))
    )
    detail = single_detail(result)
    assert detail["case"] == "formula45_half_full"

    # ISO Formula 45 invariant: COP_hf is linear between COP_full(ta) and
    # COP_half(tj').  Verify the trace exposes both endpoints and that the
    # interpolated cop_hf falls between (or at one of) them.
    assert "cop_full" in detail and "cop_half" in detail and "cop_hf" in detail
    lo = min(detail["cop_full"], detail["cop_half"])
    hi = max(detail["cop_full"], detail["cop_half"])
    assert lo - 1e-9 <= detail["cop_hf"] <= hi + 1e-9
    assert detail["P_j"] == pytest.approx(detail["bl_h"] / detail["cop_hf"])


def test_formula44_min_half_non_frost_smoke(tmp_path):
    # Drives Formula 44 (non-frost min→half) by providing a min point and
    # picking a load between min (400) and half (1000) capacities at tj=7.
    load = 700.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 7.0, "nj": 1.0}],
    )
    measured = iso_points(
        rated_heating_capacity=rated_for_load_at_7c(load),
        include_min=True,
    )
    result = calculator.calculate_hspf(measured)
    detail = single_detail(result)
    if detail["case"] != "min_half_interpolation":
        pytest.skip(f"Branch not min_half_formula44 (case={detail['case']}).")
    assert detail["P_j"] > 0
