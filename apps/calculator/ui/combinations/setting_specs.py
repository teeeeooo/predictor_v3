"""Bind shared main-page setting definitions to combination input keys."""
from dataclasses import dataclass

from apps.calculator.ui.ahri import settings_presentation as m1
from apps.calculator.ui.ahri_m import settings_presentation as m
from apps.calculator.ui.en14825 import settings_presentation as en
from apps.calculator.ui.layout_constants import (
    TABLE_ROW_HEADER_CHARS, TABLE_DATA_COLUMN_CHARS,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS, METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
    METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS, METRIC_TABLE_ANCHOR_DATA_COLUMN_CHARS,
    METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS, METRIC_TABLE_DECLARED_DATA_COLUMN_CHARS,
)


@dataclass(frozen=True)
class SettingTable:
    columns: tuple
    row_label: str = "Value"
    title: str = ""
    row_chars: int = METRIC_TABLE_COMPACT_ROW_HEADER_CHARS
    data_chars: int = METRIC_TABLE_POINT_DATA_COLUMN_CHARS
    type_selector: bool = False


def numeric_groups(context):
    if context.kind.startswith("en_"):
        yield SettingTable(tuple((key + "_w", label) for key, label in en.COMMON_COLUMNS),
                           "입력값", en.COMMON_TITLE, data_chars=METRIC_TABLE_DECLARED_DATA_COLUMN_CHARS)
        if context.kind == "en_seer":
            columns = tuple(("p_design_c_w" if key == "p_design_c" else key, label)
                            for key, label in en.SEER_DESIGN_COLUMNS)
            yield SettingTable(columns, "입력값", en.SEER_DESIGN_TITLE,
                               data_chars=METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS, type_selector=True)
        else:
            yield SettingTable(en.SCOP_CD_COLUMNS, "입력값", en.SCOP_DESIGN_TITLE,
                               data_chars=METRIC_TABLE_DECLARED_DATA_COLUMN_CHARS, type_selector=True)
            aliases = {"p_design_h": "p_design_h_w", "tbiv": "tbiv_temp_c", "tol": "tol_temp_c"}
            yield SettingTable(tuple((aliases[key], label) for key, label in en.SCOP_CLIMATE_COLUMNS),
                               "입력값", data_chars=METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS)
    elif context.kind in ("m_seer", "m_hspf"):
        yield SettingTable(m.SEER_COLUMNS if context.kind == "m_seer" else m.HSPF_COLUMNS,
                           row_chars=TABLE_ROW_HEADER_CHARS,
                           data_chars=TABLE_DATA_COLUMN_CHARS if context.kind == "m_seer"
                           else METRIC_TABLE_POINT_DATA_COLUMN_CHARS)
    elif context.kind == "seer2" and context.product == "dual_stage":
        yield SettingTable(m1.SEER2_DUAL_COLUMNS)
    elif context.kind == "hspf2":
        columns = (m1.HSPF2_VARIABLE_COLUMNS if context.product == "variable_capacity"
                   else m1.hspf2_numeric_columns(context.product))
        yield SettingTable(columns)
        yield SettingTable((("a2_capacity", m1.HSPF2_ANCHOR_COLUMNS[0][1]),),
                           m1.HSPF2_ANCHOR_ROWS[0][1], row_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
                           data_chars=METRIC_TABLE_ANCHOR_DATA_COLUMN_CHARS)
        if context.product == "triple_capacity_northern":
            yield SettingTable(m1.HSPF2_RANGE_COLUMNS, "Stage Range")
    elif context.kind in ("hong_kong_cspf", "korea_cspf", "korea_hspf"):
        heating = context.kind == "korea_hspf"
        yield SettingTable((("rated_cooling_capacity" if heating else "declared_capacity", "능력 [W]"),),
                           "정격 냉방능력" if heating else "정격 표기치",
                           row_chars=TABLE_ROW_HEADER_CHARS, data_chars=TABLE_DATA_COLUMN_CHARS)


def flag_groups(context):
    if context.kind == "m_hspf":
        return "Options", m.HSPF_FLAG_GROUPS
    if context.kind == "seer2" and context.product == "dual_stage":
        return "Dual-stage Options", (("", (("low_stage_lockout_enabled", m1.FLAG_LABELS["low_stage_lockout_enabled"]),)),)
    if context.kind == "hspf2":
        if context.product == "variable_capacity":
            return "Options", m1.HSPF2_VARIABLE_FLAG_GROUPS
        return "Product Options", (("", m1.HSPF2_DUAL_FLAGS if context.product == "dual_stage" else m1.HSPF2_TRIPLE_FLAGS),)
    return "", ()
