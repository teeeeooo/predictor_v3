"""Predict-owned canonical identity descriptor regressions."""

from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path
import subprocess
import sys

import pytest

from apps.common.runtime_generation import GenerationSnapshot
from apps.predict.application.runtime_snapshot import build_predict_runtime_snapshot
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.schema.case_table_schema_adapter import (
    build_case_table_column_schema,
)
from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    manifest_payload,
    scoped_fingerprints,
)
from core.predictor_schema.catalog_v2 import REQUIRED_HEADERS


def _snapshot(manifest) -> GenerationSnapshot:  # noqa: ANN001
    return GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )


def test_descriptor_carries_canonical_identity_and_current_generation_metadata():
    manifest = bootstrap_manifest()
    runtime = build_predict_runtime_snapshot(_snapshot(manifest))
    owner_by_identity = {item.identity: item for item in manifest.features}

    assert [item.feature_identity for item in runtime.column_descriptors] == list(
        manifest.ordering.predict
    )
    with pytest.raises(FrozenInstanceError):
        runtime.column_descriptors[0].label = "mutable"  # type: ignore[misc]
    for descriptor in runtime.column_descriptors:
        owner = owner_by_identity[descriptor.feature_identity]
        assert (
            descriptor.key,
            descriptor.label,
            descriptor.role,
            descriptor.visible,
            descriptor.display_order,
        ) == (
            owner.column_key,
            owner.label,
            owner.role,
            owner.visible,
            owner.display_order,
        )
        assert (
            descriptor.value_source,
            descriptor.mapping_entity,
            descriptor.mapping_attribute,
            descriptor.trigger_column,
            descriptor.rule_id,
        ) == (
            owner.value_source,
            owner.mapping_entity,
            owner.mapping_attribute,
            owner.trigger_column,
            owner.rule_id,
        )

    columns = build_case_table_column_schema(runtime.column_descriptors)
    generated = tuple(column for column in columns if not column.virtual)
    assert all(column.feature_identity for column in generated)
    assert all(
        column.classification in {"input", "auto", "result"}
        for column in generated
    )
    assert all(
        column.editable == (column.classification == "input" and not column.readonly)
        for column in generated
    )
    virtual = tuple(column for column in columns if column.virtual)
    assert [column.key for column in virtual] == ["status", "message"]
    assert all(column.feature_identity is None for column in virtual)
    assert all(column.classification == "app_virtual" for column in virtual)


def test_generation_rename_order_visibility_show_hide_and_add_follow_identity():
    manifest = bootstrap_manifest()
    visible = tuple(
        item for item in manifest.features
        if item.active and item.visible and item.role in {"input", "auto", "result"}
    )
    renamed, hidden, shown = visible[:3]
    manifest_a = replace(
        manifest,
        features=tuple(
            replace(item, visible=False)
            if item.identity == shown.identity else item
            for item in manifest.features
        ),
    )
    runtime_a = build_predict_runtime_snapshot(_snapshot(manifest_a))

    added = replace(
        renamed,
        identity="feature-predict-added",
        column_key="predict_added",
        label="Predict Added",
        ml_name="",
        model_input_enabled=False,
        display_order=max(item.display_order for item in manifest.features) + 10,
    )
    order_b = list(manifest_a.ordering.predict)
    order_b.remove(renamed.identity)
    order_b.insert(3, renamed.identity)
    order_b.append(added.identity)
    changed_by_identity = {
        item.identity: (
            replace(
                item,
                column_key="renamed_runtime_key",
                label="Renamed generation label",
            )
            if item.identity == renamed.identity
            else replace(item, visible=False)
            if item.identity == hidden.identity
            else replace(item, visible=True)
            if item.identity == shown.identity
            else item
        )
        for item in (*manifest_a.features, added)
    }
    features_b = tuple(
        replace(
            changed_by_identity[identity],
            display_order=(index + 1) * 10,
        )
        for index, identity in enumerate(order_b)
    )
    manifest_b = replace(
        manifest_a,
        generation=replace(manifest_a.generation, generation_id="generation-b"),
        features=features_b,
        ordering=replace(manifest_a.ordering, predict=tuple(order_b)),
    )
    runtime_b = build_predict_runtime_snapshot(_snapshot(manifest_b))
    descriptor_by_identity = {
        item.feature_identity: item for item in runtime_b.column_descriptors
    }

    renamed_descriptor = descriptor_by_identity[renamed.identity]
    assert renamed_descriptor.key == "renamed_runtime_key"
    assert renamed_descriptor.label == "Renamed generation label"
    assert renamed_descriptor.feature_identity == renamed.identity
    assert next(
        item for item in runtime_a.column_descriptors
        if item.feature_identity == shown.identity
    ).visible is False
    assert descriptor_by_identity[shown.identity].visible is True
    assert descriptor_by_identity[hidden.identity].visible is False
    assert descriptor_by_identity[added.identity].classification == "input"

    columns = build_case_table_column_schema(runtime_b.column_descriptors)
    feature_columns = tuple(item for item in columns if item.feature_identity)
    assert hidden.identity not in {item.feature_identity for item in feature_columns}
    assert shown.identity in {item.feature_identity for item in feature_columns}
    assert added.identity in {item.feature_identity for item in feature_columns}
    assert [item.display_order for item in feature_columns] == sorted(
        item.display_order for item in feature_columns
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("duplicate", "identity is duplicated"),
        ("missing", "identity is missing"),
        ("incomplete_projection", "generated projection is incomplete"),
    ),
)
def test_invalid_identity_or_projection_fails_fast(mutation, message):
    snapshot = _snapshot(bootstrap_manifest())
    if mutation == "duplicate":
        manifest = replace(
            snapshot.manifest,
            features=(
                snapshot.manifest.features[0],
                replace(
                    snapshot.manifest.features[1],
                    identity=snapshot.manifest.features[0].identity,
                ),
                *snapshot.manifest.features[2:],
            ),
        )
        invalid = replace(snapshot, manifest=manifest)
    elif mutation == "missing":
        manifest = replace(
            snapshot.manifest,
            features=(
                replace(snapshot.manifest.features[0], identity=""),
                *snapshot.manifest.features[1:],
            ),
        )
        invalid = replace(snapshot, manifest=manifest)
    else:
        projections = replace(
            snapshot.projections,
            predict=snapshot.projections.predict[:-1],
        )
        invalid = replace(snapshot, projections=projections)

    with pytest.raises(ValueError, match=message):
        build_predict_runtime_snapshot(invalid)


def test_standalone_and_embedded_composition_share_descriptor_projection():
    runtime = build_predict_runtime_snapshot(_snapshot(bootstrap_manifest()))

    standalone = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=0,
    )
    embedded = build_predict_workspace_composition(
        runtime_snapshot=runtime,
        initial_empty_rows=0,
    )

    assert standalone.columns == embedded.columns
    assert standalone.runtime_snapshot.column_descriptors == (
        embedded.runtime_snapshot.column_descriptors
    )
    assert standalone.runtime_snapshot.target_descriptors == (
        embedded.runtime_snapshot.target_descriptors
    )
    assert standalone.prediction_controller.execution_environment == (
        embedded.prediction_controller.execution_environment
    )
    assert {
        item.feature_identity
        for item in standalone.columns
        if item.feature_identity is not None
    } == {
        item.feature_identity
        for item in embedded.columns
        if item.feature_identity is not None
    }


def test_runtime_descriptor_is_qt_free_and_does_not_change_serialized_shapes():
    manifest = bootstrap_manifest()
    snapshot = _snapshot(manifest)
    persisted_before = manifest_payload(manifest)
    generated_before = tuple(asdict(row) for row in snapshot.projections.predict)

    build_predict_runtime_snapshot(snapshot)

    assert manifest_payload(manifest) == persisted_before
    assert tuple(asdict(row) for row in snapshot.projections.predict) == generated_before
    assert "identity" not in REQUIRED_HEADERS
    assert "feature_identity" not in REQUIRED_HEADERS
    code = (
        "import sys; "
        "from apps.predict.application.runtime_snapshot "
        "import compatibility_predict_runtime_snapshot; "
        "from apps.predict.schema.case_table_schema_adapter "
        "import build_case_table_column_schema; "
        "from apps.predict.application.result_contract "
        "import PredictionExecutionContext; "
        "from apps.predict.application.target_outcome import TargetOutcome; "
        "from apps.predict.state.result_row import ResultRow; "
        "runtime = compatibility_predict_runtime_snapshot(); "
        "assert runtime.column_descriptors; "
        "assert runtime.target_descriptors; "
        "assert build_case_table_column_schema(runtime.column_descriptors); "
        "assert 'PySide6' not in sys.modules"
    )
    subprocess.run([sys.executable, "-B", "-c", code], check=True)


def test_unknown_active_target_identity_fails_without_inventing_a_unit():
    manifest = bootstrap_manifest()
    target = manifest.targets[0]
    unknown = replace(target, identity="unknown-active-target")
    candidate = replace(
        manifest,
        targets=(unknown, *manifest.targets[1:]),
        ordering=replace(
            manifest.ordering,
            targets=(unknown.identity, *manifest.ordering.targets[1:]),
        ),
    )

    with pytest.raises(ValueError, match="canonical unit is missing"):
        build_predict_runtime_snapshot(_snapshot(candidate))
