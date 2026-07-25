"""Terminal result construction for the QProcess training adapter."""

from apps.train.state.training_run_state import TrainingRequest, TrainingResult


def process_result(
    request: TrainingRequest, status: str, message: str
) -> TrainingResult:
    return TrainingResult(
        run_id=request.run_id,
        status=status,
        model_path=request.model_output_path,
        message=message,
        generation_id=request.generation_id,
        registry_fingerprint=request.registry_fingerprint,
    )
