"""DTOs for the Train Feature Catalog application boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

EDITABLE_HEADERS = (
    "label",
    "notes",
    "active",
    "zero_fill_policy",
    "source",
    "mapping_key",
    "one_hot_group",
)
LOCKED_HEADERS = ("order", "ml_name", "role", "ui_key")


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
    rows: tuple[FeatureCatalogRecord, ...]
    active_count: int
    catalog_validation: ValidationResult
    project_validation: ValidationResult | None = None

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
