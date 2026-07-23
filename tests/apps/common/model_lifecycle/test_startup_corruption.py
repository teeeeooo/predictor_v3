"""Predict and Train startup fail closed on a corrupt legacy import."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import joblib
import pytest
from PySide6.QtWidgets import QApplication

from apps.common.model_lifecycle import (
    LegacyModelMigrationService,
    ModelLifecycleRepository,
)

from .conftest import artifact_for


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()


def _leave_corrupt_import(root, legacy, snapshot):  # noqa: ANN001
    importing = ModelLifecycleRepository(
        root,
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("activation interrupted"))
            if stage == "before_active_replace"
            else None
        ),
    )
    imported = LegacyModelMigrationService(
        importing, lambda: snapshot
    ).migrate_if_needed(legacy)
    assert imported.candidate_id
    candidate = root / "candidates" / imported.candidate_id
    (candidate / "model.pkl").write_bytes(b"corrupt-after-import")


@pytest.mark.parametrize("surface", ("predict", "train"))
def test_startup_does_not_raise_for_corrupt_legacy_candidate(
    tmp_path, monkeypatch, registry_snapshot, qt_app, surface
):
    legacy = tmp_path / "model.pkl"
    joblib.dump(artifact_for(registry_snapshot), legacy)
    lifecycle_root = tmp_path / f"{surface}-lifecycle"
    _leave_corrupt_import(lifecycle_root, legacy, registry_snapshot)

    if surface == "predict":
        from apps.predict import app as startup
    else:
        from apps.train.composition import runtime as startup
    monkeypatch.setattr(startup, "MODEL_FILE", legacy)

    shell = startup.create_shell(
        generation_root=tmp_path / f"{surface}-generations",
        lifecycle_root=lifecycle_root,
    )

    assert ModelLifecycleRepository(lifecycle_root).read_active(optional=True) is None
    if surface == "predict":
        assert shell.legacy_migration.status == "retraining-required"
        assert shell.legacy_migration.reason_code == "legacy_candidate_corrupt"
    shell.close()
    shell.deleteLater()
    qt_app.processEvents()
