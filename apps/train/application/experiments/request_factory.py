"""Resolved Experiment Specification to immutable TrainingRequest mapping."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from apps.train.application.experiments.contracts import (
    ExperimentContractError,
    ResolvedExperiment,
    optimization_config,
)
from apps.train.application.experiments.resolution import (
    resolve_derived,
    resolve_registry,
    resolve_target_ids,
)
from apps.train.state.training_run_state import TrainingRequest


def gui_specification(snapshot, data_path: str) -> dict:  # noqa: ANN001
    return {
        "schema_version": "predictor_v3.experiment.v1",
        "experiment": {
            "name": "gui-training",
            "purpose": "Train UI requested model training.",
        },
        "data": {"source_path": data_path},
        "targets": {
            "primary": list(snapshot.target_presentation_order),
            "production_required": list(snapshot.target_presentation_order),
        },
    }


def build_training_request(
    lifecycle,  # noqa: ANN001
    resolved: ResolvedExperiment,
    *,
    run_id: str,
    candidate_id: str,
    execution_owner: str,
    campaign_id: str,
    derived_snapshot_provider=None,  # noqa: ANN001
    data_path_override: str | None = None,
) -> TrainingRequest:
    payload = resolved.payload
    source = Path(data_path_override or payload["data"]["source_path"])
    if not source.exists() or not source.is_file():
        raise ExperimentContractError(
            "training_data_invalid", f"Training data is not a file: {source}"
        )
    current = lifecycle.registry_snapshot()
    snapshot = resolve_registry(current, payload)
    derived = resolve_derived(
        snapshot,
        payload,
        canonical=(
            derived_snapshot_provider()
            if derived_snapshot_provider is not None
            else None
        ),
    )
    config = optimization_config(payload)
    production_required = resolve_target_ids(
        current,
        payload["targets"]["production_required"],
        default_all=True,
    )
    return TrainingRequest(
        run_id=run_id,
        candidate_id=candidate_id,
        data_path=str(source),
        preprocess_version=snapshot.preprocessing_version,
        generation_id=snapshot.generation_id,
        registry_fingerprint=snapshot.registry_fingerprint,
        ordered_ml_fingerprint=snapshot.ordered_ml_fingerprint,
        derived_semantics_fingerprint=snapshot.derived_semantics_fingerprint,
        one_hot_fingerprint=snapshot.one_hot_fingerprint,
        registry_payload_json=json.dumps(snapshot.to_payload(), ensure_ascii=False),
        optimization_config_json=json.dumps(asdict(config), sort_keys=True),
        derived_evaluation_json=json.dumps(asdict(derived), ensure_ascii=False),
        resolved_experiment_json=resolved.to_json(),
        experiment_contract_fingerprint=resolved.fingerprint,
        production_required_target_ids_json=json.dumps(production_required),
        contains_unpublished_features=bool(
            payload["features"]["experimental_derived"]
        ),
        exploratory_feature_policy=bool(
            payload["features"]["included"] or payload["features"]["excluded"]
        ),
        target_scoped_exploratory=(
            set(snapshot.target_presentation_order)
            != set(current.target_presentation_order)
        ),
        execution_owner=execution_owner,
        campaign_id=campaign_id,
    )
