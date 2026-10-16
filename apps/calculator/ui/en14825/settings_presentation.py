"""EN14825 setting labels shared by the main and combination views."""

COMMON_TITLE = "공통 입력"
COMMON_COLUMNS = (("p_to", "Pto [W]"), ("p_sb", "Psb [W]"),
                  ("p_ck", "Pck [W]"), ("p_off", "Poff [W]"))
SEER_DESIGN_TITLE = "설계 사양 (Design Specs)"
SEER_DESIGN_COLUMNS = (("p_design_c", "Pdesignc [W]"), ("t_design_c", "Tdesignc [°C]"), ("cd", "Cd"))
SCOP_DESIGN_TITLE = "설계 사양"
SCOP_CD_COLUMNS = (("cd", "Cd"),)
SCOP_CLIMATE_COLUMNS = (("p_design_h", "Pdesignh [W]"), ("tbiv", "Tbiv [°C]"), ("tol", "TOL [°C]"))
