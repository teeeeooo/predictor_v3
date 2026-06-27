"""Predictor table column schema and column grouping constants."""

# =============================================================================
# UI 컬럼 구조 (COLUMNS) - 인덱스 0~27 (총 28개)
# =============================================================================
COLUMNS = [
    # INPUT_COLS (인덱스 0~10, 11개)
    {"key": "cooling_capa", "header": "냉방능력", "width": 90, "group": "input", "bg_color": "#FFFFFF"},
    {"key": "heating_capa", "header": "난방능력", "width": 90, "group": "input", "bg_color": "#FFFFFF"},
    {"key": "idu", "header": "실내기", "width": 120, "group": "input", "type": "dropdown", "mapping": "idu", "bg_color": "#FFFFFF"},
    {"key": "evap_index", "header": "증발기", "width": 100, "group": "input", "type": "dropdown", "mapping": "evap_index", "bg_color": "#FFFFFF"},
    {"key": "odu", "header": "실외기", "width": 120, "group": "input", "type": "dropdown", "mapping": "odu", "bg_color": "#FFFFFF"},
    {"key": "fin_type", "header": "FIN종류", "width": 80, "group": "input", "type": "dropdown", "mapping": "fin_type", "bg_color": "#FFFFFF"},
    {"key": "pi", "header": "PI", "width": 60, "group": "input", "type": "dropdown", "mapping": "pi", "bg_color": "#FFFFFF"},
    {"key": "row", "header": "ROW", "width": 60, "group": "input", "type": "dropdown", "mapping": "row", "bg_color": "#FFFFFF"},
    {"key": "compressor", "header": "압축기", "width": 120, "group": "input", "type": "dropdown", "mapping": "compressor", "bg_color": "#FFFFFF"},
    {"key": "ref_type", "header": "냉매종류", "width": 80, "group": "input", "type": "dropdown", "mapping": "ref_type", "bg_color": "#FFFFFF"},
    {"key": "exp_type", "header": "팽창장치", "width": 80, "group": "input", "type": "dropdown", "mapping": "exp_type", "bg_color": "#FFFFFF"},

    # AUTO_COLS (인덱스 11~18, 전략 A 적용 수정)
    {"key": "id_volume", "header": "ID Volume", "width": 90, "group": "auto", "ml_feature": "ID Volume", "bg_color": "#F2F2F2",
     "source": "idu", "mapping_key": "ID Volume"},

    {"key": "evap_area", "header": "Evap Area", "width": 90, "group": "auto", "ml_feature": "Evap Area", "bg_color": "#F2F2F2",
     "source": "evap_index", "mapping_key": "Evap Area"},

    {"key": "evap_volume", "header": "Evap Volume", "width": 90, "group": "auto", "ml_feature": "Evap Volume", "bg_color": "#F2F2F2",
     "source": "evap_index", "mapping_key": "Evap Volume"},

    {"key": "od_volume", "header": "OD Volume", "width": 90, "group": "auto", "ml_feature": "OD Volume", "bg_color": "#F2F2F2",
     "source": "odu", "mapping_key": "OD Volume"},

    {"key": "cond_area", "header": "Cond Area", "width": 90, "group": "auto", "ml_feature": "Cond Area", "bg_color": "#F2F2F2",
     "source": "odu", "mapping_key": "Cond Area"},

    {"key": "cond_volume", "header": "Cond Volume", "width": 90, "group": "auto", "ml_feature": "Cond Volume", "bg_color": "#F2F2F2",
     "source": "odu", "mapping_key": "Cond Volume"},

    {"key": "comp_eer", "header": "Comp EER", "width": 80, "group": "auto", "ml_feature": "Comp EER", "bg_color": "#F2F2F2",
     "source": "compressor", "mapping_key": "Comp EER"},

    {"key": "comp_cc", "header": "Comp cc", "width": 80, "group": "auto", "ml_feature": "Comp cc", "bg_color": "#F2F2F2",
     "source": "compressor", "mapping_key": "Comp cc"},


    # RESULT_COLS (인덱스 19~27, 9개)
    {"key": "cooling_power", "header": "냉방 소비전력", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "eer", "header": "EER (rule)", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "cspf", "header": "CSPF", "width": 110, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "heating_power", "header": "난방 소비전력", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "cop", "header": "COP (rule)", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "hspf2", "header": "HSPF2", "width": 110, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "ref_qty", "header": "냉매량", "width": 80, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "cooling_hz", "header": "냉방 주파수", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
    {"key": "heating_hz", "header": "난방 주파수", "width": 100, "group": "result", "readonly": True, "bg_color": "#E6F3E6"},
]

# =============================================================================
# 컬럼 인덱스 상수 (동적 추출)
# =============================================================================
# [INPUT_COLS]
COL_COOLING_CAPA = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cooling_capa")
COL_HEATING_CAPA = next(i for i, c in enumerate(COLUMNS) if c["key"] == "heating_capa")
COL_IDU          = next(i for i, c in enumerate(COLUMNS) if c["key"] == "idu")
COL_EVAP_INDEX   = next(i for i, c in enumerate(COLUMNS) if c["key"] == "evap_index")
COL_ODU          = next(i for i, c in enumerate(COLUMNS) if c["key"] == "odu")
COL_FIN_TYPE     = next(i for i, c in enumerate(COLUMNS) if c["key"] == "fin_type")
COL_PI           = next(i for i, c in enumerate(COLUMNS) if c["key"] == "pi")
COL_ROW          = next(i for i, c in enumerate(COLUMNS) if c["key"] == "row")
COL_COMPRESSOR   = next(i for i, c in enumerate(COLUMNS) if c["key"] == "compressor")
COL_REF_TYPE     = next(i for i, c in enumerate(COLUMNS) if c["key"] == "ref_type")
COL_EXP_TYPE     = next(i for i, c in enumerate(COLUMNS) if c["key"] == "exp_type")

# [AUTO_COLS]
COL_ID_VOLUME    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "id_volume")
COL_EVAP_AREA    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "evap_area")
COL_EVAP_VOLUME  = next(i for i, c in enumerate(COLUMNS) if c["key"] == "evap_volume")
COL_OD_VOLUME    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "od_volume")
COL_COND_AREA    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cond_area")
COL_COND_VOLUME  = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cond_volume")
COL_COMP_EER     = next(i for i, c in enumerate(COLUMNS) if c["key"] == "comp_eer")
COL_COMP_CC      = next(i for i, c in enumerate(COLUMNS) if c["key"] == "comp_cc")

# [RESULT_COLS]
COL_COOLING_POWER = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cooling_power")
COL_EER           = next(i for i, c in enumerate(COLUMNS) if c["key"] == "eer")
COL_CSPF          = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cspf")
COL_HEATING_POWER = next(i for i, c in enumerate(COLUMNS) if c["key"] == "heating_power")
COL_COP           = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cop")
COL_HSPF2         = next(i for i, c in enumerate(COLUMNS) if c["key"] == "hspf2")
COL_REF_QTY       = next(i for i, c in enumerate(COLUMNS) if c["key"] == "ref_qty")
COL_COOLING_HZ    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "cooling_hz")
COL_HEATING_HZ    = next(i for i, c in enumerate(COLUMNS) if c["key"] == "heating_hz")

# =============================================================================
# 그룹별 키 리스트 및 설정
# =============================================================================
INPUT_COLS    = [c["key"] for c in COLUMNS if c["group"] == "input"]
AUTO_COLS     = [c["key"] for c in COLUMNS if c["group"] == "auto"]
RESULT_COLS   = [c["key"] for c in COLUMNS if c["group"] == "result"]
DROPDOWN_COLS = [c["key"] for c in COLUMNS if c.get("type") == "dropdown"]

DROPDOWN_TARGET = {k: k for k in DROPDOWN_COLS}

NUM_ROWS = 10
