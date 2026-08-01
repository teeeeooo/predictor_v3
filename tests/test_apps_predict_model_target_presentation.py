"""Predict model and committed Target presentation regressions."""

from __future__ import annotations

from dataclasses import replace
import os
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication

from apps.predict.application.models import PredictionModelStatus
from apps.predict.application.runtime_snapshot import (
    PredictRuntimeSnapshot,
    compatibility_predict_runtime_snapshot,
)
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ui.shell import PredictShell
from apps.predict.ui.status_widgets import StatusBadge, target_status_badge_state
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.shell import TrainShell
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


class _ModelService:
    def __init__(self, status: str) -> None:
        self.status = status

    def model_status(self) -> PredictionModelStatus:
        return PredictionModelStatus("/internal/model.pkl", self.status)


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
    target_result_keys = {item.result_key for item in base.target_descriptors}
    results = [
        row
        for row in base.predict_projection
        if row.column_key in target_result_keys
    ]
    first, second, third = results[:3]
    runtime_a = _runtime(
        base,
        "target-a",
        (
            ("internal-alpha", first.column_key, "알파 표시 Target"),
            ("internal-beta", second.column_key, "베타 표시 Target"),
        ),
    )
    runtime_b = _runtime(
        base,
        "target-b",
        (
            ("internal-beta", second.column_key, "베타 새 이름"),
            ("internal-gamma", third.column_key, "감마 표시 Target"),
        ),
    )
    return runtime_a, runtime_b


def _runtime(base, generation_id, targets):  # noqa: ANN001, ANN202
    label_by_key = {result_key: label for _target, result_key, label in targets}
    projection = tuple(
        replace(row, label=label_by_key[row.column_key])
        if row.column_key in label_by_key
        else row
        for row in base.predict_projection
    )
    descriptors_by_key = {
        item.result_key: item for item in base.target_descriptors
    }
    target_descriptors = tuple(
        replace(descriptors_by_key[result_key], ml_name=target)
        for target, result_key, _label in targets
    )
    return replace(
        base,
        generation_id=generation_id,
        predict_projection=projection,
        column_descriptors=tuple(
            replace(item, label=label_by_key[item.key])
            if item.key in label_by_key
            else item
            for item in base.column_descriptors
        ),
        active_targets=tuple(target for target, _key, _label in targets),
        target_result_keys=tuple(
            (target, result_key) for target, result_key, _label in targets
        ),
        target_descriptors=target_descriptors,
        target_registry_fingerprint=f"fixture-targets:{generation_id}",
    )


def _composition(runtime, model_status="loaded", *, session=None):  # noqa: ANN001, ANN202
    return build_predict_workspace_composition(
        session=session,
        initial_empty_rows=0 if session is not None else 3,
        runtime_snapshot=runtime,
        prediction_service=_ModelService(model_status),
    )


@pytest.mark.parametrize(
    ("model_status", "expected"),
    (
        ("loaded", "로드됨"),
        ("missing", "없음"),
        ("load-error", "모델 로드 오류"),
    ),
)
def test_initial_model_and_ordered_user_facing_targets(model_status, expected):
    _app()
    runtime_a, _runtime_b = _runtime_pair()
    workspace = PredictWorkspace(
        composition=_composition(runtime_a, model_status)
    )

    assert expected in workspace.model_badge.text()
    assert "/internal" not in workspace.model_badge.text()
    assert "model.pkl" not in workspace.model_badge.text()
    assert "알파 표시 Target 외 1개" in workspace.target_badge.text()
    assert workspace.target_badge.toolTip() == (
        "현재 예측 Target (2): 알파 표시 Target, 베타 표시 Target"
    )


def test_runtime_a_b_a_refresh_replaces_model_and_target_presentation_once():
    app = _app()
    runtime_a, runtime_b = _runtime_pair()
    workspace = PredictWorkspace(composition=_composition(runtime_a))
    target_badge = workspace.target_badge
    workspace.show()
    app.processEvents()

    transitions = (
        (runtime_b, "missing", "베타 새 이름", "감마 표시 Target", "없음"),
        (runtime_a, "loaded", "알파 표시 Target", "베타 표시 Target", "로드됨"),
        (runtime_b, "load-error", "베타 새 이름", "감마 표시 Target", "모델 로드 오류"),
        (runtime_a, "loaded", "알파 표시 Target", "베타 표시 Target", "로드됨"),
    )
    for runtime, model_status, first, second, expected_model in transitions:
        workspace.apply_runtime_composition(
            _composition(runtime, model_status, session=workspace.session)
        )
        app.processEvents()

        assert workspace.target_badge is target_badge
        assert first in workspace.target_badge.text()
        assert workspace.target_badge.toolTip().endswith(f"{first}, {second}")
        assert expected_model in workspace.model_badge.text()
        badges = workspace.model_target_strip.findChildren(StatusBadge)
        assert badges == [workspace.model_badge, workspace.target_badge]


def test_empty_target_projection_is_safe_and_bounded():
    base = compatibility_predict_runtime_snapshot()
    value, kind, tooltip = target_status_badge_state((), (), ())

    assert base.active_targets
    assert (value, kind) == ("없음", "missing")
    assert tooltip == "현재 활성 예측 Target이 없습니다."

    long_label = "매우 긴 사용자 표시 Target 이름이 상태 영역을 넓히지 않아야 합니다"
    value, kind, tooltip = target_status_badge_state(
        ("internal-target",),
        (("internal-target", "result-key"),),
        (SimpleNamespace(group="result", key="result-key", header=long_label),),
    )
    assert value.endswith("…")
    assert len(value) == 24
    assert kind == "ready"
    assert tooltip.endswith(long_label)


def test_incomplete_typed_runtime_contract_fails_before_composition():
    runtime = replace(
        compatibility_predict_runtime_snapshot(), target_descriptors=()
    )

    with pytest.raises(ValueError, match="Target contract is empty"):
        _composition(runtime)


def test_standalone_and_embedded_show_the_same_shared_presentation():
    app = _app()
    runtime_a, _runtime_b = _runtime_pair()
    standalone = PredictShell(composition=_composition(runtime_a))
    service = DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    embedded_shell = TrainShell(
        data_definition_controller=DataDefinitionController(service),
        predict_composition=_composition(runtime_a),
    )
    standalone.resize(720, 480)
    embedded_shell.resize(720, 480)
    standalone.show()
    embedded_shell.show()
    app.processEvents()
    embedded = embedded_shell.predict_workspace

    assert tuple(
        item.ml_name for item in runtime_a.target_descriptors
    ) == runtime_a.active_targets
    assert tuple(
        (item.ml_name, item.result_key)
        for item in runtime_a.target_descriptors
    ) == runtime_a.target_result_keys

    assert standalone.workspace.model_target_strip.isVisibleTo(standalone.workspace)
    assert embedded.model_target_strip.isVisibleTo(embedded)
    assert standalone.workspace.rect().contains(
        standalone.workspace.model_target_strip.geometry()
    )
    assert embedded.rect().contains(embedded.model_target_strip.geometry())
    assert standalone.workspace.model_badge.text() == embedded.model_badge.text()
    assert standalone.workspace.target_badge.text() == embedded.target_badge.text()
    assert standalone.workspace.target_badge.toolTip() == embedded.target_badge.toolTip()
