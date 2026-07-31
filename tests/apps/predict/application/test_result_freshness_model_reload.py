"""Accepted typed result freshness across atomic Active model reload."""

import pytest

from apps.common.model_lifecycle import ActiveModelResolver, ModelLifecycleRepository
from apps.predict.application.result_contract import PredictionExecutionContext
from apps.predict.application.runtime_snapshot import compatibility_predict_runtime_snapshot
from apps.predict.application.target_outcome import TargetOutcome
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot
from tests.apps.common.model_lifecycle.conftest import publish_candidate


@pytest.fixture
def repository(tmp_path):
    return ModelLifecycleRepository(tmp_path / "lifecycle")


def _activate(repository, candidate_id: str, revision: int) -> None:  # noqa: ANN001
    repository.replace_active(
        candidate_id,
        activated_at=f"2026-08-{revision:02d}T00:00:00+00:00",
        source="test",
        expected_revision=revision - 1,
    )


def _composition(repository):  # noqa: ANN001
    resolution = ActiveModelResolver(repository).resolve()
    return build_predict_workspace_composition(
        runtime_snapshot=compatibility_predict_runtime_snapshot(),
        lifecycle_repository=repository,
        model_resolution=resolution,
        model_file=resolution.model_path,
        initial_empty_rows=1,
    )


def _install_result(composition):  # noqa: ANN001
    case_id = composition.session.case_order[0]
    semantics, model = composition.prediction_controller.execution_environment
    descriptor = composition.runtime_snapshot.target_descriptors[0]
    result = ResultRow(
        case_id,
        "complete",
        target_outcomes=(TargetOutcome(
            descriptor.target_identity,
            descriptor.result_feature_identity,
            descriptor.result_key,
            descriptor.canonical_unit,
            "available",
            raw_value=42.123456789,
        ),),
        execution_context=PredictionExecutionContext(
            composition.session.session_id,
            case_id,
            "accepted-run",
            0,
            semantics,
            model,
        ),
    )
    composition.session.set_result(result)
    return result


def test_successful_model_reload_preserves_typed_result_but_marks_it_stale(repository):
    registry = model_registry_snapshot(bootstrap_manifest())
    first = publish_candidate(repository, registry, "candidate-a")
    second = publish_candidate(repository, registry, "candidate-b")
    _activate(repository, first.manifest.candidate_id, 1)
    composition = _composition(repository)
    original = _install_result(composition)
    _activate(repository, second.manifest.candidate_id, 2)

    outcome = composition.prediction_controller.reload_active_model()
    stale = composition.session.result_for_case(original.case_id)

    assert outcome.status == "reloaded"
    assert stale.freshness == "stale"
    assert stale.stale_reason == "loaded_model_changed"
    assert stale.target_outcomes == original.target_outcomes
    assert stale.execution_context == original.execution_context


def test_failed_reload_preserving_old_model_does_not_change_currentness(repository):
    registry = model_registry_snapshot(bootstrap_manifest())
    first = publish_candidate(repository, registry, "candidate-a")
    second = publish_candidate(repository, registry, "candidate-b")
    _activate(repository, first.manifest.candidate_id, 1)
    composition = _composition(repository)
    original = _install_result(composition)
    _activate(repository, second.manifest.candidate_id, 2)
    second.model_path.write_bytes(b"corrupt")

    outcome = composition.prediction_controller.reload_active_model()

    assert outcome.status == "failed"
    assert outcome.preserved_loaded_model
    assert composition.session.result_for_case(original.case_id) == original
    assert original.freshness == "current"
