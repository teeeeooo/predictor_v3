"""Train Target presentation parity for committed runtime registries."""

import os
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from apps.common.runtime_generation import (  # noqa: E402
    GenerationCandidate,
    GenerationSnapshot,
)
from apps.train.application.runtime_generation import TrainRuntimeParticipant  # noqa: E402
from apps.train.controllers.train_controller import TrainController  # noqa: E402
from apps.train.state.training_run_state import TrainingResult  # noqa: E402
from apps.train.ui.train_model_panel import TrainModelPanel  # noqa: E402
from core.data_definition.contract import (  # noqa: E402
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
    validate_contract,
)


def _snapshot(manifest) -> GenerationSnapshot:  # noqa: ANN001
    return GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )


def _candidate(snapshot, participant) -> GenerationCandidate:  # noqa: ANN001
    return GenerationCandidate(
        snapshot,
        snapshot.manifest.generation.generation_id,
        ((participant.name, participant.revision_token()),),
        uuid4().hex,
    )


def _manifest_pair(change: str):
    active = bootstrap_manifest()
    if change == "enable":
        last = active.targets[-1]
        feature_id = last.feature_identity
        active = replace(
            active,
            features=tuple(
                replace(item, active=False)
                if item.identity == feature_id else item
                for item in active.features
            ),
            targets=tuple(
                replace(item, active=False)
                if item.identity == last.identity else item
                for item in active.targets
            ),
            ordering=replace(
                active.ordering,
                ml=tuple(
                    identity for identity in active.ordering.ml
                    if identity != feature_id
                ),
            ),
        )
        candidate = replace(
            active,
            features=tuple(
                replace(item, active=True)
                if item.identity == feature_id else item
                for item in active.features
            ),
            targets=tuple(
                replace(item, active=True)
                if item.identity == last.identity else item
                for item in active.targets
            ),
            ordering=replace(
                active.ordering,
                ml=(*active.ordering.ml, feature_id),
            ),
        )
    elif change == "add":
        source_feature = next(
            item
            for item in active.features
            if item.identity == active.targets[-1].feature_identity
        )
        source_target = active.targets[-1]
        feature = replace(
            source_feature,
            identity="feature-audit-result",
            column_key="audit_result",
            label="Audit Result",
            ml_name="Audit Result",
            display_order=max(item.display_order for item in active.features) + 1,
        )
        target = replace(
            source_target,
            identity="target-audit-result",
            feature_identity=feature.identity,
            ml_name=feature.ml_name,
            presentation_order=max(
                item.presentation_order for item in active.targets
            ) + 1,
            registry_order=max(item.registry_order for item in active.targets) + 1,
        )
        candidate = replace(
            active,
            features=(*active.features, feature),
            targets=(*active.targets, target),
            ordering=replace(
                active.ordering,
                predict=(*active.ordering.predict, feature.identity),
                ml=(*active.ordering.ml, feature.identity),
                targets=(*active.ordering.targets, target.identity),
            ),
        )
    elif change == "disable":
        removed = active.targets[1]
        candidate = replace(
            active,
            features=tuple(
                replace(item, active=False)
                if item.identity == removed.feature_identity else item
                for item in active.features
            ),
            targets=tuple(
                replace(item, active=False)
                if item.identity == removed.identity else item
                for item in active.targets
            ),
            ordering=replace(
                active.ordering,
                ml=tuple(
                    identity for identity in active.ordering.ml
                    if identity != removed.feature_identity
                ),
            ),
        )
    elif change == "rename":
        renamed = active.targets[0]
        candidate = replace(
            active,
            targets=(replace(renamed, ml_name="Cooling Power V2"), *active.targets[1:]),
            features=tuple(
                replace(item, ml_name="Cooling Power V2")
                if item.identity == renamed.feature_identity else item
                for item in active.features
            ),
        )
    elif change == "reorder":
        targets = tuple(
            replace(item, presentation_order=index)
            for index, item in enumerate(reversed(active.targets), 1)
        )
        candidate = replace(
            active,
            targets=targets,
            ordering=replace(
                active.ordering,
                targets=tuple(item.identity for item in targets),
            ),
        )
    else:
        raise AssertionError(change)
    candidate = replace(
        candidate,
        generation=replace(candidate.generation, generation_id=f"generation-{change}"),
    )
    assert not validate_contract(active)
    assert not validate_contract(candidate)
    return _snapshot(active), _snapshot(candidate)


def _summary_targets(panel: TrainModelPanel) -> tuple[str, ...]:
    model = panel.summary_table.model()
    return tuple(model.data(model.index(row, 1)) for row in range(model.rowCount()))


class _HoldingExecution:
    def __init__(self) -> None:
        self.request = None
        self.callbacks = None
        self.disposed = False

    @property
    def is_running(self) -> bool:
        return self.request is not None and not self.disposed

    def start(self, request, callbacks=None) -> None:  # noqa: ANN001
        self.request = request
        self.callbacks = callbacks

    def cancel(self) -> bool:
        return True

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture(autouse=True)
def _cleanup_widgets():
    yield
    app = QApplication.instance()
    if app is not None:
        for widget in QApplication.topLevelWidgets():
            widget.close()
            widget.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("change", ("add", "enable", "disable", "rename", "reorder"))
def test_idle_registry_commit_refreshes_every_target_presentation(change):
    QApplication.instance() or QApplication([])
    active, candidate = _manifest_pair(change)
    participant = TrainRuntimeParticipant(active)
    controller = TrainController(registry_provider=lambda: participant.registry_snapshot)
    panel = TrainModelPanel(controller=controller)

    prepared = participant.prepare(_candidate(candidate, participant))
    participant.commit(prepared)
    panel.refresh_runtime_registry()
    expected = participant.registry_snapshot.active_target_names

    assert panel.targets == expected
    assert _summary_targets(panel) == expected
    assert panel.target_list_layout.count() == len(expected)
    assert panel.target_count_heading.text().endswith(f"({len(expected)})")
    assert panel.target_count_metric_value.text() == str(len(expected))
    assert panel.complete_metric_value.text() == "0"
    assert panel.running_metric_value.text() == "0"
    assert panel.waiting_metric_value.text() == str(len(expected))
    assert tuple(
        panel.target_list_layout.itemAt(index).widget().layout().itemAt(1).widget().text()
        for index in range(panel.target_list_layout.count())
    ) == expected


def test_running_a_keeps_a_summary_until_terminal_then_applies_b_idle_and_new_run(
    tmp_path,
):
    QApplication.instance() or QApplication([])
    active, candidate = _manifest_pair("rename")
    participant = TrainRuntimeParticipant(active)
    executions = []

    def execution_factory():
        execution = _HoldingExecution()
        executions.append(execution)
        return execution

    controller = TrainController(
        execution_factory=execution_factory,
        registry_provider=lambda: participant.registry_snapshot,
    )
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("header\n", encoding="utf-8")
    panel.set_data_path(str(data_path))
    targets_a = panel.targets

    panel._run_training()
    running_request = controller.active_request
    assert running_request is not None
    assert running_request.generation_id == active.manifest.generation.generation_id
    assert _summary_targets(panel) == targets_a

    participant.commit(participant.prepare(_candidate(candidate, participant)))
    targets_b = participant.registry_snapshot.active_target_names
    panel.refresh_runtime_registry()

    assert controller.active_request is running_request
    assert panel.targets == targets_a
    assert _summary_targets(panel) == targets_a
    assert "Running generation" in panel.status_label.text()
    assert running_request.generation_id in panel.status_label.text()
    assert candidate.manifest.generation.generation_id in panel.status_label.text()

    executions[0].callbacks.finished(TrainingResult(
        run_id=running_request.run_id,
        status="complete",
        generation_id=running_request.generation_id,
    ))
    assert controller.active_request is None
    assert panel.targets == targets_b
    assert _summary_targets(panel) == targets_b
    assert all(
        panel.summary_table.model().data(panel.summary_table.model().index(row, 2))
        == "대기 중"
        for row in range(panel.summary_table.model().rowCount())
    )
    assert panel.waiting_metric_value.text() == str(len(targets_b))

    panel._run_training()
    assert controller.active_request is not None
    assert controller.active_request.generation_id == candidate.manifest.generation.generation_id
    assert executions[1].request.generation_id == candidate.manifest.generation.generation_id
