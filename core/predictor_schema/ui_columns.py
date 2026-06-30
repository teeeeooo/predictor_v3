"""UI-only predictor columns that are not ML feature catalog rows."""

DROPDOWN_INPUT_COLUMNS = [
    {
        "key": "idu",
        "header": "실내기",
        "width": 120,
        "group": "input",
        "type": "dropdown",
        "mapping": "idu",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "evap_index",
        "header": "증발기",
        "width": 100,
        "group": "input",
        "type": "dropdown",
        "mapping": "evap_index",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "odu",
        "header": "실외기",
        "width": 120,
        "group": "input",
        "type": "dropdown",
        "mapping": "odu",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "fin_type",
        "header": "FIN종류",
        "width": 80,
        "group": "input",
        "type": "dropdown",
        "mapping": "fin_type",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "pi",
        "header": "PI",
        "width": 60,
        "group": "input",
        "type": "dropdown",
        "mapping": "pi",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "row",
        "header": "ROW",
        "width": 60,
        "group": "input",
        "type": "dropdown",
        "mapping": "row",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "compressor",
        "header": "압축기",
        "width": 120,
        "group": "input",
        "type": "dropdown",
        "mapping": "compressor",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "ref_type",
        "header": "냉매종류",
        "width": 80,
        "group": "input",
        "type": "dropdown",
        "mapping": "ref_type",
        "bg_color": "#FFFFFF",
    },
    {
        "key": "exp_type",
        "header": "팽창장치",
        "width": 80,
        "group": "input",
        "type": "dropdown",
        "mapping": "exp_type",
        "bg_color": "#FFFFFF",
    },
]

RULE_RESULT_COLUMNS = [
    {
        "key": "eer",
        "header": "EER (rule)",
        "width": 100,
        "group": "result",
        "readonly": True,
        "bg_color": "#E6F3E6",
    },
    {
        "key": "cspf",
        "header": "CSPF",
        "width": 110,
        "group": "result",
        "readonly": True,
        "bg_color": "#E6F3E6",
    },
    {
        "key": "cop",
        "header": "COP (rule)",
        "width": 100,
        "group": "result",
        "readonly": True,
        "bg_color": "#E6F3E6",
    },
    {
        "key": "hspf2",
        "header": "HSPF2",
        "width": 110,
        "group": "result",
        "readonly": True,
        "bg_color": "#E6F3E6",
    },
]

INPUT_INSERT_AFTER = {
    "heating_capa": DROPDOWN_INPUT_COLUMNS,
}

RESULT_INSERT_AFTER = {
    "cooling_power": RULE_RESULT_COLUMNS[:2],
    "heating_power": RULE_RESULT_COLUMNS[2:],
}


def insert_columns_after(projected_columns, insert_after):
    columns = []
    for column in projected_columns:
        columns.append(column)
        columns.extend(insert_after.get(column["key"], ()))
    return columns
