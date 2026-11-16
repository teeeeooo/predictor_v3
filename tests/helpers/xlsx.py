"""Read test-written workbooks on PCs whose file DRM encrypts them."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from openpyxl import load_workbook

_NASCA_DRM_HEADER = b"<## NASCA DRM"


def load_written_workbook(path: str | Path, **options):  # noqa: ANN003, ANN201
    """Load a workbook, skipping only when file DRM has encrypted it."""
    path = Path(path)
    if not zipfile.is_zipfile(path):
        with path.open("rb") as source:
            if source.read(len(_NASCA_DRM_HEADER)) == _NASCA_DRM_HEADER:
                pytest.skip("file DRM encrypted the saved workbook")
    return load_workbook(path, **options)
