"""Human-readable field labels; identities and CSV keys remain application data."""
TITLES = dict(iso="ISO / ISEER", hong_kong_cspf="Hong Kong CSPF", hong_kong_hspf="Hong Kong HSPF",
              saso="SASO T3", brazil="Brazil CSPF", korea_cspf="KS C 9306 CSPF", korea_hspf="KS C 9306 HSPF",
              en_seer="EN14825 SEER · Tested", en_scop="EN14825 SCOP · Tested", m_seer="AHRI M SEER",
              m_hspf="AHRI M HSPF", seer2="AHRI M1 SEER2", hspf2="AHRI M1 HSPF2")
STATUS = {"running":"계산 중", "completed":"완료", "completed-with-errors":"완료 (오류 포함)", "cancelled":"취소됨", "failed":"실행 실패"}


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
    return labels


def point_title(point):
    return {"35_full": "STD", "35_half": "HALF"}.get(point.key, point.key)
