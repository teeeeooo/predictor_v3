"""Train/Predict startup composition over runtime-generation recovery states."""

from __future__ import annotations

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from apps.common.runtime_generation.repository import DataDefinitionGenerationRepository
from core.data_definition.contract import load_manifest


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()


def _startup(surface: str):
    if surface == "predict":
        from apps.predict import app as startup
    else:
        from apps.train.composition import runtime as startup
    return startup


def _shell_generation_id(shell, surface: str) -> str:  # noqa: ANN001
    workspace = shell.workspace if surface == "predict" else shell.predict_workspace
    return workspace.generation_id


def _close(shell, app) -> None:  # noqa: ANN001
    shell.close()
    shell.deleteLater()
    app.processEvents()


@pytest.mark.parametrize("surface", ("predict", "train"))
def test_clean_startup_publishes_readable_bootstrap(tmp_path, qt_app, surface):
    startup = _startup(surface)
    root = tmp_path / f"{surface}-generations"
    shell = startup.create_shell(
        generation_root=root,
        lifecycle_root=tmp_path / f"{surface}-lifecycle",
    )

    active = DataDefinitionGenerationRepository(root).read_active()
    assert active.manifest.generation.generation_id.startswith("bootstrap-")
    assert _shell_generation_id(shell, surface) == active.manifest.generation.generation_id
    _close(shell, qt_app)


@pytest.mark.parametrize("surface", ("predict", "train"))
def test_startup_recovers_pointer_to_missing_bootstrap_generation(
    tmp_path,
    qt_app,
    surface,
):
    startup = _startup(surface)
    manifest = load_manifest(startup.DEFAULT_BOOTSTRAP_MANIFEST_PATH)
    root = tmp_path / f"{surface}-generations"
    repository = DataDefinitionGenerationRepository(root)
    repository.root.mkdir(parents=True)
    repository.active_pointer_path.write_text(
        json.dumps({"generation_id": manifest.generation.generation_id}),
        encoding="utf-8",
    )

    shell = startup.create_shell(
        generation_root=root,
        lifecycle_root=tmp_path / f"{surface}-lifecycle",
    )

    active = repository.read_active()
    assert active.manifest == manifest
    assert _shell_generation_id(shell, surface) == manifest.generation.generation_id
    _close(shell, qt_app)


@pytest.mark.parametrize("surface", ("predict", "train"))
def test_startup_does_not_overwrite_corrupt_complete_generation(
    tmp_path,
    qt_app,
    surface,
):
    startup = _startup(surface)
    manifest = load_manifest(startup.DEFAULT_BOOTSTRAP_MANIFEST_PATH)
    root = tmp_path / f"{surface}-generations"
    repository = DataDefinitionGenerationRepository(root)
    repository.publish(manifest)
    generation = repository.generations_path / manifest.generation.generation_id
    schema = generation / "projections" / "schema.csv"
    schema.write_text("corrupt\n", encoding="utf-8")

    with pytest.raises(ValueError, match="generation bundle hash mismatch"):
        startup.create_shell(
            generation_root=root,
            lifecycle_root=tmp_path / f"{surface}-lifecycle",
        )

    assert schema.read_text(encoding="utf-8") == "corrupt\n"
