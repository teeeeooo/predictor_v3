"""Command construction for the QProcess training adapter."""

from __future__ import annotations

from pathlib import Path

from apps.train.state.training_run_state import TrainingRequest


def training_process_arguments(
    request: TrainingRequest,
    temporary_artifact: Path,
    job_module: str,
    extra_args: tuple[str, ...],
) -> list[str]:
    return [
        "-B",
        "-m",
        job_module,
        "--run-id",
        request.run_id,
        "--data-path",
        request.data_path,
        "--model-output-path",
        request.model_output_path,
        "--temp-model-output-path",
        str(temporary_artifact),
        *(
            ["--registry-payload-json", request.registry_payload_json]
            if request.registry_payload_json
            else []
        ),
        *(
            ["--optimization-config-json", request.optimization_config_json]
            if request.optimization_config_json
            else []
        ),
        *(
            ["--derived-evaluation-json", request.derived_evaluation_json]
            if request.derived_evaluation_json
            else []
        ),
        *(
            [
                "--confirmation-fixed-parameters-json",
                request.confirmation_fixed_parameters_json,
            ]
            if request.confirmation_fixed_parameters_json
            else []
        ),
        *(
            [
                "--confirmation-fixed-features-json",
                request.confirmation_fixed_features_json,
            ]
            if request.confirmation_fixed_features_json
            else []
        ),
        *extra_args,
    ]


def default_temporary_artifact(request: TrainingRequest) -> Path:
    model_path = Path(request.model_output_path)
    return model_path.with_name(f".{model_path.name}.{request.run_id}.tmp")
