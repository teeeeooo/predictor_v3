"""CSV-backed ML feature catalog loader and validator.

This module is a foundation for Arc 13 catalog parity tests. Existing runtime
modules still use their current constants and schema owners.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "config" / "ml" / "features.csv"

REQUIRED_HEADERS = (
    "order",
    "feature_id",
    "ml_name",
    "role",
    "ui_key",
    "label",
    "source",
    "mapping_key",
    "one_hot_group",
    "zero_fill_policy",
    "active",
    "notes",
)
ALLOWED_ROLES = frozenset({"input", "auto", "result", "derived", "one_hot", "hidden"})
ALLOWED_ZERO_FILL_POLICIES = frozenset({"disallow", "mode_missing_allowed"})
MODE_MISSING_ALLOWED_FEATURES = frozenset(
    {"Cooling Capa", "Cooling Power", "Heating Capa", "Heating Power"}
)
SEASONAL_OUTPUT_NAMES = frozenset({"CSPF", "HSPF", "CSEC", "HSEC", "HSPF2"})
BASE_FEATURE_ROLES = frozenset({"input", "auto", "one_hot", "result", "hidden"})
UI_VISIBLE_ROLES = frozenset({"input", "auto", "result"})
TARGET_COMPAT_ORDER = ("Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz")

@dataclass(frozen=True)
class FeatureCatalogRow:
    """One row from the user-managed ML feature catalog draft."""

    order: int
    feature_id: str
    ml_name: str
    role: str
    ui_key: str
    label: str
    source: str
    mapping_key: str
    one_hot_group: str
    zero_fill_policy: str
    active: bool
    notes: str = ""

@dataclass(frozen=True)
class FeatureCatalog:
    """Parsed feature catalog with projection helpers."""

    rows: tuple[FeatureCatalogRow, ...]
    headers: tuple[str, ...] = REQUIRED_HEADERS
    path: Path | None = None

    @property
    def active_rows(self) -> tuple[FeatureCatalogRow, ...]:
        return tuple(row for row in self.rows if row.active)

    def base_features(self) -> list[str]:
        return [
            row.ml_name
            for row in self.active_rows
            if row.role in BASE_FEATURE_ROLES and row.ml_name
        ]

    def derived_features(self) -> list[str]:
        return [row.ml_name for row in self.active_rows if row.role == "derived" and row.ml_name]

    def targets(self) -> list[str]:
        rows_by_name = {row.ml_name: row for row in self.active_rows if row.role == "result"}
        ordered = [name for name in TARGET_COMPAT_ORDER if name in rows_by_name]
        remaining = [
            row.ml_name
            for row in self.active_rows
            if row.role == "result" and row.ml_name not in TARGET_COMPAT_ORDER
        ]
        return ordered + remaining

    def predictor_rows(self) -> tuple[FeatureCatalogRow, ...]:
        return tuple(row for row in self.active_rows if row.role in UI_VISIBLE_ROLES and row.ui_key)

    def one_hot_groups(self) -> dict[str, tuple[str, ...]]:
        grouped: dict[str, list[str]] = {}
        for row in self.active_rows:
            if row.role != "one_hot":
                continue
            grouped.setdefault(row.one_hot_group, []).append(row.ml_name)
        return {group: tuple(names) for group, names in grouped.items()}

    def zero_fill_policies(self) -> dict[str, str]:
        return {
            row.ml_name: row.zero_fill_policy
            for row in self.active_rows
            if row.ml_name
        }

def load_feature_catalog(path: str | Path | None = None) -> FeatureCatalog:
    """Load a feature catalog CSV without validating registry references."""
    catalog_path = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    with catalog_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = tuple(reader.fieldnames or ())
        rows = tuple(_row_from_csv(index, row) for index, row in enumerate(reader, start=2))
    return FeatureCatalog(rows=tuple(sorted(rows, key=lambda row: row.order)), headers=headers, path=catalog_path)

def validate_feature_catalog(catalog: FeatureCatalog) -> list[str]:
    """Return validation errors for catalog-only rules."""
    errors: list[str] = []
    headers = set(catalog.headers)
    required = set(REQUIRED_HEADERS)
    missing_headers = sorted(required - headers)
    unknown_headers = sorted(headers - required)
    if missing_headers:
        errors.append(f"missing required header(s): {', '.join(missing_headers)}")
    if unknown_headers:
        errors.append(f"unknown header(s): {', '.join(unknown_headers)}")

    _validate_unique(
        errors,
        "feature_id",
        (row.feature_id for row in catalog.rows if row.active),
    )
    _validate_unique(
        errors,
        "ml_name",
        (row.ml_name for row in catalog.rows if row.active and row.ml_name),
    )
    _validate_unique(
        errors,
        "ui_key",
        (
            row.ui_key
            for row in catalog.rows
            if row.active and row.role in UI_VISIBLE_ROLES and row.ui_key
        ),
    )

    for row in catalog.rows:
        prefix = f"feature_id={row.feature_id or '<blank>'}"
        if row.role not in ALLOWED_ROLES:
            errors.append(f"{prefix}: invalid role '{row.role}'")
        if row.zero_fill_policy not in ALLOWED_ZERO_FILL_POLICIES:
            errors.append(f"{prefix}: invalid zero_fill_policy '{row.zero_fill_policy}'")
        if (
            row.zero_fill_policy == "mode_missing_allowed"
            and row.ml_name not in MODE_MISSING_ALLOWED_FEATURES
        ):
            errors.append(f"{prefix}: mode_missing_allowed is not allowed for '{row.ml_name}'")
        if row.active and row.role in UI_VISIBLE_ROLES:
            if not row.ui_key:
                errors.append(f"{prefix}: role={row.role} requires ui_key")
            if not row.label:
                errors.append(f"{prefix}: role={row.role} requires label")
        if row.active and row.role == "auto":
            if not row.source:
                errors.append(f"{prefix}: role=auto requires source")
            if not row.mapping_key:
                errors.append(f"{prefix}: role=auto requires mapping_key")
        if row.active and row.role == "one_hot" and not row.one_hot_group:
            errors.append(f"{prefix}: role=one_hot requires one_hot_group")
        if row.active and row.role == "result" and row.ml_name not in catalog.targets():
            errors.append(f"{prefix}: role=result did not enter targets projection")

    _validate_model_input_projection(errors, catalog)
    return errors

def validate_registry_references(catalog: FeatureCatalog, model_registry: dict) -> list[str]:
    """Return errors for MODEL_REGISTRY references missing from the catalog."""
    errors: list[str] = []
    catalog_names = {row.ml_name for row in catalog.active_rows if row.ml_name}
    for model_key, config in model_registry.items():
        for target in config.get("targets", ()):
            if target not in catalog_names:
                errors.append(f"{model_key}: target '{target}' is missing from catalog")
        for target, rules in config.get("target_rules", {}).items():
            if target not in catalog_names:
                errors.append(f"{model_key}: target rule '{target}' is missing from catalog")
            for rule_name in ("exclude", "allowed"):
                for feature_name in rules.get(rule_name, ()):
                    if feature_name not in catalog_names:
                        errors.append(
                            f"{model_key}: {rule_name} feature '{feature_name}' is missing from catalog"
                        )
    return errors

def _row_from_csv(line_number: int, raw: dict[str, str | None]) -> FeatureCatalogRow:
    order_text = _clean(raw.get("order"))
    try:
        order = int(order_text)
    except ValueError as exc:
        raise ValueError(f"line {line_number}: invalid order '{order_text}'") from exc
    return FeatureCatalogRow(
        order=order,
        feature_id=_clean(raw.get("feature_id")),
        ml_name=_clean(raw.get("ml_name")),
        role=_clean(raw.get("role")),
        ui_key=_clean(raw.get("ui_key")),
        label=_clean(raw.get("label")),
        source=_clean(raw.get("source")),
        mapping_key=_clean(raw.get("mapping_key")),
        one_hot_group=_clean(raw.get("one_hot_group")),
        zero_fill_policy=_clean(raw.get("zero_fill_policy")),
        active=_parse_bool(_clean(raw.get("active"))),
        notes=_clean(raw.get("notes")),
    )


def _clean(value: str | None) -> str:
    return "" if value is None else value.strip()


def _parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ValueError(f"invalid active value '{value}'")


def _validate_unique(errors: list[str], field_name: str, values: Iterable[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    for value in sorted(duplicates):
        errors.append(f"duplicate {field_name}: {value}")


def _validate_model_input_projection(errors: list[str], catalog: FeatureCatalog) -> None:
    for name in catalog.base_features():
        if name in SEASONAL_OUTPUT_NAMES:
            errors.append(f"seasonal output '{name}' cannot enter base feature projection")
