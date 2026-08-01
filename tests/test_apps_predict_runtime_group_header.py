"""Runtime projection synchronization tests for the Predict group header."""

from __future__ import annotations

from dataclasses import replace
import os

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

from apps.predict.application.models import PredictionModelStatus
from apps.predict.application.runtime_snapshot import (
    PredictRuntimeSnapshot,
    build_predict_runtime_snapshot,
    compatibility_predict_runtime_snapshot,
)
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ui.shell import PredictShell
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.shell import TrainShell
from core.data_definition.contract import bootstrap_manifest
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH
from tests.helpers.generation_authority import repository_issued_generation


class _LoadedPredictionService:
    def model_status(self) -> PredictionModelStatus:
        return PredictionModelStatus("fake", "loaded")


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _cleanup_qt_widgets():
    yield
    app = QApplication.instance()
    if app is None:
        return
    for widget in QApplication.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    app.processEvents()


def _runtime_pair() -> tuple[PredictRuntimeSnapshot, PredictRuntimeSnapshot]:
    base = compatibility_predict_runtime_snapshot()
    reduced_rows = list(base.predict_projection)
    removed = next(
        index
        for index, row in enumerate(reduced_rows)
        if row.active and row.visible and row.role == "input"
    )
    reduced_rows = [
        replace(row, visible=False)
        if index == removed or (row.active and row.visible and row.role == "auto")
        else row
        for index, row in enumerate(reduced_rows)
    ]
    hidden_keys = {
        base.predict_projection[removed].column_key,
        *(
            item.column_key for item in base.predict_projection
            if item.active and item.visible and item.role == "auto"
        ),
    }
    manifest = bootstrap_manifest()
    reduced_manifest = replace(
        manifest,
        generation=replace(
            manifest.generation,
            generation_id="group-header-reduced",
        ),
        features=tuple(
            replace(item, visible=False)
            if item.column_key in hidden_keys else item
            for item in manifest.features
        ),
    )
    full_manifest = replace(
        manifest,
        generation=replace(
            manifest.generation,
            generation_id="group-header-full",
        ),
    )
    reduced = build_predict_runtime_snapshot(
        repository_issued_generation(reduced_manifest)
    )
    full = build_predict_runtime_snapshot(
        repository_issued_generation(full_manifest)
    )
    return reduced, full


def _composition(runtime, *, session=None):  # noqa: ANN001, ANN202
    return build_predict_workspace_composition(
        session=session,
        initial_empty_rows=0 if session is not None else 3,
        runtime_snapshot=runtime,
        prediction_service=_LoadedPredictionService(),
    )


def _assert_group_geometry(workspace: PredictWorkspace) -> None:
    table = workspace.case_table
    header = table.horizontalHeader()
    viewport_left = table.verticalHeader().width()
    visible_right = viewport_left + table.viewport().width()
    columns = workspace.case_model.columns
    full_rects = workspace.group_header.group_column_rects()
    visible_rects = workspace.group_header.group_rects()
    groups = tuple(dict.fromkeys(column.group for column in columns if column.group))

    assert tuple(full_rects) == groups
    assert tuple(visible_rects) == groups
    assert tuple(workspace.group_header._labels) == groups
    assert workspace.group_header._columns == columns

    for group in groups:
        indexes = [
            index for index, column in enumerate(columns) if column.group == group
        ]
        first, last = indexes[0], indexes[-1]
        left = viewport_left + header.sectionViewportPosition(first)
        right = (
            viewport_left
            + header.sectionViewportPosition(last)
            + header.sectionSize(last)
        )
        expected_full = QRect(
            left,
            0,
            max(0, right - left),
            workspace.group_header.height(),
        )
        clipped_left = max(left, viewport_left)
        clipped_right = min(right, visible_right)
        expected_visible = QRect(
            clipped_left,
            0,
            max(0, clipped_right - clipped_left),
            workspace.group_header.height(),
        )
        assert full_rects[group] == expected_full
        assert visible_rects[group] == expected_visible
        assert workspace.group_header._labels[group].geometry() == expected_visible


def _assert_scroll_positions(workspace: PredictWorkspace) -> None:
    scroll_bar = workspace.case_table.horizontalScrollBar()
    assert scroll_bar.maximum() > 0
    for value in (scroll_bar.minimum(), scroll_bar.maximum() // 2, scroll_bar.maximum()):
        scroll_bar.setValue(value)
        QApplication.processEvents()
        _assert_group_geometry(workspace)
    status_rect = workspace.group_header.group_rects()["status"]
    assert status_rect.width() > 0
    assert workspace.group_header._labels["status"].isVisible()


def test_runtime_refresh_rebinds_removed_added_and_repeated_projections():
    app = _app()
    reduced, full = _runtime_pair()
    initial = _composition(full)
    workspace = PredictWorkspace(composition=initial)
    workspace.resize(1200, 760)
    workspace.show()
    app.processEvents()
    _assert_scroll_positions(workspace)

    for runtime in (reduced, full, reduced, full):
        prior_scroll = workspace.case_table.horizontalScrollBar().maximum() // 2
        workspace.case_table.horizontalScrollBar().setValue(prior_scroll)
        old_model = workspace.case_model
        composition = _composition(runtime, session=workspace.session)

        workspace.apply_runtime_composition(composition)
        app.processEvents()

        assert workspace.case_table.horizontalScrollBar().value() == min(
            prior_scroll,
            workspace.case_table.horizontalScrollBar().maximum(),
        )
        assert workspace.case_model is not old_model
        _assert_scroll_positions(workspace)


def test_runtime_refresh_disconnects_old_model_and_does_not_duplicate_new_model():
    app = _app()
    reduced, full = _runtime_pair()
    workspace = PredictWorkspace(composition=_composition(full))
    workspace.show()
    app.processEvents()
    old_models = []

    for runtime in (reduced, full, reduced):
        old_models.append(workspace.case_model)
        workspace.apply_runtime_composition(
            _composition(runtime, session=workspace.session)
        )

    calls = []
    original_update = workspace.group_header.update_geometry

    def record_update():
        calls.append("updated")
        original_update()

    workspace.group_header.update_geometry = record_update
    for old_model in old_models:
        old_model.modelReset.emit()
    assert calls == []

    workspace.case_model.modelReset.emit()
    assert calls == ["updated"]


def test_runtime_refresh_recovers_after_section_and_workspace_resize_and_row_reset():
    app = _app()
    reduced, full = _runtime_pair()
    workspace = PredictWorkspace(composition=_composition(reduced))
    workspace.resize(720, 480)
    workspace.show()
    app.processEvents()

    workspace.apply_runtime_composition(
        _composition(full, session=workspace.session)
    )
    section = next(
        index
        for index, column in enumerate(workspace.case_model.columns)
        if column.group == "auto"
    )
    workspace.case_table.setColumnWidth(
        section, workspace.case_table.columnWidth(section) + 37
    )
    app.processEvents()
    _assert_group_geometry(workspace)

    workspace.resize(1200, 760)
    workspace._append_row()
    workspace._reset_rows()
    app.processEvents()

    assert workspace.case_model.rowCount() == 3
    assert workspace.bottom_status.isVisibleTo(workspace)
    assert workspace.case_table.horizontalScrollBar().maximum() > 0
    _assert_scroll_positions(workspace)


def test_standalone_and_embedded_predict_consume_the_same_runtime_rebind():
    app = _app()
    reduced, full = _runtime_pair()
    standalone = PredictShell(composition=_composition(reduced))
    definition_service = DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    embedded_shell = TrainShell(
        data_definition_controller=DataDefinitionController(definition_service),
        predict_composition=_composition(reduced),
    )
    standalone.show()
    embedded_shell.show()
    app.processEvents()

    for workspace in (standalone.workspace, embedded_shell.predict_workspace):
        workspace.apply_runtime_composition(
            _composition(full, session=workspace.session)
        )
        app.processEvents()
        _assert_scroll_positions(workspace)
        assert workspace.bottom_status.isVisibleTo(workspace)
