"""Regression tests for saved-generation Data Definition Training Contract exports."""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

from apps.common.runtime_generation.repository import DataDefinitionGenerationRepository
from apps.train.adapters.data_definition_training_contract_export import (
    REFERENCE_HEADERS,
    publish_definition_reference,
    publish_training_header_template,
)
from apps.train.application.data_definition.training_contract_export import (
    build_training_contract_export,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import RenameDefinitionIntent
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


def _renamed_manifest():  # noqa: ANN202
    manifest = bootstrap_manifest()
    features = tuple(
        replace(item, ml_name="ID Volume Current")
        if item.column_key == "id_volume" else item
        for item in manifest.features
    )
    return replace(
        manifest,
        generation=replace(manifest.generation, generation_id="training-export-renamed"),
        features=features,
    )


def _active_snapshot(tmp_path, manifest=None):  # noqa: ANN001, ANN202
    repository = DataDefinitionGenerationRepository(tmp_path / "definition-store")
    repository.publish(manifest or bootstrap_manifest())
    return repository, repository.read_active()


def test_training_header_template_is_exact_saved_registry_contract(tmp_path):
    repository, snapshot = _active_snapshot(tmp_path, _renamed_manifest())
    document = build_training_contract_export(snapshot)
    expected = model_registry_snapshot(snapshot.manifest).training_headers

    assert document.training_headers == expected
    assert document.generation_id == snapshot.manifest.generation.generation_id
    assert document.training_headers[2] == "ID Volume Current"
    assert "ID Volume" not in document.training_headers
    assert not (
        {item.ml_name for item in snapshot.manifest.derived}
        & set(document.training_headers)
    )

    before = repository.read_active()
    destination = tmp_path / "training_headers.csv"
    publish_training_header_template(destination, document)
    after = repository.read_active()
    assert after.manifest == before.manifest

    assert destination.read_bytes().startswith(b"\xef\xbb\xbf")
    with destination.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))
    assert rows == [list(expected)]


def test_definition_reference_crosswalk_is_saved_generation_review_only(tmp_path):
    _repository, snapshot = _active_snapshot(tmp_path)
    document = build_training_contract_export(snapshot)
    destination = tmp_path / "definition_reference.csv"
    publish_definition_reference(destination, document)

    assert destination.read_bytes().startswith(b"\xef\xbb\xbf")
    with destination.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert tuple(rows[0]) == REFERENCE_HEADERS

    cooling = next(item for item in rows if item["column_key"] == "cooling_capa")
    assert cooling["ml_name"] == "Cooling Capa"
    assert cooling["label"] == "냉방능력"
    assert cooling["raw_train_required"] == "Yes"
    assert cooling["training_header_order"] == "1"

    derived = next(item for item in rows if item["definition_kind"] == "Derived")
    assert derived["role"] == "derived"
    assert derived["raw_train_required"] == "No"
    assert derived["training_header_order"] == ""


def test_dirty_draft_is_explicit_and_cannot_replace_saved_train_contract(tmp_path):
    repository, snapshot = _active_snapshot(tmp_path)
    controller = DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    )
    controller.bind_runtime_generation(snapshot)
    controller.refresh()
    baseline = controller.training_contract_export_context()

    state = controller.rename_definition(RenameDefinitionIntent(
        ("schema_row", "cooling_capa"),
        ml_name="Cooling Capacity Draft",
    ))
    assert state.draft_changed

    context = controller.training_contract_export_context()
    assert context.draft_dirty
    assert context.document.generation_id == baseline.document.generation_id
    assert context.document.training_headers == baseline.document.training_headers
    assert "Cooling Capa" in context.document.training_headers
    assert "Cooling Capacity Draft" not in context.document.training_headers
    assert repository.read_active().manifest == snapshot.manifest


def test_export_does_not_touch_canonical_static_feature_catalog(tmp_path):
    _repository, snapshot = _active_snapshot(tmp_path)
    document = build_training_contract_export(snapshot)
    static_catalog = Path("config/ml/features.csv")
    before = static_catalog.read_bytes()

    publish_training_header_template(tmp_path / "headers.csv", document)
    publish_definition_reference(tmp_path / "reference.csv", document)

    assert static_catalog.read_bytes() == before
