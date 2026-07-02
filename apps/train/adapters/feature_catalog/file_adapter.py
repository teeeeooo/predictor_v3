"""File adapter for Feature Catalog export workflows."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path


class FeatureCatalogFileAdapter:
    """Write Feature Catalog CSV files outside the UI layer."""

    def write_export(
        self,
        path: str | Path,
        headers: Sequence[str],
        rows: Sequence[Sequence[str]],
    ) -> Path:
        """Write an Excel-safe UTF-8-SIG CSV export."""
        destination = Path(path)
        with destination.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(tuple(headers))
            writer.writerows(tuple(row) for row in rows)
        return destination
