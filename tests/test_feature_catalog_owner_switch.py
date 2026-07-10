"""Feature Catalog legacy owner switch tests."""

from __future__ import annotations

import hashlib
import shutil

from apps.train.adapters.feature_catalog import FeatureCatalogFileAdapter
from apps.train.application.feature_catalog import FeatureCatalogService
from apps.train.application.feature_catalog.service import CANONICAL_SAVE_BLOCK_MESSAGE
from core.ml.feature_catalog import DEFAULT_CATALOG_PATH, REQUIRED_HEADERS


def test_feature_catalog_default_canonical_save_is_blocked():
    before_hash = _file_hash(DEFAULT_CATALOG_PATH)
    service = FeatureCatalogService(export_writer=FeatureCatalogFileAdapter())
    snapshot = service.load_snapshot()

    result = service.save_records(snapshot.rows)

    assert not result.saved
    assert result.snapshot is None
    assert result.message == CANONICAL_SAVE_BLOCK_MESSAGE
    assert result.errors == (CANONICAL_SAVE_BLOCK_MESSAGE,)
    assert _file_hash(DEFAULT_CATALOG_PATH) == before_hash


def test_feature_catalog_tmp_path_save_remains_available_for_compatibility(tmp_path):
    catalog_path = tmp_path / "features.csv"
    shutil.copyfile(DEFAULT_CATALOG_PATH, catalog_path)
    service = FeatureCatalogService(
        catalog_path=catalog_path,
        export_writer=FeatureCatalogFileAdapter(),
    )
    snapshot = service.load_snapshot()
    label_col = REQUIRED_HEADERS.index("label")
    rows = [list(record.values) for record in snapshot.rows]
    rows[0][label_col] = "Compatibility Export Label"
    records = tuple(type(snapshot.rows[0])(values=tuple(row)) for row in rows)

    result = service.save_records(records)

    assert result.saved
    assert result.snapshot is not None
    assert result.snapshot.rows[0].value_at(label_col) == "Compatibility Export Label"


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
