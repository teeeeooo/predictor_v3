"""Child-process entrypoint for one training run."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from apps.train.state.training_run_state import TrainingRequest
_CANCELLED = False


def _handle_signal(_signum, _frame) -> None:  # noqa: ANN001
    global _CANCELLED
    _CANCELLED = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--model-output-path", required=True)
    parser.add_argument("--temp-model-output-path")
    parser.add_argument("--dev-fast", action="store_true")
    parser.add_argument("--dev-rows", type=int, default=12)
    parser.add_argument("--dev-predict-delay-ms", type=int, default=0)
    parser.add_argument("--hang-before-start", action="store_true")
    parser.add_argument("--registry-payload-json", default="")
    parser.add_argument("--optimization-config-json", default="")
    parser.add_argument("--derived-evaluation-json", default="")
    return parser.parse_args()


def emit(event: dict) -> None:
    print(json.dumps(event, ensure_ascii=False), flush=True)


def emit_log(run_id: str, message: str, level: str = "info") -> None:
    emit({"type": "log", "run_id": run_id, "message": message, "level": level})


def emit_progress(
    run_id: str,
    completed: int,
    total: int,
    message: str,
    *,
    indeterminate: bool = True,
) -> None:
    emit(
        {
            "type": "progress",
            "run_id": run_id,
            "completed": completed,
            "total": total,
            "message": message,
            "indeterminate": indeterminate,
        }
    )


def emit_training_started(run_id: str) -> None:
    emit({"type": "training_started", "run_id": run_id})


def emit_result(
    request: TrainingRequest,
    status: str,
    *,
    summary: str = "",
    log_path: str = "",
    message: str = "",
    evidence_path: str = "",
) -> None:
    emit(
        {
            "type": "result",
            "run_id": request.run_id,
            "status": status,
            "summary": summary,
            "model_path": request.model_output_path,
            "log_path": log_path,
            "message": message,
            "generation_id": request.generation_id,
            "registry_fingerprint": request.registry_fingerprint,
            "evidence_path": evidence_path,
        }
    )


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_signal)
    args = parse_args()
    registry_payload = json.loads(args.registry_payload_json) if args.registry_payload_json else {}
    request = TrainingRequest(
        run_id=args.run_id,
        data_path=args.data_path,
        model_output_path=args.model_output_path,
        registry_payload_json=args.registry_payload_json,
        preprocess_version=str(registry_payload.get("preprocessing_version", "v1.0")),
        generation_id=str(registry_payload.get("generation_id", "")),
        registry_fingerprint=str(registry_payload.get("registry_fingerprint", "")),
        ordered_ml_fingerprint=str(registry_payload.get("ordered_ml_fingerprint", "")),
        derived_semantics_fingerprint=str(registry_payload.get("derived_semantics_fingerprint", "")),
        one_hot_fingerprint=str(registry_payload.get("one_hot_fingerprint", "")),
    )
    temp_model_path = Path(
        args.temp_model_output_path
        or Path(request.model_output_path).with_name(
            f".{Path(request.model_output_path).name}.{request.run_id}.tmp"
        )
    )
    final_model_path = Path(request.model_output_path)

    if args.hang_before_start:
        emit_log(request.run_id, "Training job hang requested for cancel smoke.")
        while not _CANCELLED:
            time.sleep(0.1)
        cleanup_temp(temp_model_path)
        emit_result(request, "cancelled", message="Training process cancelled.")
        return 0

    log_path = ""

    def _log(message: str) -> None:
        nonlocal log_path
        text = str(message)
        marker = "학습 로그 저장 완료:"
        if marker in text:
            log_path = text.split(marker, 1)[1].strip()
        emit_log(request.run_id, text)

    try:
        temp_model_path.parent.mkdir(parents=True, exist_ok=True)
        emit_progress(request.run_id, 0, 0, "Training started.", indeterminate=True)
        if args.dev_fast:
            summary = _run_dev_fast(request, temp_model_path, args)
        else:
            from core.data_definition.target_registry.runtime import ModelRegistrySnapshot

            output, evidence_path = run_production_training(
                request,
                temp_model_path,
                log_callback=_log,
                registry_snapshot=(
                    ModelRegistrySnapshot.from_payload(json.loads(request.registry_payload_json))
                    if request.registry_payload_json else None
                ),
                optimization_config=_optimization_config(
                    args.optimization_config_json
                ),
                derived_evaluation_snapshot=_derived_evaluation_snapshot(
                    args.derived_evaluation_json
                ),
            )
            summary = output.summary
        if _CANCELLED:
            cleanup_temp(temp_model_path)
            emit_result(request, "cancelled", message="Training process cancelled.")
            return 0
        final_model_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temp_model_path, final_model_path)
        emit_progress(request.run_id, 1, 1, "Training finished.", indeterminate=False)
        emit_result(
            request,
            (
                output.evidence.status
                if not args.dev_fast
                else "complete"
            ),
            summary=summary,
            log_path=log_path,
            message="Training completed.",
            evidence_path=(
                str(evidence_path)
                if not args.dev_fast
                else ""
            ),
        )
        return 0 if args.dev_fast or output.evidence.status == "complete" else 2
    except Exception as exc:
        cleanup_temp(temp_model_path)
        emit_log(request.run_id, str(exc).splitlines()[0], "error")
        emit_result(request, "error", message=str(exc).splitlines()[0])
        return 1


def run_production_training(
    request: TrainingRequest,
    temp_model_path: Path,
    *,
    log_callback,
    registry_snapshot=None,  # noqa: ANN001
    optimization_config=None,  # noqa: ANN001
    derived_evaluation_snapshot=None,  # noqa: ANN001
):
    """Run the production Core owner and persist its structured evidence."""
    from core.ml.training import train_all_models_with_analysis

    output = train_all_models_with_analysis(
        data_path=request.data_path,
        log_callback=log_callback,
        model_output_path=str(temp_model_path),
        registry_snapshot=registry_snapshot,
        optimization_config=optimization_config,
        derived_evaluation_snapshot=derived_evaluation_snapshot,
        training_started_callback=lambda: emit_training_started(request.run_id),
    )
    evidence_path = Path(request.model_output_path).parent / "core_training_evidence.json"
    evidence_path.write_text(
        json.dumps(
            output.evidence.to_payload(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output, evidence_path


def _optimization_config(payload_json: str):  # noqa: ANN202
    if not payload_json:
        return None
    from core.ml.training_results import TrainingOptimizationConfig

    payload = json.loads(payload_json)
    if not isinstance(payload, dict):
        raise ValueError("optimization configuration must be an object")
    allowed = set(TrainingOptimizationConfig.__dataclass_fields__)
    if set(payload) != allowed:
        raise ValueError("optimization configuration fields are invalid")
    config = TrainingOptimizationConfig(**payload)
    config.validate()
    return config


def _derived_evaluation_snapshot(payload_json: str):  # noqa: ANN202
    if not payload_json:
        return None
    from core.data_definition.derived.evaluator import (
        DerivedEvaluationDefinition,
        DerivedEvaluationSnapshot,
        DerivedEvaluatorInput,
    )

    payload = json.loads(payload_json)
    if not isinstance(payload, dict) or set(payload) != {
        "generation_id", "definitions", "evaluator_inputs"
    }:
        raise ValueError("derived evaluation snapshot fields are invalid")
    return DerivedEvaluationSnapshot(
        generation_id=str(payload["generation_id"]),
        definitions=tuple(
            DerivedEvaluationDefinition(**item) for item in payload["definitions"]
        ),
        evaluator_inputs=tuple(
            DerivedEvaluatorInput(**item) for item in payload["evaluator_inputs"]
        ),
    )


def _run_dev_fast(request: TrainingRequest, temp_model_path: Path, args: argparse.Namespace) -> str:
    from dataclasses import replace

    from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend

    backend = DevFastTrainingBackend(
        rows=args.dev_rows,
        predict_delay_ms=args.dev_predict_delay_ms,
    )
    temp_request = replace(request, model_output_path=str(temp_model_path))
    result = backend(
        temp_request,
        log_callback=_emit_payload_log,
        progress_callback=_emit_payload_progress,
        training_started_callback=lambda: emit_training_started(request.run_id),
    )
    if result.status != "complete":
        raise RuntimeError(result.message or "DEV fast training failed.")
    return result.summary


def _emit_payload_log(event) -> None:  # noqa: ANN001
    emit({"type": "log", "run_id": event.run_id, "message": event.message, "level": event.level})


def _emit_payload_progress(progress) -> None:  # noqa: ANN001
    emit(
        {
            "type": "progress",
            "run_id": progress.run_id,
            "completed": progress.completed,
            "total": progress.total,
            "message": progress.message,
            "indeterminate": progress.indeterminate,
        }
    )


def cleanup_temp(path: Path) -> None:
    path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
