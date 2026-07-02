"""CSV-backed ML feature catalog loader and data model.

The catalog contract is based on `ml_name`: training data headers and internal
ML feature names must match the catalog exactly. Header aliases are not
supported.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from core.ml.feature_catalog_projection import (
    active_rows,
    base_features,
    derived_features,
    one_hot_groups,
    predictor_rows,
    targets,
    training_headers,
    validate_training_headers,
    zero_fill_policies,
)
from core.ml.feature_catalog_validation import (
    validate_feature_catalog,
    validate_registry_references,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "config" / "ml" / "features.csv"

REQUIRED_HEADERS = (
    "order",
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


@dataclass(frozen=True)
class FeatureCatalogRow:
    """One row from the user-managed ML feature catalog draft."""

    order: int
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
    required_headers: tuple[str, ...] = REQUIRED_HEADERS

    @property
    def active_rows(self) -> tuple[FeatureCatalogRow, ...]:
        return active_rows(self.rows)

    def base_features(self) -> list[str]:
        return base_features(self.rows)

    def derived_features(self) -> list[str]:
        return derived_features(self.rows)

    def targets(self) -> list[str]:
        return targets(self.rows)

    def predictor_rows(self) -> tuple[FeatureCatalogRow, ...]:
        return predictor_rows(self.rows)

    def one_hot_groups(self) -> dict[str, tuple[str, ...]]:
        return one_hot_groups(self.rows)

    def zero_fill_policies(self) -> dict[str, str]:
        return zero_fill_policies(self.rows)

    def training_headers(self) -> list[str]:
        return training_headers(self.rows)

    def validate_training_headers(self, headers) -> list[str]:
        return validate_training_headers(headers, self)

def load_feature_catalog(path: str | Path | None = None) -> FeatureCatalog:
    """Load a feature catalog CSV without validating registry references."""
    catalog_path = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    try:
        with catalog_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            headers = tuple(reader.fieldnames or ())
            rows = tuple(_row_from_csv(index, row) for index, row in enumerate(reader, start=2))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"ML feature catalog not found: {catalog_path}") from exc
    return FeatureCatalog(
        rows=tuple(sorted(rows, key=lambda row: row.order)),
        headers=headers,
        path=catalog_path,
    )

def _row_from_csv(line_number: int, raw: dict[str, str | None]) -> FeatureCatalogRow:
    order_text = _clean(raw.get("order"))
    try:
        order = int(order_text)
    except ValueError as exc:
        raise ValueError(f"line {line_number}: invalid order '{order_text}'") from exc
    return FeatureCatalogRow(
        order=order,
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
