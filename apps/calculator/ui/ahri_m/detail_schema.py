"""Appendix M-specific bin detail schemas."""

from apps.calculator.ui.sections.bin_detail_schema import BinDetailSchema

AHRI_M_SEER_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=("Tj [°F]", "Fraction", "Case", "Building Load [Btu/h]", "Min Cap", "Int Cap", "Full Cap", "EER Bin", "Cooling", "Energy"),
    column_keys=("tj", "hours", "operating_case", "building_load", "q_low", "q_int", "q_full", "eer_bin", "q_total", "e_total"),
    graph_series=(("Building Load [Btu/h]", "building_load"), ("Cooling", "q_total"), ("Energy", "e_total"), ("EER Bin", "eer_bin")),
    table_title="AHRI Appendix M SEER Bin Detail",
)

AHRI_M_HSPF_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=("Tj [°F]", "Fraction", "Case", "Building Load [Btu/h]", "Min Cap", "Int Cap", "Full Cap", "COP Bin", "Cutout δ", "Comp Energy", "Aux Energy", "Total Energy"),
    column_keys=("tj", "hours", "operating_case", "building_load", "q_low", "q_int", "q_full", "cop_bin", "cutout_delta", "e_comp", "e_aux", "e_total"),
    graph_series=(("Building Load [Btu/h]", "building_load"), ("Comp Energy", "e_comp"), ("Aux Energy", "e_aux"), ("Total Energy", "e_total"), ("COP Bin", "cop_bin")),
    table_title="AHRI Appendix M HSPF Bin Detail",
)
