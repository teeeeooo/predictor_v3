"""Product-specific AHRI multi-capacity bin-detail schemas."""

from apps.calculator.ui.sections.bin_detail_schema import BinDetailSchema

AHRI_DUAL_SEER2_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Bin No", "Tj [°F]", "Case", "Building Load [Btu/h]",
        "Low Cap [Btu/h]", "Full Cap [Btu/h]", "Low Permitted",
        "CLF Low", "CLF Full", "PLF", "Cooling [Btu]", "Energy [Wh]",
    ),
    column_keys=(
        "bin_no", "tj", "operating_case", "building_load", "q_low", "q_full",
        "low_permitted", "clf_low", "clf_full", "plf", "q_total", "e_total",
    ),
    graph_series=(
        ("Building Load [Btu/h]", "building_load"),
        ("Low Capacity [Btu/h]", "q_low"),
        ("Full Capacity [Btu/h]", "q_full"),
        ("Cooling [Btu]", "q_total"),
        ("Energy [Wh]", "e_total"),
    ),
    table_title="AHRI Dual-stage SEER2 Bin Detail",
)

AHRI_DUAL_HSPF2_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Tj [°F]", "Fraction", "Case", "Availability", "Building Load [Btu/h]",
        "Low Cap [Btu/h]", "Full Cap [Btu/h]", "Low Permitted",
        "Comp Heat [Btu]", "Comp Energy [Wh]", "Aux Heat [Btu]",
        "Aux Energy [Wh]", "Total Heat [Btu]", "Total Energy [Wh]",
    ),
    column_keys=(
        "tj", "hours", "operating_case", "availability", "building_load",
        "q_low", "q_full", "low_permitted", "q_comp", "e_comp", "q_aux",
        "e_aux", "q_total", "e_total",
    ),
    graph_series=(
        ("Building Load [Btu/h]", "building_load"),
        ("Low Capacity [Btu/h]", "q_low"),
        ("Full Capacity [Btu/h]", "q_full"),
        ("Comp Energy [Wh]", "e_comp"),
        ("Aux Energy [Wh]", "e_aux"),
        ("Total Energy [Wh]", "e_total"),
    ),
    table_title="AHRI Dual-stage HSPF2 Bin Detail",
)

AHRI_TRIPLE_HSPF2_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Tj [°F]", "Fraction", "Case", "Availability", "Building Load [Btu/h]",
        "Low Cap [Btu/h]", "Full Cap [Btu/h]", "Boost Cap [Btu/h]",
        "Low Permitted", "Full Permitted", "Boost Permitted",
        "Comp Heat [Btu]", "Comp Energy [Wh]", "Aux Heat [Btu]",
        "Aux Energy [Wh]", "Total Heat [Btu]", "Total Energy [Wh]",
    ),
    column_keys=(
        "tj", "hours", "operating_case", "availability", "building_load",
        "q_low", "q_full", "q_boost", "low_permitted", "full_permitted",
        "boost_permitted", "q_comp", "e_comp", "q_aux", "e_aux", "q_total",
        "e_total",
    ),
    graph_series=(
        ("Building Load [Btu/h]", "building_load"),
        ("Low Capacity [Btu/h]", "q_low"),
        ("Full Capacity [Btu/h]", "q_full"),
        ("Boost Capacity [Btu/h]", "q_boost"),
        ("Comp Energy [Wh]", "e_comp"),
        ("Aux Energy [Wh]", "e_aux"),
        ("Total Energy [Wh]", "e_total"),
    ),
    table_title="AHRI Triple Northern HSPF2 Bin Detail",
)
