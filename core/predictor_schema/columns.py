"""Predictor table column schema and column grouping constants."""

from core.ml.feature_catalog import load_feature_catalog, validate_feature_catalog
from core.ml.feature_catalog_projection import predictor_columns_projection
from core.predictor_schema.ui_columns import (
    INPUT_INSERT_AFTER,
    RESULT_INSERT_AFTER,
    insert_columns_after,
)


ROLE_PRESENTATION_DEFAULTS = {
    "input": {"width": 90, "bg_color": "#FFFFFF"},
    "auto": {"width": 90, "bg_color": "#F2F2F2"},
    "result": {"width": 100, "bg_color": "#E6F3E6"},
}

WIDTH_OVERRIDES = {
    "comp_eer": 80,
    "comp_cc": 80,
    "ref_qty": 80,
}

def _load_validated_catalog():
    catalog = load_feature_catalog()
    errors = validate_feature_catalog(catalog)
    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"invalid predictor schema feature catalog: {joined}")
    return catalog


def _build_columns():
    catalog = _load_validated_catalog()
    projected = predictor_columns_projection(
        catalog.rows,
        ROLE_PRESENTATION_DEFAULTS,
        WIDTH_OVERRIDES,
    )
    input_columns = [column for column in projected if column["group"] == "input"]
    auto_columns = [column for column in projected if column["group"] == "auto"]
    result_columns = [column for column in projected if column["group"] == "result"]
    return (
        insert_columns_after(input_columns, INPUT_INSERT_AFTER)
        + auto_columns
        + insert_columns_after(result_columns, RESULT_INSERT_AFTER)
    )


COLUMNS = _build_columns()

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
