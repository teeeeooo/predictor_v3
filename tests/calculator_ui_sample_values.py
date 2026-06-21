"""Explicit calculator performance samples for focused UI tests only."""

HSPF2_SAMPLE_VALUES = {
    "a2_capacity": "24000",
    "capacity_H01": "12500",
    "power_H01": "980",
    "capacity_H11": "12000",
    "power_H11": "1000",
    "capacity_H1N": "22000",
    "power_H1N": "2000",
    "capacity_H2Int": "13000",
    "power_H2Int": "1200",
    "capacity_H32": "22000",
    "power_H32": "2100",
    "capacity_H42": "18000",
    "power_H42": "1900",
    "capacity_H12": "24000",
    "power_H12": "2200",
    "capacity_H22": "23200",
    "power_H22": "2160",
}
HSPF2_HEATING_SAMPLE_VALUES = {
    key: value for key, value in HSPF2_SAMPLE_VALUES.items() if key != "a2_capacity"
}

ISO_TWO_POINT_SAMPLE_VALUES = {
    "full_capacity": "3600",
    "full_power": "900",
    "half_capacity": "1700",
    "half_power": "380",
}

HONG_KONG_CSPF_SAMPLE_VALUES = {
    "declared_capacity": "3500",
    **ISO_TWO_POINT_SAMPLE_VALUES,
}

HONG_KONG_HSPF_SAMPLE_VALUES = {
    "full_capacity": "6300",
    "full_power": "1500",
    "half_capacity": "3200",
    "half_power": "800",
}

SASO_T3_SAMPLE_VALUES = {
    "full_46_capacity": "5000",
    "full_46_power": "1500",
    "full_35_capacity": "6000",
    "full_35_power": "1500",
    "half_35_capacity": "3000",
    "half_35_power": "680",
    "min_35_capacity": "1200",
    "min_35_power": "300",
}

EN14825_SEER_SAMPLE_VALUES = {
    "declared_capacity_A": "3600",
    "declared_capacity_B": "2650",
    "declared_capacity_C": "1700",
    "declared_capacity_D": "1200",
    "declared_eer_A": "4.00",
    "declared_eer_B": "4.60",
    "declared_eer_C": "5.40",
    "declared_eer_D": "6.20",
    "tested_capacity_A": "3600",
    "tested_capacity_B": "2650",
    "tested_capacity_C": "1700",
    "tested_capacity_D": "1200",
    "tested_power_A": "900",
    "tested_power_B": "576",
    "tested_power_C": "315",
    "tested_power_D": "194",
}

EN14825_SCOP_SAMPLE_VALUES = {
    "declared_capacity_A": "3000",
    "declared_capacity_B": "3000",
    "declared_capacity_C": "3000",
    "declared_capacity_D": "3000",
    "declared_capacity_TOL": "3000",
    "declared_capacity_Tbiv": "3000",
    "declared_cop_A": "2.80",
    "declared_cop_B": "3.20",
    "declared_cop_C": "3.60",
    "declared_cop_D": "4.00",
    "declared_cop_TOL": "2.20",
    "declared_cop_Tbiv": "2.80",
    "tested_capacity_A": "3000",
    "tested_capacity_B": "3000",
    "tested_capacity_C": "3000",
    "tested_capacity_D": "3000",
    "tested_capacity_TOL": "3000",
    "tested_capacity_Tbiv": "3000",
    "tested_power_A": "1070",
    "tested_power_B": "938",
    "tested_power_C": "833",
    "tested_power_D": "750",
    "tested_power_TOL": "1360",
    "tested_power_Tbiv": "1070",
}
