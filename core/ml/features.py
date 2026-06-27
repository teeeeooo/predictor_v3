"""ML feature and target constants."""

BASE_FEATURES = [
    "Cooling Capa", "Heating Capa", "ID Volume", "Evap Area", "Evap Volume",
    "OD Volume", "Cond Area", "Cond Volume", "Comp EER", "Comp cc",
    "R410A", "R32", "R290", "EEV", "Capi", "Ref Qty",
    "Cooling Power", "Heating Power", "Cooling Hz", "Heating Hz"
]

DERIVED_FEATURES = [
    "Cool_Capa_per_EER", "Cool_Capa_per_CondArea",
    "Cool_Capa_per_EvapArea", "Cool_Capa_per_cc",
    "Heat_Capa_per_EER", "Heat_Capa_per_CondArea",
    "Heat_Capa_per_EvapArea", "Heat_Capa_per_cc"
]

TARGETS = ["Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz"]
