"""DTOs for the Train Feature Catalog application boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DISPLAY_HEADERS = {
    "order": "순서",
    "ml_name": "학습 데이터 컬럼명",
    "role": "Feature 유형",
    "ui_key": "화면 항목 키",
    "label": "화면 표시명",
    "source": "데이터 출처",
    "mapping_key": "매핑 키",
    "one_hot_group": "One-hot 그룹",
    "zero_fill_policy": "누락값 처리",
    "active": "사용 여부",
    "notes": "메모",
}
EDITABLE_HEADERS = (
    "role",
    "label",
    "notes",
    "active",
    "zero_fill_policy",
    "source",
    "mapping_key",
    "one_hot_group",
)
LOCKED_HEADERS = ("order", "ml_name", "ui_key")


@dataclass(frozen=True)
class FeatureCatalogFieldOptions:
    """Dropdown candidates by canonical Feature Catalog header."""

    values_by_header: dict[str, tuple[str, ...]]

    def values_for(self, header: str) -> tuple[str, ...]:
        """Return dropdown candidates for a canonical header."""
        return self.values_by_header.get(header, ())


@dataclass(frozen=True)
class FeatureCatalogRecord:
    """Table-ready Feature Catalog row values in canonical header order."""

    values: tuple[str, ...]

    def value_at(self, column: int) -> str:
        """Return a safe display value for a column index."""
        if 0 <= column < len(self.values):
            return self.values[column]
        return ""


@dataclass(frozen=True)
class FeatureCatalogDraftRequest:
    """User-entered fields for creating a draft Feature Catalog row."""

    ml_name: str
    role: str
    label: str
    source: str = ""
    mapping_key: str = ""
    one_hot_group: str = ""
    zero_fill_policy: str = "disallow"
    active: bool = True
    notes: str = ""


@dataclass(frozen=True)
class ValidationResult:
    """Validation messages for one Feature Catalog validation scope."""

    scope: str
    errors: tuple[str, ...] = ()
    checked: bool = True

    @property
    def ok(self) -> bool:
        """Return whether this checked scope has no validation errors."""
        return self.checked and not self.errors


@dataclass(frozen=True)
class FeatureCatalogSnapshot:
    """Loaded Feature Catalog table rows and validation state."""

    path: Path
    headers: tuple[str, ...]
    display_headers: tuple[str, ...]
    rows: tuple[FeatureCatalogRecord, ...]
    active_count: int
    catalog_validation: ValidationResult
    project_validation: ValidationResult | None = None
    field_options: FeatureCatalogFieldOptions = field(
        default_factory=lambda: FeatureCatalogFieldOptions({})
    )

    @property
    def row_count(self) -> int:
        """Return total row count."""
        return len(self.rows)

    @property
    def has_errors(self) -> bool:
        """Return whether any checked validation scope has errors."""
        validations = (self.catalog_validation, self.project_validation)
        return any(result is not None and bool(result.errors) for result in validations)

    def validation_messages(self) -> tuple[str, ...]:
        """Return display-ready validation messages grouped by scope."""
        messages: list[str] = []
        for result in (self.catalog_validation, self.project_validation):
            if result is None or not result.checked:
                continue
            if result.errors:
                messages.extend(f"{result.scope}: {error}" for error in result.errors)
            else:
                messages.append(f"{result.scope}: OK")
        return tuple(messages)
