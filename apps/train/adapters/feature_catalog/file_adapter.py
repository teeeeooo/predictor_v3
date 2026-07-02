"""File adapter for Feature Catalog export workflows."""

from __future__ import annotations

import csv
import os
import tempfile
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

    def write_canonical(
        self,
        path: str | Path,
        headers: Sequence[str],
        rows: Sequence[Sequence[str]],
    ) -> Path:
        """Safely replace the canonical UTF-8 Feature Catalog CSV."""
        destination = Path(path)
        tmp_name = ""
        try:
            fd, tmp_name = tempfile.mkstemp(
                prefix=f".{destination.name}.",
                suffix=".tmp",
                dir=str(destination.parent),
            )
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(tuple(headers))
                writer.writerows(tuple(row) for row in rows)
            os.replace(tmp_name, destination)
        except Exception:
            if tmp_name:
                try:
                    Path(tmp_name).unlink(missing_ok=True)
                except OSError:
                    pass
            raise
        return destination
