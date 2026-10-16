"""Appendix M setting labels shared by the main and combination views."""

SEER_COLUMNS = (("cd", "CDc"),)
HSPF_COLUMNS = (
    ("cd", "CDh"), ("defrost_credit", "Defrost Credit"),
    ("defrost_test_minutes", "Defrost Test [min]"),
    ("defrost_max_minutes", "Defrost Max [min]"),
    ("cut_out_c", "Cut Out [°C]"), ("cut_in_c", "Cut In [°C]"),
)
HSPF_FLAG_GROUPS = (
    ("Measured:", (("measured_h12", "H12"), ("measured_h22", "H22"))),
    ("Flags:", (("h1n_same_speed_as_h32", "H1N=H32 Hz"),
                ("demand_defrost", "Demand Defrost"), ("automatic_cutout", "Automatic Cutout"))),
)
HSPF_FLAG_LABELS = dict(item for _, group in HSPF_FLAG_GROUPS for item in group)
