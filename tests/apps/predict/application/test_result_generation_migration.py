"""Stable-identity Predict Result migration across runtime generations."""

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
from apps.predict.application.model_compatibility import (  # noqa: E402
    ModelCompatibilityEvidence,
)
from apps.predict.application.runtime_generation_participant import (  # noqa: E402
    PredictRuntimeParticipant,
)
from apps.predict.application.runtime_snapshot import (  # noqa: E402
    build_predict_runtime_snapshot,
)
from apps.predict.composition import build_predict_workspace_composition  # noqa: E402
from apps.predict.state.result_row import ResultRow  # noqa: E402
from apps.predict.ui.workspace import PredictWorkspace  # noqa: E402
from apps.train.application.runtime_generation.participants import (  # noqa: E402
    ParticipantPrepareError,
)
from core.data_definition.contract import (  # noqa: E402
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
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


def _participant(active, candidate, tmp_path, *, rows=1):  # noqa: ANN001
    composition = build_predict_workspace_composition(
        runtime_snapshot=build_predict_runtime_snapshot(active),
        initial_empty_rows=rows,
    )
    participant = PredictRuntimeParticipant(
        active,
        composition,
        model_file=str(tmp_path / "model.pkl"),
        compatibility_inspector=lambda _path, _snapshot: ModelCompatibilityEvidence(
            "compatible", "ok"
        ),
    )
    return composition, participant, _candidate(candidate, participant)


def _renamed_result_pair():  # noqa: ANN201
    manifest_a = bootstrap_manifest()
    target = manifest_a.targets[0]
    result = next(
        item for item in manifest_a.features if item.identity == target.feature_identity
    )
    manifest_b = replace(
        manifest_a,
        generation=replace(manifest_a.generation, generation_id="generation-b"),
        features=tuple(
            replace(
                item,
                column_key="cooling_power_v2",
                ml_name="Cooling Power V2",
            )
            if item.identity == result.identity else item
            for item in manifest_a.features
        ),
        targets=(
            replace(target, ml_name="Cooling Power V2"),
            *manifest_a.targets[1:],
        ),
    )
    return _snapshot(manifest_a), _snapshot(manifest_b), result.identity


@pytest.fixture(autouse=True)
def _cleanup_widgets():
    yield
    app = QApplication.instance()
    if app is not None:
        for widget in QApplication.topLevelWidgets():
            widget.close()
            widget.deleteLater()
        app.processEvents()


def test_result_and_target_rename_moves_existing_value_to_committed_table_model(
    tmp_path,
):
    QApplication.instance() or QApplication([])
    active, candidate, _identity = _renamed_result_pair()
    composition, participant, transition = _participant(
        active, candidate, tmp_path
    )
    workspace = PredictWorkspace(composition=composition)
    case_id = composition.session.case_order[0]
    original = ResultRow(
        case_id,
        "complete",
        {"cooling_power": "123"},
        "original result",
    )
    composition.session.set_result(original)
    old_column = next(
        index
        for index, column in enumerate(workspace.case_model.columns)
        if column.key == "cooling_power"
    )

    prepared = participant.prepare(transition)
    assert workspace.case_model.cell_value(0, old_column) == "123"
    assert composition.session.result_for_case(case_id) == original

    prior = participant.commit(prepared)
    workspace.apply_runtime_composition(participant.composition)
    migrated = composition.session.result_for_case(case_id)
    new_column = next(
        index
        for index, column in enumerate(workspace.case_model.columns)
        if column.key == "cooling_power_v2"
    )
    assert workspace.case_model.cell_value(0, new_column) == "123"
    assert migrated.result_values == {"cooling_power_v2": "123"}
    assert migrated.status == "complete"
    assert migrated.message == "original result"
    assert participant.composition.result_mapper.active_targets[0] == "Cooling Power V2"
    assert participant.composition.runtime_snapshot.target_result_keys[0] == (
        "Cooling Power V2", "cooling_power_v2"
    )
    assert participant.active_generation_id == "generation-b"

    participant.rollback(prior)
    workspace.apply_runtime_composition(participant.composition)
    restored = composition.session.result_for_case(case_id)
    restored_column = next(
        index
        for index, column in enumerate(workspace.case_model.columns)
        if column.key == "cooling_power"
    )
    assert workspace.case_model.cell_value(0, restored_column) == "123"
    assert restored == original
    assert participant.active_generation_id == active.manifest.generation.generation_id


def test_added_removed_hidden_and_unchanged_results_follow_canonical_identity(
    tmp_path,
):
    bootstrap = bootstrap_manifest()
    added_target = bootstrap.targets[-1]
    added_feature_id = added_target.feature_identity
    manifest_a = replace(
        bootstrap,
        features=tuple(
            replace(item, active=False)
            if item.identity == added_feature_id else item
            for item in bootstrap.features
        ),
        targets=tuple(
            replace(item, active=False)
            if item.identity == added_target.identity else item
            for item in bootstrap.targets
        ),
        ordering=replace(
            bootstrap.ordering,
            ml=tuple(
                identity for identity in bootstrap.ordering.ml
                if identity != added_feature_id
            ),
        ),
    )
    removed_target = manifest_a.targets[1]
    hidden_target = manifest_a.targets[2]
    manifest_b = replace(
        manifest_a,
        generation=replace(manifest_a.generation, generation_id="generation-b"),
        features=tuple(
            replace(item, active=False)
            if item.identity == removed_target.feature_identity
            else replace(item, visible=False)
            if item.identity == hidden_target.feature_identity
            else replace(item, active=True)
            if item.identity == added_feature_id
            else item
            for item in manifest_a.features
        ),
        targets=tuple(
            replace(item, active=False)
            if item.identity == removed_target.identity
            else replace(item, active=True)
            if item.identity == added_target.identity
            else item
            for item in manifest_a.targets
        ),
        ordering=replace(
            manifest_a.ordering,
            ml=tuple(
                identity for identity in manifest_a.ordering.ml
                if identity != removed_target.feature_identity
            ) + (added_feature_id,),
        ),
    )
    active, candidate = _snapshot(manifest_a), _snapshot(manifest_b)
    composition, participant, transition = _participant(
        active, candidate, tmp_path
    )
    case_id = composition.session.case_order[0]
    key_by_identity = {
        item.identity: item.column_key for item in manifest_a.features
    }
    unchanged_key = key_by_identity[manifest_a.targets[0].feature_identity]
    removed_key = key_by_identity[removed_target.feature_identity]
    hidden_key = key_by_identity[hidden_target.feature_identity]
    added_key = key_by_identity[added_feature_id]
    composition.session.set_result(ResultRow(
        case_id,
        "complete",
        {
            unchanged_key: "unchanged",
            removed_key: "removed",
            hidden_key: "hidden",
            added_key: "must-not-copy",
        },
        "keep status and message",
    ))

    prepared = participant.prepare(transition)
    assert composition.session.result_for_case(case_id).result_values[removed_key] == "removed"
    participant.commit(prepared)
    migrated = composition.session.result_for_case(case_id)

    assert migrated.result_values[unchanged_key] == "unchanged"
    assert migrated.result_values[hidden_key] == "hidden"
    assert removed_key not in migrated.result_values
    assert added_key not in migrated.result_values
    assert hidden_key not in {
        column.key for column in participant.composition.columns
    }
    assert migrated.status == "complete"
    assert migrated.message == "keep status and message"


@pytest.mark.parametrize("mutation", ("clear", "running", "complete"))
def test_result_mutation_after_prepare_rejects_without_overwriting_latest(
    tmp_path, mutation
):
    active, candidate, _identity = _renamed_result_pair()
    composition, participant, transition = _participant(
        active, candidate, tmp_path
    )
    case_id = composition.session.case_order[0]
    composition.session.set_result(ResultRow(
        case_id, "complete", {"cooling_power": "100"}, "before"
    ))
    prepared = participant.prepare(transition)
    if mutation == "clear":
        composition.session.clear_result(case_id)
    elif mutation == "running":
        composition.session.set_result(ResultRow(
            case_id, "running", {"cooling_power": "101"}, "progress"
        ))
    else:
        composition.session.set_result(ResultRow(
            case_id, "complete", {"cooling_power": "102"}, "latest"
        ))
    latest = composition.session.snapshot_runtime_projection()

    with pytest.raises(ParticipantPrepareError) as error:
        participant.commit(prepared)

    assert error.value.code == "predict_revision_stale"
    assert composition.session.snapshot_runtime_projection() == latest
    assert participant.active_generation_id == active.manifest.generation.generation_id
