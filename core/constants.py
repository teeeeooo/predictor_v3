# V3 constants.py — compatibility surface for constants and predictor schema.

import os

from core.ml.artifacts import BASE_DIR, DATA_DIR, MODEL_DIR, MODEL_FILE, TRAIN_DATA_FILE
from core.ml.features import BASE_FEATURES, DERIVED_FEATURES, TARGETS
from core.mapping.paths import MAPPING_JSON_FILE

# =============================================================================
# 경로 및 파일 상수
# =============================================================================
LOG_DIR = os.path.join(BASE_DIR, "logs")


from core.predictor_schema.columns import (
    AUTO_COLS,
    COL_COMPRESSOR,
    COL_COMP_CC,
    COL_COMP_EER,
    COL_COND_AREA,
    COL_COND_VOLUME,
    COL_COOLING_CAPA,
    COL_COOLING_HZ,
    COL_COOLING_POWER,
    COL_COP,
    COL_CSPF,
    COL_EER,
    COL_EVAP_AREA,
    COL_EVAP_INDEX,
    COL_EVAP_VOLUME,
    COL_EXP_TYPE,
    COL_FIN_TYPE,
    COL_HEATING_CAPA,
    COL_HEATING_HZ,
    COL_HEATING_POWER,
    COL_HSPF2,
    COL_IDU,
    COL_ID_VOLUME,
    COL_ODU,
    COL_OD_VOLUME,
    COL_PI,
    COL_REF_QTY,
    COL_REF_TYPE,
    COL_ROW,
    COLUMNS,
    DROPDOWN_COLS,
    DROPDOWN_TARGET,
    INPUT_COLS,
    NUM_ROWS,
    RESULT_COLS,
)

# ML feature, target, and artifact constants are imported from `core.ml`.
