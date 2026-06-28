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
from core.ml.artifacts import MODEL_FILE


_CANCELLED = False


def _handle_signal(_signum, _frame) -> None:  # noqa: ANN001
    global _CANCELLED
    _CANCELLED = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--model-output-path", default=MODEL_FILE)
    parser.add_argument("--temp-model-output-path")
    parser.add_argument("--dev-fast", action="store_true")
    parser.add_argument("--dev-rows", type=int, default=12)
    parser.add_argument("--dev-predict-delay-ms", type=int, default=0)
    parser.add_argument("--hang-before-start", action="store_true")
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


def emit_result(
    request: TrainingRequest,
    status: str,
    *,
    summary: str = "",
    log_path: str = "",
    message: str = "",
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
        }
    )


def main() -> int:
    signal.signal(signal.SIGTERM, _handle_signal)
    args = parse_args()
    request = TrainingRequest(
        run_id=args.run_id,
        data_path=args.data_path,
        model_output_path=args.model_output_path,
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
            from core.ml.training import train_all_models

            summary = train_all_models(
                data_path=request.data_path,
                log_callback=_log,
                model_output_path=str(temp_model_path),
            )
        if _CANCELLED:
            cleanup_temp(temp_model_path)
            emit_result(request, "cancelled", message="Training process cancelled.")
            return 0
        final_model_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temp_model_path, final_model_path)
        emit_progress(request.run_id, 1, 1, "Training finished.", indeterminate=False)
        emit_result(
            request,
            "complete",
            summary=summary,
            log_path=log_path,
            message="Training completed.",
        )
        return 0
    except Exception as exc:
        cleanup_temp(temp_model_path)
        emit_log(request.run_id, str(exc).splitlines()[0], "error")
        emit_result(request, "error", message=str(exc).splitlines()[0])
        return 1


def _run_dev_fast(request: TrainingRequest, temp_model_path: Path, args: argparse.Namespace) -> str:
    from dataclasses import replace

    from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend

    backend = DevFastTrainingBackend(
        rows=args.dev_rows,
        predict_delay_ms=args.dev_predict_delay_ms,
    )
    temp_request = replace(request, model_output_path=str(temp_model_path))
    result = backend(temp_request, log_callback=_emit_payload_log, progress_callback=_emit_payload_progress)
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
