"""Appendix M1 setting labels shared by the main and combination views."""

SEER2_DUAL_COLUMNS = (
    ("cd_low", "Cd Low"), ("cd_full", "Cd Full"), ("low_stage_lockout_temp_f", "Lockout [°F]"),
)
HSPF2_VARIABLE_COLUMNS = (
    ("cd", "Cd"), ("defrost_credit", "Defrost Credit"),
    ("cut_out_c", "Cut Out [°C]"), ("cut_in_c", "Cut In [°C]"),
)
HSPF2_RANGE_COLUMNS = tuple(
    (f"{stage}_{edge}_c", f"{stage.title()} {edge.title()} [°C]")
    for stage in ("low", "full", "boost") for edge in ("min", "max")
)
HSPF2_ANCHOR_COLUMNS = (("A2", "A2"),)
HSPF2_ANCHOR_ROWS = (("capacity", "Capacity [Btu/h]"),)
HSPF2_VARIABLE_FLAG_GROUPS = (
    ("Measured:", (("measured_h42", "H42"), ("measured_h12", "H12"), ("measured_h22", "H22"))),
    ("Flags:", (("h1n_same_speed_as_h32", "H1N=H32 Hz"), ("minimum_speed_limited", "MinSpd"))),
)
HSPF2_DUAL_FLAGS = (
    ("measured_h4_full", "H4Full tested"), ("measured_h2_low", "H2Low tested"),
    ("low_stage_lockout_enabled", "Low-stage lockout"),
)
HSPF2_TRIPLE_FLAGS = (
    ("measured_h2_low", "H2Low tested"), ("measured_h2_boost", "H2Boost tested"),
    ("measured_h3_low", "H3Low tested"),
)
FLAG_LABELS = dict(
    [item for _, group in HSPF2_VARIABLE_FLAG_GROUPS for item in group]
    + list(HSPF2_DUAL_FLAGS) + list(HSPF2_TRIPLE_FLAGS)
)
DEFROST_CHOICES = ("none", "explicit_override", "calculated_from_timing")


def hspf2_numeric_columns(product):
    columns = [("cut_out_c", "Cut Out [°C]"), ("cut_in_c", "Cut In [°C]"),
               ("cd_low", "Cd Low"), ("cd_full", "Cd Full")]
    if product == "triple_capacity_northern":
        columns.append(("cd_boost", "Cd Boost"))
    columns.extend((("defrost_factor", "Fdef"), ("defrost_t_test_minutes", "Ttest [min]"),
                    ("defrost_t_max_minutes", "Tmax [min]")))
    if product == "dual_stage":
        columns.append(("low_stage_lockout_temp_c", "Low Lockout [°C]"))
    return tuple(columns)
