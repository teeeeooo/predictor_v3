"""Human-readable field labels; identities and CSV keys remain application data."""
TITLES = dict(iso="ISO / ISEER", hong_kong_cspf="Hong Kong CSPF", hong_kong_hspf="Hong Kong HSPF",
              saso="SASO T3", brazil="Brazil CSPF", korea_cspf="KS C 9306 CSPF", korea_hspf="KS C 9306 HSPF",
              en_seer="EN14825 SEER · Tested", en_scop="EN14825 SCOP · Tested", m_seer="AHRI M SEER",
              m_hspf="AHRI M HSPF", seer2="AHRI M1 SEER2", hspf2="AHRI M1 HSPF2")
LABELS = {
    "declared_capacity": "정격 냉방능력 [W]", "rated_cooling_capacity": "정격 냉방능력 [W]",
    "a2_capacity": "A2 / AFull 냉방능력 [Btu/h]", "p_design_c_w": "Pdesignc [W]", "p_design_h_w": "Pdesignh [W]",
    "t_design_c": "설계 냉방 온도 [°C]", "tbiv_temp_c": "Tbiv [°C]", "tol_temp_c": "TOL [°C]",
    "p_to_w": "Thermostat-off [W]", "p_sb_w": "Standby [W]", "p_ck_w": "Crankcase [W]", "p_off_w": "Off [W]",
    "cd": "Cd", "cd_low": "Cd Low", "cd_full": "Cd Full", "cd_boost": "Cd Boost",
    "cut_out_c": "Cut-out [°C]", "cut_in_c": "Cut-in [°C]", "defrost_credit": "Defrost credit",
    "defrost_factor": "Defrost factor", "defrost_mode": "제상 모드", "appliance_type": "기기 형식",
    "defrost_test_minutes": "Defrost test [min]", "defrost_max_minutes": "Defrost max [min]",
    "defrost_t_test_minutes": "Defrost test [min]", "defrost_t_max_minutes": "Defrost max [min]",
    "low_stage_lockout_enabled": "Low stage lockout", "low_stage_lockout_temp_f": "Low stage lockout [°F]",
    "low_stage_lockout_temp_c": "Low stage lockout [°C]", "automatic_cutout": "자동 Cut-out",
    "demand_defrost": "Demand defrost", "minimum_speed_limited": "최저 속도 제한",
    "h1n_same_speed_as_h32": "H1N / H32 동일 속도", "region": "Region", "product_classification": "제품 형식",
}
STATUS = {"running":"계산 중", "completed":"완료", "completed-with-errors":"완료 (오류 포함)", "cancelled":"취소됨", "failed":"실행 실패"}


def field_label(key):
    if key in LABELS:
        return LABELS[key]
    if key.startswith("measured_"):
        return key.removeprefix("measured_").replace("_", " ").upper()+" 실측"
    if key.endswith(("_min_c", "_max_c")):
        return key.replace("_min_c", " 최저 [°C]").replace("_max_c", " 최고 [°C]").title()
    return key.replace("_", " ")


def context_tab_labels(contexts):
    """Show the varying calculation choice, without internal option dictionaries."""
    products = {"variable_capacity": "Variable Capacity", "dual_stage": "Dual Stage",
                "triple_capacity_northern": "Triple Northern"}
    climates = {"average": "평균 기후", "warmer": "온난 기후", "colder": "한랭 기후"}
    modes = {"required_only": "필수 시험", "with_optional_test": "35 Min 실측 포함"}
    labels = []
    for context in contexts:
        if context.kind == "iso":
            label = context.profile
        else:
            label = " · ".join(str(value) for value in (
                TITLES[context.kind], climates.get(context.climate, context.climate),
                products.get(context.product, context.product), context.system_type,
                modes.get(context.mode, context.mode)) if value)
        labels.append(label)
    # Options create separate sessions. Keep their tabs distinct and concise;
    # the selected session's exact flags remain visible in 실행 옵션.
    counts = {}
    result = []
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
        result.append(f"{label} · 설정 {counts[label]}" if labels.count(label) > 1 else label)
    return result
