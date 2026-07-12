"""Audited AHRI 210/240-2026 multi-capacity UI defaults."""

AHRI_HSPF2_COMMON_DEFAULTS = {
    "cut_out_c": "-40.0",
    "cut_in_c": "-40.0",
    "cd_low": "0.25",
    "cd_full": "0.25",
    "cd_boost": "0.25",
    "defrost_factor": "1.0",
    "defrost_t_test_minutes": "90.0",
    "defrost_t_max_minutes": "720.0",
    "low_stage_lockout_temp_c": "4.4",
}

AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS = {
    "low_min_c": "4.4",
    "low_max_c": "18.3",
    "full_min_c": "-6.7",
    "full_max_c": "10.0",
    "boost_min_c": "-28.9",
    "boost_max_c": "-1.1",
}
