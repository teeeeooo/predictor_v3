"""Read-only Predict Schema Catalog v2 draft loader and validation."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "config" / "predict" / "schema.csv"

REQUIRED_HEADERS = (
    "display_order",
    "column_key",
    "label",
    "role",
    "editor",
    "data_type",
    "visible",
    "required",
    "readonly",
    "value_source",
    "mapping_entity",
    "mapping_attribute",
    "trigger_column",
    "rule_id",
    "model_input_enabled",
    "ml_name",
    "one_hot_group",
    "active",
    "notes",
)

ALLOWED_ROLES = frozenset(
    {"input", "auto", "helper", "result", "status", "one_hot_feature", "hidden"}
)
ALLOWED_EDITORS = frozenset({"text", "number", "dropdown", "readonly", "status"})
ALLOWED_DATA_TYPES = frozenset({"string", "number", "boolean", "status"})
ALLOWED_VALUE_SOURCES = frozenset(
    {"manual", "mapping_lookup", "formula", "result", "one_hot", "status", "rule_options"}
)

_TRUE_VALUES = frozenset({"true", "1", "yes"})
_FALSE_VALUES = frozenset({"false", "0", "no"})


@dataclass(frozen=True)
class PredictSchemaV2Row:
    """One row from the read-only Predict Schema Catalog v2 draft."""

    line_number: int
    display_order: int
    column_key: str
    label: str
    role: str
    editor: str
    data_type: str
    visible: bool
    required: bool
    readonly: bool
    value_source: str
    mapping_entity: str
    mapping_attribute: str
    trigger_column: str
    rule_id: str
    model_input_enabled: bool
    ml_name: str
    one_hot_group: str
    active: bool
    notes: str = ""


@dataclass(frozen=True)
class PredictSchemaCatalogV2:
    """Parsed read-only Predict Schema Catalog v2 draft."""

    rows: tuple[PredictSchemaV2Row, ...]
    headers: tuple[str, ...] = REQUIRED_HEADERS
    path: Path | None = None
    load_errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def active_rows(self) -> tuple[PredictSchemaV2Row, ...]:
        return tuple(row for row in self.rows if row.active)


def load_predict_schema_catalog_v2(
    path: str | Path | None = None,
) -> PredictSchemaCatalogV2:
    """Load the read-only Predict Schema Catalog v2 draft."""
    schema_path = Path(path) if path is not None else DEFAULT_SCHEMA_PATH
    try:
        with schema_path.open("r", encoding="utf-8", newline="") as schema_file:
            reader = csv.DictReader(schema_file)
            headers = tuple(reader.fieldnames or ())
            rows: list[PredictSchemaV2Row] = []
            load_errors: list[str] = []
            for line_number, raw in enumerate(reader, start=2):
                row, errors = _row_from_csv(line_number, raw)
                rows.append(row)
                load_errors.extend(errors)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Predict schema v2 draft not found: {schema_path}") from exc
    return PredictSchemaCatalogV2(
        rows=tuple(sorted(rows, key=lambda row: row.display_order)),
        headers=headers,
        path=schema_path,
        load_errors=tuple(load_errors),
    )


def validate_predict_schema_catalog_v2(catalog: PredictSchemaCatalogV2) -> list[str]:
    """Return validation errors for the read-only v2 draft."""
    errors = list(catalog.load_errors)
    headers = set(catalog.headers)
    required_headers = set(REQUIRED_HEADERS)
    missing = sorted(required_headers - headers)
    unknown = sorted(headers - required_headers)
    if missing:
        errors.append(f"missing required header(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown header(s): {', '.join(unknown)}")

    seen_keys: dict[str, int] = {}
    for row in catalog.rows:
        prefix = _row_prefix(row)
        if row.active:
            if not row.column_key:
                errors.append(f"{prefix}: active row requires column_key")
            elif row.column_key in seen_keys:
                errors.append(
                    f"{prefix}: duplicate active column_key '{row.column_key}' "
                    f"(first seen on line {seen_keys[row.column_key]})"
                )
            else:
                seen_keys[row.column_key] = row.line_number
        if row.role not in ALLOWED_ROLES:
            errors.append(f"{prefix}: invalid role '{row.role}'")
        if row.editor not in ALLOWED_EDITORS:
            errors.append(f"{prefix}: invalid editor '{row.editor}'")
        if row.data_type not in ALLOWED_DATA_TYPES:
            errors.append(f"{prefix}: invalid data_type '{row.data_type}'")
        if row.value_source not in ALLOWED_VALUE_SOURCES:
            errors.append(f"{prefix}: invalid value_source '{row.value_source}'")
        if row.visible and not row.label:
            errors.append(f"{prefix}: visible row requires label")
        if row.value_source == "mapping_lookup" and not row.rule_id:
            if not row.mapping_entity:
                errors.append(f"{prefix}: mapping_lookup requires mapping_entity")
            if not row.mapping_attribute:
                errors.append(f"{prefix}: mapping_lookup requires mapping_attribute")
            if not row.trigger_column:
                errors.append(f"{prefix}: mapping_lookup requires trigger_column")
        if row.model_input_enabled and not (row.ml_name or row.one_hot_group):
            errors.append(
                f"{prefix}: model_input_enabled requires ml_name or one_hot_group"
            )
    return errors


def _row_from_csv(
    line_number: int,
    raw: dict[str, str | None],
) -> tuple[PredictSchemaV2Row, tuple[str, ...]]:
    errors: list[str] = []
    order = _parse_int(raw.get("display_order"), line_number, "display_order", errors)
    row = PredictSchemaV2Row(
        line_number=line_number,
        display_order=order,
        column_key=_clean(raw.get("column_key")),
        label=_clean(raw.get("label")),
        role=_clean(raw.get("role")),
        editor=_clean(raw.get("editor")),
        data_type=_clean(raw.get("data_type")),
        visible=_parse_bool(raw.get("visible"), line_number, "visible", errors),
        required=_parse_bool(raw.get("required"), line_number, "required", errors),
        readonly=_parse_bool(raw.get("readonly"), line_number, "readonly", errors),
        value_source=_clean(raw.get("value_source")),
        mapping_entity=_clean(raw.get("mapping_entity")),
        mapping_attribute=_clean(raw.get("mapping_attribute")),
        trigger_column=_clean(raw.get("trigger_column")),
        rule_id=_clean(raw.get("rule_id")),
        model_input_enabled=_parse_bool(
            raw.get("model_input_enabled"),
            line_number,
            "model_input_enabled",
            errors,
        ),
        ml_name=_clean(raw.get("ml_name")),
        one_hot_group=_clean(raw.get("one_hot_group")),
        active=_parse_bool(raw.get("active"), line_number, "active", errors),
        notes=_clean(raw.get("notes")),
    )
    return row, tuple(errors)


def _parse_int(
    raw_value: str | None,
    line_number: int,
    field_name: str,
    errors: list[str],
) -> int:
    value = _clean(raw_value)
    try:
        return int(value)
    except ValueError:
        errors.append(f"line {line_number}: {field_name} must be an integer")
        return 0


def _parse_bool(
    raw_value: str | None,
    line_number: int,
    field_name: str,
    errors: list[str],
) -> bool:
    value = _clean(raw_value).lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    errors.append(f"line {line_number}: {field_name} must be a boolean")
    return False


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def _row_prefix(row: PredictSchemaV2Row) -> str:
    key = row.column_key or "<blank>"
    return f"line {row.line_number} column_key={key}"
