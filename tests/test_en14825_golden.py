import pytest

from core.calculator_en14825 import EN14825Calculator


TOLERANCE = 0.005

# Standby power inputs are provided by the source sample in W.
# The calculator API expects kW, so 6.6 W is passed as 0.0066 kW.
STANDBY_POWER_KW = {
    "p_to": 0.0066,
    "p_sb": 0.0012,
    "p_ck": 0.0,
    "p_off": 0.0012,
}


def assert_golden_close(actual, expected, label):
    assert abs(actual - expected) < TOLERANCE, (
        f"{label} golden mismatch: expected={expected:.3f}, actual={actual:.3f}, "
        f"tolerance={TOLERANCE:.3f}"
    )


def scop_points(tbiv_temp_c, tol_temp_c):
    return {
        "A": {"capacity": 2.1598, "power": 0.6062, "temp_c": -7},
        "B": {"capacity": 1.3293, "power": 0.2542, "temp_c": 2},
        "C": {"capacity": 0.9083, "power": 0.1540, "temp_c": 7},
        "D": {"capacity": 0.9299, "power": 0.1231, "temp_c": 12},
        "TOL": {"capacity": 2.3698, "power": 0.8067, "temp_c": tol_temp_c},
        "Tbiv": {"capacity": 2.3669, "power": 0.7820, "temp_c": tbiv_temp_c},
    }


@pytest.mark.xfail(
    strict=True,
    reason="TODO: EERpl direct interpolation fix should make this golden SEER pass.",
)
def test_en14825_golden_seer():
    calculator = EN14825Calculator()
    result = calculator.calculate_seer(
        test_points={
            "A": (3.6233, 0.847),
            "B": (2.4691, 0.389),
            "C": (1.5150, 0.137),
            "D": (1.1277, 0.062),
        },
        p_design_c=3.5,
        t_design_c=35,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["seer"], 9.104, "SEER")


@pytest.mark.xfail(
    strict=True,
    reason="TODO: COPPL direct interpolation fix should make this golden SCOP pass.",
)
def test_en14825_golden_scop_average():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=-10, tol_temp_c=-11),
        p_design_h=2.4,
        climate="average",
        tbiv_temp_c=-10,
        tol_temp_c=-11,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 5.108, "SCOP average")


@pytest.mark.xfail(
    strict=True,
    reason="TODO: Tbiv/B duplicate temperature point split should make this golden SCOP pass.",
)
def test_en14825_golden_scop_warmer():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=2, tol_temp_c=-11),
        p_design_h=1.3,
        climate="warmer",
        tbiv_temp_c=2,
        tol_temp_c=-11,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 6.008, "SCOP warmer")


@pytest.mark.xfail(
    strict=True,
    reason="TODO: Colder climate TOL below -20 C needs schema support before this golden SCOP passes.",
)
def test_en14825_golden_scop_colder():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=-15, tol_temp_c=-22),
        p_design_h=2.942,
        climate="colder",
        tbiv_temp_c=-15,
        tol_temp_c=-22,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 4.190, "SCOP colder")
