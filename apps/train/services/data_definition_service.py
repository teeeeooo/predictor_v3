"""Read-only Data Definition service for Train/Admin."""

from __future__ import annotations

from pathlib import Path

from core.data_definition import DataDefinitionReport, build_data_definition_report


class DataDefinitionService:
    """Load Data Definition reports without owning save paths or defaults."""

    def load_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Return the current read-only Data Definition report."""
        return build_data_definition_report(training_data_path=training_data_path)

    def refresh_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Reload the report for refresh actions."""
        return self.load_report(training_data_path=training_data_path)
